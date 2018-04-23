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


def fully_connected(features, mode):
    keep_prob = hypers.get_param('fd')
    training = (mode == tf.contrib.learn.ModeKeys.TRAIN)
    fc_act_func = activationFunc(hypers.get_param('fa'))
    width = hypers.get_param('fw')
    bias = hypers.get_param('fb')
    scale = hypers.get_param('ff')
    mode = hypers.get_param('fm')
    uniform = hypers.get_param('fu')

    if width > 0:
        winitializer = ctblayers.variance_scaling_initializer(factor=scale, mode=mode, uniform=uniform)
        binitializer = tf.constant_initializer(bias)
        output = ctblayers.fully_connected(features, width, weights_initializer=winitializer, biases_initializer=binitializer, activation_fn=fc_act_func)
    else:
        output = features

    if keep_prob > 0.0 and keep_prob < 1.0:
        output = tf.layers.dropout(output, keep_prob, training=training)

    # [dim] output fc fw>0 [bc, fw]
    # [dim] output fc fw=0 [bc, input]
    return output
