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
lstm_cell = tf.contrib.rnn.LSTMCell
gru_cell = tf.contrib.rnn.GRUCell
clstm_cell = tf.contrib.rnn.CoupledInputForgetGateLSTMCell
ugrnn_cell = tf.contrib.rnn.UGRNNCell
dyn_bidir_rnn = tf.nn.bidirectional_dynamic_rnn
dyn_unidir_rnn = tf.nn.dynamic_rnn
rnn_dropout = tf.contrib.rnn.DropoutWrapper

from notionnd.layers.activations import activation_functions as activationFunc

mlog = None
hypers = None


def init(logger, hyper_params):
    global mlog, hypers
    mlog = logger
    hypers = hyper_params


def recurrent(features, lengths, mode):
    layer_type = hypers.get_param('rt')
    keep_prob = hypers.get_param('rd')
    training = (mode == tf.contrib.learn.ModeKeys.TRAIN)

    if layer_type == "bidir":
        output = rnn_bidir(features, lengths)
    elif layer_type == "unidir":
        output = rnn_unidir(features, lengths)

    if keep_prob > 0.0 and keep_prob < 1.0:
        output = tf.layers.dropout(output, keep_prob, training=training)

    output = ctblayers.layer_norm(output)
    # [dim] output rnn rt='unidir' ['tb', rw']
    # [dim] output rnn rt='bidir' ['tb', 2 * 'rw']
    return output


def rnn_last_output(rnn_output, seq_length):
    # batch_size = tf.shape(rnn_output)[0]
    # max_length = hypers.get_param('dx')
    # rnn_width = hypers.get_param('rw')
    # index = tf.range(0, batch_size) * max_length + (seq_length - 1)
    # flat = tf.reshape(rnn_output, [-1, rnn_width])
    # rnn_output = tf.gather(flat, index)

    rng = tf.range(0, tf.shape(seq_length)[0])
    indexes = tf.stack([rng, seq_length - 1], 1)
    rnn_output = tf.gather_nd(rnn_output, indexes)

    return rnn_output


def rnn_cells():
    cell_type = hypers.get_param('rc')
    act_func = activationFunc(hypers.get_param('ra'))
    forget_bias = hypers.get_param('rb')
    rnn_width = hypers.get_param('rw')
    peepholes = hypers.get_param('rp')

    # Forward / Backward layer_type cell
    if cell_type == "lstm":
        fw_cell = lstm_cell(rnn_width, use_peepholes=peepholes, forget_bias=forget_bias, activation=act_func)
        bw_cell = lstm_cell(rnn_width, use_peepholes=peepholes, forget_bias=forget_bias, activation=act_func)
    elif cell_type == "clstm":
        fw_cell = clstm_cell(rnn_width, use_peepholes=peepholes, forget_bias=forget_bias, activation=act_func)
        bw_cell = clstm_cell(rnn_width, use_peepholes=peepholes, forget_bias=forget_bias, activation=act_func)
    elif cell_type == "gru":
        fw_cell = gru_cell(rnn_width, activation=act_func)
        bw_cell = gru_cell(rnn_width, activation=act_func)
    elif cell_type == "ugrnn":
        fw_cell = ugrnn_cell(rnn_width, forget_bias=forget_bias, activation=act_func)
        bw_cell = ugrnn_cell(rnn_width, forget_bias=forget_bias, activation=act_func)

    return fw_cell, bw_cell


def rnn_bidir_reduce_states(rnn_state):
    cell_type = hypers.get_param('rc')
    reduce_mode = hypers.get_param('rr')

    # [dim] transform [fw, bw] ro=states rt=bidir ['tb', 'dx', 2 * 'rw']
    if cell_type == 'lstm' or cell_type == 'clstm':
        state_fw_c = rnn_state[0][0]
        state_fw_m = rnn_state[0][1]
        state_bw_c = rnn_state[1][0]
        state_bw_m = rnn_state[1][1]
        if reduce_mode == 'concat':
            state_c = tf.concat([state_fw_c, state_bw_c], axis=1)
            state_m = tf.concat([state_fw_m, state_bw_m], axis=1)
        else:
            state_c = tf.stack([state_fw_c, state_bw_c], axis=0)
            state_m = tf.stack([state_fw_m, state_bw_m], axis=0)
            state_c = tf.transpose(state_c, [1, 2, 0])
            state_m = tf.transpose(state_m, [1, 2, 0])
            if reduce_mode == 'max':
                state_c = tf.reduce_max(state_c, axis=2)
                state_m = tf.reduce_max(state_m, axis=2)
            elif reduce_mode == 'mean':
                state_c = tf.reduce_mean(state_c, axis=2)
                state_m = tf.reduce_mean(state_m, axis=2)
        states = tf.concat([state_c, state_m], axis=1)
    else:
        state_fw = rnn_state[0]
        state_bw = rnn_state[1]
        states = tf.concat([state_fw, state_bw], axis=1)
    return states


