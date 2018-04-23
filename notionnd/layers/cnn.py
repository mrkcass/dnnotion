# dnnotion ie 2017
# mark r. cass

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

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


def multidim_convolution(features, mode):
    filter_pool = []
    max_words = hypers.get_param('dx') + (max(hypers.get_param('cw')) * 2)
    pad_width = max(hypers.get_param('cw'))
    bias = hypers.get_param('cb')
    scale = hypers.get_param('cf')
    mode = hypers.get_param('cm')
    uniform = hypers.get_param('cu')
    total_filter_count = 0
    features = tf.pad(features, paddings=[[0, 0], [pad_width, pad_width], [0, 0]], mode="CONSTANT")
    word_vectors = tf.expand_dims(features, 3)

    for i, filter_width in enumerate(hypers.get_param('cw')):
        conv_filter_shape = [filter_width, hypers.get_param('ws')]
        num_filters = hypers.get_param('cn')[i]
        total_filter_count += num_filters
        winitializer = ctblayers.variance_scaling_initializer(factor=scale, mode=mode, uniform=uniform)
        binitializer = tf.constant_initializer(bias)
        # [dim] calc conv2d ['tb', 'dx' + (2 * max 'cw') - 'cw', 1, 'cn']
        conv_2d = ctblayers.convolution2d(word_vectors, num_filters, conv_filter_shape, weights_initializer=winitializer, biases_initializer=binitializer, padding='VALID')
        # Max pooling across output of Convolution+Relu.
        pool_filter_shape = [1, max_words - filter_width + 1, 1, 1]
        pool_stride = [1, 1, 1, 1]
        # [dim] calc maxpool ['tb', 1, 1, 'cn']
        conv2d_max_pool = tf.nn.max_pool(conv_2d, ksize=pool_filter_shape, strides=pool_stride, padding='VALID')
        filter_pool.append(conv2d_max_pool)

    filter_array = tf.concat(filter_pool, 3)
    # [dim] transform flatten ['tb', sum 'cn']
    output = tf.reshape(filter_array, [-1, total_filter_count])

    keep_prob = hypers.get_param('cd')
    training = (mode == tf.contrib.learn.ModeKeys.TRAIN)
    if keep_prob > 0.0 and keep_prob < 1.0:
        output = tf.layers.dropout(output, keep_prob, training=training)

    # [dim] output cnn ['tb', sum 'cn']
    return output
