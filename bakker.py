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

def calculate_blurriness(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()

def calculate_noise(image):
    return 0.1  # Placeholder value

def calculate_brightness(image):
    return image.mean()

def calculate_contrast(image):
    return image.max() - image.min()

def calculate_text_density(image):
    return 0.05  # Placeholder value

def check_image_quality(image_path, thresholds=None):
    if thresholds is None:
        thresholds = {
            "blurriness": 4000,
            "noise": 0.2,
            "brightness_low": 200,
            "brightness_high": 500,
            "contrast": 200,
            "text_density": 0.04
        }

    image = cv2.imread(image_path)
    if image is None:
        return "Image not found or invalid format"

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

    # Image quality determination
    image_quality = "Good" if true_conditions >= 3 else "Bad"

    return {
        "quality_checks": quality_checks,
        "true_conditions": true_conditions,
        "image_quality": image_quality
    }

# Example usage
image_path = r"C:\CitiDev Projects\Trade_data\AB\310093900 21530315_1_2303786310093900.007.tiff"
quality_report = check_image_quality(image_path)

for key, value in quality_report["quality_checks"].items():
    print(f"{key}: {value}")

print(f"True Conditions: {quality_report['true_conditions']}")
print(f"Image Quality: {quality_report['image_quality']}")
