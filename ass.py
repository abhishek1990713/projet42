import cv2
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

def rotate_image(image_path, output_folder):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error loading image: {image_path}")
        return []
    
    filename = os.path.basename(image_path).split('.')[0]
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    dataset = []
    labels = []
    
    for angle in range(0, 361, 10):  # Rotate from 0 to 360 in steps of 10
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))
        output_path = os.path.join(output_folder, f"{filename}_rotated_{angle}.jpg")
        cv2.imwrite(output_path, rotated_image)
        dataset.append(rotated_image)
        labels.append(angle)
        print(f"Saved: {output_path}")
    
    return np.array(dataset), np.array(labels)

def build_model():
    model = models.Sequential([
        layers.Conv2D(32, (3,3), activation='relu', input_shape=(128, 128, 3)),
        layers.MaxPooling2D((2,2)),
        layers.Conv2D(64, (3,3), activation='relu'),
        layers.MaxPooling2D((2,2)),
        layers.Conv2D(128, (3,3), activation='relu'),
        layers.MaxPooling2D((2,2)),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])
    return model

if __name__ == "__main__":
    input_folder = "input_images"  # Change to your image folder
    output_folder = "output_images"  # Change to your output folder
    os.makedirs(output_folder, exist_ok=True)
    
    X, y = [], []
    for image_file in os.listdir(input_folder):
        if image_file.lower().endswith(('png', 'jpg', 'jpeg')):
            images, labels = rotate_image(os.path.join(input_folder, image_file), output_folder)
            X.extend(images)
            y.extend(labels)
    
    X = np.array(X)
    y = np.array(y)
    X = X / 255.0  # Normalize images
    
    model = build_model()
    model.fit(X, y, epochs=10, batch_size=32, validation_split=0.2)
    model.save("rotation_angle_model.h5")

