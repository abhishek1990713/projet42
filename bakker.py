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

def calculate_blurriness(image):
    # Convert to grayscale if the image is not already grayscale
    if len(image.shape) == 3:  # Check if the image has 3 channels
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image  # Already grayscale
    return cv2.Laplacian(gray, cv2.CV_64F).var()

def advanced_preprocess_image(image):
    """
    Advanced preprocessing to improve image quality:
    1. Non-local Means Denoising
    2. CLAHE for adaptive contrast enhancement
    3. Unsharp Masking for sharpening
    """
    # Convert to grayscale if the image is not already grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # 1. Non-Local Means Denoising (advanced noise reduction)
    denoised = cv2.fastNlMeansDenoising(gray, None, h=30, templateWindowSize=7, searchWindowSize=21)

    # 2. CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced_contrast = clahe.apply(denoised)

    # 3. Unsharp Masking for sharpening
    gaussian_blurred = cv2.GaussianBlur(enhanced_contrast, (9, 9), 10.0)
    sharpened = cv2.addWeighted(enhanced_contrast, 1.5, gaussian_blurred, -0.5, 0)

    return sharpened
