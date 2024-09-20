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
import numpy as np
from gensim.models import KeyedVectors
from sklearn.metrics.pairwise import cosine_similarity

# Step 1: Load the text file
def load_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

# Step 2: Tokenize sentences by splitting on periods (.)
def tokenize_sentences(text):
    return [sentence.strip() for sentence in text.split('.') if sentence]

# Step 3: Tokenize words by splitting on spaces and remove punctuation
def tokenize_words(sentence):
    sentence = ''.join([char if char.isalnum() or char.isspace() else ' ' for char in sentence])
    return sentence.lower().split()

# Step 4: Load your pre-trained Word2Vec model
def load_pretrained_word2vec_model(model_path):
    model = KeyedVectors.load_word2vec_format(model_path, binary=True)  # Assuming binary format
    return model

# Step 5: Get the sentence embedding by averaging word vectors from the pre-trained model
def get_sentence_embedding(model, sentence_tokens):
    word_vectors = []
    for word in sentence_tokens:
        if word in model:  # Check if the word exists in the pre-trained Word2Vec model
            word_vectors.append(model[word])
    if word_vectors:
        return np.mean(word_vectors, axis=0)  # Average word vectors to get sentence embedding
    else:
        return np.zeros(model.vector_size)

# Step 6: Find the most similar sentence to the user query
def find_most_similar_sentence(model, sentences, tokenized_sentences, query):
    query_tokens = tokenize_words(query)
    query_embedding = get_sentence_embedding(model, query_tokens)

    sentence_embeddings = [get_sentence_embedding(model, sent) for sent in tokenized_sentences]
    similarities = cosine_similarity([query_embedding], sentence_embeddings)[0]

    most_similar_idx = np.argmax(similarities)
    return sentences[most_similar_idx], similarities[most_similar_idx]

# Main function to load text, process user query, and find the answer
def main(file_path, user_query, word2vec_model_path):
    # Load and tokenize the text
    text = load_text(file_path)
    sentences = tokenize_sentences(text)
    tokenized_sentences = [tokenize_words(sentence) for sentence in sentences]

    # Load pre-trained Word2Vec model
    model = load_pretrained_word2vec_model(word2vec_model_path)

    # Find the most similar sentence
    best_sentence, similarity_score = find_most_similar_sentence(model, sentences, tokenized_sentences, user_query)

    # Output the results
    print(f"Question: {user_query}")
    print(f"Answer: {best_sentence}")
    print(f"Similarity Score: {similarity_score:.4f}")

# Example usage:
if __name__ == "__main__":
    text_file_path = 'your_text_file.txt'  # Specify the path to your text file
    word2vec_model_path = 'your_pretrained_model.bin'  # Path to your pre-trained Word2Vec model
    user_question = input("Enter your question: ")  # User's question
    main(text_file_path, user_question, word2vec_model_path)

