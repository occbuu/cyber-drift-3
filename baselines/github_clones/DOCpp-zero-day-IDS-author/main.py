import socket
import tensorflow as tf
if socket.gethostname() != 'soltani-server':
    assert tf.__version__ == '2.0.0'
    import tensorflow.compat.v1 as tf
    tf.disable_eager_execution()
import config
from data import DataController

from model import Model

import logging 

logging.basicConfig(level=logging.DEBUG, format='%(message)s', datefmt='%m-%d %H:%M', filename='main.log', filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--validation_mode', action='store', type=str, default='DOC')
parser.add_argument('--arch', action='store', type=str, default='CNN')
parser.add_argument('--loss_function', action='store', type=str, default='1-vs-rest')
parser.add_argument('--openmax_treshold', action='store', type=float, default=0.90)

args = parser.parse_args()

validation_mode = args.validation_mode
arch = args.arch
loss_function = args.loss_function

logging.info('---- Running main with arch {}, validation mode {}'.format(arch, validation_mode))

batch_size = config.batch_size
flow_size = config.flow_size
pkt_size = config.pkt_size
input_size = flow_size * pkt_size
n_classes = config.n_classes

def run(model, train_set=[], test_sets=[]):
    dataController = DataController(batch_size=batch_size, data_list=train_set)
    logging.info("Training on: {}".format(train_set))
    model.train(dataController)
    for test_set in test_sets:
        dataController = DataController(batch_size=batch_size, data_list=test_set)
        model.load()
        if validation_mode == 'OpenMax':
            model.calc_mean_and_dist(dataController, 4)
        logging.info("Validate on: {}".format(test_set))
        model.validate(dataController, 4, mode=validation_mode)

all_labels = ['vectorize_friday/benign', 'attack_bot', 'attack_DDOS',\
            'attack_portscan', 'Benign_Wednesday', 'DOS_SlowHttpTest',\
            'DOS_SlowLoris', 'DOS_Hulk', 'DOS_GoldenEye', 'FTPPatator',\
            'SSHPatator', 'Web_BruteForce', 'Web_XSS']

# all_labels = ['vectorize_friday/benign', 'attack_bot', 'attack_DDOS', 'attack_portscan']


import itertools
import random

def get_unknown_label(train_set):
    index = random.randint(0, len(all_labels)-1)
    while all_labels[index] in train_set:
        index = random.randint(0, len(all_labels)-1)

    return all_labels[index]


# test_datas = list(itertools.combinations(all_labels, 3))
# random.Random(52).shuffle(test_datas)

model = Model(input_size, n_classes, batch_size, loss_function, logging)
if arch == 'LSTM':
    model.build_lstm_model()
elif arch == 'CNN':
    model.build_model()
model.build_classification()
model.sess.run(tf.global_variables_initializer())

if loss_function == 'softmax':
    traning_size = n_classes
elif loss_function == '1-vs-rest':
    traning_size = n_classes + 1

train_datas = list(itertools.combinations(all_labels, traning_size))
random.Random(52).shuffle(train_datas)

for train_data in train_datas:
    test_datas = []
    for i in range(8):
        unknown_label = get_unknown_label(train_data)
        test_data = list(train_data[:n_classes]) + [unknown_label]
        if test_data not in test_datas: 
            test_datas.append(test_data)
    run(model, train_data, test_datas)
    model.sess.run(tf.global_variables_initializer())


# dataController = DataController(batch_size=batch_size, data_list=train_data_list)

# model.load('train_phase/')
# clustering_output = run_clustering(model, dataController)
# print(clustering_output)
# model.post_train(dataController)
# model.load()

# clustering_output = run_clustering(model, dataController)
# print(clustering_output)
