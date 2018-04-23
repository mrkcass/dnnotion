
from sklearn import metrics


classStats = []
epochStats = []


def summarize(result, train_x, test_x, dataset_meta):
    train_y = result['train_actual']
    train_predicted = result['train_infer_y']
    test_y = result['test_actual']
    test_predicted = result['test_infer_y']
    # show_class_stats('train', train_predicted, dataset_meta['label_id_dict'], train_y, True, True)
    # show_class_stats('test', test_predicted, dataset_meta['label_id_dict'], test_y, True, True, True)
    save_result(train_y, train_predicted, test_y, test_predicted, dataset_meta)
    save_vocab_stats(train_x, train_y, train_predicted, test_x, test_y, test_predicted, dataset_meta)
    mlog.usrmsg(3, 0, ' ')


def show_epoch_stats(result):
    stats_rec = get_stat_rec()
    compute_set_stats("trn", result['train_actual'], result['train_infer_y'], result['train_infer_prob_y'], stats_rec)
    compute_set_stats("tst", result['test_actual'], result['test_infer_y'], result['test_infer_prob_y'], stats_rec)
    display_train = print_stats(stats_rec, "trn")
    display_test = print_stats(stats_rec, "tst")
    mlog.usrmsg(0, 0, "  {:<32}|  {}".format("TRAINING", "TEST"))
    for row in xrange(len(display_train)):
        mlog.usrmsg(0, 0, "  {:<32}|  {}".format(display_train[row], display_test[row]))
    return stats_rec


def print_stats(stats_rec, dset):
    dset += "_"
    display_rec = ["" for x in range(9)]
    display_rec[0] = "  CONFUSION: {:<6}    {:<6}".format(stats_rec[dset + 'tp']['meter'], stats_rec[dset + 'fp']['meter'])
    display_rec[1] = "     MATRIX: {:<6}    {:<6}".format(stats_rec[dset + 'fn']['meter'], stats_rec[dset + 'tn']['meter'])
    display_rec[2] = " TPR /  FPR: {:0.4f} / {:0.4f}".format(stats_rec[dset + 'tpr']['meter'], stats_rec[dset + 'fpr']['meter'])
    display_rec[3] = " TNR /  FNR: {:0.4f} / {:0.4f}".format(stats_rec[dset + 'tnr']['meter'], stats_rec[dset + 'fnr']['meter'])
    display_rec[4] = " PPV /  NPV: {:0.4f} / {:0.4f}".format(stats_rec[dset + 'ppv']['meter'], stats_rec[dset + 'npv']['meter'])
    display_rec[5] = " FOR /  FDR: {:0.4f} / {:0.4f}".format(stats_rec[dset + 'for']['meter'], stats_rec[dset + 'fdr']['meter'])
    display_rec[6] = "SPEC / SENS: {:0.4f} / {:0.4f}".format(stats_rec[dset + 'tnr']['meter'], stats_rec[dset + 'tpr']['meter'])
    display_rec[7] = "PREC / RECA: {:0.4f} / {:0.4f}".format(stats_rec[dset + 'ppv']['meter'], stats_rec[dset + 'tpr']['meter'])
    display_rec[8] = "  F1 /  ACC: {:0.4f} / {:0.4f}".format(stats_rec[dset + 'f1']['meter'], stats_rec[dset + 'acc']['meter'])
    return display_rec


