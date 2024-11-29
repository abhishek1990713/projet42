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

import cv2
import numpy as np
import time

# Super-resolution function
def super_resolution(image):
    """
    Applies super-resolution using the FSRCNN model to upscale the image.
    """
    model_path = r"C:\Citidev\SuperResolution\FSRCNN_Tensorflow-master\models\FSRCNN_x2.pb"

    # Create and configure the super-resolution model
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    sr.readModel(model_path)
    sr.setModel("fsrcnn", 2)

    print("Applying super-resolution...")
    start = time.time()
    upscaled_image = sr.upsample(image)
    print(f"Super-resolution completed in {time.time() - start:.2f} seconds.")

    return upscaled_image

# Quality checking function
def check_image_quality(image, thresholds=None):
    if thresholds is None:
        thresholds = {
            "blurriness": 4000,
            "noise": 0.2,
            "brightness_low": 200,
            "brightness_high": 500,
            "contrast": 200,
            "text_density": 0.04
        }

    # Ensure the image is valid
    if image is None or image.size == 0:
        return "Bad"

    # Quality metrics calculation
    blurriness = calculate_blurriness(image)
    noise_level = calculate_noise(image)
    brightness = calculate_brightness(image)
    contrast = calculate_contrast(image)
    text_density = calculate_text_density(image)

    # Quality checks
    quality_checks = {
        "blurriness": blurriness > thresholds["blurriness"],
        "noise": noise_level < thresholds["noise"],
        "brightness": thresholds["brightness_low"] <= brightness <= thresholds["brightness_high"],
        "contrast": contrast > thresholds["contrast"],
        "text_density": text_density > thresholds["text_density"]
    }

    # Count how many conditions are True
    true_conditions = sum(quality_checks.values())

    # Determine image quality
    return "Good" if true_conditions >= 3 else "Bad"

# Process image function
def process_image(image_path, max_attempts=2):
    """Main function to process image quality with iterative improvement."""
    image = cv2.imread(image_path)
    if image is None or image.size == 0:
        print("Image not found or invalid format.")
        return "Error"

    for attempt in range(max_attempts):
        print(f"Attempt {attempt + 1}: Checking image quality...")
        result = check_image_quality(image)

        if result == "Good":
            print("Image is Good.")
            return "Good"

        print("Image is Bad. Applying super-resolution...")
        image = super_resolution(image)

        # Validate the processed image
        if image is None or image.size == 0:
            print("Super-resolution resulted in an invalid image.")
            return "Error"

    print("Image quality could not be improved further.")
    return "Bad"

# Example usage
image_path = r"C:\CitiDev Projects\Trade_data\AB\310093900 21530315_1_2303786310093900.007.tiff"
final_result = process_image(image_path)

if final_result == "Bad":
    print("Final result: Image is Bad after two attempts.")
elif final_result == "Good":
    print("Final result: Image is Good.")
