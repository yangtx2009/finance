import tensorflow as tf

class MultiHeadAttention(tf.keras.layers.Layer):
    def __init__(self, d_model, num_heads):
        super(MultiHeadAttention, self).__init__()
        self.num_heads = num_heads
        self.d_model = d_model

        assert d_model % self.num_heads == 0

        self.depth = d_model // self.num_heads

        self.wq = tf.keras.layers.Dense(d_model)
        self.wk = tf.keras.layers.Dense(d_model)
        self.wv = tf.keras.layers.Dense(d_model)

        self.dense = tf.keras.layers.Dense(d_model)

    def split_heads(self, x, batch_size):
        """分拆最后一个维度到 (num_heads, depth). 注意d_model必须等于num_heads x depth
        转置结果使得形状为 (batch_size, num_heads, seq_len, depth)
        """
        x = tf.reshape(x, (batch_size, -1, self.num_heads, self.depth))
        return tf.transpose(x, perm=[0, 2, 1, 3])

    def call(self, v, k, q, mask):
        batch_size = tf.shape(q)[0]

        q = self.wq(q)  # (batch_size, seq_len, d_model)
        k = self.wk(k)  # (batch_size, seq_len, d_model)
        v = self.wv(v)  # (batch_size, seq_len, d_model)

        q = self.split_heads(q, batch_size)  # (batch_size, num_heads, seq_len_q, depth)
        k = self.split_heads(k, batch_size)  # (batch_size, num_heads, seq_len_k, depth)
        v = self.split_heads(v, batch_size)  # (batch_size, num_heads, seq_len_v, depth)

        # scaled_attention.shape == (batch_size, num_heads, seq_len_q, depth)
        # attention_weights.shape == (batch_size, num_heads, seq_len_q, seq_len_k)
        scaled_attention, attention_weights = self.scaledDotProductAttention(q, k, v, mask)

        scaled_attention = tf.transpose(scaled_attention, perm=[0, 2, 1, 3])  # (batch_size, seq_len_q, num_heads, depth)
        concat_attention = tf.reshape(scaled_attention, (batch_size, -1, self.d_model))  # (batch_size, seq_len_q, d_model)

        output = self.dense(concat_attention)  # (batch_size, seq_len_q, d_model)

        return output, attention_weights

    def scaledDotProductAttention(self, q, k, v, mask):
        """计算注意力权重。
            self attention的第一步是从每个Encoder的输入向量上创建3个向量 q, k, v
            q, k, v 必须具有匹配的前置维度。
            k, v 必须有匹配的倒数第二个维度，例如：seq_len_k = seq_len_v。
            虽然 mask 根据其类型（填充或前瞻）有不同的形状，
            但是 mask 必须能进行广播转换以便求和。

            1. q代表当前单词, k表示句中其他单词。q和k的点乘+scale+mask+softmax生成权重分数(score),
                表示当前单词在句子中与其他单词位置的相关程度
            2. 这个score实际是一个seq_len_q x seq_len_k 的注意力矩阵， 第i行表示字i与其他字的相关性
            3. q和k都理论上是标准分布，方差为1，点积把方差放大了sqrt(d_k)倍，所以为了不让梯度爆炸，还要把点积结果缩放回去
            4. v表示从当前字抽取出的信息
            5. score点乘v，旨在保留对当前词关注度不变的情况下，降低对不相关词的关注
            6. 一个self-attention block输入输出的矩阵大小是一样的，所以可以重复多次
            7. Encoder最后一个block的输出的K，V被带到Decoder的self-attention block中
            2. Encoder输出m,则Encoder-Decoder-Attention block只通过m得到K,V, 而Q来源于output(shifted right)的attention结果

            参数:
                q: 请求的形状 == (..., seq_len_q, depth)
                k: 主键的形状 == (..., seq_len_k, depth)
                v: 数值的形状 == (..., seq_len_v, depth_v)
                mask: Float 张量，其形状能转换成
                  (..., seq_len_q, seq_len_k)。默认为None。

            返回值:
                输出，注意力权重
            https://www.youtube.com/watch?v=ugWDIIOHtPA
            https://www.tensorflow.org/tutorials/text/transformer

        """
        matmul_qk = tf.matmul(q, k, transpose_b=True)  # (..., seq_len_q, seq_len_k)

        # 缩放 matmul_qk
        dk = tf.cast(tf.shape(k)[-1], tf.float32)
        scaled_attention_logits = matmul_qk / tf.math.sqrt(dk)

        # 将 mask 加入到缩放的张量上。
        if mask is not None:
            scaled_attention_logits += (mask * -1e9)

            # softmax 在最后一个轴（seq_len_k）上归一化，因此分数
        # 相加等于1。
        attention_weights = tf.nn.softmax(scaled_attention_logits, axis=-1)  # (..., seq_len_q, seq_len_k)
        output = tf.matmul(attention_weights, v)  # (..., seq_len_q, depth_v)

        return output, attention_weights