def rnn_bidir_reduce_output(rnn_output):
    reduce_mode = hypers.get_param('rr')

    output_fw = rnn_output[0]
    output_bw = rnn_output[1]

    if reduce_mode == 'concat':
        output = tf.concat([output_fw, output_bw], axis=2)
        output = tf.reshape(output, [-1, hypers.get_param('dx') * hypers.get_param('rw') * 2])
    else:
        output = tf.concat([output_fw, output_bw], axis=2)
        if reduce_mode == 'max':
            output = tf.reduce_max(output, axis=2)
        elif reduce_mode == 'mean':
            output = tf.reduce_mean(output, axis=2)

    return output


def rnn_bidir_reduce_lastoutput(rnn_output, lengths):
    reduce_mode = hypers.get_param('rr')

    output_fw = rnn_output[0]
    output_bw = rnn_output[1]

    output_fw = rnn_last_output(output_fw, lengths)
    output_bw = rnn_last_output(output_bw, lengths)

    if reduce_mode == 'concat':
        output = tf.concat([output_fw, output_bw], axis=1)
        output = tf.reshape(output, [-1, hypers.get_param('dx') * hypers.get_param('rw') * 2])
    else:
        output_fw = tf.expand_dims(output_fw, -1)
        output_bw = tf.expand_dims(output_bw, -1)
        output = tf.concat([output_fw, output_bw], axis=2)
        if reduce_mode == 'max':
            output = tf.reduce_max(output, axis=2)
        elif reduce_mode == 'mean':
            output = tf.reduce_mean(output, axis=2)

    return output


def rnn_bidir(features, lengths):
    output_type = hypers.get_param('ro')

    fw_cell, bw_cell = rnn_cells()

    # [dim] calc features->rnn_output rc=gru rt=bidir ['tb', 'dx', 'rw', 2]
    # [dim] calc features->rnn_state rc=gru rt=bidir ['tb', 'rw', 2]
    # [dim] calc features->rnn_output rc=[lstm,clstm] rt=bidir ['tb', 'dx', 'rw', 4]
    # [dim] calc features->rnn_state rc=[lstm,clstm] rt=bidir ['tb', 'rw', 4]
    rnn_output, rnn_state = dyn_bidir_rnn(fw_cell, bw_cell, features, sequence_length=lengths, dtype=tf.float32)
    if output_type == 'last_output':
        output = rnn_bidir_reduce_lastoutput(rnn_output, lengths)
    elif output_type == 'output':
        output = rnn_bidir_reduce_output(rnn_output)
    elif output_type == "states":
        output = rnn_bidir_reduce_states(rnn_state)

    # [dim] calc rnn_output rc=gru rt=bidir ro=last_output ['tb', 'dx', 'rw']
    # [dim] calc rnn_state rc=gru rt=bidir ro=states ['tb', 'rw']
    return output


def rnn_unidir_reduce_states(rnn_state):
    cell_type = hypers.get_param('rc')
    reduce_mode = hypers.get_param('rr')

    # [dim] transform [fw, bw] ro=states rt=bidir ['tb', 'dx', 2 * 'rw']
    if cell_type == 'lstm' or cell_type == 'clstm':
        state_fw_c = rnn_state[0]
        state_fw_m = rnn_state[1]
        if reduce_mode == 'concat':
            states = tf.concat([state_fw_c, state_fw_m], axis=1)
        else:
            states = tf.stack([state_fw_c, state_fw_m], axis=0)
            states = tf.transpose(states, [1, 2, 0])
            if reduce_mode == 'max':
                states = tf.reduce_max(states, axis=2)
            elif reduce_mode == 'mean':
                states = tf.reduce_mean(states, axis=2)
    else:
        states = rnn_state

    return states


def rnn_unidir_reduce_output(rnn_output):
    reduce_mode = hypers.get_param('rr')

    output_fw = rnn_output

    if reduce_mode == 'concat':
        output = tf.reshape(output_fw, [-1, hypers.get_param('dx') * hypers.get_param('rw')])
    else:
        if reduce_mode == 'max':
            output = tf.reduce_max(output_fw, axis=2)
        elif reduce_mode == 'mean':
            output = tf.reduce_mean(output_fw, axis=2)

    return output


def rnn_unidir(features, lengths):
    cell_type = hypers.get_param('rc')
    output_type = hypers.get_param('ro')

    fw_cell, _ = rnn_cells()

    # [dim] calc fw rt=unidir ['tb', 'dx', 'rw']
    rnn_output, rnn_state = dyn_unidir_rnn(fw_cell, features, sequence_length=lengths, dtype=tf.float32)
    if output_type == 'last_output':
        # [dim] transform fw ro=last_output rt=unidir ['tb', 'dx', 'rw']
        output = rnn_last_output(rnn_output, lengths)
    elif output_type == 'output':
        # [dim] transform fw ro=last_output rt=unidir ['tb', 'dx', 'rw']
        output = rnn_unidir_reduce_output(rnn_output)
    elif output_type == 'states':
        output = rnn_unidir_reduce_states(rnn_state)

    # [dim] output rnn rt='unidir' ['tb', rw']
    # [dim] output rnn rt='bidir' ['tb', 2 * 'rw']
    return output
