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
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from gensim.models import Word2Vec
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Download NLTK data for sentence and word tokenization
nltk.download('punkt')

# Load text data
def load_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

# Preprocess text into sentences and tokenize
def preprocess_text(text):
    sentences = sent_tokenize(text)  # Tokenize into sentences
    tokenized_sentences = [word_tokenize(sentence.lower()) for sentence in sentences]  # Tokenize words in each sentence
    return sentences, tokenized_sentences

# Train or load Word2Vec model
def train_word2vec(tokenized_sentences, vector_size=100, window=5, min_count=1):
    model = Word2Vec(tokenized_sentences, vector_size=vector_size, window=window, min_count=min_count)
    return model

# Get the sentence embedding by averaging word vectors
def get_sentence_embedding(model, sentence_tokens):
    word_vectors = []
    for word in sentence_tokens:
        if word in model.wv:
            word_vectors.append(model.wv[word])
    if word_vectors:
        return np.mean(word_vectors, axis=0)
    else:
        return np.zeros(model.vector_size)

# Find the most similar sentence to the user query
def find_most_similar_sentence(model, sentences, tokenized_sentences, query):
    query_tokens = word_tokenize(query.lower())
    query_embedding = get_sentence_embedding(model, query_tokens)

    sentence_embeddings = [get_sentence_embedding(model, sent) for sent in tokenized_sentences]
    similarities = cosine_similarity([query_embedding], sentence_embeddings)[0]

    most_similar_idx = np.argmax(similarities)
    return sentences[most_similar_idx], similarities[most_similar_idx]

# Main function to load text and perform Q&A
def main(file_path, user_query):
    # Step 1: Load and preprocess the text
    text = load_text(file_path)
    sentences, tokenized_sentences = preprocess_text(text)

    # Step 2: Train Word2Vec on the tokenized sentences
    model = train_word2vec(tokenized_sentences)

    # Step 3: Find the most similar sentence to the user's query
    most_similar_sentence, similarity_score = find_most_similar_sentence(model, sentences, tokenized_sentences, user_query)

    print(f"Question: {user_query}")
    print(f"Answer: {most_similar_sentence}")
    print(f"Similarity Score: {similarity_score:.4f}")

# Example usage:
if __name__ == "__main__":
    text_file_path = 'your_text_file.txt'  # Path to your .txt file
    user_question = input("Enter your question: ")  # User's question
    main(text_file_path, user_question)
