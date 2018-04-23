# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Text datasets."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import collections
import random
import numpy as np
import pandas

mlog = None
hypers = None

import tensorflow as tf
from tensorflow.contrib.learn.python.learn.datasets import base
learn = tf.contrib.learn

Dataset = collections.namedtuple('Dataset', ['data', 'target'])
Datasets = collections.namedtuple('Datasets', ['train', 'validation', 'test'])


def init(logger, hyper_params):
    global mlog, hypers
    mlog = logger
    hypers = hyper_params


def load():
    if hypers.get_param('ds') == 'dbpedia_small':
        return loadDbpediaDataset("small")
    elif hypers.get_param('ds') == 'dbpedia_large':
        return loadDbpediaDataset("large")
    elif hypers.get_param('ds') == 'rotten':
        return loadRottenDataset()
    else:
        return loadCsvDataset()


def loadDbpediaDataset(size):
    dbpediaSet = loadDbpedia(size=size)
    x_train = pandas.DataFrame(dbpediaSet.train.data)[1]
    y_train = pandas.Series(dbpediaSet.train.target)
    x_test = pandas.DataFrame(dbpediaSet.test.data)[1]
    y_test = pandas.Series(dbpediaSet.test.target)
    return x_train, y_train, x_test, y_test, None


def loadRottenDataset():
    # returns [bugDataSet, targetIdDict, targetFreqDict, targets]
    ds = load_csv_data(hypers.get_param('ds'),
                       hypers.get_param('di'),
                       hypers.get_param('dn'),
                       hypers.get_param('dx'),
                       hypers.get_param('dc'),
                       hypers.get_param('dr'),
                       hypers.get_param('db'),
                       hypers.get_param('dv'))
    x_train = pandas.DataFrame(ds[0].train.data)[0]
    y_train = pandas.Series(ds[0].train.target)
    x_test = pandas.DataFrame(ds[0].test.data)[0]
    y_test = pandas.Series(ds[0].test.target)
    return x_train, y_train, x_test, y_test, ds[1]


def loadCsvDataset():
    # returns [bugDataSet, targetIdDict, targetFreqDict, targets]
    ds = load_csv_data(hypers.get_param('ds'),
                       hypers.get_param('di'),
                       hypers.get_param('dn'),
                       hypers.get_param('dx'),
                       hypers.get_param('dc'),
                       hypers.get_param('dr'),
                       hypers.get_param('db'),
                       hypers.get_param('dv'))
    x_train = ds[0].train.data
    y_train = ds[0].train.target
    l_train = ds[1]['train']
    lw_train = ds[2]['train']
    x_test = ds[0].test.data
    y_test = ds[0].test.target
    l_test = ds[1]['test']
    lw_test = ds[2]['test']
    return x_train, y_train, l_train, lw_train, x_test, y_test, l_test, lw_test, ds[3]


def encode(train, test):
    mlog.usrmsg(1, 2, 'creating vocabulary...')
    if hypers.get_param('wv') is not None:
        wv_vocab = loadWordVectorsVocab(hypers.get_param('wv'))
        n_words = len(wv_vocab)
        train = encodeUsingVocab(wv_vocab, train)
        test = encodeUsingVocab(wv_vocab, test)
    else:
        # Process vocabulary
        vocab_processor = learn.preprocessing.VocabularyProcessor(hypers.get_param('dx') + max(hypers.get_param('cw')))
        train = np.array(list(vocab_processor.transform(train)))
        test = np.array(list(vocab_processor.transform(test)))
        n_words = len(vocab_processor.vocabulary_)

    mlog.usrmsg(0, 4, 'Total words: %d' % n_words)
    mlog.usrmsg(0, 4, 'train size: %d' % len(train))
    mlog.usrmsg(0, 4, 'test size: %d' % len(test))

    return train, test, n_words


