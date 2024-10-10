from flask import Flask, redirect, url_for, request, render_template, jsonify
import speech_recognition as sr
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
from flask_cors import CORS, cross_origin
import boto3
import glob

app = Flask(__name__)

CORS(app)


@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index4.html')


@app.route('/predict', methods=['GET'])
def Upload():
    if request.method == 'GET':
        # print(request.json['file'])


        r = sr.Recognizer()

        sound = AudioSegment.from_wav("inp/splite.wav")

        audio_chunks = split_on_silence(sound, min_silence_len=1000, silence_thresh=sound.dBFS - 14, keep_silence=500)
        whole_text = ""
        textMap = {}
        for i, chunk in enumerate(audio_chunks):
            output_file = os.path.join('InputFiles', f"speech_chunk{i}.wav")
            print("Exporting file", output_file)
            result = chunk.export(output_file, format="wav")




        # os.remove("inp/splite.wav")
        return str(result)

    # return str(result)
    return None


if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='0.0.0.0', port=6000, debug=True)
 import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np
import matplotlib.pyplot as plt

# Step 1: Load Data from a Single Folder
# Define the path to the dataset folder (which contains subfolders for each class)
dataset_dir = 'path/to/dataset/'

# Create an ImageDataGenerator for training and validation, with a 20% split for validation
import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np
import matplotlib.pyplot as plt

# Step 1: Load Data from a Single Folder
# Define the path to the dataset folder (which contains subfolders for each class)
dataset_dir = 'path/to/dataset/'

# Create an ImageDataGenerator for training and validation, with a 20% split for validation
datagen = ImageDataGenerator(
    rescale=1.0/255,  # Normalize pixel values
    validation_split=0.2,  # Split the data into 80% training and 20% validation
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

# Load training data from the folder
train_generator = datagen.flow_from_directory(
    dataset_dir,
    target_size=(299, 299),  # InceptionV3 requires 299x299 images
    batch_size=32,
    class_mode='categorical',
    subset='training'  # Set as training data
)

# Load validation data from the folder
validation_generator = datagen.flow_from_directory(
    dataset_dir,
    target_size=(299, 299),
    batch_size=32,
    class_mode='categorical',
    subset='validation'  # Set as validation data
)

# Step 2: Build the InceptionV3 Model

# Load the InceptionV3 model without the top layer (include_top=False)
base_model = InceptionV3(weights='imagenet', include_top=False, input_shape=(299, 299, 3))

# Freeze the base model
base_model.trainable = False

# Build the custom model
model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    Dropout(0.5),  # Add dropout to prevent overfitting
    Dense(256, activation='relu'),  # Fully connected layer
    Dropout(0.5),  # Add another dropout
    Dense(6, activation='softmax')  # Output layer for 6 classes
])

# Step 3: Compile the Model with Multiple Metrics
model.compile(optimizer=Adam(), 
              loss='categorical_crossentropy', 
              metrics=['accuracy', 'Precision', 'Recall', 'AUC'])

# Step 4: Add Early Stopping and Model Checkpointing
early_stopping = EarlyStopping(
    monitor='val_loss',  # Monitor validation loss
    patience=3,  # Stop training if no improvement for 3 epochs
    restore_best_weights=True  # Restore the weights from the best epoch
)

model_checkpoint = ModelCheckpoint(
    'best_inception_v3_model.h5',  # Path to save the best model
    monitor='val_loss',  # Monitor validation loss
    save_best_only=True  # Save only the best model
)

# Step 5: Train the Model with Early Stopping and Checkpointing
history = model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // train_generator.batch_size,
    validation_data=validation_generator,
    validation_steps=validation_generator.samples // validation_generator.batch_size,
    epochs=50,  # Maximum number of epochs
    callbacks=[early_stopping, model_checkpoint]
)

# Step 6: Evaluate the Model
validation_loss, validation_accuracy, validation_precision, validation_recall, validation_auc = model.evaluate(validation_generator)
print(f"Validation Loss: {validation_loss:.4f}")
print(f"Validation Accuracy: {validation_accuracy * 100:.2f}%")
print(f"Validation Precision: {validation_precision:.4f}")
print(f"Validation Recall: {validation_recall:.4f}")
print(f"Validation AUC: {validation_auc:.4f}")

# Optional: Plot Training History
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')
plt.show()

# Step 7: Make Predictions and Generate Classification Report
def get_classification_report(generator):
    # Get true labels and predictions
    true_labels = generator.classes
    predictions = model.predict(generator)
    predicted_classes = np.argmax(predictions, axis=1)
    
    # Classification report
    report = classification_report(true_labels, predicted_classes, target_names=generator.class_indices.keys())
    print(report)

# Generate classification report on validation data
get_classification_report(validation_generator)
