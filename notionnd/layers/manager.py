# dnnotion ie 2017
# mark r. cass

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import notionnd.layers.embed as embed
import notionnd.layers.norm as normalize
import notionnd.layers.cnn as convolution
import notionnd.layers.rnn as recurrent
import notionnd.layers.dense as dense
import notionnd.layers.output as output

# todo this is messy and only for debugging
import tensorflow as tf
learn = tf.contrib.learn

mlog = None
hypers = None


def init(logger, hyper_params):
    global mlog, hypers
    mlog = logger
    hypers = hyper_params
    embed.init(logger, hyper_params)
    normalize.init(logger, hyper_params)
    convolution.init(logger, hyper_params)
    recurrent.init(logger, hyper_params)
    dense.init(logger, hyper_params)
    output.init(logger, hyper_params)
