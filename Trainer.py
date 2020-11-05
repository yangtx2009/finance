import tensorflow as tf

from CustomSchedule import CustomSchedule
from StockTransformer import StockTransformer
from MaskHandler import MaskHandler
from time import time

class Trainer:
    def __init__(self):
        self.num_layers = 4
        self.d_model = 128
        self.dff = 512
        self.num_heads = 8

        self.input_feature_size = 1
        self.target_feature_size = 1
        self.dropout_rate = 0.1

        self.batch_size = 64

        self.epochs = 20

        learning_rate = CustomSchedule(self.d_model)
        self.maskHandler = MaskHandler()
        self.optimizer = tf.keras.optimizers.Adam(learning_rate, beta_1=0.9, beta_2=0.98, epsilon=1e-9)
        self.train_loss = tf.keras.metrics.Mean(name='train_loss')

        self.transformer = StockTransformer(self.num_layers, self.d_model, self.num_heads, self.dff,
                                  self.input_feature_size, self.target_feature_size,
                                  pe_input=self.input_feature_size,
                                  pe_target=self.target_feature_size,
                                  rate=self.dropout_rate)

        self.checkpoint_path = "./checkpoints/train"
        ckpt = tf.train.Checkpoint(transformer=self.transformer,
                                   optimizer=self.optimizer)
        self.ckpt_manager = tf.train.CheckpointManager(ckpt, self.checkpoint_path, max_to_keep=5)
        if self.ckpt_manager.latest_checkpoint:
            ckpt.restore(self.ckpt_manager.latest_checkpoint)
            print('Latest checkpoint restored!!')

    def parse_example(self, serial_exmp):
        features = {
            # 定义Feature结构，告诉解码器每个Feature的类型是什么
            "input": tf.io.FixedLenFeature([], tf.float64),
            "target": tf.io.FixedLenFeature([], tf.float64)
        }
        feats = tf.io.parse_single_example(serial_exmp, features)
        input = feats["input"]
        target = feats["target"]
        return input, target

    def load_data(self):
        BUFFER_SIZE = 64

        train_dataset = tf.data.TFRecordDataset("data/train.tfrecords")
        train_dataset = train_dataset.map(self.parse_example)
        test_dataset = tf.data.TFRecordDataset("data/test.tfrecords")
        test_dataset = test_dataset.map(self.parse_example)

        # self.train_dataset = train_dataset.filter(filter_max_length)
        # 将数据集缓存到内存中以加快读取速度。
        train_dataset = train_dataset.cache()
        train_dataset = train_dataset.shuffle(BUFFER_SIZE) # .padded_batch(self.batch_size) no need padding
        self.train_dataset = train_dataset.prefetch(tf.data.experimental.AUTOTUNE)

        self.test_dataset = test_dataset

    def loss_function(self, real, pred):
        """
        There is no padding. No need for masking.
        @param real:
        @param pred:
        @return:
        """
        # mask = tf.math.logical_not(tf.math.equal(real, 0))
        loss_ = tf.keras.losses.MeanSquaredError(real, pred)
        # mask = tf.cast(mask, dtype=loss_.dtype)
        # loss_ *= mask
        return tf.reduce_mean(loss_)

    def create_masks(self, inp, tar):
        # 编码器填充遮挡
        enc_padding_mask = self.maskHandler.padding_mask(inp)

        # 在解码器的第二个注意力模块使用。
        # 该填充遮挡用于遮挡编码器的输出。
        dec_padding_mask = self.maskHandler.padding_mask(inp)

        # 在解码器的第一个注意力模块使用。
        # 用于填充（pad）和遮挡（mask）解码器获取到的输入的后续标记（future tokens）。
        look_ahead_mask = self.maskHandler.look_ahead_mask(tf.shape(tar)[1])
        dec_target_padding_mask = self.maskHandler.padding_mask(tar)
        combined_mask = tf.maximum(dec_target_padding_mask, look_ahead_mask)

        return enc_padding_mask, combined_mask, dec_padding_mask

    train_step_signature = [
        tf.TensorSpec(shape=(None, None), dtype=tf.int64),
        tf.TensorSpec(shape=(None, None), dtype=tf.int64),
    ]

    @tf.function(input_signature=train_step_signature)
    def train_step(self, inp, tar):
        tar_inp = tar[:, :-1]
        tar_real = tar[:, 1:]

        enc_padding_mask, combined_mask, dec_padding_mask = self.create_masks(inp, tar_inp)

        with tf.GradientTape() as tape:
            predictions, _ = self.transformer(inp, tar_inp,
                                         True,
                                         enc_padding_mask,
                                         combined_mask,
                                         dec_padding_mask)
            loss = self.loss_function(tar_real, predictions)

        gradients = tape.gradient(loss, self.transformer.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.transformer.trainable_variables))

        self.train_loss(loss)

    def train(self):
        for epoch in range(self.epochs):
            start = time()

            self.train_loss.reset_states()

            # inp -> portuguese, tar -> english
            for (batch, (input, target)) in enumerate(self.train_dataset):
                self.train_step(input, target)

                if batch % 50 == 0:
                    print('Epoch {} Batch {} Loss {:.4f}'.format(
                        epoch + 1, batch, self.train_loss.result()))

            if (epoch + 1) % 5 == 0:
                ckpt_save_path = self.ckpt_manager.save()
                print('Saving checkpoint for epoch {} at {}'.format(epoch + 1, ckpt_save_path))

            print('Epoch {} Loss {:.4f}'.format(epoch + 1, self.train_loss.result()))

            print('Time taken for 1 epoch: {} secs\n'.format(time() - start))

    # def evaluate(self, inp_sentence):
    #
    #     # 输入语句是葡萄牙语，增加开始和结束标记
    #     inp_sentence = start_token + tokenizer_pt.encode(inp_sentence) + end_token
    #     encoder_input = tf.expand_dims(inp_sentence, 0)
    #
    #     # 因为目标是英语，输入 transformer 的第一个词应该是
    #     # 英语的开始标记。
    #     decoder_input = [tokenizer_en.vocab_size]
    #     output = tf.expand_dims(decoder_input, 0)
    #
    #     for i in range(MAX_LENGTH):
    #         enc_padding_mask, combined_mask, dec_padding_mask = create_masks(
    #             encoder_input, output)
    #
    #         # predictions.shape == (batch_size, seq_len, vocab_size)
    #         predictions, attention_weights = transformer(encoder_input,
    #                                                      output,
    #                                                      False,
    #                                                      enc_padding_mask,
    #                                                      combined_mask,
    #                                                      dec_padding_mask)
    #
    #         # 从 seq_len 维度选择最后一个词
    #         predictions = predictions[:, -1:, :]  # (batch_size, 1, vocab_size)
    #
    #         predicted_id = tf.cast(tf.argmax(predictions, axis=-1), tf.int32)
    #
    #         # 如果 predicted_id 等于结束标记，就返回结果
    #         if predicted_id == tokenizer_en.vocab_size + 1:
    #             return tf.squeeze(output, axis=0), attention_weights
    #
    #         # 连接 predicted_id 与输出，作为解码器的输入传递到解码器。
    #         output = tf.concat([output, predicted_id], axis=-1)
    #
    #     return tf.squeeze(output, axis=0), attention_weights