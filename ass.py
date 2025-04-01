import cv2
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.preprocessing.image import img_to_array

# Function to rotate images and save them
def rotate_image(image_path, output_folder):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error loading image: {image_path}")
        return [], []
    
    filename = os.path.basename(image_path).split('.')[0]
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    
    dataset = []
    labels = []
    
    # Rotate images from 0 to 360 degrees in steps of 10
    for angle in range(0, 361, 10):
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))
        
        # Resize to fixed size (128x128) before appending
        resized_image = cv2.resize(rotated_image, (299, 299))  # InceptionV3 expects 299x299 images
        output_path = os.path.join(output_folder, f"{filename}_rotated_{angle}.jpg")
        cv2.imwrite(output_path, rotated_image)
        
        dataset.append(resized_image)
        labels.append(angle)
        print(f"Saved: {output_path}")
    
    return np.array(dataset), np.array(labels)

# Function to build the model using InceptionV3
def build_model():
    base_model = InceptionV3(weights='imagenet', include_top=False, input_shape=(299, 299, 3))
    
    # Freeze the base model to use its learned features without retraining
    base_model.trainable = False
    
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation='relu'),
        layers.Dense(1)  # Regression output for angle
    ])
    
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])
    return model

# Main function to train the model
if __name__ == "__main__":
    input_folder = "input_images"  # Change to your image folder
    output_folder = "output_images"  # Change to your output folder
    os.makedirs(output_folder, exist_ok=True)
    
    # Prepare the dataset
    X, y = [], []
    for image_file in os.listdir(input_folder):
        if image_file.lower().endswith(('png', 'jpg', 'jpeg')):
            images, labels = rotate_image(os.path.join(input_folder, image_file), output_folder)
            X.extend(images)
            y.extend(labels)
    
    # Convert to numpy arrays and normalize
    X = np.array(X, dtype=np.float32) / 255.0
    y = np.array(y, dtype=np.float32)

    # Build the model using InceptionV3
    model = build_model()
    
    # Train the model
    model.fit(X, y, epochs=10, batch_size=32, validation_split=0.2)

    # Save the trained model
    model.save("rotation_angle_model_inceptionv3.h5")
