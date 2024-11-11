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


import os
from ultralytics import YOLO
from lap_image import ImageQualityAssessor
from allmodel_test import ImageClassifier

# Process functions for each document type
def process_dl_image(input_file_path, confidence_threshold=0.70, output_filename="test_result_dl.jpg"):
    model_path = r"C:\CitiDev\text_ocr\image_quality\yolo_model\best_DL.pt"
    model = YOLO(model_path)
    results = model(input_file_path)
    all_boxes_present, confidence_check = False, False
    
    for result in results:
        boxes = result.boxes
        result.show()
        result.save(filename=output_filename)
        
        if boxes is not None and len(boxes) == 4:
            all_boxes_present = True
            print("All four bounding boxes are present.")
        
        confidence_scores = boxes.conf if boxes is not None else []
        if all(score >= confidence_threshold for score in confidence_scores):
            confidence_check = True
            print(f"All confidence scores are above the threshold of {confidence_threshold}.")
    
    return "Image is uploaded correctly." if all_boxes_present and confidence_check else "Image is not good."

def process_passport_image(input_file_path, confidence_threshold=0.70, output_filename="test_result_passport.jpg"):
    model_path = r"C:\CitiDev\text_ocr\image_quality\yolo_model\best_passport.pt"
    model = YOLO(model_path)
    results = model(input_file_path)
    # Implement similar checks as in `process_dl_image`
    # ...
    return "Passport processed."

def process_rc_image(input_file_path, confidence_threshold=0.70, output_filename="test_result_rc.jpg"):
    model_path = r"C:\CitiDev\text_ocr\image_quality\yolo_model\best_rc.pt"
    model = YOLO(model_path)
    results = model(input_file_path)
    # Implement similar checks as in `process_dl_image`
    # ...
    return "Residence card processed."

def process_image_pipeline(image_path, quality_assessor, classifier):
    # Step 1: Check if the image is blurry
    quality_result = quality_assessor.is_image_blurry(image_path)
    if quality_result == "Blurry":
        print("The image is blurry and cannot be processed for classification.")
        return None
    
    # Step 2: Classify the image
    classification_result = classifier.classify(image_path)
    if classification_result:
        predicted_label = classification_result['predicted_label']
        print(f"Predicted Class: {predicted_label} (Confidence: {classification_result['confidence']:.2f})")
        
        # Step 3: Call the corresponding processing function based on predicted label
        if predicted_label == 'driving_license':
            return process_dl_image(image_path)
        elif predicted_label == 'passport':
            return process_passport_image(image_path)
        elif predicted_label == 'residence_card':
            return process_rc_image(image_path)
        else:
            print("No processing function for this class.")
            return "Class not recognized for further processing."
    else:
        print("Image classification failed.")
        return None

if __name__ == "__main__":
    model_path = r'C:\CitiDev\text_ocr\image_quality\inception_v3_model_newtrain_japan.h5'
    class_indices = {0: 'driving_license', 1: 'others', 2: 'passport', 3: 'residence_card'}
    image_path = r"C:\CitiDev\text_ocr\image_quality\test_data\augmented_me_bge9m4lu.png"

    # Initialize the ImageQualityAssessor and ImageClassifier
    image_quality_assessor = ImageQualityAssessor(blur_threshold=100.0)
    classifier = ImageClassifier(model_path, class_indices)

    # Process the image through the pipeline
    result_message = process_image_pipeline(image_path, image_quality_assessor, classifier)
    print(result_message)
