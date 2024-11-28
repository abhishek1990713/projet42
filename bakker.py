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

def calculate_noise(image):
    # Ensure the image is in grayscale format
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image  # Already grayscale
    # Placeholder noise calculation (replace with your logic)
    return np.std(gray)

def advanced_preprocess_image(image):
    """
    Advanced preprocessing to improve image quality:
    1. Non-local Means Denoising
    2. CLAHE for adaptive contrast enhancement
    3. Unsharp Masking for sharpening
    """
    if len(image.shape) == 3:  # Convert to grayscale if not already grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # 1. Non-Local Means Denoising
    denoised = cv2.fastNlMeansDenoising(gray, None, h=30, templateWindowSize=7, searchWindowSize=21)

    # 2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced_contrast = clahe.apply(denoised)

    # 3. Unsharp Masking for sharpening
    gaussian_blurred = cv2.GaussianBlur(enhanced_contrast, (9, 9), 10.0)
    sharpened = cv2.addWeighted(enhanced_contrast, 1.5, gaussian_blurred, -0.5, 0)

    # Convert back to 3-channel format for downstream compatibility
    processed_image = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)
    return processed_image

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

        print("Image is Bad. Applying preprocessing...")
        image = advanced_preprocess_image(image)

        # Validate the processed image
        if image is None or image.size == 0:
            print("Preprocessing resulted in an invalid image.")
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
