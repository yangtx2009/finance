import tensorflow as tf
import numpy as np

class PositionalEncoding(object):
    """
        In https://rubikscode.net/2019/08/05/transformer-with-python-and-tensorflow-2-0-attention-layers/,
        he uses [sin(w*0), sin(w*1), ..., cos(w*0), cos(w*1), ...]
        but in tensorflow tutorial https://www.tensorflow.org/tutorials/text/transformer
        the vector is [sin(w*0), cos(w*0), sin(w*1), cos(w*1), ...]

        The both are equivalent but we choose the second one, because the original paper proposes in this way
    """
    def __init__(self, position, d):
        angle_rads = self._get_angles(np.arange(position)[:, np.newaxis],
                                      np.arange(d)[np.newaxis, :], d)
        # print("angle_rads", angle_rads)
        # 0::2 = start from 0, get value at every 2 step (2i)
        angle_rads[:, 0::2] = np.sin(angle_rads[:, 0::2])
        # 1::2 = start from 1, get value at every 2 step (2i+1)
        angle_rads[:, 1::2] = np.cos(angle_rads[:, 1::2])
        self._encoding = angle_rads[np.newaxis,...] # ... = :,:

    def _get_angles(self, position, i, d):
        # print("position", position)
        # print("index", i)
        angle_rates = 1 / np.power(10000, (2 * (i // 2)) / np.float32(d))
        # print("angle_rates", angle_rates)
        return position * angle_rates   # = matmal

    def get_positional_encoding(self):
        return tf.cast(self._encoding, dtype=tf.float32)

if __name__ == '__main__':
    positionalEncoding = PositionalEncoding(8,4)
    print(positionalEncoding.get_positional_encoding())