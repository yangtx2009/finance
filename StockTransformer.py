import tensorflow as tf
from tensorflow.keras.layers import Layer, Dense, LayerNormalization, Embedding, Dropout
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.optimizers.schedules import LearningRateSchedule
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import Mean
from tensorflow.keras.losses import MeanSquaredError

from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt

from StockDataset import StockBuilderDataset, StockTFRecordDataset
from Encoder import Encoder
from Decoder import Decoder

class StockTransformer(tf.keras.Model):
    def __init__(self, num_layers, d_model, num_heads, dff, input_feature_size,
                 target_feature_size, pe_input, pe_target, rate=0.1):
        super(StockTransformer, self).__init__()

        self.encoder = Encoder(num_layers, d_model, num_heads, dff,
                               input_feature_size, pe_input, rate)
        self.decoder = Decoder(num_layers, d_model, num_heads, dff,
                               target_feature_size, pe_target, rate)

        self.final_layer = tf.keras.layers.Dense(target_feature_size)

    def call(self, inp, tar, training, enc_padding_mask,
             look_ahead_mask, dec_padding_mask):
        enc_output = self.encoder(inp, training, enc_padding_mask)  # (batch_size, inp_seq_len, d_model)

        # dec_output.shape == (batch_size, tar_seq_len, d_model)
        dec_output, attention_weights = self.decoder(
            tar, enc_output, training, look_ahead_mask, dec_padding_mask)

        final_output = self.final_layer(dec_output)  # (batch_size, tar_seq_len, target_vocab_size)

        return final_output, attention_weights



