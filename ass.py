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
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.applications import VGG16, ResNet50, InceptionV3
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.metrics import classification_report, accuracy_score

# Parameters
IMG_SIZE = 224  # Input image size
BATCH_SIZE = 32
EPOCHS = 10  # Adjust based on your needs
DATA_DIR = 'data/'  # Update this with your dataset path
RESULTS_EXCEL = 'model_results.xlsx'

# Data Preparation
datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)  # 20% for validation

train_generator = datagen.flow_from_directory(
    DATA_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'  # Set as training data
)

validation_generator = datagen.flow_from_directory(
    DATA_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'  # Set as validation data
)

# Function to build and compile model
def build_model(base_model, num_classes):
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(num_classes, activation='softmax')(x)
    model = Model(inputs=base_model.input, outputs=x)
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

# Models to train
models = {
    'VGG16': VGG16(weights='imagenet', include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3)),
    'ResNet50': ResNet50(weights='imagenet', include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3)),
    'InceptionV3': InceptionV3(weights='imagenet', include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
}

results = []

# Train and evaluate each model
for model_name, base_model in models.items():
    model = build_model(base_model, num_classes=len(train_generator.class_indices))
    metrics = train_and_evaluate_model(model_name, model, train_generator, validation_generator)
    results.append(metrics)

# Convert results to DataFrame
results_df = pd.DataFrame(results)

# Save to Excel file
if os.path.exists(RESULTS_EXCEL):
    with pd.ExcelWriter(RESULTS_EXCEL, mode='a', if_sheet_exists='new') as writer:
        results_df.to_excel(writer, sheet_name='Results', index=False)
else:
    results_df.to_excel(RESULTS_EXCEL, sheet_name='Results', index=False)

print(f'Results saved to {RESULTS_EXCEL}')
