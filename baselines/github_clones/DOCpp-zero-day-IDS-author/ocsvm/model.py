from keras.layers import Input, Dense
from keras.models import Model


def build_ae_model(input_size = 20000):
    """
    build convolutional autoencoder model
    """
    input_data = Input(shape=(input_size,))

    # encoder
    net = Dense(5000, activation='relu')(input_data)
    net = Dense(1000, activation='relu')(net)
    encoded = Dense(1000, activation='relu', name='enc')(net)

    net = Dense(1000, activation='relu')(encoded)
    net = Dense(5000, activation='relu')(net)
    decoded = Dense(input_size, activation='sigmoid')(encoded)

    return Model(input_data, decoded)
