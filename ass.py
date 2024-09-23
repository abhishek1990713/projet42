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

from __future__ import absolute_import, division, print_function
import json
import os
import shutil

import tensorflow.compat.v1 as tf

import electra.configure_finetuning
from electra.finetune import preprocessing, task_builder
from electra.model import modeling, optimization
from electra.util import training_utils, utils

# Enable GPU growth to allow dynamic memory allocation
session_config = tf.ConfigProto()
session_config.gpu_options.allow_growth = True

DATA_MODEL_DIR = '/Users/renato/Documents/deep_learning/TensorFlow/electra_large_qa_model/'
INIT_CHECKPOINT = os.path.join(DATA_MODEL_DIR, 'model/model.ckpt-64000')

class FinetuningModel:
    """Finetuning model with support for multi-task training."""

    def __init__(self, config, tasks, is_training, features, num_train_steps):
        # Create a shared transformer encoder
        bert_config = training_utils.get_bert_config(config)
        self.bert_config = bert_config

        # Modify model size for debugging
        if config.debug:
            bert_config.num_hidden_layers = 3
            bert_config.hidden_size = 144
            bert_config.intermediate_size = 144 * 4
            bert_config.num_attention_heads = 4

        assert config.max_seq_length <= bert_config.max_position_embeddings

        # Instantiate BERT model
        bert_model = modeling.BertModel(
            bert_config=bert_config,
            is_training=is_training,
            input_ids=features["input_ids"],
            input_mask=features["input_mask"],
            token_type_ids=features["segment_ids"],
            use_one_hot_embeddings=config.use_tpu,
            embedding_size=config.embedding_size
        )

        # Calculate task progress
        percent_done = (tf.cast(tf.train.get_or_create_global_step(), tf.float32) /
                        tf.cast(num_train_steps, tf.float32))

        # Initialize outputs and losses for multi-task learning
        self.outputs = {"task_id": features["task_id"]}
        losses = []
        for task in tasks:
            with tf.variable_scope(f"task_specific/{task.name}"):
                task_losses, task_outputs = task.get_prediction_module(bert_model, features, is_training, percent_done)
                losses.append(task_losses)
                self.outputs[task.name] = task_outputs

        # Compute total loss
        self.loss = tf.reduce_sum(
            tf.stack(losses, axis=-1) *
            tf.one_hot(features["task_id"], len(config.task_names))
        )

def model_fn_builder(config, tasks, num_train_steps, pretraining_config=None):
    """Returns `model_fn` closure for TPUEstimator."""

    def model_fn(features, labels, mode, params):
        """The `model_fn` for TPUEstimator."""
        utils.log("Building model...")
        is_training = (mode == tf.estimator.ModeKeys.TRAIN)
        model = FinetuningModel(config, tasks, is_training, features, num_train_steps)

        init_checkpoint = pretraining_config.get('checkpoint', None) if pretraining_config else None
        if init_checkpoint:
            utils.log("Using checkpoint", init_checkpoint)
            tvars = tf.trainable_variables()
            assignment_map, _ = modeling.get_assignment_map_from_checkpoint(tvars, init_checkpoint)
            tf.train.init_from_checkpoint(init_checkpoint, assignment_map)

        # Build model for training or prediction
        if mode == tf.estimator.ModeKeys.TRAIN:
            train_op = optimization.create_optimizer(
                model.loss, config.learning_rate, num_train_steps,
                weight_decay_rate=config.weight_decay_rate,
                use_tpu=config.use_tpu,
                warmup_proportion=config.warmup_proportion,
                layerwise_lr_decay_power=config.layerwise_lr_decay,
                n_transformer_layers=model.bert_config.num_hidden_layers
            )

            output_spec = tf.estimator.tpu.TPUEstimatorSpec(
                mode=mode,
                loss=model.loss,
                train_op=train_op,
                scaffold_fn=None,
                training_hooks=[training_utils.ETAHook(
                    {} if config.use_tpu else dict(loss=model.loss),
                    num_train_steps, config.iterations_per_loop, config.use_tpu, 10
                )]
            )
        else:
            assert mode == tf.estimator.ModeKeys.PREDICT
            output_spec = tf.estimator.tpu.TPUEstimatorSpec(
                mode=mode,
                predictions=utils.flatten_dict(model.outputs),
                scaffold_fn=None
            )

        utils.log("Building complete")
        return output_spec

    return model_fn

