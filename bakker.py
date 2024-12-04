from flask import Flask, jsonify, request
import ssl

app = Flask(__name__)

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Hello, client! Connection is secure."})

if __name__ == '__main__':
    # SSL context configuration
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.verify_mode = ssl.CERT_REQUIRED  # Require client certificate verification
    context.load_cert_chain(certfile='certificate.cer', keyfile='private.key')
    context.load_verify_locations(cafile='CA.pem')  # Load the CA certificate for client verification
    
    # Run the Flask app with SSL enabled
    app.run(host='127.0.0.1', port=8013, ssl_context=context)

# Define constants for the model path and other parameters
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import os
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("processing.log"), logging.StreamHandler()],
)

THRESHOLD = {
    "blurriness": 50,
    "brightness": (50, 200),
    "contrast": 50,
    "noise_level": 30,
    "skew_angle": 5,
    "text_area": 20,
}


def adjust_dpi(image_path, target_dpi=300):
    img = Image.open(image_path)
    current_dpi = img.info.get("dpi", (72, 72))[0]
    if current_dpi != target_dpi:
        img = img.resize(img.size, Image.Resampling.LANCZOS)
        img.save(image_path, dpi=(target_dpi, target_dpi))
    return cv2.imread(image_path)


def check_blurriness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()


def adjust_blurriness(image):
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    return cv2.filter2D(image, -1, kernel)


def check_brightness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return np.mean(gray)


def adjust_brightness(image, target=120):
    factor = target / check_brightness(image)
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    enhancer = ImageEnhance.Brightness(pil_image)
    return cv2.cvtColor(np.array(enhancer.enhance(factor)), cv2.COLOR_RGB2BGR)


def check_contrast(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return np.std(gray)


def adjust_contrast(image, factor=1.5):
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    enhancer = ImageEnhance.Contrast(pil_image)
    return cv2.cvtColor(np.array(enhancer.enhance(factor)), cv2.COLOR_RGB2BGR)


def check_noise_level(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    return np.mean(edges)


def denoise_image(image):
    return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)


def check_skew_angle(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
    angles = [np.degrees(theta) - 90 for rho, theta in (lines[:, 0] if lines is not None else [])]
    return np.mean(angles) if angles else 0


def deskew_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, -angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def process_image(input_image_path, output_image_path):
    logging.info(f"Processing image: {input_image_path}")
    try:
        image = adjust_dpi(input_image_path)

        # Blurriness adjustment
        blurriness = check_blurriness(image)
        if blurriness < THRESHOLD["blurriness"]:
            image = adjust_blurriness(image)

        # Brightness adjustment
        brightness = check_brightness(image)
        if not THRESHOLD["brightness"][0] < brightness < THRESHOLD["brightness"][1]:
            image = adjust_brightness(image)

        # Contrast adjustment
        contrast = check_contrast(image)
        if contrast < THRESHOLD["contrast"]:
            image = adjust_contrast(image)

        # Noise reduction
        noise = check_noise_level(image)
        if noise > THRESHOLD["noise_level"]:
            image = denoise_image(image)

        # Deskewing
        skew_angle = check_skew_angle(image)
        if abs(skew_angle) > THRESHOLD["skew_angle"]:
            image = deskew_image(image, skew_angle)

        cv2.imwrite(output_image_path, image)
        logging.info(f"Saved processed image: {output_image_path}")
        return {"status": "success", "output": output_image_path}
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        return {"status": "error", "message": str(e)}