def compute_set_stats(setprefix, expected, predicted, probabilities, stat_rec):
    pre = setprefix + '_'
    conmat = metrics.confusion_matrix(expected, predicted)
    acc = metrics.accuracy_score(expected, predicted)
    stat_rec[pre + 'acc']['meter'] = acc
    stat_rec[pre + 'tp']['meter'] = conmat[0][0]
    stat_rec[pre + 'fp']['meter'] = conmat[0][1]
    stat_rec[pre + 'tn']['meter'] = conmat[1][1]
    stat_rec[pre + 'fn']['meter'] = conmat[1][0]
    TP = float(stat_rec[pre + 'tp']['meter'])
    FP = float(stat_rec[pre + 'fp']['meter'])
    TN = float(stat_rec[pre + 'tn']['meter'])
    FN = float(stat_rec[pre + 'fn']['meter'])
    PPV = TPR = 0.0
    if TP != 0.0 or FN != 0.0:
        stat_rec[pre + 'tpr']['meter'] = TPR = TP / (TP + FN)
    if FP != 0.0 or TN != 0.0:
        stat_rec[pre + 'fpr']['meter'] = FPR = FP / (FP + TN)
    if TN != 0.0 or FP != 0.0:
        stat_rec[pre + 'tnr']['meter'] = TNR = TN / (TN + FP)
    if TP != 0.0 or FN != 0.0:
        stat_rec[pre + 'fnr']['meter'] = FNR = FN / (FN + TP)
    if TP != 0.0 or FP != 0.0:
        stat_rec[pre + 'ppv']['meter'] = PPV = TP / (TP + FP)
    if TN != 0.0 or FN != 0.0:
        stat_rec[pre + 'npv']['meter'] = NPV = TN / (TN + FN)
    if TP != 0.0 or FP != 0.0:
        stat_rec[pre + 'fdr']['meter'] = FDR = FP / (FP + TP)
    if TN != 0.0 or FN != 0.0:
        stat_rec[pre + 'for']['meter'] = FOR = FN / (FN + TN)
    if TP != 0.0 or FP != 0.0 or TN != 0.0 or FN != 0.0:
        stat_rec[pre + 'acc']['meter'] = (TP + TN) / (TP + FP + TN + FN)
    if PPV != 0.0 or TPR != 0.0:
        stat_rec[pre + 'f1']['meter'] = F1 = 2.0 * ((PPV * TPR) / (PPV + TPR))
    return stat_rec


def get_result_rec():
    rec = {}
    rec['positive label'] = ""
    rec['negative label'] = ""
    rec['train_actual'] = []
    rec['train_infer_y'] = []
    rec['train_infer_prob_y'] = []
    rec['test_actual'] = []
    rec['test_infer_y'] = []
    rec['test_infer_prob_y'] = []
    rec['stop_value'] = 0.0
    return rec


def get_stat_rec():
    # meterid defines the row column and width of a meter
    # ex: ab___
    #   first letter is row ('a' above)
    #   second letter is the row relative meter column ('b' above)
    #
    srec = {}
    get_statrec_fields_misc(srec)
    get_statrec_fields_dset(srec, "trn")
    get_statrec_fields_dset(srec, "tst")
    return srec


def get_statrec_fields_misc(srec):
    srec['current_epoch']  = {'row': "a", 'column': "a", 'meter': 0}
    srec['total_epochs']   = {'row': "a", 'column': "b", 'meter': 0}
    srec['speed_training'] = {'row': "a", 'column': "c", 'meter': 0}
    srec['speed_infer']    = {'row': "a", 'column': "d", 'meter': 0}
    srec['et_hr']          = {'row': "a", 'column': "e", 'meter': 0}
    srec['et_min']         = {'row': "a", 'column': "f", 'meter': 0}
    srec['et_sec']         = {'row': "a", 'column': "g", 'meter': 0}
    srec['eta_hr']         = {'row': "a", 'column': "h", 'meter': 0}
    srec['eta_min']        = {'row': "a", 'column': "i", 'meter': 0}
    srec['eta_sec']        = {'row': "a", 'column': "j", 'meter': 0}
    srec['acc_train']      = {'row': "b", 'column': "a", 'meter': 0}
    srec['acc_train_best'] = {'row': "b", 'column': "b", 'meter': 0}
    srec['acc_test']       = {'row': "b", 'column': "c", 'meter': 0}
    srec['acc_test_best']  = {'row': "b", 'column': "d", 'meter': 0}
    srec['loss']           = {'row': "b", 'column': "e", 'meter': 0}
    srec['loss_avg']       = {'row': "b", 'column': "f", 'meter': 0}
    srec['estop']          = {'row': "c", 'column': "a", 'meter': 0}
    srec['estop_targ']     = {'row': "c", 'column': "b", 'meter': 0}
    return srec