def load_csv_data(file_name, start_ex_id, min_ex_len, max_ex_len, max_examples, training_test_ratio, trainlabel_ratios, testlabel_ratios):
    detail_dict = {}
    random.seed(hypers.get_param('da'))
    np.random.seed(seed=hypers.get_param('da'))
    tf.set_random_seed(hypers.get_param('da'))

    ex_dict = build_example_dict(file_name, start_ex_id, detail_dict)
    prune_example_vocab(ex_dict, detail_dict)
    pruned_dict = prune_short_long(ex_dict, min_ex_len, max_ex_len, detail_dict)

    datasets = assemble_datasets(pruned_dict, max_examples, training_test_ratio, trainlabel_ratios, testlabel_ratios, detail_dict)

    bugset = Datasets(train=datasets['training_set'], validation=None, test=datasets['test_set'])

    return bugset, datasets['lengths'], datasets['lbl_weights'], datasets['details']


def loadDbpedia(size='small'):
    """Get DBpedia datasets from CSV files."""
    data_dir = '../data/dbpedia_data'

    train_path = os.path.join(data_dir, 'dbpedia_csv', 'train.csv')
    test_path = os.path.join(data_dir, 'dbpedia_csv', 'test.csv')

    if size == 'small':
        # Reduce the size of original data by a factor of 1000.
        train_path = train_path.replace('train.csv', 'train_small.csv')
        test_path = test_path.replace('test.csv', 'test_small.csv')

    train = base.load_csv_without_header(train_path, target_dtype=np.int32, features_dtype=np.str, target_column=0)
    test = base.load_csv_without_header(test_path, target_dtype=np.int32, features_dtype=np.str, target_column=0)

    return base.Datasets(train=train, validation=None, test=test)


def disassymble_example(example):
    parts = example.split(',')

    ex_id = int(parts[0].strip())
    ex_label = parts[1].strip()

    ex_data = parts[2].strip().split(' ')
    ex_data = filter(None, ex_data)

    return ex_id, ex_label, ex_data


def add_example_to_vocab(vocab_dict, ex_id, ex_label, word_list):
    word_count = 0
    for word in word_list:
        if word not in vocab_dict:
            vocab_dict[word] = {}
            vocab_dict[word]['labels'] = {}
            vocab_dict[word]['freq'] = 0
        if ex_label not in vocab_dict[word]['labels']:
            vocab_dict[word]['labels'][ex_label] = []
        vocab_dict[word]['freq'] += 1
        vocab_dict[word]['labels'][ex_label].append(ex_id)
        word_count += 1


def build_example_dict(fileName, start_ex_id, detail_dict):

    # ex_dict layout (dictionary of examples)
    # {
    #   key = (example label)
    #   value = {
    #               key = (example input length) length of the example input
    #                       character string.
    #               value = {
    #                           key = (example unique id) example id
    #                           value = example input character str
    #                       }
    #           }
    # }
    #

    mlog.usrmsg(0, 2, "Reading {}".format(fileName))
    _, infile = mlog.openFileR(fileName)
    _, dataRows = mlog.readFileLines(infile)
    mlog.closeFile(infile)
    mlog.usrmsg(0, 3, "read {} examples".format(fileName))

    mlog.usrmsg(0, 2, "Removing examples with id less than {}".format(start_ex_id))
    label_dict = {}
    vocab_dict = {}
    removed_dict = {}
    num_removed = 0
    for row in dataRows:
        ex_id, ex_label, ex_data = disassymble_example(row)

        if ex_id < start_ex_id:
            removed_dict[ex_id] = {"label": ex_label, "example": ex_data, "reason": "min_id"}
            num_removed += 1
            continue
        if ex_data is None or len(ex_data) == 0:
            removed_dict[ex_id] = {"label": ex_label, "example": ex_data, "reason": "zero_len"}
            num_removed += 1
            continue

        add_example_to_vocab(vocab_dict, ex_id, ex_label, ex_data)

        if ex_label not in label_dict:
            label_dict[ex_label] = {len(ex_data): {ex_id: ex_data}}
        elif len(ex_data) not in label_dict[ex_label]:
            label_dict[ex_label][len(ex_data)] = {ex_id: ex_data}
        else:
            label_dict[ex_label][len(ex_data)][ex_id] = ex_data

    detail_dict['vocab_dict'] = vocab_dict
    detail_dict['exclude_dict'] = removed_dict
    mlog.usrmsg(0, 3, "Examples: removed {}. remaining = {}".format(num_removed, len(dataRows) - num_removed))

    return label_dict


