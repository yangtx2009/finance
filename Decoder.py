import tensorflow as tf
from DecoderLayer import DecoderLayer
from PositionalEncoding import PositionalEncoding

class Decoder(tf.keras.layers.Layer):
    def __init__(self, num_layers, output_seq_len, d_model, num_heads, dff, target_feature_size,
                 maximum_position_encoding, rate=0.1):
        super(Decoder, self).__init__()
        print("Decoder:\nd_model:{}, num_layers:{}, num_heads:{}, dff:{}, "
              "target_feature_size:{}, maximum_position_encoding:{}"
              .format(d_model, num_layers, num_heads, dff, target_feature_size, maximum_position_encoding))
        self.d_model = d_model
        self.num_layers = num_layers
        self.target_feature_size = target_feature_size
        self.output_seq_len = output_seq_len

        # self.embedding = tf.keras.layers.Embedding(target_feature_size, d_model)
        self.embedding = tf.keras.layers.Dense(d_model, input_shape=(self.target_feature_size,))
        self.positionEncoder = PositionalEncoding(maximum_position_encoding, self.d_model)
        self.pos_encoding = self.positionEncoder.get_positional_encoding()
        # print("pos_encoding", self.pos_encoding)  # (1,1,d_model)

        self.dec_layers = [DecoderLayer(d_model, num_heads, dff, rate)
                           for _ in range(num_layers)]
        self.dropout = tf.keras.layers.Dropout(rate)

    def call(self, x, enc_output, training,
             look_ahead_mask, padding_mask):
        # (batch_size,target_seq_len,d_model)
        attention_weights = {}
        seq_len = tf.shape(x)[1]

        x = tf.reshape(x, shape=[-1, self.target_feature_size])
        x = self.embedding(x)  # (batch_size, input_seq_len, d_model)
        x = tf.reshape(x, shape=[-1, seq_len, self.d_model])

        # print("embedding", x)
        x *= tf.math.sqrt(tf.cast(self.d_model, tf.float32))
        x += self.pos_encoding[:, :self.output_seq_len, :]

        x = self.dropout(x, training=training)

        for i in range(self.num_layers):
            x, block1, block2 = self.dec_layers[i](x, enc_output, training,
                                                   look_ahead_mask, padding_mask)

            attention_weights['decoder_layer{}_block1'.format(i + 1)] = block1
            attention_weights['decoder_layer{}_block2'.format(i + 1)] = block2

        # x.shape == (batch_size, target_seq_len, d_model)
        return x, attention_weights