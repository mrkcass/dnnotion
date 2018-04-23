import tensorflow as tf

mlog = None
hyper_dict = {}

import notionnd.hparams.cnn_rand as cnn_rand
import notionnd.hparams.cnn_static as cnn_static
import notionnd.hparams.cnn_nonstatic as cnn_nonstatic

import notionnd.hparams.rnn_rand as rnn_rand
import notionnd.hparams.rnn_static as rnn_static
import notionnd.hparams.rnn_nonstatic as rnn_nonstatic


def init_common():
    global hyper_dict

    hyper_dict['ds'] = {
        'description': "data set to load",
        'default': ["dbpedia_small", "dbpedia_large", "rotten", "../data/scrape_570_625_dataset.txt"],
        'value': "../../data/current4/bug_scrape_500000_676000_corpus_peopled_csv_stm.txt"}
    hyper_dict['dn'] = {
        'description': "minimum document length",
        'default': 64,
        'value': 64}
    hyper_dict['dx'] = {
        'description': "maximum document length",
        'default': 256,
        'value': 128}
    hyper_dict['di'] = {
        'description': "minimum example id (with respect to the dataset column 0)",
        'default': 0,
        'value': 600002}
    hyper_dict['db'] = {
        'description': "training labels data balance",
        'default': [.50, .50],
        'value': [.50, .50]}
    hyper_dict['dc'] = {
        'description': "maximum examples in dataset",
        'default': 16000,
        'value': 16000}
    hyper_dict['dl'] = {
        'description': "training label ratio mode",
        'default': "dont_care same_random (same_ordered)",
        'value': "dont_care"}
    hyper_dict['do'] = {
        'description': "dataset training/test ordering",
        'default': "train_first test_first (alternate)",
        'value': "alternate"}
    hyper_dict['dr'] = {
        'description': "test data ratio",
        'default': 1,
        'value': .25}
    hyper_dict['dw'] = {
        'description': "training dataset label weighting",
        'default': [.50, .50],
        'value': [.50, .50]}
    hyper_dict['dv'] = {
        'description': "validation labels data balance",
        'default': [.50, .50],
        'value': [.50, .50]}
    hyper_dict['da'] = {
        'description': "dataset random seed",
        'default': 121212,
        'value': 121212}
    hyper_dict['dm'] = {
        'description': "dataset minority label oversampling rate",
        'default': 0,
        'value': 0}
    hyper_dict['tt'] = {
        'description': "epochs to train",
        'default': 10,
        'value': 100}
    hyper_dict['ts'] = {
        'description': "epochs to train before shuffling",
        'default': 10,
        'value': 2}
    hyper_dict['tc'] = {
        'description': "epochs to combine per round",
        'default': 10,
        'value': 2}
    hyper_dict['ti'] = {
        'description': "training schedule index",
        'default': 0,
        'value': 0}
    hyper_dict['wn'] = {
        'description': "normalize embedding layer",
        'default': False,
        'value': False}
    hyper_dict['tr'] = {
        'description': "epochs per stats report",
        'default': 1,
        'value': 25}
    hyper_dict['lp'] = {
        'description': "run result log path. directory where run result log should be stored",
        'default': 'runlogs',
        'value': 'logs/past'}
    hyper_dict['li'] = {
        'description': "log id for this session",
        'default': '0001',
        'value': '0001'}
    hyper_dict['ls'] = {
        'description': "run status log path. directory where run current status logs are stored",
        'default': 'runstatus',
        'value': 'logs/current'}
    hyper_dict['ma'] = {
        'description': "Model seed. random seed used by model training.",
        'default': 0,
        'value': 123456}
    hyper_dict['sp'] = {
        'description': "save path. directory where model results are stored",
        'default': 'tfresult',
        'value': 'trained'}
    hyper_dict['st'] = {
        'description': "session type: info, train, predict",
        'default': 'info',
        'value': 'train'}
    hyper_dict['sg'] = {
        'description': "session gpu preference",
        'default': 0,
        'value': 0}
    hyper_dict['df'] = {
        'description': "minimum word frequency. remove words appearing no more than minumim frequency",
        'default': 3,
        'value': 3}


def init_rotten_common():
    init_common()

    hyper_dict['ds'] = {
        'description': "data set to load",
        'default': ["dbpedia_small", "dbpedia_large", "rotten", "../data/scrape_570_625_dataset.txt"],
        'value': "../data/rotten/rotten.csv"
    }
    hyper_dict['di'] = {
        'description': "minimum example id (with respect to the dataset column 0)",
        'default': 0,
        'value': 1}
    hyper_dict['dl'] = {
        'description': "label ratio mode",
        'default': "dont_care",
        'value': "same"}
    hyper_dict['dr'] = {
        'description': "test data ratio",
        'default': 1,
        'value': .25}


