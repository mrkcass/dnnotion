# dnnotion ie 2017
# mark r. cass
# based on text_classification_cnn.py tensorflow model.


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from datetime import datetime
import collections
import numpy as np
import tensorflow as tf

from tensorflow import contrib as tfc
from tensorflow.python.estimator.inputs.queues import feeding_functions
from tensorflow.python.estimator import run_config

import notionnd.models.builder as models
import notionnd.analytics.stats as stats
import notionnd.datapipe.shuffler as shuffler

mlog = None
hypers = None


def init(logger, hyper_params):
    global mlog, hypers
    mlog = logger
    hypers = hyper_params
    shuffler.init(logger, hyper_params)


def get_run_config(num_session_steps):
    sess_cfg = tf.ConfigProto(allow_soft_placement=True)
    sess_cfg.gpu_options.allow_growth = True
    sess_cfg.intra_op_parallelism_threads = 32
    seed = hypers.get_param('ma')
    if seed == -1:
        seed = None
    cfg = tfc.learn.RunConfig(model_dir=hypers.get_param('sp'),
                              keep_checkpoint_max=10,
                              save_checkpoints_steps=num_session_steps,
                              save_summary_steps=num_session_steps,
                              log_step_count_steps=num_session_steps,
                              tf_random_seed=seed,
                              session_config=sess_cfg)
    return cfg


def train(train_x, train_y, train_l, train_lw, test_x, test_y, test_l, test_lw, n_words):
    if hypers.get_param('ma') != -1:
        np.random.seed(hypers.get_param('ma'))
    num_training_examples = len(train_y)
    num_session_steps = (num_training_examples / hypers.get_param('tb')) * sum(hypers.get_param('tt'))
    steps_per_epoch = num_training_examples / hypers.get_param('tb')
    modelParams = {'n_words': n_words, 'steps_per_session': num_session_steps}
    config = get_run_config(num_session_steps)
    classifier = models.create_model(hypers.get_param('mt'), modelParams, config)
    analyzer = analyzer_init()
    trainidx = 0

    best_result = None
    if hypers.get_param('tr')[trainidx] < (hypers.get_param('ts')[trainidx] * hypers.get_param('tc')[trainidx]):
        hypers.set_param_at('tr', trainidx, hypers.get_param('ts')[trainidx] * hypers.get_param('tc')[trainidx])
    epoch = 0
    shuffled_job = shuffler.shuffle(train_x, train_y, train_l, train_lw)
    predict_dataset = {'train_x': train_x, 'train_y': train_y, 'train_l': train_l, 'train_lw': train_lw,
                       'test_x': test_x, 'test_y': test_y, 'test_l': test_l, 'test_lw': test_lw}
    steps_to_train = steps_per_epoch * hypers.get_param('tc')[trainidx] * hypers.get_param('ts')[trainidx]

    hooks = [tf.train.CheckpointSaverHook(hypers.get_param('sp'), save_steps=1000000)]
    if hypers.get_param('md'):
        hooks.append(tfd.LocalCLIDebugHook())

    while epoch < sum(hypers.get_param('tt')):
        num_reshuffles = int(hypers.get_param('tr')[trainidx] / (hypers.get_param('tc')[trainidx] * hypers.get_param('ts')[trainidx]))
        if num_reshuffles == 0 or hypers.get_param('tr')[trainidx] % num_reshuffles:
            num_reshuffles += 1

        startTime = datetime.now()
        epoch += hypers.get_param('tc')[trainidx] * hypers.get_param('ts')[trainidx] * num_reshuffles
        mlog.usrmsg(0, 1, 'epoch {:<3s} --------------------------------------------'. format(str(epoch)))

        for _ in xrange(num_reshuffles):
            classifier.train(input_fn=train_shuffled_input(shuffled_job), hooks=hooks)

        endTime = datetime.now()
        rate = (steps_to_train * hypers.get_param('tb') * num_reshuffles) / (endTime - startTime).total_seconds()
        analyzer['train_speed'] = rate
        analyzer['epochs_complete'] = epoch

        stop, result = analyze(analyzer, classifier, predict_dataset)
        if best_result is None:
            best_result = result
        elif analyzer['best_stop_value'] == result['stop_value']:
            best_result = result

        if stop or epoch >= sum(hypers.get_param('tt')):
            break

        if epoch == sum(hypers.get_param('tt')[:trainidx + 1]):
            trainidx += 1
            hypers.set_param('ti', trainidx)
        if len(hypers.get_param('tt')) > 1 and trainidx <= len(hypers.get_param('tt')):
            steps_to_train = steps_per_epoch * hypers.get_param('tr')[trainidx]
            shuffled_job = shuffler.shuffle(train_x, train_y, train_l, train_lw)

    return best_result


