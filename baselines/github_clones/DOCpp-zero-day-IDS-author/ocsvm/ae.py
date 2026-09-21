import argparse
import sys

from keras.models import Model
import numpy as np

from model import build_ae_model

import config
flow_size = config.flow_size
pkt_size = config.pkt_size
input_size = flow_size * pkt_size


def parse_args():
    parser = argparse.ArgumentParser(description='Train Convolutional AutoEncoder and inference')
    parser.add_argument('--data_path', default='./data/cifar10.npz', type=str, help='path to dataset')
    parser.add_argument('--height', default=32, type=int, help='height of images')
    parser.add_argument('--width', default=32, type=int, help='width of images')
    parser.add_argument('--channel', default=3, type=int, help='channel of images')
    parser.add_argument('--num_epoch', default=50, type=int, help='the number of epochs')
    parser.add_argument('--batch_size', default=100, type=int, help='mini batch size')
    parser.add_argument('--output_path', default='./data/cifar10_cae.npz', type=str, help='path to directory to output')

    args = parser.parse_args()

    return args

def flat_feature(enc_out):
    """flat feature of CAE features
    """
    enc_out_flat = []

    s1, s2, s3 = enc_out[0].shape
    s = s1 * s2 * s3
    for con in enc_out:
        enc_out_flat.append(con.reshape((s,)))

    return np.array(enc_out_flat)

from data import DataController

def main():
    """main function"""
    args = parse_args()
    data_path = args.data_path
    height = args.height
    width = args.width
    channel = args.channel
    num_epoch = args.num_epoch
    batch_size = args.batch_size
    output_path = args.output_path

    
    # labels = ['vectorize_friday/benign', 'attack_bot', 'attack_DDOS', 'attack_portscan']

    labels = ['attack_bot', 'attack_DDOS',\
            'attack_portscan', 'DOS_SlowHttpTest',\
            'DOS_SlowLoris', 'DOS_Hulk', 'DOS_GoldenEye', 'FTPPatator',\
            'SSHPatator', 'Web_BruteForce', 'Web_XSS']
    dataController = DataController(batch_size=batch_size, data_list=labels)
    autoencoder = build_ae_model(input_size)
    autoencoder.compile(optimizer='adam', loss='binary_crossentropy')

    for i in range(num_epoch):
        dataController.reset()
        while 1:
            # print(i)
            data = dataController.generate('full')
            if data is False:
                break
            x = data["x"]

            autoencoder.fit(x, x,
                    epochs=1,
                    batch_size=batch_size,
                    shuffle=True)

        if i % 5 == 0:
            autoencoder.save('model')
        
    # inference from encoder
    layer_name = 'enc'
    encoded_layer = Model(inputs=autoencoder.input, outputs=autoencoder.get_layer(layer_name).output)
    enc_out = encoded_layer.predict(all_image)

    # # flat features for OC-SVM input
    # enc_out = flat_feature(enc_out)

    # save cae output
    # np.savez(output_path, ae_out=enc_out, labels=all_label)


def get_enc():
    batch_size = args.batch_size
    labels = ['vectorize_friday/benign', 'attack_bot', 'attack_DDOS', 'attack_portscan']

    # labels = ['attack_bot', 'attack_DDOS',\
    #         'attack_portscan', 'DOS_SlowHttpTest',\
    #         'DOS_SlowLoris', 'DOS_Hulk', 'DOS_GoldenEye', 'FTPPatator',\
    #         'SSHPatator', 'Web_BruteForce', 'Web_XSS']
    dataController = DataController(batch_size=batch_size, data_list=labels)
    autoencoder = build_ae_model(input_size)
    autoencoder.compile(optimizer='adam', loss='binary_crossentropy')

    for i in range(num_epoch):
        dataController.reset()
        while 1:
            print(i)
            data = dataController.generate('full')
            if data is False:
                break
            x = data["x"]

            autoencoder.fit(x, x,
                    epochs=1,
                    batch_size=batch_size,
                    shuffle=True)

        if i % 5 == 0:
            autoencoder.save('model')
    

if __name__ == '__main__':
    # main()
    get_enc()
    
