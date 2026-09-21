from sklearn import svm
import numpy as np
import itertools
import random

import pickle
with open('encoded_datas.pkl', 'rb') as f:
    datas = pickle.load(f)

# print(datas['DOS_SlowLoris'].shape)

labels = ['attack_bot', 'attack_DDOS',\
        'attack_portscan', 'DOS_SlowHttpTest',\
        'DOS_SlowLoris', 'DOS_Hulk', 'DOS_GoldenEye', 'FTPPatator',\
        'SSHPatator', 'Web_BruteForce', 'Web_XSS']

import logging 

logging.basicConfig(level=logging.DEBUG, format='%(message)s', datefmt='%m-%d %H:%M', filename='svm.log', filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# clf = svm.OneClassSVM(nu=0.01, kernel='rbf', gamma='auto')

# train_labels = 

# train_label = 'DOS_SlowLoris'
# test_label = 'attack_portscan'
# print(datas[train_label].shape)

# clf.fit(datas[train_label])

# predicts = clf.predict(datas[test_label])
# c=0
# print(predicts)
# for i in predicts:
#         if i == -1:
#                 c += 1
# print(c)
# print(len(predicts))


def train_svms(train_labels):
    svms = []
    for i, train_label in enumerate(train_labels):
        ocsvm = clf = svm.OneClassSVM(nu=0.01, kernel='rbf', gamma='auto')
        ocsvm.fit(datas[train_label])
        svms.append(ocsvm)

    return svms


def validate(svms, test_label):
    samples = datas[test_label]
    
    unknown_count = 0
    for sample in samples:
        classifications = []
        for i, ocsvm in enumerate(svms):
            predicts = ocsvm.predict([sample])
            if predicts[0] == 1:
                classifications.append(i)
        if len(classifications) == 0:
            unknown_count += 1
    
    # print(unknown_count/len(samples))
    return unknown_count/len(samples)

def get_unknown_label(train_set):
    index = random.randint(0, len(labels)-1)
    while labels[index] in train_set:
        index = random.randint(0, len(labels)-1)

    return labels[index]


test_sets = list(itertools.combinations(labels, 4))
random.Random(52).shuffle(test_sets)

for train_data in test_sets:
    test_datas = []
    for i in range(8):
        unknown_label = get_unknown_label(train_data)
        svms = train_svms(train_data)
        acc = validate(svms, unknown_label)
        print(train_data, unknown_label, acc)
