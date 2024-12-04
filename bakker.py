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

# Threshold values for quality checks
THRESHOLD = {
    "blurriness": 50,
    "brightness": (50, 200),
    "contrast": 50,
    "noise_level": 30,
    "skew_angle": 5,
    "text_area": 20
}

# Define quality check and adjustment functions
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
    brightness = check_brightness(image)
    factor = target / brightness
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
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
    angles = []
    if lines is not None:
        for rho, theta in lines[:, 0]:
            angles.append(np.degrees(theta) - 90)
    return np.mean(angles) if angles else 0

def deskew_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, -angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

def check_text_area(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    text_area = cv2.countNonZero(thresh)
    total_area = image.shape[0] * image.shape[1]
    return (text_area / total_area) * 100

def process_image(input_image_path, output_image_path):
    image = cv2.imread(input_image_path)

    # Metrics to track adjustments
    metrics = {}

    # Blurriness check and adjustment
    blurriness = check_blurriness(image)
    metrics["blurriness_before"] = blurriness
    if blurriness < THRESHOLD["blurriness"]:
        image = adjust_blurriness(image)
        metrics["blurriness_after"] = check_blurriness(image)
    else:
        metrics["blurriness_after"] = blurriness

    # Brightness check and adjustment
    brightness = check_brightness(image)
    metrics["brightness_before"] = brightness
    if not (THRESHOLD["brightness"][0] <= brightness <= THRESHOLD["brightness"][1]):
        image = adjust_brightness(image)
        metrics["brightness_after"] = check_brightness(image)
    else:
        metrics["brightness_after"] = brightness

    # Contrast check and adjustment
    contrast = check_contrast(image)
    metrics["contrast_before"] = contrast
    if contrast < THRESHOLD["contrast"]:
        image = adjust_contrast(image)
        metrics["contrast_after"] = check_contrast(image)
    else:
        metrics["contrast_after"] = contrast

    # Noise level check and adjustment
    noise_level = check_noise_level(image)
    metrics["noise_level_before"] = noise_level
    if noise_level > THRESHOLD["noise_level"]:
        image = denoise_image(image)
        metrics["noise_level_after"] = check_noise_level(image)
    else:
        metrics["noise_level_after"] = noise_level

    # Skew angle check and adjustment
    skew_angle = check_skew_angle(image)
    metrics["skew_angle_before"] = skew_angle
    if abs(skew_angle) > THRESHOLD["skew_angle"]:
        image = deskew_image(image, skew_angle)
        metrics["skew_angle_after"] = check_skew_angle(image)
    else:
        metrics["skew_angle_after"] = skew_angle

    # Text area coverage check
    text_area = check_text_area(image)
    metrics["text_area_coverage"] = text_area

    # Save the processed image
    cv2.imwrite(output_image_path, image)

    # Print metrics
    print(f"Metrics for {input_image_path}: {metrics}")

# Example usage
input_image_path = "img.png"  # Replace with your input image path
output_image_path = "output.png"  # Replace with your desired output image path

process_image(input_image_path, output_image_path)