def prune_example_vocab(label_dict, detail_dict):
    min_freq = hypers.get_param('df')
    mlog.usrmsg(0, 2, "Removing low frequency words limit = {} words".format(min_freq))
    num_words_removed = 0
    num_examples_removed = 0
    vocab_prunes = {}

    for label, ex_len_dict in label_dict.iteritems():
        for _, ex_dict in ex_len_dict.iteritems():
            del_keys = []
            for key, word_list in ex_dict.iteritems():
                keep = []
                for word in word_list:
                    if detail_dict['vocab_dict'][word]['freq'] > min_freq:
                        keep.append(word)
                    else:
                        num_words_removed += 1
                        if word not in vocab_prunes:
                            vocab_prunes[word] = 1
                        else:
                            vocab_prunes[word] += 1
                if len(keep) == 0:
                    del_keys.append(key)
                    num_examples_removed += 1
                else:
                    ex_dict[key] = keep
            for dk in del_keys:
                detail_dict['exclude_dict'][dk] = {"label": label, "example": ex_dict[dk], "reason": "vocab_prune"}
                del ex_dict[dk]

    detail_dict['vocab_prunes'] = vocab_prunes
    mlog.usrmsg(0, 3, "Pruned: words {}. examples = {}".format(num_words_removed, num_examples_removed))


def pad_example_data(ex_words, fixed_length):
    #num_pre_pad = max(hypers.get_param("cw"))
    num_pre_pad = 0
    num_post_pad = num_pre_pad
    if len(ex_words) > fixed_length:
        formatted_data = ex_words[:fixed_length]
    elif len(ex_words) < fixed_length:
        formatted_data = ex_words
        num_post_pad = fixed_length - len(ex_words)
        num_post_pad += num_pre_pad
    else:
        formatted_data = ex_words

    pre_padding = ['$PAD'] * num_pre_pad
    post_padding = ['$PAD'] * num_post_pad
    formatted_data = pre_padding + formatted_data + post_padding

    return formatted_data, max(fixed_length - len(ex_words), 0)


def prune_short_long(data_label_dict, min_ex_len, max_ex_len, detail_dict):
    #pruned dict layout
    # {
    #   key = (example label)
    #   value = {
    #               key = (example input length) length of the example input
    #                       character string.
    #               value = {
    #                           key = (example unique id) example id
    #                           value = example input character str
    #                       }
    #           }
    # }
    mlog.usrmsg(0, 2, "Removing examples with less than {} words".format(min_ex_len))
    pruned_dict = {}
    length_dict = {}
    detail_dict['lengths'] = length_dict
    num_pruned = 0
    num_remaining = 0
    total_pad_added = examples_padded = 0
    num_truncated = 0
    for label, len_dict in data_label_dict.iteritems():
        for ex_data_len, id_dict in len_dict.iteritems():
            for ex_id, ex_data in id_dict.iteritems():
                if label not in pruned_dict:
                    pruned_dict[label] = {}
                if ex_data_len >= min_ex_len:
                    pruned_dict[label][ex_id], num_pad_added = pad_example_data(ex_data, max_ex_len)
                    length_dict[ex_id] = max_ex_len - num_pad_added
                    num_remaining += 1
                    total_pad_added += num_pad_added
                    if num_pad_added > 0:
                        examples_padded += 1
                    elif ex_data_len > max_ex_len:
                        num_truncated += 1
                else:
                    num_pruned += 1
                    detail_dict['exclude_dict'][ex_id] = {"label": label, "example": ex_data, "reason": "vocab_prune"}

    trunc_perc = (float(num_truncated) / float(num_remaining)) * 100.0
    mlog.usrmsg(0, 3, "Truncation: examples truncated : {} ({:.2f}%)".format(num_truncated, trunc_perc))
    examples_padded_perc = (float(examples_padded) / float(num_remaining)) * 100.0
    mlog.usrmsg(0, 3, "Padding: examples padded       : {} ({:.2f}%)".format(examples_padded, examples_padded_perc))
    total_words = num_remaining * max_ex_len
    pad_words_perc = (float(total_pad_added) / float(total_words)) * 100.0
    mlog.usrmsg(0, 3, "         pad words             : {} ({:.2f}%)".format(total_pad_added, pad_words_perc))
    mlog.usrmsg(0, 3, "Examples: removed {}. remaining = {}".format(num_pruned, num_remaining))
    return pruned_dict