def get_statrec_fields_dset(srec, dset):
    dset += "_"
    srec[dset + 'acc']     = {'row': "a2", 'column': "a", 'meter': 0.0}
    srec[dset + 'pos']     = {'row': "b1", 'column': "a", 'meter': ""}
    srec[dset + 'tp']      = {'row': "b1", 'column': "b", 'meter': 0}
    srec[dset + 'fp']      = {'row': "b1", 'column': "c", 'meter': 0}
    srec[dset + 'neg']     = {'row': "b2", 'column': "a", 'meter': ""}
    srec[dset + 'fn']      = {'row': "b2", 'column': "b", 'meter': 0}
    srec[dset + 'tn']      = {'row': "b2", 'column': "c", 'meter': 0}
    srec[dset + 'tpr']     = {'row': "b3", 'column': "a", 'meter': 0.0}
    srec[dset + 'fpr']     = {'row': "b3", 'column': "b", 'meter': 0.0}
    srec[dset + 'tnr']     = {'row': "b3", 'column': "c", 'meter': 0.0}
    srec[dset + 'fnr']     = {'row': "b3", 'column': "d", 'meter': 0.0}
    srec[dset + 'ppv']     = {'row': "b4", 'column': "a", 'meter': 0.0}
    srec[dset + 'npv']     = {'row': "b4", 'column': "b", 'meter': 0.0}
    srec[dset + 'fdr']     = {'row': "b4", 'column': "c", 'meter': 0.0}
    srec[dset + 'for']     = {'row': "b4", 'column': "d", 'meter': 0.0}
    srec[dset + 'f1']      = {'row': "b5", 'column': "a", 'meter': 0.0}
    srec[dset + 'roc1']    = {'row': "b5", 'column': "b", 'meter': 0.0}
    srec[dset + 'roc2']    = {'row': "b5", 'column': "c", 'meter': 0.0}
    srec[dset + 'roc3']    = {'row': "b5", 'column': "d", 'meter': 0.0}
    srec[dset + 'roc4']    = {'row': "b5", 'column': "e", 'meter': 0.0}
    srec[dset + 'rocauc']  = {'row': "b5", 'column': "f", 'meter': 0.0}
    srec[dset + 'prc1']    = {'row': "b6", 'column': "a", 'meter': 0.0}
    srec[dset + 'prc2']    = {'row': "b6", 'column': "b", 'meter': 0.0}
    srec[dset + 'prc3']    = {'row': "b6", 'column': "c", 'meter': 0.0}
    srec[dset + 'prc4']    = {'row': "b6", 'column': "d", 'meter': 0.0}
    srec[dset + 'prcauc']  = {'row': "b6", 'column': "e", 'meter': 0.0}
    return srec


def init(logger, hyper_params):
    global mlog, hypers
    mlog = logger
    hypers = hyper_params


def save_result(train_expected, train_actual, test_expected, test_actual, dataset_info):
    result = {}

    for idx in xrange(len(train_expected)):
        ex_id = dataset_info['info']['train'][idx]['id']
        exp_label = dataset_info['label_id_dict'][train_expected[idx]]
        act_label = dataset_info['label_id_dict'][train_actual[idx]]
        if ex_id not in result:
            result[ex_id] = []
        if train_expected[idx] == train_actual[idx]:
            result[ex_id].append({'datasubset': 'train', 'result': "pass", 'expected': exp_label, 'actual': act_label})
        else:
            result[ex_id].append({'datasubset': 'train', 'result': "fail", 'expected': exp_label, 'actual': act_label})

    for idx in xrange(len(test_expected)):
        ex_id = dataset_info['info']['test'][idx]['id']
        exp_label = dataset_info['label_id_dict'][test_expected[idx]]
        act_label = dataset_info['label_id_dict'][test_actual[idx]]
        if ex_id not in result:
            result[ex_id] = []
        if test_expected[idx] == test_actual[idx]:
            result[ex_id].append({'datasubset': 'test', 'result': 'pass', 'expected': exp_label, 'actual': act_label})
        else:
            result[ex_id].append({'datasubset': 'test', 'result': "fail", 'expected': exp_label, 'actual': act_label})

    fname = '{}/run.{}.result'.format(mlog.getLogPath(), mlog.getLogId())
    _, rfile = mlog.openFileW(fname)

    for ex_id, ex_result_recs in sorted(result.iteritems()):
        for ex_result_rec in ex_result_recs:
            output = "{0:<25s}    {1:<5s}     {2:<4s}     {3:<20}    {4:}".format(str(ex_id), ex_result_rec['datasubset'], ex_result_rec['result'], ex_result_rec['expected'], ex_result_rec['actual'])
            mlog.writeFileLine(rfile, output)

    mlog.closeFile(rfile)