class ModelRunner:
    """Fine-tunes a model on a supervised task."""

    def __init__(self, config, tasks, pretraining_config=None):
        self._config = config
        self._tasks = tasks
        self._preprocessor = preprocessing.Preprocessor(config, self._tasks)

        tpu_cluster_resolver = None
        is_per_host = tf.estimator.tpu.InputPipelineConfig.PER_HOST_V2
        tpu_config = tf.estimator.tpu.TPUConfig(
            iterations_per_loop=config.iterations_per_loop,
            num_shards=config.num_tpu_cores,
            per_host_input_for_training=is_per_host,
            tpu_job_name=config.tpu_job_name
        )

        run_config = tf.estimator.tpu.RunConfig(
            cluster=tpu_cluster_resolver,
            model_dir=config.model_dir,
            save_checkpoints_steps=config.save_checkpoints_steps,
            tpu_config=tpu_config,
            session_config=session_config,
            keep_checkpoint_max=config.max_save
        )

        model_fn = model_fn_builder(config=config, tasks=self._tasks, num_train_steps=0, pretraining_config=pretraining_config)

        self._estimator = tf.estimator.tpu.TPUEstimator(
            use_tpu=config.use_tpu,
            model_fn=model_fn,
            config=run_config,
            train_batch_size=config.train_batch_size,
            eval_batch_size=config.eval_batch_size,
            predict_batch_size=config.predict_batch_size
        )

    def predict(self, split="dev", return_results=False):
        task = self._tasks[0]
        eval_input_fn, _ = self._preprocessor.prepare_predict([task], split)
        results = self._estimator.predict(input_fn=eval_input_fn, yield_single_examples=True)

        scorer = task.get_scorer()
        for r in results:
            if r["task_id"] != len(self._tasks):  # ignore padding examples
                r = utils.nest_dict(r, self._config.task_names)
                scorer.update(r[task.name])
        return scorer.get_results()

def init_model():
    data_dir = os.path.join(DATA_MODEL_DIR, 'data')
    os.makedirs(data_dir, exist_ok=True)

    hparams = dict()
    config = electra.configure_finetuning.FinetuningConfig('electra_large', DATA_MODEL_DIR, **hparams)
    tasks = task_builder.get_tasks(config)

    pretraining_config = {'checkpoint': INIT_CHECKPOINT}
    model_runner = ModelRunner(config, tasks, pretraining_config=pretraining_config)
    return model_runner

def predict_from_file(question, context_file_path, model):
    """
    Predict the answer for the given question based on the context from a file.

    Args:
        question (str or list): The question(s) to ask.
        context_file_path (str): Path to the text file containing the context.
        model (ModelRunner): The initialized QA model.
    
    Returns:
        dict: The model's prediction.
    """
    # Reset the examples
    model._tasks[0]._examples = {}

    # If the question is a single string, wrap it in a list
    question = [question] if isinstance(question, str) else question

    # Read the context from the .txt file
    try:
        with open(context_file_path, 'r', encoding='utf-8') as f:
            context = f.read()
    except FileNotFoundError:
        print(f"Error: The file {context_file_path} was not found.")
        return None

    # Prepare the example in the format required by the model
    example = {
        "data": [
            {
                "paragraphs": [
                    {
                        "qas": [{"question": q, "id": f'q_{i}'} for i, q in enumerate(question)],
                        "context": context
                    }
                ]
            }
        ]
    }

    # Clean up old data files
    try:
        os.remove(os.path.join(DATA_MODEL_DIR, 'data/dev.json'))
        shutil.rmtree(os.path.join(DATA_MODEL_DIR, 'tfrecords'))
    except Exception as err:
        print(f"Error during file cleanup: {err}")

    # Save the new example to the data folder
    with open(os.path.join(DATA_MODEL_DIR, 'data/dev.json'), 'w', encoding='utf-8') as f:
        json.dump(example, f)

    # Run the prediction
    return model.predict()

# Example usage
if __name__ == "__main__":
    model_runner = init_model()  # Initialize your model

    # Specify the question and path to the context file
    question = "What is the capital of France?"
    context_file = "/path/to/your/context.txt"

    # Call the modified predict function
    results = predict_from_file(question, context_file, model_runner)

    # Output the prediction results
    print(results)
