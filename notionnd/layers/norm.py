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

from notionnd.layers.activations import activation_functions as activationFunc

mlog = None
hypers = None


def init(logger, hyper_params):
    global mlog, hypers
    mlog = logger
    hypers = hyper_params


def normalize(features, mode):
    if hypers.get_param("wn") == 'layer':
        output = layer_normalize(features, mode)
    elif hypers.get_param("wn") == 'batch':
        output = batch_normalize(features, mode)
    else:
        output = features

    keep_prob = 1.0 - hypers.get_param('wd')
    if keep_prob > 0.0 and keep_prob < 1.0:
        training = (mode == tf.contrib.learn.ModeKeys.TRAIN)
        output = tf.layers.dropout(output, keep_prob, training=training)

    return output


def layer_normalize(features, mode):
    act_func = activationFunc(hypers.get_param('wa'))
    center = hypers.get_param('wc')
    scale = hypers.get_param('w1')

    output = ctblayers.layer_norm(features, center=center, scale=scale, activation_fn=act_func)

    # dim output normalize ['tb', 'dx', 'ws']
    return output


def batch_normalize(features, mode):
    act_func = activationFunc(hypers.get_param('wa'))
    decay = hypers.get_param('wy')
    center = hypers.get_param('wc')
    scale = hypers.get_param('w1')
    epsilon = hypers.get_param('we')
    training = (mode == tf.contrib.learn.ModeKeys.TRAIN)

    output = ctblayers.batch_norm(features, decay=decay, center=center, scale=scale, epsilon=epsilon, activation_fn=act_func, is_training=training)

    # dim output normalize ['tb', 'dx', 'ws']
    return output
