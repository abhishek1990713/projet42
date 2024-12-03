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
import os
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer

# Function to check and adjust DPI and pixel dimensions
def check_and_adjust_dpi_and_pixels(image_path, min_dpi=300, min_width=550, min_height=330):
    """
    Checks the DPI and pixel dimensions of the image. 
    Adjusts the DPI and resizes the image if required.
    """
    print("Checking image properties...")
    pil_image = Image.open(image_path)

    # Get the current DPI
    dpi = pil_image.info.get("dpi", (200, 200))[0]  # Default DPI is 200 if metadata is missing
    print(f"Current DPI: {dpi}")

    # Get current dimensions
    width, height = pil_image.size
    print(f"Current Dimensions (WxH): {width}x{height}")

    adjustments_made = False

    # Adjust DPI if below the threshold
    if dpi < min_dpi:
        print(f"DPI is lower than {min_dpi}. Adjusting DPI to {min_dpi}...")
        temp_path = "temp_image_with_dpi.png"
        pil_image.save(temp_path, dpi=(min_dpi, min_dpi))
        pil_image = Image.open(temp_path)  # Reload the updated image
        adjustments_made = True

    # Adjust pixel dimensions if below the threshold
    if width < min_width or height < min_height:
        print(f"Image dimensions are smaller than {min_width}x{min_height}. Resizing the image...")
        resized_image = pil_image.resize((min_width, min_height), Image.ANTIALIAS)
        temp_path = "temp_image_resized.png"
        resized_image.save(temp_path, dpi=(min_dpi, min_dpi))
        pil_image = Image.open(temp_path)  # Reload the updated image
        adjustments_made = True

    # Convert the updated PIL image to OpenCV format
    updated_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    if adjustments_made:
        print("Image properties were adjusted.")
        return updated_image, "Bad"
    else:
        print("Image properties are sufficient.")
        return updated_image, "Good"

# SEGAN-based image enhancement
def apply_segan_enhancement(image, save_path):
    """
    Applies SEGAN-based super-resolution to enhance the quality of the image.
    Saves the enhanced image.
    """
    print("Applying SEGAN-based enhancement...")

    # Define the SEGAN model
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
    model_path = r"C:\Citidev\SuperResolution\FSRCNN_Tensorflow-master\models\x.pth"

    upsampler = RealESRGANer(
        scale=4,
        model_path=model_path,
        dni_weight=None,
        model=model,
        tile=0,
        tile_pad=10,
        pre_pad=10,
        half=False,
        device="cpu",
        gpu_id=None
    )

    # Enhance the image
    output, _ = upsampler.enhance(image, outscale=2)
    print("SEGAN-based enhancement applied successfully.")

    # Save the enhanced image
    cv2.imwrite(save_path, output)
    print(f"Enhanced image saved at {save_path}")

    return output

# Function to calculate image quality parameters
def check_image_quality(image):
    """
    Function to check the quality of the image (blurriness, noise, brightness, contrast, text density).
    Returns "Good" or "Bad".
    """
    print("Checking image quality...")
    # Check blurriness
    blurriness = calculate_blurriness(image)
    # Check noise level
    noise_level = calculate_noise(image)
    # Check brightness
    brightness = calculate_brightness(image)
    # Check contrast
    contrast = calculate_contrast(image)
    # Check text density
    text_density = calculate_text_density(image)

    # Set thresholds for image quality
    thresholds = {
        "blurriness": 4000, 
        "noise": 0.2, 
        "brightness_low": 200, 
        "brightness_high": 500, 
        "contrast": 200, 
        "text_density": 0.04
    }

    # Evaluate quality
    quality = {
        "blurriness": blurriness < thresholds["blurriness"],
        "noise": noise_level < thresholds["noise"],
        "brightness": thresholds["brightness_low"] < brightness <= thresholds["brightness_high"],
        "contrast": contrast > thresholds["contrast"],
        "text_density": text_density > thresholds["text_density"]
    }

    print("Blurriness:", quality["blurriness"])
    print("Noise:", quality["noise"])
    print("Brightness:", quality["brightness"])
    print("Contrast:", quality["contrast"])
    print("Text Density:", quality["text_density"])

    # If 3 out of 5 are bad, return "Bad", else "Good"
    if sum(quality.values()) >= 3:
        return "Bad"
    else:
        return "Good"

# Dummy function to calculate blurriness
def calculate_blurriness(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()

# Dummy function to calculate noise level
def calculate_noise(image):
    return np.random.rand()  # Placeholder for actual noise calculation

# Dummy function to calculate brightness
def calculate_brightness(image):
    return np.mean(image)

# Dummy function to calculate contrast
def calculate_contrast(image):
    return np.std(image)

# Dummy function to calculate text density
def calculate_text_density(image):
    return 0.05  # Placeholder value for text density calculation

# Main process function
def process_image(image_path, save_dir, min_dpi=300, min_width=550, min_height=330):
    """
    Main function to process the image. Checks and adjusts DPI and pixel dimensions if necessary.
    """
    print("Starting image processing...")

    # First attempt to check and adjust the image
    image, status = check_and_adjust_dpi_and_pixels(image_path, min_dpi, min_width, min_height)

    # Check image quality
    quality_status = check_image_quality(image)

    if quality_status == "Bad":
        print("Attempt 1: Image is bad. Applying SEGAN-based enhancement...")
        # Apply SEGAN-based enhancement after the first bad attempt
        enhanced_image_path = os.path.join(save_dir, "enhanced_image.jpg")
        image = apply_segan_enhancement(image, enhanced_image_path)
        # Second attempt to check the adjusted image
        quality_status = check_image_quality(image)
        if quality_status == "Bad":
            print("Attempt 2: Image is still bad after adjustments. Stopping process.")
        else:
            print("Attempt 2: Image is now good after enhancement.")
    else:
        print("Attempt 1: Image is good. No adjustments needed.")

    print("Processing completed.")
    return image, quality_status

# Example usage
image_path = r"C:\CitiDev\SuperResolution\Input Images\sample.jpg"
save_dir = r"C:\CitiDev\SuperResolution\Enhanced_Images"

# Ensure the save directory exists
os.makedirs(save_dir, exist_ok=True)

# Process the image
image, status = process_image(image_path, save_dir)

# Show the final image
if image is not None:
    pil_final_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    pil_final_image.show()

if status == "Bad":
    print("Final Status: Image properties were adjusted but still bad after two attempts.")
elif status == "Good":
    print("Final Status: Image properties are good.")