# Key name to pack the target into dict of `features`. See
# `_get_unique_target_key` for details.
_TARGET_KEY = '__target_key__'


def _get_unique_target_key(features):
    """Returns a key not existed in the input dict `features`.
    Caller of `input_fn` usually provides `features` (dict of numpy arrays) and
    `target`, but the underlying feeding module expects a single dict of numpy
    arrays as input. So, the `target` needs to be packed into the `features`
    temporarily and unpacked after calling the feeding function. Toward this goal,
    this function returns a key not existed in the `features` to pack the
    `target`.
    """
    target_key = _TARGET_KEY
    while target_key in features:
        target_key += '_n'
    return target_key


def train_shuffled_input(shuffle_job):
    data = shuffler.get_round_data(shuffle_job)

    def input_fn():
        x = {'INPUT': data['data']['features'],
             'INPUTLEN': data['data']['lengths'],
             'LBLWEIGHTS': data['data']['lbl_weights']}
        y = data['data']['labels']

        # Make a shadow copy and also ensure the order of iteration is consistent.
        ordered_dict_x = collections.OrderedDict(sorted(x.items(), key=lambda t: t[0]))

        unique_target_key = _get_unique_target_key(ordered_dict_x)
        if y is not None:
            ordered_dict_x[unique_target_key] = y

        queue = feeding_functions._enqueue_data(  # pylint: disable=protected-access
            ordered_dict_x,
            1000,
            shuffle=hypers.get_param('th'),
            num_threads=1,
            enqueue_size=data['batch_size'],
            num_epochs=hypers.get_param('ts')[hypers.get_param('ti')])

        features = queue.dequeue_many(data['batch_size'])
        # Remove the first `Tensor` in `features`, which is the row number.
        if len(features) > 0:
            features.pop(0)

        features = dict(zip(ordered_dict_x.keys(), features))
        if y is not None:
            target = features.pop(unique_target_key)
            return features, target

        return features
    return input_fn


def predict_input(eval_data):
    pred_x = np.append(eval_data['train_x'], eval_data['test_x'], axis=0)
    pred_l = np.append(eval_data['train_l'], eval_data['test_l'], axis=0)
    pred_lw = np.append(eval_data['train_lw'], eval_data['test_lw'], axis=0)
    pred_y = np.append(eval_data['train_y'], eval_data['test_y'])

    input_fn = tf.estimator.inputs.numpy_input_fn(
        x={'INPUT': pred_x, 'INPUTLEN': pred_l, 'LBLWEIGHTS': pred_lw},
        y=pred_y,
        batch_size=hypers.get_param('tb'),
        num_epochs=1,
        shuffle=False)

    return input_fn


def predict(classifier, eval_data):
    result = classifier.predict(input_fn=predict_input(eval_data))
    predicted = [p['class'] for p in result]
    train_predicted = predicted[:eval_data['train_y'].size]
    test_predicted = predicted[eval_data['train_y'].size:]

    return test_predicted, train_predicted


def analyzer_init():
    analyzer_state = {}
    analyzer_state['stop_trigger'] = hypers.get_param('te')
    analyzer_state['stop_threshold'] = hypers.get_param('td')
    analyzer_state['best_stop_value'] = 0.0
    analyzer_state['ok_trigger'] = hypers.get_param('tj')
    analyzer_state['ok_threshold'] = hypers.get_param('ta')
    analyzer_state['best_ok_value'] = 0.0
    analyzer_state['train_speed'] = 0.0
    analyzer_state['loss'] = 0.0
    analyzer_state['epochs_complete'] = 0
    return analyzer_state


