from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow.python.estimator.estimator import Estimator as tfestimator

import notionnd.models.cnn as cnn
import notionnd.models.rnn as rnn

mlog = None
hypers = None


def init(logger, hyper_params):
    global mlog, hypers
    mlog = logger
    hypers = hyper_params
    cnn.init(logger, hyper_params)
    rnn.init(logger, hyper_params)


def create_model(model_type, model_params, config):
    classifier = None
    if model_type == "cnn_rand":
        classifier = tfestimator(model_fn=cnn.rand, params=model_params, config=config)
    elif model_type == "cnn_static":
        classifier = tfestimator(model_fn=cnn.static, params=model_params, config=config)
    elif model_type == "cnn_nonstatic":
        classifier = tfestimator(model_fn=cnn.nonstatic, params=model_params, config=config)
    elif model_type == "rnn_rand":
        classifier = tfestimator(model_fn=rnn.rand, params=model_params, config=config)
    elif model_type == "rnn_static":
        classifier = tfestimator(model_fn=rnn.static, params=model_params, config=config)
    elif model_type == "rnn_nonstatic":
        classifier = tfestimator(model_fn=rnn.nonstatic, params=model_params, config=config)
    else:
        mlog.usrmsg(1, 2, "Error: unknown model {}".format(model_type))

    return classifier