def get_samplingformat_uniform(label_dict, max_examples, trainlabel_ratios, testlabel_ratios, trainingtest_ratio):
    label_key_dict = {}

    # for each label determine the first,last exid and count.
    label_idx = 0
    num_labels = 2
    balanced_ratio = 1.0 / float(num_labels)
    for label, id_dict in sorted(label_dict.iteritems()):
        #max_test = testlabel_ratios[label_idx] * (max_examples / 2)
        #max_train = trainlabel_ratios[label_idx] * (max_examples / 2)
        testbalanced_pool_size = (max_examples * trainingtest_ratio) / num_labels
        trainbalanced_pool_size = (max_examples * (1.0 - trainingtest_ratio)) / num_labels
        max_test = (testlabel_ratios[label_idx] / balanced_ratio) * testbalanced_pool_size
        max_train = (trainlabel_ratios[label_idx] / balanced_ratio) * trainbalanced_pool_size
        max_label_examples = int(max_train + max_test)
        num_label_examples = 0
        label_key_dict[label] = {'max': max_label_examples, 'first_key': 0, 'last_key': 0, 'count': 0, 'step': 1.0}
        for ex_id, _ in sorted(id_dict.iteritems()):
            if label_key_dict[label]['count'] == 0:
                label_key_dict[label]['first_key'] = ex_id
                label_key_dict[label]['last_key'] = ex_id
            else:
                label_key_dict[label]['last_key'] = ex_id
            label_key_dict[label]['count'] += 1
            num_label_examples += 1
            if num_label_examples >= label_key_dict[label]['max']:
                break
        label_idx += 1

    # the label whos last_key (exid) is the greatest is the label with the least examples
    last_label = ""
    for label, label_data in sorted(label_key_dict.iteritems()):
        if last_label == "" or label_data['last_key'] > label_key_dict[last_label]['last_key']:
            last_label = label

    # for all labels except the label with the fewest examples. adjust the
    # last key (exid) to the greatest id that is less then the fewest label
    # last example.
    last_id = label_key_dict[last_label]['last_key']
    for label, label_data in sorted(label_key_dict.iteritems()):
        label_key_dict[label]['count'] = 0
        for ex_id, _ in sorted(label_dict[label].iteritems()):
            if ex_id < label_data['first_key']:
                continue
            if ex_id <= last_id:
                label_data['last_key'] = ex_id
                label_data['count'] += 1
            else:
                break
        label_data['step'] = float(label_key_dict[label]['count']) / float(label_key_dict[label]['max'])

    for label, data in sorted(label_key_dict.iteritems()):
        mlog.usrmsg(0, 3, "ranges {:<10}: first= {:<7} last= {:<7} count= {:<7} step= {:1.2f}".format(label, data['first_key'], data['last_key'], data['count'], data['step']))

    return label_key_dict


def uniform_sample_exdict(ex_dict, sampling_format):
    samples = []

    next_sample_idx = 0
    ex_idx = 0
    num_samples = 0
    for ex_id, _ in sorted(ex_dict.iteritems()):
        if ex_id < sampling_format['first_key']:
            continue
        if ex_idx == next_sample_idx:
            samples.append(ex_id)
            num_samples += 1
            next_sample_idx = int((float(num_samples) * sampling_format['step']) + .5)
        if ex_id >= sampling_format['last_key']:
            break
        ex_idx += 1
    return samples


def uniform_split(exid_list, ratio):
    split_a = []
    split_b = []

    step = 1.0 / ratio
    next_b_idx = 0.0
    for idx in xrange(len(exid_list)):
        if idx == int(next_b_idx + .5):
            split_b.append(exid_list[idx])
            next_b_idx += step
        else:
            split_a.append(exid_list[idx])
    return split_a, split_b


