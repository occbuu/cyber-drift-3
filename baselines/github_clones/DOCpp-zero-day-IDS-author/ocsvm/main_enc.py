import keras
from keras.models import Model
from sklearn import svm
import numpy as np
batch_size = 20

from data import DataController

def prepare_data(labels):
    datas = {}
    autoencoder = keras.models.load_model('model')

    layer_name = 'enc'
    encoded_layer = Model(inputs=autoencoder.input, outputs=autoencoder.get_layer(layer_name).output)
    
    for label in labels:
        print("Getting encoded data for", label)
        datas[label] = []
        dataController = DataController(batch_size=batch_size, data_list=normal_labels)
        while 1:
            data = dataController.generate('full')
            if data is False:
                break
            x = data["x"]
            enc_out = encoded_layer.predict(x)
            datas[label].extend(enc_out)
        datas[label] = np.array(datas[label])

    
    with open('encoded_datas.pkl', 'wb') as f:
        pickle.dump(datas, f, pickle.HIGHEST_PROTOCOL)

    return datas

# labels = ['vectorize_friday/benign', 'attack_bot', 'attack_DDOS', 'attack_portscan']

labels = ['attack_bot', 'attack_DDOS',\
            'attack_portscan', 'DOS_SlowHttpTest',\
            'DOS_SlowLoris', 'DOS_Hulk', 'DOS_GoldenEye', 'FTPPatator',\
            'SSHPatator', 'Web_BruteForce', 'Web_XSS']

data = prepare_data(labels)

# def save_obj(obj, name):
#     with open('obj/'+ name + '.pkl', 'wb') as f:
#         pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

# def load_obj(name ):
#     with open('obj/' + name + '.pkl', 'rb') as f:
#         return pickle.load(f)