def save_vocab_stats(train_input, train_labels_expected, train_labels_actual, test_input, test_labels_expected, test_labels_actual, dataset_info):
    label_names = dataset_info['label_id_dict']
    train_set_stats, train_vocab_stats = dataset_vocab_stats(train_input, train_labels_expected, train_labels_actual, label_names)
    test_set_stats, test_vocab_stats = dataset_vocab_stats(test_input, test_labels_expected, test_labels_actual, label_names)
    mlog.usrmsg(1, 0, ' ')
    show_truth_stats('training', label_names, train_set_stats)
    show_truth_stats('test', label_names, test_set_stats)
    mlog.usrmsg(1, 0, ' ')
    show_vocab_stats('train', train_vocab_stats, dataset_info)
    show_vocab_stats('test', test_vocab_stats, dataset_info)


def show_truth_stats(dataset_name, label_names, truth_stats):
    mlog.usrmsg(0, 1, 'dataset truths: {}'.format(dataset_name))
    num_labels = len(label_names)
    for x in xrange(num_labels):
        x_truths = truth_stats['labels'][x]
        row_header = "{:10s}:".format(label_names[x])
        row_data = ""
        for y in xrange(num_labels):
            y_truths = truth_stats['labels'][y]
            if x == y:
                row_data += "  {:4d}".format(x_truths['true_pos'])
            else:
                row_data += "  {:4d}".format(y_truths['false_pos'])
        mlog.usrmsg(0, 2, '{}{}'.format(row_header, row_data))
    mlog.usrmsg(0, 2, '  ')
    for x in xrange(num_labels):
        mlog.usrmsg(0, 2, '{:10s}:'.format(label_names[x]))
        true_pos = truth_stats['labels'][x]['true_pos']
        false_pos = truth_stats['labels'][x]['false_pos']
        false_neg = truth_stats['labels'][x]['false_neg']
        pr = rc = 0.0
        if true_pos + false_pos:
            pr = true_pos / float(true_pos + false_pos)
        if true_pos + false_neg:
            rc = true_pos / float(true_pos + false_neg)
        if pr + rc != 0.0:
            f1 = (2.0 * pr * rc) / (pr + rc)
        else:
            f1 = 0
        mlog.usrmsg(0, 3, 'precision: {:0.4f}'.format(pr))
        mlog.usrmsg(0, 3, 'recall   : {:0.4f}'.format(rc))
        mlog.usrmsg(0, 3, 'f1       : {:0.4f}'.format(f1))
    mlog.usrmsg(0, 2, 'overall:')
    mlog.usrmsg(0, 3, 'micro-precision: {:0.4f}'.format(truth_stats['precision']))