def merge_labels_interleaved(labels_iddict):
    longest_idlist_len = 0
    interleaved_idlist = []
    for label, idlist in labels_iddict.iteritems():
        if len(idlist) > longest_idlist_len:
            longest_idlist_len = len(idlist)

    for idx in xrange(longest_idlist_len):
        for label, idlist in labels_iddict.iteritems():
            if len(idlist) > idx:
                interleaved_idlist.append({'label': label, 'id': idlist[idx]})

    return interleaved_idlist


def idlist_to_dataset(idlist, id_labels, label_examples, length_dict):
    count = 0
    examples = []
    labels = []
    lengths = []
    weights = []
    meta_data = {}

    label_ids = dict((v, k) for k, v in id_labels.iteritems())
    weightings = hypers.get_param('dw')

    for idx in xrange(len(idlist)):
        label = idlist[idx]['label']
        exid = idlist[idx]['id']
        ex_string = ' '.join(label_examples[label][exid])
        examples.append(np.asarray(ex_string, dtype=np.str))
        labels.append(label_ids[label])
        lengths.append(length_dict[exid])
        weights.append(weightings[label_ids[label]])
        meta_data[count] = {'id': exid}
        count += 1

    return {'examples': examples, 'lengths': lengths, 'labels': labels, 'meta': meta_data, 'weights': weights}


def encode_labels(label_dict):
    encoding = {}
    for label, _ in sorted(label_dict.iteritems()):
        encoding[len(encoding)] = label
    return encoding


def form_trainingtest(label_dict, max_examples, trainingtest_ratio, train_label_ratios, test_label_ratios, length_dict):
    label_id_dict = {}

    train_ids = {}
    test_ids = {}

    set_metrics = {'train': {}, 'test': {}}

    sampling_format = get_samplingformat_uniform(label_dict, max_examples, train_label_ratios, test_label_ratios, trainingtest_ratio)

    pool_size = 0
    label_idx = 0
    for label, ex_dict in sorted(label_dict.iteritems()):
        pool_size += len(ex_dict)
        samples = uniform_sample_exdict(ex_dict, sampling_format[label])
        num_samples = len(samples)
        num_test = float(max_examples * trainingtest_ratio) * test_label_ratios[label_idx]
        ratio = float(num_test) / float(num_samples)
        train, test = uniform_split(samples, ratio)
        set_metrics['train'][label] = len(train)
        set_metrics['test'][label] = len(test)
        train_ids[label] = train
        test_ids[label] = test
        label_idx += 1

    train_merged = merge_labels_interleaved(train_ids)
    test_merged = merge_labels_interleaved(test_ids)

    label_id_dict = encode_labels(label_dict)

    training = idlist_to_dataset(train_merged, label_id_dict, label_dict, length_dict)
    testing = idlist_to_dataset(test_merged, label_id_dict, label_dict, length_dict)

    tt_data = {}
    tt_data['pool_size'] = pool_size
    tt_data['num_ex'] = len(training['examples']) + len(testing['examples'])
    tt_data['num_train'] = len(training['examples'])
    tt_data['num_test'] = len(testing['examples'])
    tt_data['train_ex'] = training['examples']
    tt_data['train_ex_len'] = training['lengths']
    tt_data['train_lbl_weights'] = training['weights']
    tt_data['train_label'] = training['labels']
    tt_data['test_ex'] = testing['examples']
    tt_data['test_label'] = testing['labels']
    tt_data['test_ex_len'] = testing['lengths']
    tt_data['test_lbl_weights'] = testing['weights']
    tt_data['label_id_dict'] = label_id_dict
    tt_data['ex_info_dict'] = {'train': training['meta'], 'test': testing['meta']}

    return tt_data, set_metrics