def analyze(azstate, classifier, eval_data):
    test_predicted, train_predicted = predict(classifier, eval_data)

    stats_results_rec = stats.get_result_rec()
    stats_results_rec['positive label'] = "bug"
    stats_results_rec['negative label'] = "not_a_bug"
    stats_results_rec['train_actual'] = eval_data['train_y']
    stats_results_rec['train_infer_y'] = train_predicted
    stats_results_rec['test_actual'] = eval_data['test_y']
    stats_results_rec['test_infer_y'] = test_predicted
    stats_rec = stats.show_epoch_stats(stats_results_rec)

    learningRate = classifier.get_variable_value("decayed_lrn_rate")
    loss = classifier.get_variable_value("avg_loss")
    rate = azstate['train_speed']

    best_ok_value = azstate['best_ok_value']
    ok_trigger = azstate['ok_trigger']
    ok_indicator_threshold = azstate['ok_threshold']
    ok_indicator_value = max(stats_rec['tst_for']['meter'], stats_rec['tst_fdr']['meter'])
    stop_value = min(stats_rec['tst_f1']['meter'], stats_rec['tst_acc']['meter'])
    immediate_stop_value = max(stats_rec['tst_f1']['meter'], stats_rec['tst_acc']['meter'])
    best_stop_value = azstate['best_stop_value']
    stop_threshold = azstate['stop_threshold']
    failsafe_indicator = min(stats_rec['trn_tp']['meter'] + stats_rec['trn_fn']['meter'], stats_rec['trn_fp']['meter'] + stats_rec['trn_tn']['meter'])

    stop = False
    if failsafe_indicator < hypers.get_param('tf'):
        mlog.usrmsg(0, 0, "    FAILSAFE CONDITION - FPR INITIATED ABORT")
        stop = True
    elif ok_indicator_value >= hypers.get_param('tg'):
        mlog.usrmsg(0, 0, "    FAILSAFE CONDITION - OK INITIATED ABORT")
        stop = True
    elif stop_value >= hypers.get_param('td') and immediate_stop_value >= azstate['stop_trigger']:
        mlog.usrmsg(0, 0, "      EARLY STOP FIRED - IMMEDIATE STOP INITIATED")
        stop = True
    elif ok_indicator_value <= ok_trigger:
        mlog.usrmsg(0, 0, "    OK INDICATOR FIRED - IMMEDIATE STOP INITIATED")
        stop = True
    elif ok_indicator_value <= ok_indicator_threshold and stop_value >= stop_threshold:
        mlog.usrmsg(0, 0, "       STOP GOAL FOUND - STOP INITIATED")
        best_stop_value = stop_value
        stop = True
    elif ok_indicator_value < ok_indicator_threshold:
        if ok_indicator_value < best_ok_value:
            best_ok_value = ok_indicator_value
        mlog.usrmsg(0, 0, "         OK INDICATOR LOCKED {:0.4f} > {:0.4f}".format(ok_indicator_threshold, ok_indicator_value))
        if stop_threshold < 0.0 and stop_value > hypers.get_param('td'):
            stop_threshold = stop_value
        elif stop_threshold > 0.0 and stop_value > best_stop_value:
            best_stop_value = stop_value
    else:
        mlog.usrmsg(0, 0, "      OK INDICATOR SEARCHING {:0.4f} > {:0.4f}".format(ok_indicator_threshold, ok_indicator_value))

    mlog.usrmsg(0, 0, "                   STOP GOAL {:0.4f} <= {:0.4f}".format(max(stop_threshold, hypers.get_param('td')), best_stop_value))
    mlog.usrmsg(0, 0, "    STEPS/sec: {:5.1f}   LEARNRATE: {:.07f}   LOSS: {:.07f}".format(rate, learningRate, loss))

    azstate['ok_trigger'] += hypers.get_param('tk')
    azstate['best_ok_value'] = best_ok_value
    azstate['stop_threshold'] = stop_threshold
    azstate['best_stop_value'] = best_stop_value
    azstate['loss'] = loss

    stats_results_rec['stop_value'] = stop_value

    return stop, stats_results_rec


def print_elapsed_time(start_time, end_time):
    hours, rem = divmod((end_time - start_time).total_seconds(), 3600)
    minutes, seconds = divmod(rem, 60)
    mlog.usrmsg(0, 1, "Training time: {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))

