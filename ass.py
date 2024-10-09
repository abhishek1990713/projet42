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
import numpy as np
import pandas as pd
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.metrics import classification_report, accuracy_score

# Parameters
IMG_SIZE = 256  # Increased input image size
BATCH_SIZE = 32
EPOCHS = 10  # Adjust based on your needs
DATA_DIR = 'data/'  # Update this with your dataset path
RESULTS_EXCEL = 'custom_cnn_results.xlsx'

# Data Preparation with Augmentation
train_datagen = ImageDataGenerator(
    rescale=1./255,              # Normalize pixel values
    rotation_range=20,           # Randomly rotate images
    width_shift_range=0.2,       # Randomly shift images horizontally
    height_shift_range=0.2,      # Randomly shift images vertically
    shear_range=0.2,             # Shear transformation
    zoom_range=0.2,              # Randomly zoom in/out
    horizontal_flip=True,        # Randomly flip images
    fill_mode='nearest',         # Fill empty pixels after transformations
    validation_split=0.2         # 20% for validation
)

train_generator = train_datagen.flow_from_directory(
    DATA_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'  # Set as training data
)

validation_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

validation_generator = validation_datagen.flow_from_directory(
    DATA_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'  # Set as validation data
)

# Function to build custom CNN model
def build_custom_cnn(num_classes):
    model = Sequential()
    
    # Input layer with 256x256 image size
    model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_SIZE, IMG_SIZE, 3)))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    
    model.add(Conv2D(128, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    
    model.add(Conv2D(256, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(256, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    
    model.add(Flatten())
    
    model.add(Dense(512, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes, activation='softmax'))
    
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

# Function to train and evaluate model
def train_and_evaluate_model(model_name, model, train_gen, val_gen):
    model_checkpoint = ModelCheckpoint(f'{model_name}_best_model.h5', monitor='val_loss', save_best_only=True, mode='min')
    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS,
        callbacks=[model_checkpoint, early_stopping]
    )

    # Evaluation
    val_loss, val_accuracy = model.evaluate(val_gen)
    
    # Predictions
    val_gen.reset()
    predictions = model.predict(val_gen)
    predicted_classes = np.argmax(predictions, axis=1)
    true_classes = val_gen.classes

    # Classification report
    report = classification_report(true_classes, predicted_classes, target_names=val_gen.class_indices.keys(), output_dict=True)
    
    return {
        'Model': model_name,
        'Val Loss': val_loss,
        'Val Accuracy': val_accuracy,
        'Precision': report['weighted avg']['precision'],
        'Recall': report['weighted avg']['recall'],
        'F1-score': report['weighted avg']['f1-score']
    }

# Train the custom CNN model
custom_cnn_model = build_custom_cnn(num_classes=len(train_generator.class_indices))
metrics = train_and_evaluate_model('Custom_CNN', custom_cnn_model, train_generator, validation_generator)

# Convert results to DataFrame
results_df = pd.DataFrame([metrics])

# Save to Excel file
if os.path.exists(RESULTS_EXCEL):
    with pd.ExcelWriter(RESULTS_EXCEL, mode='a', if_sheet_exists='new') as writer:
        results_df.to_excel(writer, sheet_name='Results', index=False)
else:
    results_df.to_excel(RESULTS_EXCEL, sheet_name='Results', index=False)

print(f'Results saved to {RESULTS_EXCEL}')

# Load the best model for further use
loaded_model = load_model('Custom_CNN_best_model.h5')
print("Model loaded successfully.")