def assemble_datasets(label_dict, max_examples, training_test_ratio, train_label_ratios, test_label_ratios, detail_dict):
    mlog.usrmsg(0, 2, "Assemblying final dataset")

    tt_data, metrics = form_trainingtest(label_dict, max_examples, training_test_ratio, train_label_ratios, test_label_ratios, detail_dict['lengths'])
    # tt_data = shuffle_trainingtest(tt_data)

    datasets = {}

    examples = np.array(tt_data['train_ex'])
    lengths = np.array(tt_data['train_ex_len'], dtype=np.int32)
    labels = np.array(tt_data['train_label'], dtype=np.int32)
    weights = np.array(tt_data['train_lbl_weights'], dtype=np.float32)
    datasets['training_set'] = Dataset(data=examples, target=labels)
    datasets['lengths'] = {'train': lengths, 'test': None}
    datasets['lbl_weights'] = {'train': weights, 'test': None}

    examples = np.array(tt_data['test_ex'])
    lengths = np.array(tt_data['test_ex_len'], dtype=np.int32)
    labels = np.array(tt_data['test_label'], dtype=np.int32)
    weights = np.array(tt_data['test_lbl_weights'], dtype=np.float32)
    datasets['test_set'] = Dataset(data=examples, target=labels)
    datasets['lengths']['test'] = lengths
    datasets['lbl_weights']['test'] = weights

    dataset_details = detail_dict
    dataset_details['label_id_dict'] = tt_data['label_id_dict']
    dataset_details['info'] = tt_data['ex_info_dict']
    datasets['details'] = dataset_details

    mlog.usrmsg(0, 3, "Training set size= {} ({:0.2f})".format(tt_data['num_train'], float(tt_data['num_train']) / float(max_examples)))
    label_idx = 0
    for label, count in sorted(metrics['train'].iteritems()):
        actual_perc = float(count) / (float(max_examples) * (1.0 - training_test_ratio))
        mlog.usrmsg(0, 4, "{:<10}= {} ({:.2f})".format(label, count, actual_perc))
        label_idx += 1
    mlog.usrmsg(0, 3, "Test   set   size= {} ({:.2f})".format(tt_data['num_test'], float(tt_data['num_test']) / float(max_examples)))
    label_idx = 0
    for label, count in sorted(metrics['test'].iteritems()):
        actual_perc = float(count) / (float(max_examples) * training_test_ratio)
        mlog.usrmsg(0, 4, "{:<10}= {} ({:.2f})".format(label, count, actual_perc))
        label_idx += 1
    mlog.usrmsg(0, 3, "Examples: removed = {} remaining = {}".format(tt_data['pool_size'] - (tt_data['num_train'] + tt_data['num_test']), tt_data['num_ex']))

    return datasets


def loadWordVectorsVocab(wv_path):
    _, fin = mlog.openFileR(wv_path + "/vocab.txt")
    _, fin_lines = mlog.readFileLines(fin)
    mlog.closeFile(fin)

    vocab_dict = {}
    counter = 1
    for line in fin_lines:
        line_parts = line.split(" ")
        word = line_parts[0].strip()
        vocab_dict[word] = counter
        counter += 1
    vocab_dict["$PAD"] = counter
    return vocab_dict


def encodeUsingVocab(vocab_dict, data):
    encoded_data = np.ndarray((len(data), len(data[0].split())), dtype=np.int32)
    unknowns = 0
    total_words = 0
    unknown_dict = {}
    row = 0
    for elem in data:
        words = elem.split(" ")
        if hypers.get_param('de'):
            words.reverse()
        column = 0
        for word in words:
            word = word.strip()
            if word == '$PAD':
                encoded_data[row][column] = 0
            elif word in vocab_dict:
                encoded_data[row][column] = vocab_dict[word]
            else:
                encoded_data[row][column] = vocab_dict["UNK"]
                unknowns += 1
                if word not in unknown_dict:
                    unknown_dict[word] = 0
                unknown_dict[word] += 1
            column += 1
            total_words += 1
        row += 1

    unknowns_by_key_ascending = sorted(unknown_dict)
    _, fout = mlog.openFileW("{}/word2vec_unknowns.txt".format(hypers.get_param('ls')))
    for key in unknowns_by_key_ascending:
        mlog.writeFileLine(fout, "{} {}".format(key, unknown_dict[key]))
    mlog.closeFile(fout)

    return encoded_data
