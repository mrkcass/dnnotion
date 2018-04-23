# dnnotion ie 2017
# mark r. cass
# based on text_classification_cnn.py tensorflow model.
# modifications from original:
#   input:
#       choose dpedia or provide your own csv file.
#       use a subset of the dataset with selectable starting point and size.
#       selectable training to test ratio.
#   convolution layer 1:
#       multiple filter sizes.
#       number of filters adjustable for each filter size.
#       stride of filters adjustable for each filter size.
#   pooling layer (convolution layer 2):
#       adjustable filter size.`
#       adjustable number of filters.
#   fully connected layer:
#       adjustable width.
#       adjustable drop out normalization.
#       selectable activation function.
#   training:
#       adjustable expotential decay function.
#       adjustable number of training epochs
#       adjustable batch size
#       adjustable batch repeat.
#   misc:
#       logging of all output to a selectable log path.
#       automatically increasing log id appended to log name
#       detailed list of class hits amd misses dumped to log and screen
#       dump test error corpus for a specific class.
#       verbose tensorflow messaging output is turned off so output to screen is cleaner.
#
# todo:
#   * more clean up
#   * command line args
#   * connect to sweeper automation
#   * investigate the usefulness of the 2nd conv layer
#   * generate reports.
#        * summarize hyperparameter vs accuracy (overall and by class)
#   * graphs
#   * tensorboard
#   * model save and reload
#   * inference interactive and from file
#
# reference:
#   Convolutional Neural Networks for Sentence Classification
#     Yoon Kim
#     https://arxiv.org/abs/1408.5882

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from datetime import datetime
import os
from os import path
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import sys
import tensorflow as tf
#os.sys.path.append(os.path.dirname(os.path.abspath('.')))
import notionnd.logging.console_log as clog
import notionnd.datapipe.datasets as datasets
import notionnd.layers.manager as layers
import notionnd.models.builder as models
import notionnd.analytics.stats as stats
import notionnd.hparams.hyper_parameters as hypers
import notionnd.main.trainer as trainer

FLAGS = hypers.init_flags()


def init_subsystem():
    hypers.init_hyperparams(tf.__version__, "cnn_static", FLAGS.flag_values_dict())

    clog.setLogPath(hypers.get_param('lp'), hypers.get_param('li'))

    datasets.init(clog, hypers)
    layers.init(clog, hypers)
    models.init(clog, hypers)
    stats.init(clog, hypers)
    trainer.init(clog, hypers)

    hypers.show_params(clog)


def main(_):
    # tf.logging.set_verbosity(tf.logging.INFO)
    tf.logging.set_verbosity(tf.logging.ERROR)

    # todo accept parameters and map them to hypers.get_param
    init_subsystem()
    if hypers.get_param('st') == 'info':
        quit()

    # Prepare training and testing data
    clog.usrmsg(1, 2, 'loading dataset...')
    train_x, train_y, train_l, train_lw, test_x, test_y, test_l, test_lw, dataset_info = datasets.load()
    train_x, test_x, n_words = datasets.encode(train_x, test_x)

    clog.usrmsg(1, 2, 'training...')
    training_start_time = datetime.now()
    final_result = trainer.train(train_x, train_y, train_l, train_lw, test_x, test_y, test_l, test_lw, n_words)
    training_end_time = datetime.now()
    trainer.print_elapsed_time(training_start_time, training_end_time)
    stats.summarize(final_result, train_x, test_x, dataset_info)

    # if hypers.get_param('sp') != "":
    #    model_saver.save(sess, os.path.join(hypers.get_param('sp'), "model.ckpt"), global_step=classifier.get_variable_value("global_step"))


if __name__ == '__main__':
    tf.app.run()
