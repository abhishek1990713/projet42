from __future__ import division, print_function
import json
import sys
import os
import glob
import re
import json
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import numpy as np
import numpy as np
import librosa
import pandas as pd
# Flask utils
from flask import Flask, redirect, url_for, request, render_template, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
import boto3
# Define a flask app
app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index4.html')


@app.route('/predict', methods=['POST'])
def Upload():
    if request.method == 'POST':
        print(request.json['user_id'])

        def download_all_objects_in_folder(xyz):
            print(xyz)
            print("location ")
            _BUCKET_NAME = 'sbr-project-2021'
            _PREFIX = "machine learning/" + xyz + "/audio/"

            session = boto3.Session(
                aws_access_key_id='AKIAQRGY6UM3ZUL5MUCG',
                aws_secret_access_key='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'
            )
            s3_resource = session.resource('s3')
            my_bucket = s3_resource.Bucket(_BUCKET_NAME)
            objects = my_bucket.objects.filter(Prefix=_PREFIX)
            for obj in objects:
                path, filename = os.path.split(obj.key)
                print(path)
                print(filename)
                newpath = "audio/" + xyz
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                my_bucket.download_file(obj.key, "audio/" + xyz + "/" + filename)

            return "audio/"

        DATASET_PATH = download_all_objects_in_folder(request.json['user_id'])

        JSON_PATH = "saved_models/best126.json"
        SAMPLES_TO_CONSIDER = 22050

        def preprocess_dataset(dataset_path, json_path, num_mfcc=13, n_fft=2048, hop_length=512):
            """Extracts MFCCs from music dataset and saves them into a json file.
            :param dataset_path (str): Path to dataset
            :param json_path (str): Path to json file used to save MFCCs
            :param num_mfcc (int): Number of coefficients to extract
            :param n_fft (int): Interval we consider to apply FFT. Measured in # of samples
            :param hop_length (int): Sliding window for FFT. Measured in # of samples
            :return:
            """

            # dictionary where we'll store mapping, labels, MFCCs and filenames
            data = {
                "mapping": [],
                "labels": [],
                "MFCCs": [],
                "files": []
            }

            # loop through all sub-dirs
            for i, (dirpath, dirnames, filenames) in enumerate(os.walk(dataset_path)):

                # ensure we're at sub-folder level
                if dirpath is not dataset_path:

                    # save label (i.e., sub-folder name) in the mapping
                    label = dirpath.split("/")[-1]
                    data["mapping"].append(label)
                    print("\nProcessing: '{}'".format(label))

                    # process all audio files in sub-dir and store MFCCs
                    for f in filenames:
                        file_path = os.path.join(dirpath, f)

                        # load audio file and slice it to ensure length consistency among different files
                        signal, sample_rate = librosa.load(file_path)

                        # drop audio files with less than pre-decided number of samples
                        if len(signal) >= SAMPLES_TO_CONSIDER:
                            # ensure consistency of the length of the signal
                            signal = signal[:SAMPLES_TO_CONSIDER]

                            # extract MFCCs
                            MFCCs = librosa.feature.mfcc(signal, sample_rate, n_mfcc=num_mfcc, n_fft=n_fft,
                                                         hop_length=hop_length)

                            # store data for analysed track
                            data["MFCCs"].append(MFCCs.T.tolist())
                            data["labels"].append(i - 1)
                            data["files"].append(file_path)
                            print("{}: {}".format(file_path, i - 1))

            # save data in json file
            with open(json_path, "w") as fp:
                json.dump(data, fp, indent=4)

        if __name__ == "__main__":
            preprocess_dataset(DATASET_PATH, JSON_PATH)



            DATA_PATH = "saved_models/best126.json"
            SAVED_MODEL_PATH = "saved_models/best126.h5"
            EPOCHS = 50
            BATCH_SIZE = 32
            PATIENCE = 5
            LEARNING_RATE = 0.0001

            def load_data(data_path):
                """Loads training dataset from json file.
                :param data_path (str): Path to json file containing data
                :return X (ndarray): Inputs
                :return y (ndarray): Targets
                """
                with open(data_path, "r") as fp:
                    data = json.load(fp)

                X = np.array(data["MFCCs"])
                y = np.array(data["labels"])
                print("Training sets loaded!")
                return X, y

            def prepare_dataset(data_path, test_size=0.2, validation_size=0.2):
                """Creates train, validation and test sets.
                :param data_path (str): Path to json file containing data
                :param test_size (flaot): Percentage of dataset used for testing
                :param validation_size (float): Percentage of train set used for cross-validation
                :return X_train (ndarray): Inputs for the train set
                :return y_train (ndarray): Targets for the train set
                :return X_validation (ndarray): Inputs for the validation set
                :return y_validation (ndarray): Targets for the validation set
                :return X_test (ndarray): Inputs for the test set
                :return X_test (ndarray): Targets for the test set
                """

                # load dataset
                X, y = load_data(data_path)

                # create train, validation, test split
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)
                X_train, X_validation, y_train, y_validation = train_test_split(X_train, y_train,
                                                                                test_size=validation_size)

                # add an axis to nd array
                X_train = X_train[..., np.newaxis]
                X_test = X_test[..., np.newaxis]
                X_validation = X_validation[..., np.newaxis]

                return X_train, y_train, X_validation, y_validation, X_test, y_test

            def build_model(input_shape, loss="sparse_categorical_crossentropy", learning_rate=0.0001):
                """Build neural network using keras.
                :param input_shape (tuple): Shape of array representing a sample train. E.g.: (44, 13, 1)
                :param loss (str): Loss function to use
                :param learning_rate (float):
                :return model: TensorFlow model

                """
                DATA_PATH = "saved_models/best123.json"

                with open(DATA_PATH, "r") as fp:
                    data = json.load(fp)
                batch = len(data["mapping"])

                # build network architecture using convolutional layers
                model = tf.keras.models.Sequential()

                # 1st conv layer
                model.add(tf.keras.layers.Conv2D(64, (3, 3), activation='relu', input_shape=input_shape,
                                                 kernel_regularizer=tf.keras.regularizers.l2(0.001)))
                model.add(tf.keras.layers.BatchNormalization())
                model.add(tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2), padding='same'))

                # 2nd conv layer
                model.add(tf.keras.layers.Conv2D(32, (3, 3), activation='relu',
                                                 kernel_regularizer=tf.keras.regularizers.l2(0.001)))
                model.add(tf.keras.layers.BatchNormalization())
                model.add(tf.keras.layers.MaxPooling2D((3, 3), strides=(2, 2), padding='same'))

                # 3rd conv layer
                model.add(tf.keras.layers.Conv2D(32, (2, 2), activation='relu',
                                                 kernel_regularizer=tf.keras.regularizers.l2(0.001)))
                model.add(tf.keras.layers.BatchNormalization())
                model.add(tf.keras.layers.MaxPooling2D((2, 2), strides=(2, 2), padding='same'))

                # flatten output and feed into dense layer
                model.add(tf.keras.layers.Flatten())
                model.add(tf.keras.layers.Dense(64, activation='relu'))
                tf.keras.layers.Dropout(0.3)

                # softmax output layer
                model.add(tf.keras.layers.Dense(batch, activation='softmax'))

                optimiser = tf.optimizers.Adam(learning_rate=learning_rate)

                # compile model
                model.compile(optimizer=optimiser,
                              loss=loss,
                              metrics=["accuracy"])

                # print model parameters on console
                model.summary()

                return model

            def train(model, epochs, batch_size, patience, X_train, y_train, X_validation, y_validation):
                """Trains model
                :param epochs (int): Num training epochs
                :param batch_size (int): Samples per batch
                :param patience (int): Num epochs to wait before early stop, if there isn't an improvement on accuracy
                :param X_train (ndarray): Inputs for the train set
                :param y_train (ndarray): Targets for the train set
                :param X_validation (ndarray): Inputs for the validation set
                :param y_validation (ndarray): Targets for the validation set
                :return history: Training history
                """

                # earlystop_callback = tf.keras.callbacks.EarlyStopping(monitor="accuracy", min_delta=0.001, patience=patience)

                # train model
                history = model.fit(X_train,
                                    y_train,
                                    epochs=epochs,
                                    batch_size=batch_size,
                                    validation_data=(X_validation, y_validation)
                                    )
                return history



            def main():
                # generate train, validation and test sets
                X_train, y_train, X_validation, y_validation, X_test, y_test = prepare_dataset(DATA_PATH)

                # create network
                input_shape = (X_train.shape[1], X_train.shape[2], 1)
                model = build_model(input_shape, learning_rate=LEARNING_RATE)

                # train network
                history = train(model, EPOCHS, BATCH_SIZE, PATIENCE, X_train, y_train, X_validation, y_validation)

                # plot accuracy/loss for training/validation set as a function of the epochs
                #plot_history(history)

                # evaluate network on test set
                test_loss, test_acc = model.evaluate(X_test, y_test)
                print("\nTest loss: {}, test accuracy: {}".format(test_loss, 100 * test_acc))

                # save model
                model.save(SAVED_MODEL_PATH)
                _BUCKET_NAME = 'sbr-project-2021'

                session = boto3.Session(
                    aws_access_key_id='AKIAQRGY6UM3ZUL5MUCG',
                    aws_secret_access_key='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'
                )
                s3 = session.resource('s3')
                s3.Bucket(_BUCKET_NAME).upload_file('saved_models/best126.h5', "machine learning/" + request.json['user_id'] + "/models/best126.h5")
                s3.Bucket(_BUCKET_NAME).upload_file('saved_models/best126.json', "machine learning/" + request.json['user_id'] + "/models/best126.json")



            if __name__ == "__main__":
                main()
                return render_template('index4.html')







if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='0.0.0.0', port=5000, debug=True)