def init_hparams(hyper_dict):
    hyper_dict['tb'] = {
        'description': "batch count - number of training examples in a batch",
        'default': 1024,
        'value': 70}
    hyper_dict['th'] = {
        'description': "batch shuffle",
        'default': [True, False],
        'value': True}
    hyper_dict['db'] = {
        'description': "dataset label balance",
        'default': [.50, .50],
        'value': [.515, .5]}
    hyper_dict['dc'] = {
        'description': "maximum examples",
        'default': 16000,
        'value': 12000}
    hyper_dict['de'] = {
        'description': "reverse document order",
        'default': False,
        'value': False}
    hyper_dict['dm'] = {
        'description': "dataset minority label oversampling rate",
        'default': 0,
        'value': 0}
    hyper_dict['dn'] = {
        'description': "minimum document length",
        'default': 64,
        'value': 8}
    hyper_dict['do'] = {
        'description': "dataset training/test ordering",
        'default': "train_first test_first (alternate)",
        'value': "alternate"}
    hyper_dict['dw'] = {
        'description': "dataset label weighting",
        'default': [.50, .50],
        'value': [.5, .5]}
    hyper_dict['dx'] = {
        'description': "maximum document length",
        'default': 256,
        'value': 60}
    hyper_dict['fa'] = {
        'description': "fully connected layer activation function (relu, tanh, sigmoid, elu, linear)",
        'default': 'relu',
        'value': 'tanh'}
    hyper_dict['fb'] = {
        'description': "connected layer bias initializer",
        'default': 0.0,
        'value': 0.0}
    hyper_dict['fd'] = {
        'description': "connected layer dropout rate",
        'default': .5,
        'value': 0.0}
    hyper_dict['ff'] = {
        'description': "connected layer weight initializer use scaling factor",
        'default': [1.0, 2.0],
        'value': 1.0}
    hyper_dict['fm'] = {
        'description': "connected layer weight initializer mode",
        'default': ['FAN_IN', "FAN_OUT", 'FAN_AVG'],
        'value': 'FAN_AVG'}
    hyper_dict['fw'] = {
        'description': "fully connected layer width",
        'default': [70, 130],
        'value': 0}
    hyper_dict['fu'] = {
        'description': "connected layer weight initializer use uniform mode",
        'default': False,
        'value': False}
    hyper_dict['ld'] = {
        'description': "learning rate decay rate",
        'default': .96,
        'value': 1.0}
    hyper_dict['le'] = {
        'description': "learning rate during early stop",
        'default': .001,
        'value': .001}
    hyper_dict['lr'] = {
        'description': "learning rate",
        'default': .001,
        'value': .001}
    hyper_dict['ma'] = {
        'description': "Model seed. random seed used by model training. -1 for random.",
        'default': 0,
        'value': -1}
    hyper_dict['oa'] = {
        'description': "fully connected layer activation function (relu, tanh, sigmoid, elu, linear)",
        'default': 'linear',
        'value': 'linear'}
    hyper_dict['ob'] = {
        'description': "output layer bias initializer",
        'default': 0.0,
        'value': 0.0}
    hyper_dict['of'] = {
        'description': "output layer weight initializer scaling factor",
        'default': [1.0, 2.0],
        'value': 1.0}
    hyper_dict['om'] = {
        'description': "output layer weight initializer mode",
        'default': ['FAN_IN', "FAN_OUT", 'FAN_AVG'],
        'value': 'FAN_AVG'}
    hyper_dict['on'] = {
        'description': "number of output classes",
        'default': 2,
        'value': 2}
    hyper_dict['ou'] = {
        'description': "output layer weight initializer use uniform mode",
        'default': False,
        'value': False}
    hyper_dict['o1'] = {
        'description': "output layer l1 regularizer",
        'default': [5],
        'value': 0.0}
    hyper_dict['o2'] = {
        'description': "output layer l2 regularizer",
        'default': [5],
        'value': .1}
    hyper_dict['ra'] = {
        'description': "recurrent layer activation function (relu, tanh, sigmoid, elu, linear)",
        'default': 'tanh',
        'value': 'tanh'}
    hyper_dict['rb'] = {
        'description': "recurrent layer forget bias",
        'default': 1.0,
        'value': 1.0}
    hyper_dict['rc'] = {
        'description': "recurrent layer cell type: lstm (vanilla lstm). clstm (coupled input-forget gate lstm), gru (gated recurrent unit)",
        'default': 'clstm',
        'value': 'gru'}
    hyper_dict['rd'] = {
        'description': "recurrent layer dropout rate",
        'default': 1.0,
        'value': 0.0}
    hyper_dict['ro'] = {
        'description': "recurrent layer output type",
        'default': '(last_output) output states',
        'value': 'output'}
    hyper_dict['rr'] = {
        'description': "recurrent layer output reduction mode",
        'default': 'concat, mean, max',
        'value': 'max'}
    hyper_dict['rt'] = {
        'description': "recurrent layer type. bidirectional or unidirectional",
        'default': '(unidir) bidir',
        'value': 'unidir'}
    hyper_dict['rw'] = {
        'description': "recurrent layer width",
        'default': 9,
        'value': 60}
    hyper_dict['tc'] = {
        'description': "chain epochs together to form a larger training run",
        'default': 10,
        'value': 1}
    hyper_dict['td'] = {
        'description': "minimum value of f1 or acc to stop early",
        'default': .1,
        'value': .6100}
    hyper_dict['te'] = {
        'description': "immediate stop if f1 and acc are greater than 'td' and f1 or acc is greater than value",
        'default': .1,
        'value': .6300}
    hyper_dict['tf'] = {
        'description': "fail safe threshold. trigger when sum of TP/FN or sum of TN/FP is less than threshold",
        'default': 50,
        'value': 300}
    hyper_dict['ta'] = {
        'description': "ok indicator threshold. only early stop if for and fdr are below value",
        'default': .5,
        'value': .5}
    hyper_dict['tj'] = {
        'description': "ok indicator immediate stop",
        'default': .5,
        'value': .393}
    hyper_dict['tk'] = {
        'description': "ok indicator immediate stop relax rate. after 'tr' epochs relax at value per epoch",
        'default': .5,
        'value': .001}
    hyper_dict['tl'] = {
        'description': "loss function",
        'default': ['softmax_cross_entropy', 'sigmoid_cross_entropy', 'mean_squared'],
        'value': 'softmax_cross_entropy'}
    hyper_dict['tm'] = {
        'description': "scale loss to sequence length",
        'default': True,
        'value': True}
    hyper_dict['to'] = {
        'description': "training optimizer",
        'default': ["Adagrad", "Adam", "Ftrl", "RMSProp", "SGD"],
        'value': 'Adam'}
    hyper_dict['tr'] = {
        'description': "epochs per stats report",
        'default': 1,
        'value': 30}
    hyper_dict['ts'] = {
        'description': "epochs to train before shuffling",
        'default': 10,
        'value': 30}
    hyper_dict['tt'] = {
        'description': "epochs to train",
        'default': 10,
        'value': 36}
    hyper_dict['df'] = {
        'description': "minimum word frequency. remove words appearing no more than minumim frequency",
        'default': 3,
        'value': 3}
    hyper_dict['wa'] = {
        'description': "word vector normalize layer activation function (relu, tanh, sigmoid, elu, linear)",
        'default': 'linear',
        'value': 'linear'}
    hyper_dict['wc'] = {
        'description': "normalize word vector layer use centering",
        'default': True,
        'value': True}
    hyper_dict['wd'] = {
        'description': "word vector drop out rate",
        'default': .6,
        'value': 0.0}
    hyper_dict['we'] = {
        'description': "normalize word vector layer epsilon",
        'default': .001,
        'value': .001}
    hyper_dict['wl'] = {
        'description': "normalize word vector layer use scaling",
        'default': True,
        'value': True}
    hyper_dict['wn'] = {
        'description': "normalize word vector layer",
        'default': ['off', 'layer', 'batch'],
        'value': 'layer'}
    hyper_dict['ws'] = {
        'description': "word vector size",
        'default': [80, 140, 190],
        'value': 175}
    hyper_dict['wv'] = {
        'description': "directory containing pre-trained word vectors tensorflow checkpoint",
        'default': "",
        'value': "../../data/current4/wordvectors_175"}
    hyper_dict['wy'] = {
        'description': "normalize word vector layer decay",
        'default': .999,
        'value': .999}