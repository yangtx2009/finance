import tensorflow as tf

class MaskHandler(object):
    def padding_mask(self, sequence):
        """
        @param sequence: all zeros are masked by 1, all non-zeros are masked by 0
        @return:
        """
        sequence = tf.cast(tf.math.equal(sequence, 0), tf.float32)
        return sequence[:, tf.newaxis, tf.newaxis, :]

    def look_ahead_mask(self, size):
        """
        前瞻遮挡（look-ahead mask）用于遮挡一个序列中的后续标记（future tokens）。换句话说，该 mask 表明了不应该使用的条目。
        这意味着要预测第三个词，将仅使用第一个和第二个词。与此类似，预测第四个词，仅使用第一个，第二个和第三个词，依此类推。
        因此一般是个类似于上三角矩阵的矩阵
        如:
        array([[0., 1., 1.],
                [0., 0., 1.],
                [0., 0., 0.]], dtype=float32)>
        @param size:
        @return:
        """
        mask = 1 - tf.linalg.band_part(tf.ones((size, size)), -1, 0)
        return mask