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
def convert_to_tif_with_dpi(image, output_path, min_dpi=300):
    print("Checking image properties...")
    
    # Convert numpy array to PIL Image
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    # Get DPI information (default DPI = 200 if not specified)
    dpi = pil_image.info.get("dpi", (200, 200))[0]
    print(f"Current DPI: {dpi}")
    width, height = pil_image.size
    print(f"Current Dimensions: {width}x{height}")

    # Adjust DPI if needed
    adjustments_made = False
    if dpi < min_dpi:
        print(f"DPI is lower than {min_dpi}. Adjusting DPI to {min_dpi}...")
        pil_image.save(output_path, dpi=(min_dpi, min_dpi))
        adjustments_made = True
    else:
        pil_image.save(output_path, dpi=(dpi, dpi))

    print(f"Image saved as {output_path}")
    return output_path
