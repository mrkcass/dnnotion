from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

import notionnd.layers.embed as embed
from notionnd.layers.norm import normalize
from notionnd.layers.cnn import multidim_convolution as convolution
from notionnd.layers.dense import fully_connected as dense
import notionnd.layers.output as output

mlog = None
hypers = None


def init(logger, hyper_params):
    global mlog, hypers
    mlog = logger
    hypers = hyper_params


def rand(features, labels, mode, params):
    with tf.device('/cpu:0'):
        word_vecs = embed.rand(features, params)
    with tf.device('/gpu:0'):
        normed_word_vecs = normalize(word_vecs, mode)
        rnn = convolution(normed_word_vecs, features['INPUTLEN'], mode)
        fully_connected = dense(rnn, mode)
        outputs = output.output(fully_connected)
        return output.train_or_predict(features, labels, mode, params, outputs)


def static(features, labels, mode, params):
    with tf.device('/cpu:0'):
        word_vecs = embed.static(features)
    with tf.device('/gpu:0'):
        normed_word_vecs = normalize(word_vecs, mode)
        rnn = convolution(normed_word_vecs, features['INPUTLEN'], mode)
        fully_connected = dense(rnn, mode)
        outputs = output.output(fully_connected)
        return output.train_or_predict(features, labels, mode, params, outputs)


def nonstatic(features, labels, mode, params):
    with tf.device('/cpu:0'):
        word_vecs = embed.nonstatic(features)
    with tf.device('/gpu:0'):
        normed_word_vecs = normalize(word_vecs, mode)
        rnn = convolution(normed_word_vecs, features['INPUTLEN'], mode)
        fully_connected = dense(rnn, mode)
        outputs = output.output(fully_connected)
        return output.train_or_predict(features, labels, mode, params, outputs)
