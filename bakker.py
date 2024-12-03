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
SEGAN_MODEL_PATH = r"C:\Citidev\SuperResolution\FSRCNN_Tensorflow-master\models\x.pth"
INPUT_IMAGE_PATH = r"C:\CitiDev\SuperResolution\Input Images\sample.jpg"
OUTPUT_IMAGE_DIR = r"C:\CitiDev\SuperResolution\Enhanced_Images"
MIN_DPI = 300
MIN_WIDTH = 550
MIN_HEIGHT = 330
import cv2
import numpy as np
from PIL import Image
import os
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from constant import SEGAN_MODEL_PATH, INPUT_IMAGE_PATH, OUTPUT_IMAGE_DIR, MIN_DPI, MIN_WIDTH, MIN_HEIGHT

# Function to check and adjust DPI and pixel dimensions
def check_and_adjust_dpi_and_pixels(image_path, min_dpi=MIN_DPI, min_width=MIN_WIDTH, min_height=MIN_HEIGHT):
    print("Checking image properties...")
    pil_image = Image.open(image_path)

    # Get the current DPI
    dpi = pil_image.info.get("dpi", (200, 200))[0]
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
        pil_image = Image.open(temp_path)
        adjustments_made = True

    # Adjust pixel dimensions if below the threshold
    if width < min_width or height < min_height:
        print(f"Image dimensions are smaller than {min_width}x{min_height}. Resizing the image...")
        resized_image = pil_image.resize((min_width, min_height), Image.ANTIALIAS)
        temp_path = "temp_image_resized.png"
        resized_image.save(temp_path, dpi=(min_dpi, min_dpi))
        pil_image = Image.open(temp_path)
        adjustments_made = True

    updated_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    if adjustments_made:
        print("Image properties were adjusted.")
        return updated_image, "Bad"
    else:
        print("Image properties are sufficient.")
        return updated_image, "Good"

# SEGAN-based image enhancement
def apply_segan_enhancement(image, save_path):
    print("Applying SEGAN-based enhancement...")
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)

    upsampler = RealESRGANer(
        scale=4,
        model_path=SEGAN_MODEL_PATH,
        dni_weight=None,
        model=model,
        tile=0,
        tile_pad=10,
        pre_pad=10,
        half=False,
        device="cpu",
        gpu_id=None
    )

    output, _ = upsampler.enhance(image, outscale=2)
    print("SEGAN-based enhancement applied successfully.")

    cv2.imwrite(save_path, output)
    print(f"Enhanced image saved at {save_path}")
    return output

# Function to calculate image quality parameters
def check_image_quality(image):
    print("Checking image quality...")
    blurriness = calculate_blurriness(image)
    noise_level = calculate_noise(image)
    brightness = calculate_brightness(image)
    contrast = calculate_contrast(image)
    text_density = calculate_text_density(image)

    thresholds = {
        "blurriness": 4000,
        "noise": 0.2,
        "brightness_low": 200,
        "brightness_high": 500,
        "contrast": 200,
        "text_density": 0.04
    }

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

    if sum(quality.values()) >= 3:
        return "Bad"
    else:
        return "Good"

def calculate_blurriness(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()

def calculate_noise(image):
    return np.random.rand()

def calculate_brightness(image):
    return np.mean(image)

def calculate_contrast(image):
    return np.std(image)

def calculate_text_density(image):
    return 0.05

# Main process function
def process_image(image_path, save_dir):
    print("Starting image processing...")
    image, status = check_and_adjust_dpi_and_pixels(image_path)

    quality_status = check_image_quality(image)

    if quality_status == "Bad":
        print("Attempt 1: Image is bad. Applying SEGAN-based enhancement...")
        enhanced_image_path = os.path.join(save_dir, "enhanced_image.jpg")
        image = apply_segan_enhancement(image, enhanced_image_path)
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
os.makedirs(OUTPUT_IMAGE_DIR, exist_ok=True)
processed_image, final_status = process_image(INPUT_IMAGE_PATH, OUTPUT_IMAGE_DIR)

if processed_image is not None:
    pil_image = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
    pil_image.show()

if final_status == "Bad":
    print("Final Status: Image is still bad after two attempts.")
else:
    print("Final Status: Image is good.")
