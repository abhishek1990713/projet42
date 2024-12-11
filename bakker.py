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

# constant.py
# preprocess.py

import cv2
import numpy as np
from PIL import Image, ImageEnhance

# Define the threshold values
THRESHOLD = {
    "dpi": 300,
    "min_width": 550,
    "min_height": 330,
    "blurriness": 50,
    "brightness": (50, 200),
    "contrast": 50,
    "noise_level": 30,
    "skew_angle": 5,
    "text_area": 20
}

# Ensure DPI is at least 300
def check_and_adjust_dpi(image_path):
    metrics = {}
    with Image.open(image_path) as img:
        dpi = img.info.get("dpi", (72, 72))  # Default DPI is 72 if not set
        metrics["dpi_before"] = dpi
        if dpi[0] < THRESHOLD["dpi"] or dpi[1] < THRESHOLD["dpi"]:
            # Update DPI to 300
            updated_path = image_path.replace(".png", "_updated.png")
            img.save(updated_path, dpi=(300, 300))
            metrics["dpi_after"] = (300, 300)
            return updated_path, metrics
        metrics["dpi_after"] = dpi
        return image_path, metrics

# Ensure image dimensions are at least 550x330
def check_and_resize_dimensions(image):
    metrics = {}
    height, width = image.shape[:2]
    metrics["image_size_before"] = (width, height)
    if width < THRESHOLD["min_width"] or height < THRESHOLD["min_height"]:
        # Resize image while maintaining aspect ratio
        new_width = max(THRESHOLD["min_width"], width)
        new_height = max(THRESHOLD["min_height"], height)
        resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        metrics["image_size_after"] = (new_width, new_height)
        return resized_image, metrics
    metrics["image_size_after"] = (width, height)
    return image, metrics

# Blurriness check
def check_blurriness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

# Blurriness adjustment
def adjust_blurriness(image):
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    return cv2.filter2D(image, -1, kernel)

# Brightness check
def check_brightness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return np.mean(gray)

# Brightness adjustment
def adjust_brightness(image, target=120):
    brightness = check_brightness(image)
    factor = target / brightness
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    enhancer = ImageEnhance.Brightness(pil_image)
    return cv2.cvtColor(np.array(enhancer.enhance(factor)), cv2.COLOR_RGB2BGR)

# Contrast check
def check_contrast(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return np.std(gray)

# Contrast adjustment
def adjust_contrast(image, factor=1.5):
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    enhancer = ImageEnhance.Contrast(pil_image)
    return cv2.cvtColor(np.array(enhancer.enhance(factor)), cv2.COLOR_RGB2BGR)

# Noise level check
def check_noise_level(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    return np.mean(edges)

# Denoising the image
def denoise_image(image):
    return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

# Skew angle check
def check_skew_angle(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
    angles = []
    if lines is not None:
        for rho, theta in lines[:, 0]:
            angle = np.degrees(theta) - 90
            if angle < -45:
                angle += 90
            elif angle > 45:
                angle -= 90
            angles.append(angle)
    return np.median(angles) if angles else 0

# Deskew the image
def deskew_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, -angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

# Text area check
def check_text_area(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    text_area = cv2.countNonZero(thresh)
    total_area = image.shape[0] * image.shape[1]
    return (text_area / total_area) * 100

# Process image (all checks and adjustments)
def process_image(image_path):
    metrics = {}

    # Step 1: Check and adjust DPI
    image_path, dpi_metrics = check_and_adjust_dpi(image_path)
    metrics.update(dpi_metrics)

    # Step 2: Load image using OpenCV
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Unable to load image at {image_path}")

    # Step 3: Check and adjust dimensions
    image, size_metrics = check_and_resize_dimensions(image)
    metrics.update(size_metrics)

    # Step 4: Blurriness
    blurriness = check_blurriness(image)
    metrics["blurriness_before"] = blurriness
    if blurriness < THRESHOLD["blurriness"]:
        image = adjust_blurriness(image)
    metrics["blurriness_after"] = check_blurriness(image)

    # Step 5: Brightness
    brightness = check_brightness(image)
    metrics["brightness_before"] = brightness
    if not (THRESHOLD["brightness"][0] <= brightness <= THRESHOLD["brightness"][1]):
        image = adjust_brightness(image)
    metrics["brightness_after"] = check_brightness(image)

    # Step 6: Contrast
    contrast = check_contrast(image)
    metrics["contrast_before"] = contrast
    if contrast < THRESHOLD["contrast"]:
        image = adjust_contrast(image)
    metrics["contrast_after"] = check_contrast(image)

    # Step 7: Noise Level
    noise_level = check_noise_level(image)
    metrics["noise_level_before"] = noise_level
    if noise_level > THRESHOLD["noise_level"]:
        image = denoise_image(image)
    metrics["noise_level_after"] = check_noise_level(image)

    # Step 8: Skew Angle
    skew_angle = check_skew_angle(image)
    metrics["skew_angle_before"] = skew_angle
    if abs(skew_angle) > THRESHOLD["skew_angle"]:
        image = deskew_image(image, skew_angle)
    metrics["skew_angle_after"] = check_skew_angle(image)

    # Step 9: Text Area Coverage
    text_area = check_text_area(image)
    metrics["text_area_coverage"] = text_area

    return image, metrics
