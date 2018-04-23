# dnnotion ie 2017
# mark r. cass

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import numpy as np

# todo this is messy and only for debugging
import tensorflow as tf
learn = tf.contrib.learn
framework = tf.contrib.framework
ctblayers = tf.contrib.layers

mlog = None
hypers = None


def init(logger, hyper_params):
    global mlog, hypers
    mlog = logger
    hypers = hyper_params


def rand(features, params):
    # input layer / hidden layer 1
    # embedding layer to convert sparse vector to dense vector for encoding
    # todo: investigate different args for embed_sequence (i.e unique)
    initializer = ctblayers.xavier_initializer()
    feature_vectors = ctblayers.embed_sequence(features['INPUT'],
                                               vocab_size=params['n_words'],
                                               embed_dim=hypers.get_param('ws'),
                                               initializer=initializer,
                                               unique=False)
    # dim output embed ['tb', 'dx', 'ws']
    return feature_vectors


def static(features):
    # input layer / hidden layer 1
    # embedding layer to convert sparse vector to dense vector for encoding
    # todo: investigate different args for embed_sequence (i.e unique)
    wordvec_path = hypers.get_param("wv")
    ckpt = tf.train.get_checkpoint_state(wordvec_path)
    word_vectors_tensor = framework.load_variable(ckpt.model_checkpoint_path, 'w_out')
    word_vectors_unstacked = tf.unstack(word_vectors_tensor, axis=0)
    pad_vector = tf.zeros([1, hypers.get_param('ws')], tf.float32)
    word_vectors_unstacked = tf.concat([word_vectors_unstacked, pad_vector], 0)
    word_vectors = framework.variable('wordvecs/embeddings', initializer=word_vectors_unstacked, trainable=False)
    feature_vectors = ctblayers.embed_sequence(features['INPUT'],
                                               initializer=word_vectors,
                                               reuse=True,
                                               trainable=False,
                                               scope="wordvecs",
                                               unique=True)
    # dim output embed ['tb', 'dx', 'ws']
    return feature_vectors


def nonstatic(features):
    # input layer / hidden layer 1
    # embedding layer to convert sparse vector to dense vector for encoding
    # todo: investigate different args for embed_sequence (i.e unique)
    wordvec_path = hypers.get_param("wv")
    ckpt = tf.train.get_checkpoint_state(wordvec_path)
    word_vectors_tensor = framework.load_variable(ckpt.model_checkpoint_path, 'w_out')
    word_vectors_unstacked = tf.unstack(word_vectors_tensor, axis=0)
    pad_vector = tf.zeros([1, hypers.get_param('ws')], tf.float32)
    word_vectors_unstacked = tf.concat([word_vectors_unstacked, pad_vector], 0)
    word_vectors = framework.variable('wordvecs/embeddings', initializer=word_vectors_unstacked, trainable=False)
    feature_vectors = ctblayers.embed_sequence(features['INPUT'],
                                               initializer=word_vectors,
                                               reuse=True,
                                               trainable=True,
                                               scope="wordvecs",
                                               unique=True)
    # dim output embed ['tb', 'dx', 'ws']
    return feature_vectors


