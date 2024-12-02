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
from PIL import Image
import time

# Function to check and adjust DPI
def check_and_adjust_dpi(image_path, min_dpi=300):
    """
    Checks the DPI of the image and increases it if below the required threshold.
    """
    print("Checking DPI...")
    pil_image = Image.open(image_path)

    # Extract DPI info
    dpi = pil_image.info.get("dpi", (200, 200))[0]
    print(f"Current DPI: {dpi}")

    if dpi < min_dpi:
        print(f"DPI is lower than {min_dpi}. Adjusting DPI...")
        pil_image.save("temp_image_with_dpi.png", dpi=(min_dpi, min_dpi))
        pil_image = Image.open("temp_image_with_dpi.png")
        updated_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        return updated_image, "Bad"  # Return updated image and mark as "Bad"
    else:
        print("DPI is sufficient.")
        image = cv2.imread(image_path)
        return image, "Good"  # No DPI adjustment needed

# Function to adjust pixel dimensions if needed
def adjust_pixel_dimensions(image, min_pixels=300):
    """
    Adjusts the pixel dimensions of the image if below the required threshold.
    """
    height, width = image.shape[:2]
    print(f"Current dimensions: {width}x{height}")

    if height < min_pixels or width < min_pixels:
        print(f"Dimensions are smaller than {min_pixels}px. Resizing...")
        scale_factor = max(min_pixels / width, min_pixels / height)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        print(f"Resized to: {new_width}x{new_height}")
    else:
        print("Dimensions are sufficient.")

    return image

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

    # Display the upscaled image
    image_to_show = Image.fromarray(cv2.cvtColor(upscaled_image, cv2.COLOR_BGR2RGB))
    image_to_show.show(title="Super-Resolution Image")

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
    for attempt in range(max_attempts):
        print(f"Attempt {attempt + 1}: Checking image quality...")

        # Check and adjust DPI
        image, dpi_result = check_and_adjust_dpi(image_path)

        if dpi_result == "Bad":
            print("DPI was too low and has been adjusted.")

        # Check pixel dimensions
        image = adjust_pixel_dimensions(image)

        # Check overall quality
        result = check_image_quality(image)
        if result == "Good":
            print("Image is Good.")
            return "Good"

        print("Image is Bad. Applying super-resolution...")
        image = super_resolution(image)

    print("Image quality could not be improved further.")
    return "Bad"

# Example usage
image_path = r"C:\CitiDev Projects\Trade_data\AB\310093900 21530315_1_2303786310093900.007.tiff"
final_result = process_image(image_path)

if final_result == "Bad":
    print("Final result: Image is Bad after two attempts.")
elif final_result == "Good":
    print("Final result: Image is Good.")