def dataset_vocab_stats(dataset_input, dataset_labels_expected, dataset_labels_actual, label_id_dict):
    set_stats = {'labels': {}, 'precision': 0.0, 'recall': 0.0, 'f1': 0.0}
    vocab_stats = {}

    for label in dataset_labels_expected:
        if label not in set_stats:
            set_stats['labels'][label] = {'true_pos': 0, "false_pos": 0, "true_neg": 0, "false_neg": 0}

    num_tp = 0.0
    num_fp = 0.0
    num_tn = 0.0
    num_fn = 0.0
    for idx in xrange(len(dataset_input)):
        ex = dataset_input[idx]
        ex_label = dataset_labels_expected[idx]
        ac_label = dataset_labels_actual[idx]

        if ex_label == ac_label:
            set_stats['labels'][ex_label]['true_pos'] += 1
            num_tp += 1
            for any_label in label_id_dict:
                if ex_label != any_label:
                    set_stats['labels'][any_label]['true_neg'] += 1
                    num_tn += 1
        else:
            set_stats['labels'][ex_label]['false_neg'] += 1
            set_stats['labels'][ac_label]['false_pos'] += 1
            for any_label in label_id_dict:
                if ex_label != any_label and ac_label != any_label:
                    set_stats['labels'][any_label]['true_neg'] += 1
                    num_tn += 1
            num_fp += 1
            num_fn += 1

        for word in ex:
            if word not in vocab_stats:
                vocab_stats[word] = {'ex_idxs': {}, 'label_counters': {'expected': {}, 'actual': {}}, 'truth_counters': {'true_pos': 0, "false_pos": 0, "true_neg": 0, "false_neg": 0}}
            # track the examples used by this word
            if idx not in vocab_stats[word]['ex_idxs']:
                vocab_stats[word]['ex_idxs'][idx] = 1
            else:
                vocab_stats[word]['ex_idxs'][idx] += 1
            # track the labels using this word
            if ex_label not in vocab_stats[word]['label_counters']['expected']:
                vocab_stats[word]['label_counters']['expected'][ex_label] = 1
            else:
                vocab_stats[word]['label_counters']['expected'][ex_label] += 1
            if ac_label not in vocab_stats[word]['label_counters']['actual']:
                vocab_stats[word]['label_counters']['actual'][ac_label] = 1
            else:
                vocab_stats[word]['label_counters']['actual'][ac_label] += 1
            if ex_label == ac_label:
                vocab_stats[word]['truth_counters']['true_pos'] += 1
                vocab_stats[word]['truth_counters']['false_pos'] += 1
            else:
                vocab_stats[word]['truth_counters']['true_neg'] += 1
                vocab_stats[word]['truth_counters']['false_neg'] += 1

    set_stats['precision'] = num_tp / (num_tp + num_fp)
    set_stats['recall'] = num_tp / (num_tp + num_fn)
    set_stats['f1'] = (2.0 * set_stats['precision'] * set_stats['recall']) / (set_stats['precision'] + set_stats['recall'])

    return set_stats, vocab_stats


def show_vocab_stats(setname, vocab_stats, dataset_info):
    label_word_count = {}

    num_labels = len(dataset_info['label_id_dict'])
    num_examples = len(dataset_info['info'][setname])

    # how many examples have exclusive words
    label_word_count = {}
    label_word_count['common'] = {}
    # now many exclusive words are in more than 0-5%, 6-10, 11-15..95-100% of examples
    for word, word_rec in vocab_stats.iteritems():
        if len(word_rec['label_counters']['actual']) == 1:
            label = next(iter(word_rec['label_counters']['actual']))
            if label not in label_word_count:
                label_word_count[label] = {}
            label_word_count[label][word] = len(word_rec['ex_idxs'])
        else:
            label_word_count['common'][word] = len(word_rec['ex_idxs'])

    mlog.usrmsg(0, 1, 'vocab stats for set: {}'.format(setname))
    mlog.usrmsg(0, 2, '{:10s} words: {}'.format('total', len(vocab_stats)))
    mlog.usrmsg(0, 2, '{:10s} words: {}'.format('common', len(label_word_count['common'])))
    for label, word_dict in label_word_count.iteritems():
        if label is not "common":
            label_text = dataset_info['label_id_dict'][int(label)]
            mlog.usrmsg(0, 2, '{:10s} words: {}'.format(label_text, len(word_dict)))