def init_dbpsmall_common():
    init_common()

    hyper_dict['ds'] = {
        'description': "data set to load",
        'default': ["dbpedia_small", "dbpedia_large", "rotten", "../data/scrape_570_625_dataset.txt"],
        'value': "../data/dbpedia/train_small.csv"
    }
    hyper_dict['di'] = {
        'description': "minimum example id (with respect to the dataset column 0)",
        'default': 0,
        'value': 1}
    hyper_dict['dl'] = {
        'description': "label ratio mode",
        'default': "dont_care",
        'value': "same"}
    hyper_dict['dr'] = {
        'description': "test data ratio",
        'default': 1,
        'value': .25}


def init_flags():
    flags = tf.app.flags
    init_hyperparams("", "all", None)
    for param, value in hyper_dict.iteritems():
        flags.DEFINE_string(param, None, value['description'])
    return flags.FLAGS


def init_hyperparams(tensorflow_version, model_type, flags):
    global hyper_dict

    hyper_dict = {}
    hyper_dict['tv'] = {
        'description': "tensorflow version",
        'default': tensorflow_version,
        'value': tensorflow_version}
    hyper_dict['mt'] = {
        'description': "model type: cnn_rand, cnn_static, cnn_nonstatic, rcnn_rand, rnn_rand",
        'default': model_type,
        'value': model_type}
    hyper_dict['md'] = {
        'description': "enable tfdbg",
        'default': False,
        'value': False}

    if flags is not None:
        if 'mt' in flags and flags['mt'] is not None:
            model_type = flags['mt'].strip('\"')

    if model_type == "cnn_rand" or model_type == "all":
        init_common()
        cnn_rand.init_hparams(hyper_dict)
    if model_type == "cnn_static" or model_type == "all":
        init_common()
        cnn_static.init_hparams(hyper_dict)
    if model_type == "cnn_nonstatic" or model_type == "all":
        init_common()
        cnn_nonstatic.init_hparams(hyper_dict)
    if model_type == "rnn_rand" or model_type == "all":
        init_common()
        rnn_rand.init_hparams(hyper_dict)
    if model_type == "rnn_static" or model_type == "all":
        init_common()
        rnn_static.init_hparams(hyper_dict)
    if model_type == "rnn_nonstatic" or model_type == "all":
        init_common()
        rnn_nonstatic.init_hparams(hyper_dict)

    apply_flags(hyper_dict, flags)

    if model_type == "cnn_rand" and hyper_dict['ds']['value'] == 'dbpedia_small':
        init_dbpsmall_common()
        rnn_rand.init_dbpsmall_hparams(hyper_dict)
        apply_flags(hyper_dict, flags)

    if 'ds' in hyper_dict and hyper_dict['ds']['value'] == 'rotten':
        if model_type == "cnn_rand":
            init_rotten_common()
            cnn_rand.init_rotten_hparams(hyper_dict)
        elif model_type == "rnn_rand":
            init_rotten_common()
            rnn_rand.init_rotten_hparams(hyper_dict)
        dataset_path = hyper_dict['ds']['value']
        apply_flags(hyper_dict, flags)
        hyper_dict['ds']['value'] = dataset_path

    return hyper_dict


def apply_flags(hdict, flags):
    if flags is None:
        return
    for param_name, param_dict_value in hdict.iteritems():
        if param_name in flags and flags[param_name] is not None:
            flag_value = flags[param_name].strip('\"')
            apply_flag(param_dict_value, flag_value)


def apply_flag(param_dict, flag_value):
    if isinstance(param_dict['value'], list):
        flist = flag_value.strip('[] ')
        flist_elems = flist.split(',')
        param_type_sample = param_dict['value'][0]
    else:
        param_type_sample = param_dict['value']
        flist_elems = [flag_value]

    new_value = []
    for idx in xrange(len(flist_elems)):
        if isinstance(param_type_sample, bool):
            new_value.append(bool(flist_elems[idx]))
        elif isinstance(param_type_sample, int):
            new_value.append(int(flist_elems[idx]))
        elif isinstance(param_type_sample, float):
            new_value.append(float(flist_elems[idx]))
        else:
            new_value.append(flist_elems[idx])

    if isinstance(param_dict['value'], list):
        param_dict['value'] = new_value
    else:
        param_dict['value'] = new_value[0]


def get_param(param_name):
    global hyper_dict
    if param_name in hyper_dict:
        return hyper_dict[param_name]['value']
    else:
        return None


def set_param(param_name, value):
    global hyper_dict
    hyper_dict[param_name]['value'] = value


def set_param_at(param_name, index, value):
    global hyper_dict
    hyper_dict[param_name]['value'][index] = value


def show_params(mlog):
    global hyper_dict
    mlog.usrmsg(4, 2, "hyper parameters")
    for param, value in sorted(hyper_dict.iteritems()):
        mlog.usrmsg(0, 4, "param {} : {}".format(param, value['value']))
