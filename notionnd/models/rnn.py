# dnnotion ie 2017
# mark r. cass
# based on text_classification_cnn.py tensorflow model.
# modifications from original:
#   input:
#       choose dpedia or provide your own csv file.
#       use a subset of the dataset with selectable starting point and size.
#       selectable training to test ratio.
#   convolution layer 1:
#       multiple filter sizes.
#       number of filters adjustable for each filter size.
#       stride of filters adjustable for each filter size.
#   pooling layer (convolution layer 2):
#       adjustable filter size.`
#       adjustable number of filters.
#   fully connected layer:
#       adjustable width.
#       adjustable drop out normalization.
#       selectable activation function.
#   training:
#       adjustable expotential decay function.
#       adjustable number of training epochs
#       adjustable batch size
#       adjustable batch repeat.
#   misc:
#       logging of all output to a selectable log path.
#       automatically increasing log id appended to log name
#       detailed list of class hits amd misses dumped to log and screen
#       dump test error corpus for a specific class.
#       verbose tensorflow messaging output is turned off so output to screen is cleaner.
#
# todo:
#   * more clean up
#   * command line args
#   * connect to sweeper automation
#   * investigate the usefulness of the 2nd conv layer
#   * generate reports.
#        * summarize hyperparameter vs accuracy (overall and by class)
#   * graphs
#   * tensorboard
#   * model save and reload
#   * inference interactive and from file
#
# reference:
#   Convolutional Neural Networks for Sentence Classification
#     Yoon Kim
#     https://arxiv.org/abs/1408.5882

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

import notionnd.layers.embed as embed
from notionnd.layers.norm import normalize
from notionnd.layers.rnn import recurrent as recurrent
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
        rnn = recurrent(normed_word_vecs, features['INPUTLEN'], mode)
        fully_connected = dense(rnn, mode)
        outputs = output.output(fully_connected)
        return output.train_or_predict(features, labels, mode, params, outputs)


def static(features, labels, mode, params):
    with tf.device('/cpu:0'):
        word_vecs = embed.static(features)
    with tf.device('/gpu:0'):
        normed_word_vecs = normalize(word_vecs, mode)
        rnn = recurrent(normed_word_vecs, features['INPUTLEN'], mode)
        fully_connected = dense(rnn, mode)
        outputs = output.output(fully_connected)
        return output.train_or_predict(features, labels, mode, params, outputs)


def nonstatic(features, labels, mode, params):
    with tf.device('/gpu:{}'.format(hypers.get_param('sg'))):
        word_vecs = embed.nonstatic(features)
    with tf.device('/gpu:{}'.format(hypers.get_param('sg'))):
        normed_word_vecs = normalize(word_vecs, mode)
        rnn = recurrent(normed_word_vecs, features['INPUTLEN'], mode)
        fully_connected = dense(rnn, mode)
        outputs = output.output(fully_connected)
        return output.train_or_predict(features, labels, mode, params, outputs)
