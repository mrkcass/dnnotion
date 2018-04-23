def init_hparams(hyper_dict):
    hyper_dict['wv'] = {
        'description': "directory containing pre-trained word vectors tensorflow checkpoint",
        'default': "",
        'value': "../../data/current3/wordvectors_400"}
    hyper_dict['ws'] = {
        'description': "word vector size",
        'default': [80, 140, 190],
        'value': 400}
    hyper_dict['wn'] = {
        'description': "normalize word vector layer",
        'default': False,
        'value': True}
    hyper_dict['wa'] = {
        'description': "word vector normalize layer activation function (relu, tanh, sigmoid, elu, linear)",
        'default': 'linear',
        'value': 'linear'}
    hyper_dict['wd'] = {
        'description': "word vector drop out rate",
        'default': .6,
        'value': 0.0}
    hyper_dict['dc'] = {
        'description': "maximum examples",
        'default': 16000,
        'value': 12000}
    hyper_dict['dn'] = {
        'description': "minimum document length",
        'default': 64,
        'value': 32}
    hyper_dict['dm'] = {
        'description': "dataset minority label oversampling rate",
        'default': 0,
        'value': 0}
    hyper_dict['dx'] = {
        'description': "maximum document length",
        'default': 256,
        'value': 128}
    hyper_dict['do'] = {
        'description': "dataset training/test ordering",
        'default': "train_first test_first (alternate)",
        'value': "alternate"}
    hyper_dict['de'] = {
        'description': "reverse document order",
        'default': False,
        'value': False}
    hyper_dict['tb'] = {
        'description': "batch count - number of training examples in a batch",
        'default': 1024,
        'value': 50}
    hyper_dict['th'] = {
        'description': "batch shuffle",
        'default': [True, False],
        'value': False}
    hyper_dict['tt'] = {
        'description': "epochs to train",
        'default': 10,
        'value': 10}
    hyper_dict['ts'] = {
        'description': "epochs to train before shuffling",
        'default': 10,
        'value': 1}
    hyper_dict['tc'] = {
        'description': "chain epochs together to form a larger training run",
        'default': 10,
        'value': 5}
    hyper_dict['tr'] = {
        'description': "epochs per stats report",
        'default': 1,
        'value': 5}
    hyper_dict['td'] = {
        'description': "minimum value of f1 or acc to stop early",
        'default': .1,
        'value': .6100}
    hyper_dict['te'] = {
        'description': "immediate stop if f1 and acc are greater than 'td' and f1 or acc is greater than value",
        'default': .1,
        'value': .6300}
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
    hyper_dict['lr'] = {
        'description': "learning rate",
        'default': .001,
        'value': .001}
    hyper_dict['ld'] = {
        'description': "learning rate decay rate",
        'default': .96,
        'value': 1.0}
    hyper_dict['le'] = {
        'description': "learning rate during early stop",
        'default': .001,
        'value': .001}
    hyper_dict['cw'] = {
        'description': "convolution 1 (learned filter size uses element 0 only): filter widths",
        'default': [14],
        'value': [2, 3, 4, 5]}
    hyper_dict['cn'] = {
        'description': "convolution 1 (learned filter size uses element 0 only): number of filters per filter width",
        'default': [600],
        'value': [175, 175, 175, 175]}
    hyper_dict['ci'] = {
        'description': "convolution feature map initial value",
        'default': .6,
        'value': 9e-38}
    hyper_dict['fw'] = {
        'description': "fully connected layer width",
        'default': [70, 130],
        'value': 625}
    hyper_dict['fa'] = {
        'description': "fully connected layer activation function (relu, tanh, sigmoid, elu, linear)",
        'default': 'relu',
        'value': 'relu'}
    hyper_dict['fd'] = {
        'description': "connected layer dropout rate",
        'default': .5,
        'value': .25}
    hyper_dict['f1'] = {
        'description': "connected layer l1 regularizer",
        'default': [5],
        'value': .001}
    hyper_dict['f2'] = {
        'description': "connected layer l2 regularizer",
        'default': [5],
        'value': .001}
    hyper_dict['on'] = {
        'description': "number of output classes",
        'default': 2,
        'value': 2}
    hyper_dict['o1'] = {
        'description': "output layer l1 regularizer",
        'default': [5],
        'value': .001}
    hyper_dict['o2'] = {
        'description': "output layer l2 regularizer",
        'default': [5],
        'value': .001}
    hyper_dict['df'] = {
        'description': "minimum word frequency. remove words appearing no more than minumim frequency",
        'default': 3,
        'value': 3}


