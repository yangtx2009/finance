import tensorflow as tf

from Analyser.MachineLearning.CustomSchedule import CustomSchedule
from Analyser.MachineLearning.StockTransformer import StockTransformer
from Analyser.MachineLearning.MaskHandler import MaskHandler
from time import time
import datetime
import os
import subprocess

class Trainer:
    def __init__(self):
        self.localDir = os.path.dirname(os.path.realpath(__file__))
        self.num_layers = 4
        self.d_model = 32 #128  # output dim of embedding
        self.dff = 512
        self.num_heads = 8

        self.input_feature_size = 1
        self.target_feature_size = 1
        self.dropout_rate = 0.1
        self.batch_size = 64
        self.max_output_length = 7

        self.epochs = 20

        learning_rate = CustomSchedule(self.d_model)
        self.maskHandler = MaskHandler()
        self.optimizer = tf.keras.optimizers.Adam(learning_rate, beta_1=0.9, beta_2=0.98, epsilon=1e-9)
        self.train_loss = tf.keras.metrics.Mean(name='train_loss')
        self.train_error = tf.keras.losses.MeanSquaredError()   # reduction=tf.keras.losses.Reduction.SUM
        self.test_loss = tf.keras.metrics.Mean(name='test_loss')
        self.test_error = tf.keras.losses.MeanSquaredError()

        self.transformer = StockTransformer(self.num_layers, self.max_output_length, self.d_model, self.num_heads, self.dff,
                                  self.input_feature_size, self.target_feature_size,
                                  pe_input=self.input_feature_size,
                                  pe_target=self.target_feature_size,
                                  rate=self.dropout_rate)

        self.checkpoint_path = os.path.join(self.localDir, "checkpoints", "train")
        ckpt = tf.train.Checkpoint(transformer=self.transformer,
                                   optimizer=self.optimizer)
        self.ckpt_manager = tf.train.CheckpointManager(ckpt, self.checkpoint_path, max_to_keep=5)
        if self.ckpt_manager.latest_checkpoint:
            ckpt.restore(self.ckpt_manager.latest_checkpoint)
            print('Latest checkpoint restored!!')

        current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        root_dir = os.path.join(self.localDir, "logs", current_time)
        train_log_dir = root_dir + '/train'
        test_log_dir = root_dir + '/test'
        self.train_summary_writer = tf.summary.create_file_writer(train_log_dir)
        self.test_summary_writer = tf.summary.create_file_writer(test_log_dir)

        print("Launching tensorboard in logdir", 'tensorboard --logdir', os.path.join(self.localDir, "logs"))
        # cmd = ['tensorboard', '--logdir', root_dir]
        # subprocess.Popen(cmd, stdout=subprocess.STDOUT)

    def parse_example(self, serial_exmp):
        features = {
            # 定义Feature结构，告诉解码器每个Feature的类型是什么
            "input": tf.io.FixedLenFeature([30], tf.float32),
            "target": tf.io.FixedLenFeature([7], tf.float32)
        }
        feats = tf.io.parse_single_example(serial_exmp, features)
        input = feats["input"]
        target = feats["target"]
        return input, target

    def load_data(self):
        train_dataset = tf.data.TFRecordDataset(os.path.join(self.localDir, "data", "train.tfrecords"))
        train_dataset = train_dataset.map(self.parse_example)
        test_dataset = tf.data.TFRecordDataset(os.path.join(self.localDir, "data", "test.tfrecords"))
        test_dataset = test_dataset.map(self.parse_example)

        # self.train_dataset = train_dataset.filter(filter_max_length)
        # 将数据集缓存到内存中以加快读取速度。
        train_dataset = train_dataset.cache()
        train_dataset = train_dataset.shuffle(128).batch(self.batch_size) # .padded_batch(self.batch_size) no need padding
        self.train_dataset = train_dataset.prefetch(tf.data.experimental.AUTOTUNE)

        self.test_dataset = test_dataset.batch(self.batch_size)   #

    def loss_function(self, real, pred):
        """
        There is no padding. No need for masking.
        @param real:
        @param pred:
        @return:
        """
        # mask = tf.math.logical_not(tf.math.equal(real, 0))
        # print("loss_function", real, pred)
        loss_ = self.train_error(real, pred)
        # mask = tf.cast(mask, dtype=loss_.dtype)
        # loss_ *= mask
        return loss_

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
        tf.TensorSpec(shape=(None, None), dtype=tf.float32),
        tf.TensorSpec(shape=(None, None), dtype=tf.float32),
    ]

    @tf.function(input_signature=train_step_signature)
    def train_step(self, inp, tar):
        tar_inp = tar[:, :-1]
        tar_real = tar[:, 1:]

        enc_padding_mask, combined_mask, dec_padding_mask = self.create_masks(inp, tar_inp)

        with tf.GradientTape() as tape:
            predictions, _ = self.transformer(inp, tar_inp, True, enc_padding_mask, combined_mask, dec_padding_mask)
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
                if input.shape[0] != self.batch_size:
                    continue

                self.train_step(input, target)

                if batch % 100 == 0:
                    print('Epoch {}: Batch {}/{} Train Loss {}'.format(
                        epoch + 1, batch, len(list(self.train_dataset)), self.train_loss.result()))

            if (epoch + 1) % 5 == 0:
                ckpt_save_path = self.ckpt_manager.save()
                print('Saving checkpoint for epoch {} at {}'.format(epoch + 1, ckpt_save_path))

            with self.train_summary_writer.as_default():
                tf.summary.scalar('loss', self.train_loss.result(), step=epoch)

            print('Epoch {}: Train Loss {}'.format(epoch + 1, self.train_loss.result()))
            print('Time taken for 1 epoch: {} secs\n'.format(time() - start))

            self.evaluate(epoch)

    def evaluate(self, epoch):
        self.test_loss.reset_states()
        for (batch, (input, target)) in enumerate(self.test_dataset):
            if input.shape[0] != self.batch_size:
                    continue

            # input = tf.expand_dims(input, -1)
            decoder_input = input[:,-1:]            # (batch_size, 1, 1)
            # output = tf.expand_dims(decoder_input, -1)   # (batch_size, 1, 1)
            output = decoder_input

            for i in range(self.max_output_length-1):
                enc_padding_mask, combined_mask, dec_padding_mask = self.create_masks(
                    input, output)
                # predictions.shape == (batch_size, seq_len, feature_size)
                predictions, attention_weights = self.transformer(input, output, False,
                                                                     enc_padding_mask,
                                                                     combined_mask,
                                                                     dec_padding_mask)
                predictions = predictions[:, -1:, 0]
                output = tf.concat([output, predictions], axis=-1)

            loss_ = tf.reduce_mean(self.test_error(output, target))
            self.test_loss(loss_)
            # print(output, target)

            if batch % 100 == 0:
                print('Epoch {}: Batch {}/{} Validation Loss {}'.format(epoch + 1, batch,
                                                                    len(list(self.test_dataset)),
                                                                    self.test_loss.result()))
        # except BaseException:
        #     print("Reached final batch. Continue ...")

        print('Epcoh {}: Validation Loss {}'.format(epoch, self.test_loss.result()))
        with self.test_summary_writer.as_default():
            tf.summary.scalar('loss', self.test_loss.result(), step=epoch)

    def test(self, input):
        pass

if __name__ == '__main__':
    trainer = Trainer()
    trainer.load_data()
    trainer.train()
    # trainer.evaluate(0)