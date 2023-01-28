from flask import Flask, redirect, url_for, request, render_template, jsonify
from scipy.io.wavfile import write
import numpy as np
import noisereduce as nr
import IPython
from flask_cors import CORS, cross_origin
#from pydub.playback import play
from moviepy.editor import concatenate_audioclips, AudioFileClip
import librosa
import moviepy.editor as mp
import ffmpeg
import os

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index1.html')

@app.route('/predict', methods=['GET', 'POST'])
def Upload():
    if request.method == 'GET':
        video = 'video_name/video.mp4'
        video_clip = mp.VideoFileClip(video)
        video_clip.audio.write_audiofile("AudioFileClip/audio_file12.wav")

        audio_path = 'AudioFileClip/audio_file12.wav'
        data, rate = librosa.load(audio_path)

        reduced_noise = nr.reduce_noise(y=data, sr=rate, n_std_thresh_stationary=1.5, stationary=True)
        sbr = IPython.display.Audio(data=reduced_noise, rate=rate)
        print(type(sbr))
        write('AudioFileClip/test1.wav', rate, reduced_noise)



        input_video = ffmpeg.input('video_name/video.mp4')

        input_audio = ffmpeg.input('AudioFileClip/test1.wav')

        ffmpeg.concat(input_video, input_audio, v=1, a=1).output('output/finished_video.mp4').run()
        os.remove(audio_path)

        os.remove('AudioFileClip/test1.wav')


        return render_template('index1.html')
    return None


if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='0.0.0.0', port=5000, debug=True)