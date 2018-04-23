# dnnotion ie 2017
# mark r. cass

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf


def activation_functions(hyperName):
    funcs = {
        'relu': tf.nn.relu,
        'elu': tf.nn.elu,
        'tanh': tf.nn.tanh,
        'sigmoid': tf.sigmoid,
        'selu': tf.nn.selu,
        'crelu': tf.nn.crelu,
        'relu6': tf.nn.relu6,
        'softsign': tf.nn.softsign,
        'softplus': tf.nn.softplus,
        'linear': None
    }
    return funcs[hyperName]
