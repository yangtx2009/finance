import tensorflow as tf
from EncoderLayer import EncoderLayer
from PositionalEncoding import PositionalEncoding

class Encoder(tf.keras.layers.Layer):
    def __init__(self, num_layers, d_model, num_heads, dff, input_feature_size,
                 maximum_position_encoding, rate=0.1):
        super(Encoder, self).__init__()

        self.d_model = d_model
        self.num_layers = num_layers
        self.input_feature_size = input_feature_size

        # self.embedding = tf.keras.layers.Embedding(input_feature_size, d_model)
        self.embedding = tf.keras.layers.Dense(d_model, input_shape=(input_feature_size,))

        self.positionEncoder = PositionalEncoding(maximum_position_encoding, self.d_model)
        self.pos_encoding = self.positionEncoder.get_positional_encoding()

        self.enc_layers = [EncoderLayer(d_model, num_heads, dff, rate)
                           for _ in range(num_layers)]

        self.dropout = tf.keras.layers.Dropout(rate)

    def call(self, x, training, mask):
        seq_len = tf.shape(x)[1]

        # 将嵌入和位置编码相加。
        # print("encoder input", x.shape)
        x = tf.reshape(x, shape=[-1, self.input_feature_size])
        x = self.embedding(x)  # (batch_size, input_seq_len, d_model)
        x = tf.reshape(x, shape=[-1, seq_len, self.d_model])

        x *= tf.math.sqrt(tf.cast(self.d_model, tf.float32))
        x += self.pos_encoding[:, :seq_len, :]

        x = self.dropout(x, training=training)

        for i in range(self.num_layers):
            x = self.enc_layers[i](x, training, mask)

        return x  # (batch_size, input_seq_len, d_model)