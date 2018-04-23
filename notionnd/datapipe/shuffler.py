# dnnotion ie 2017
# mark r. cass
# based on text_classification_cnn.py tensorflow model.


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import random
import multiprocessing
import numpy as np

mlog = None
hypers = None


def init(logger, hyper_params):
    global mlog, hypers
    mlog = logger
    hypers = hyper_params


def shuffle_thread(features, labels, lengths, lbl_weights, threadid, shuffle_result):
    num_batches = int(len(features) / hypers.get_param('tb'))
    if num_batches * hypers.get_param('tb') != len(features):
        num_batches += 1
    shuffled_features = []
    shuffled_labels = []
    shuffled_lengths = []
    shuffled_weights = []
    order = []
    for idx in xrange(num_batches):
        order.append(idx)
    random.shuffle(order)
    for order_idx in xrange(num_batches):
        start = order[order_idx] * hypers.get_param('tb')
        if start + hypers.get_param('tb') >= len(features):
            start = len(features) - hypers.get_param('tb')
        for batch_idx in xrange(hypers.get_param('tb')):
            shuffled_features.append(features[start + batch_idx])
            shuffled_labels.append(labels[start + batch_idx])
            shuffled_lengths.append(lengths[start + batch_idx])
            shuffled_weights.append(lbl_weights[start + batch_idx])
    shuffle_result['shuffle_buffers'][threadid] = {'features': shuffled_features, 'labels': shuffled_labels, 'lengths': shuffled_lengths, 'lbl_weights': shuffled_weights}
    shuffle_result['shuffles_completed'] += 1


def shuffle(features, labels, lengths, lbl_weights):
    round_data = {}
    round_data['ready'] = False
    round_data['batch_size'] = hypers.get_param('tb')
    round_data['num_batches_fed'] = 0
    round_data['shuffles_completed'] = 0
    round_data['shuffle_buffers'] = [None] * hypers.get_param('tc')[hypers.get_param('ti')]
    round_data['data'] = {'features': None, 'labels': None, 'lengths': None, 'lbl_weights': None}
    round_data['threads'] = []

    for i in xrange(hypers.get_param('tc')[hypers.get_param('ti')]):
        thread = multiprocessing.Process(target=shuffle_thread(features, labels, lengths, lbl_weights, i, round_data))
        round_data['threads'].append(thread)

    for thread in round_data['threads']:
        thread.start()

    return round_data


def get_round_data(round_data):
    for thread in round_data['threads']:
        thread.join()

    all_features = []
    all_lengths = []
    all_labels = []
    all_weights = []
    for result in round_data['shuffle_buffers']:
        all_features += result['features']
        all_lengths += result['lengths']
        all_labels += result['labels']
        all_weights += result['lbl_weights']

    round_data['data']['features'] = np.array(all_features, dtype=np.int32)
    round_data['data']['labels'] = np.array(all_labels, dtype=np.int32)
    round_data['data']['lengths'] = np.array(all_lengths, dtype=np.int32)
    round_data['data']['lbl_weights'] = np.array(all_weights, dtype=np.float32)
    round_data['ready'] = True

    return round_data

