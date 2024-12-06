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

from ultralytics import YOLO
import os

def predict_image_class(model_path, image_path):
    """
    Predicts the class of a given image using a pre-trained YOLO model.

    Args:
        model_path (str): Path to the YOLO model file (.pt).
        image_path (str): Path to the image to be classified.

    Returns:
        str: The predicted class for the image.
    """
    try:
        # Load the YOLO model
        model = YOLO(model_path)

        # Predict the class for the image
        results = model.predict(source=image_path)

        if not results:
            raise ValueError("No results returned by the model.")

        # Assuming top prediction is the most relevant
        for result in results:
            predicted_class = result.names[result.probs.top1]
            return predicted_class

    except Exception as e:
        print(f"Error occurred: {e}")
        return None

# Example usage:
model_path = r"C:\CitiDev\japan_pipeline\all_model\classification_model.pt"
image_path = r'C:\CitiDev\japan_pipeline\data_set\Test image\6f7rch30.png'

predicted_class = predict_image_class(model_path, image_path)
print(f"Predicted Class: {predicted_class}")

# Example usage
image_path = r'C:\CitiDev\japan_pipeline\data_set\Test image\6f7rch30.png'
model_path = r"C:\CitiDev\japan_pipeline\all_model\classification_model.pt"
classification_result = classify_image(image_path, model_path)

# Check the predicted label and take action
if classification_result:
    predicted_label = classification_result[0][1]  # Extract the predicted label
    confidence = float(classification_result[0][2])  # Extract the confidence

    print(f"Predicted Class: {predicted_label} (Confidence: {confidence:.2f})")
    
    if predicted_label == 'driving license':
        # Implement any additional logic for 'driving license'
        pass
