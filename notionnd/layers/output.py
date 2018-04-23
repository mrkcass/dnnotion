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


def train_or_predict(features, labels, mode, params, model_output):
    #if mode == tf.contrib.learn.ModeKeys.TRAIN or mode == tf.contrib.learn.ModeKeys.EVAL:
    if mode == tf.contrib.learn.ModeKeys.TRAIN:
        return model_train(model_output, labels, features['LBLWEIGHTS'], features['INPUTLEN'], params, mode)
    else:
        return model_predict(model_output)


def output(features):
    width = hypers.get_param('on')
    act_func = activationFunc(hypers.get_param('oa'))
    bias = hypers.get_param('ob')
    scale = hypers.get_param('of')
    mode = hypers.get_param('om')
    uniform = hypers.get_param('ou')

    winitializer = ctblayers.variance_scaling_initializer(factor=scale, mode=mode, uniform=uniform)
    binitializer = tf.constant_initializer(bias)
    regularizer = ctblayers.l1_l2_regularizer(scale_l1=hypers.get_param('o1'), scale_l2=hypers.get_param('o2'))
    out_layer = ctblayers.fully_connected(features, width, weights_initializer=winitializer, weights_regularizer=regularizer, biases_initializer=binitializer, biases_regularizer=regularizer, activation_fn=act_func)

    # [dim] output ot fw>0 [bc, fw]
    return out_layer


def model_predict(features):

    inferred = {'class': tf.argmax(features, 1),
                'prob': tf.nn.softmax(features)}
    return tf.estimator.EstimatorSpec(tf.estimator.ModeKeys.PREDICT, inferred, None, None, None)


def model_train_decayfn(new_ops, gbl_step, steps_per_session, lr_rate):

    def decay_func(lrning_rate, gobal_step):
        new_rate = tf.train.exponential_decay(learning_rate=lrning_rate,
                                              global_step=gobal_step,
                                              decay_steps=steps_per_session,
                                              decay_rate=hypers.get_param('ld'),
                                              staircase=False,
                                              name="decayed_lrn_rate_op")
        return new_rate

    def_func_ref = decay_func

    decay_lrn_rate_op = framework.model_variable("decayed_lrn_rate", lr_rate.shape, lr_rate.dtype, trainable=False)
    new_rate = decay_func(lr_rate, gbl_step)
    op = tf.assign(decay_lrn_rate_op, new_rate)
    new_ops.append(op)

    return def_func_ref


def model_loss(new_ops, features, labels, lbl_weights, seq_length):
    logits_width = hypers.get_param('on')
    onehots = tf.one_hot(labels, logits_width, 1, 0, 1)
    loss_function = hypers.get_param('tl')

    lbl_weights = tf.scalar_mul(logits_width, lbl_weights)

    if loss_function == "softmax_cross_entropy":
        loss = tf.losses.softmax_cross_entropy(onehots, features, weights=lbl_weights)
    elif loss_function == "sigmoid_cross_entropy":
        loss = tf.losses.sigmoid_cross_entropy(onehots, features, weights=lbl_weights)
    elif loss_function == "mean_squared":
        loss = tf.losses.mean_squared_error(onehots, features, weights=lbl_weights)

    if hypers.get_param('tm'):
        max_length = tf.constant(hypers.get_param('dx'), tf.float32)
        length_scalar = tf.to_float(seq_length) / max_length
        length_scalar *= tf.to_float(tf.shape(seq_length)[0]) / tf.reduce_sum(length_scalar)
        loss = loss * length_scalar

    loss = tf.reduce_mean(loss)

    loss_var = framework.model_variable("avg_loss", loss.shape, loss.dtype, trainable=False)
    op = tf.assign(loss_var, loss)
    new_ops.append(op)

    return loss


def model_train(features, labels, lbl_weights, seq_len, params, mode):
    loss = None
    train_op = None
    update_ops = []

    eval_metric_ops = {}
    if mode != tf.contrib.learn.ModeKeys.INFER:
        gbl_step = tf.train.get_global_step()
        lr_rate = tf.constant(hypers.get_param('lr'))

        decay_func = model_train_decayfn(update_ops, gbl_step, params['steps_per_session'], lr_rate)

        loss = model_loss(update_ops, features, labels, lbl_weights, seq_len)

        optimizer_name = hypers.get_param('to')
        train_op = ctblayers.optimize_loss(loss,
                                           global_step=gbl_step,
                                           optimizer=optimizer_name,
                                           learning_rate=hypers.get_param('lr'),
                                           learning_rate_decay_fn=decay_func,
                                           update_ops=update_ops,
                                           name="model_train_optimizer")

    return tf.estimator.EstimatorSpec(mode, None, loss, train_op, eval_metric_ops)

