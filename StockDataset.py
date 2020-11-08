"""
    https://www.tensorflow.org/datasets/add_dataset
    There are three ways to implement a custom dataset
    1. tf.data.Dataset.from_tensor_slices
    2. tf.data.TFRecordDataset
    3. tfds.builder: users need to register the builder in tfds dataset folder
"""
import tensorflow_datasets.public_api as tfds
import tensorflow as tf
import os
import sys
from glob import glob
from googletrans import Translator
import pandas as pd
import numpy as np
import random
from sklearn.preprocessing import MinMaxScaler
import json

# tfds.builder
class StockBuilderDataset(tfds.core.GeneratorBasedBuilder):
    """
    save stock data in a unified dataset
    """
    VERSION = tfds.core.Version('0.1.0')

    def __init__(self, inputLength=30, targetLength=7):
        self.inputLength = inputLength
        self.targetLength = targetLength

        self.trainInputData = None
        self.trainTargetData = None
        self.trainLabel = None
        self.testInputData = None
        self.testTargetData = None
        self.testLabel = None
        self.min = None
        self.max = None

        self.createDataFiles()
        super(StockBuilderDataset, self).__init__()

    def _info(self):
        return tfds.core.DatasetInfo(
            builder=self,
            # 这是将在数据集页面上显示的描述。
            description=("This is the dataset for stock prediction. "
                         "It contains prices of all stocks. "
                         "Train/Test data are 30-days prices of a stock."
                         "Target is the next 7-days prices."),
            # tfds.features.FeatureConnectors
            features=tfds.features.FeaturesDict({
                "input": tfds.features.Tensor(shape=(self.inputLength), dtype=tf.float32),
                "target": tfds.features.Tensor(shape=(self.targetLength), dtype=tf.float32)
            }),
            # 如果特征中有一个通用的（输入，目标）元组，
            # 请在此处指定它们。它们将会在
            # builder.as_dataset 中的
            # as_supervised=True 时被使用。
            supervised_keys=("input", "target"),
            # 数据集的 Bibtex 引用
            citation=r"""@article{StockDataset, author = {Yang, Tianxiang},"}""",
        )

    def _split_generators(self, dl_manager):
        # 下载数据并定义划分
        # dl_manager 是一个 tfds.download.DownloadManager，其能够被用于
        # 下载并提取 URLs
        # 这里我们直接从本地数据加载所有数据并预先进行分类
        return [
            tfds.core.SplitGenerator(
                name=tfds.Split.TRAIN,
                gen_kwargs={
                    "dataset_type": "train"
                },
            ),
            tfds.core.SplitGenerator(
                name=tfds.Split.TEST,
                gen_kwargs={
                    "dataset_type": "test"
                },
            ),
        ]

    def _generate_examples(self, dataset_type):
        # 从数据集中产生样本
        # 对应SplitGenerator中的参数
        if (dataset_type == "train"):
            for i in range(self.trainInputData.shape[0]):
                yield {
                    "input": self.trainInputData[i,:],
                    "target": self.trainTargetData[i,:]
                }
        else:
            for i in range(self.testInputData.shape[0]):
                yield {
                    "input": self.testInputData[i, :],
                    "target": self.testTargetData[i, :]
                }

    def createDataFiles(self):
        """
        @param trainval:
        inputData: [:, inputLength]
        targetData: [:, targetLength]
        label: [:, [industry, name]]
        @return:
        """

        if os.path.exists("data/TrainInputData.npy"):
            self.trainInputData = np.load("data/TrainInputData.npy")
            self.trainTargetData = np.load("data/TrainTargetData.npy")
            self.trainLabel = pd.read_csv('data/TrainLabel.csv')

            self.testInputData = np.load("data/TestInputData.npy")
            self.testTargetData = np.load("data/TestTargetData.npy")
            self.testLabel = pd.read_csv('data/TestLabel.csv')
        else:
            # translator = Translator()
            inputData = None
            targetData = None
            label = pd.DataFrame(columns=["industry", "stock"])

            for industryName in tf.io.gfile.listdir("industries"):
                chineseName = os.path.splitext(industryName)[0]
                # print("chineseName", chineseName)
                # engName = translator.translate(chineseName).text
                # print("englishName", engName, type(engName))

                localData = pd.read_csv(os.path.join("industries", industryName))
                localData.set_index("times", inplace=True)

                stockNames = localData.columns.to_list()
                # stockNames.remove("times")
                print("column number", localData.shape[1])
                print("stock names", stockNames)

                for stockName in stockNames:
                    # process data
                    stockData = localData[stockName].to_numpy(dtype=float)
                    stockData[np.isnan(stockData)] = 0

                    currentStart = 0
                    while (currentStart <= (stockData.size - self.inputLength - self.targetLength)):
                        if np.count_nonzero(stockData[currentStart:currentStart + 30]) == 0:
                            currentStart += 30
                            continue

                        if inputData is None:
                            inputData = np.expand_dims(stockData[currentStart:currentStart + 30], axis=0)
                            targetData = np.expand_dims(stockData[currentStart+30:currentStart+37], axis=0)
                        else:
                            inputData = np.concatenate([inputData,
                                                             np.expand_dims(stockData[currentStart:currentStart + 30],
                                                                            axis=0)], axis=0)
                            targetData = np.concatenate([targetData,
                                                             np.expand_dims(stockData[currentStart + 30:currentStart + 37],
                                                                            axis=0)], axis=0)
                        currentStart += 30
                        label = label.append({"industry": chineseName, "stock": stockName}, ignore_index=True)

                    break

            # normalize data
            if not os.path.exists("data/info.json"):
                self.normalize(inputData, True)
            else:
                self.normalize(inputData)
            self.normalize(targetData)

            # split train/test
            indices = [i for i in range(inputData.shape[0])]
            random.shuffle(indices)
            trainIndices = indices[:int(len(indices)*0.8)]
            testIndices = indices[int(len(indices)*0.8):]

            self.trainInputData = inputData[trainIndices, :]
            self.trainTargetData = targetData[trainIndices, :]
            self.trainLabel = label.iloc[trainIndices,:]

            self.testInputData = inputData[testIndices, :]
            self.testTargetData = targetData[testIndices, :]
            self.testLabel = label.iloc[testIndices,:]

            print(self.trainLabel)
            np.save("data/TrainInputData.npy", self.trainInputData)
            np.save("data/TrainTargetData.npy", self.trainTargetData)
            self.trainLabel.to_csv('data/TrainLabel.csv')

            np.save("data/TestInputData.npy", self.testInputData)
            np.save("data/TestTargetData.npy", self.testTargetData)
            self.testLabel.to_csv('data/TestLabel.csv')

    def normalize(self, data, update=True):
        if update:
            self.max = np.max(data)
            self.min = np.min(data)

            json_data = {}
            json_data['min'] = self.min
            json_data['max'] = self.max
            with open("data/info.json", 'w') as outfile:
                json.dump(json_data, outfile)
        elif self.min is None or self.max is None:
            if os.path.exists("data/info.json"):
                with open("data/info.json", 'r') as outfile:
                    json_data = json.load(outfile)
                    self.min = json_data['min']
                    self.max = json_data['max']
            else:
                raise Warning("Cannot find info.json")

        if self.max - self.min == 0:
            raise Warning("max = min!")

        return (data - self.min) / (self.max - self.min)

    def scale(self, data):
        if self.min is None or self.max is None:
            with open("data/info.json", 'r') as outfile:
                data = json.load(outfile)
                self.min = data['min']
                self.max = data['max']

        return data * (self.max - self.min) + self.min

class StockTFRecordDataset(object):
    def __init__(self, inputLength=30, targetLength=7):
        self.inputLength = inputLength
        self.targetLength = targetLength

        self.trainInputData = None
        self.trainTargetData = None
        self.trainLabel = None
        self.testInputData = None
        self.testTargetData = None
        self.testLabel = None
        self.min = None
        self.max = None

        self.createDataFiles()
        self.createTFRecord()

    def createTFRecord(self):
        if not os.path.exists("data/train.tfrecords"):
            with tf.io.TFRecordWriter("data/train.tfrecords") as writer:
                for i in range(self.trainInputData.shape[0]):
                    feature = {
                        "input": tf.train.Feature(
                            float_list=tf.train.FloatList(value=self.trainInputData[i, :].tolist())),
                        "target": tf.train.Feature(
                            float_list=tf.train.FloatList(value=self.trainTargetData[i, :].tolist()))
                    }
                    example = tf.train.Example(features=tf.train.Features(feature=feature))
                    writer.write(example.SerializeToString())

            with tf.io.TFRecordWriter("data/test.tfrecords") as writer:
                for i in range(self.testInputData.shape[0]):
                    feature = {
                        "input": tf.train.Feature(
                            float_list=tf.train.FloatList(value=self.testInputData[i, :].tolist())),
                        "target": tf.train.Feature(
                            float_list=tf.train.FloatList(value=self.testTargetData[i, :].tolist()))
                    }
                    example = tf.train.Example(features=tf.train.Features(feature=feature))
                    writer.write(example.SerializeToString())

    def createDataFiles(self):
        """
        @param trainval:
        inputData: [:, inputLength]
        targetData: [:, targetLength]
        label: [:, [industry, name]]
        @return:
        """

        if os.path.exists("data/TrainInputData.npy"):
            self.trainInputData = np.load("data/TrainInputData.npy")
            self.trainTargetData = np.load("data/TrainTargetData.npy")
            self.trainLabel = pd.read_csv('data/TrainLabel.csv')

            self.testInputData = np.load("data/TestInputData.npy")
            self.testTargetData = np.load("data/TestTargetData.npy")
            self.testLabel = pd.read_csv('data/TestLabel.csv')
        else:
            # translator = Translator()
            inputData = None
            targetData = None
            label = pd.DataFrame(columns=["industry", "stock"])

            for industryName in tf.io.gfile.listdir("industries"):
                chineseName = os.path.splitext(industryName)[0]
                # print("chineseName", chineseName)
                # engName = translator.translate(chineseName).text
                # print("englishName", engName, type(engName))

                localData = pd.read_csv(os.path.join("industries", industryName))
                localData.set_index("times", inplace=True)

                stockNames = localData.columns.to_list()
                # stockNames.remove("times")
                print("column number", localData.shape[1])
                print("stock names", stockNames)

                for stockName in stockNames:
                    # process data
                    stockData = localData[stockName].to_numpy(dtype=float)
                    stockData[np.isnan(stockData)] = 0

                    currentStart = 0
                    while (currentStart <= (stockData.size - self.inputLength - self.targetLength)):
                        if np.count_nonzero(stockData[currentStart:currentStart + 30]) == 0:
                            currentStart += 30
                            continue

                        if inputData is None:
                            # input: 30 days
                            inputData = np.expand_dims(stockData[currentStart:currentStart+self.inputLength], axis=0)
                            # target: 37-1 days
                            targetData = np.expand_dims(stockData[currentStart+self.inputLength-1:
                                                        currentStart+self.inputLength+self.targetLength-1], axis=0)
                                                        # start from the last of input sequence!
                        else:
                            inputData = np.concatenate([inputData,
                                                        np.expand_dims(stockData[currentStart:currentStart
                                                                      +self.inputLength], axis=0)], axis=0)
                            targetData = np.concatenate([targetData,
                                                         np.expand_dims(stockData[currentStart+self.inputLength-1:
                                                         currentStart+self.inputLength+self.targetLength-1],
                                                            axis=0)], axis=0)
                        currentStart += 30
                        label = label.append({"industry": chineseName, "stock": stockName}, ignore_index=True)

            # normalize data
            if not os.path.exists("data/info.json"):
                inputData = self.normalize(inputData, True)
            else:
                inputData = self.normalize(inputData)
            targetData = self.normalize(targetData)


            # split train/test
            indices = [i for i in range(inputData.shape[0])]
            random.shuffle(indices)
            trainIndices = indices[:int(len(indices)*0.9)]
            testIndices = indices[int(len(indices)*0.9):]

            self.trainInputData = inputData[trainIndices, :]
            self.trainTargetData = targetData[trainIndices, :]
            self.trainLabel = label.iloc[trainIndices,:]

            self.testInputData = inputData[testIndices, :]
            self.testTargetData = targetData[testIndices, :]
            self.testLabel = label.iloc[testIndices,:]

            print(self.trainLabel)
            np.save("data/TrainInputData.npy", self.trainInputData)
            np.save("data/TrainTargetData.npy", self.trainTargetData)
            self.trainLabel.to_csv('data/TrainLabel.csv')

            np.save("data/TestInputData.npy", self.testInputData)
            np.save("data/TestTargetData.npy", self.testTargetData)
            self.testLabel.to_csv('data/TestLabel.csv')

    def normalize(self, data, update=True):
        if update:
            self.max = np.max(data)
            self.min = np.min(data)

            json_data = {}
            json_data['min'] = self.min
            json_data['max'] = self.max
            with open("data/info.json", 'w') as outfile:
                json.dump(json_data, outfile)
        elif self.min is None or self.max is None:
            if os.path.exists("data/info.json"):
                with open("data/info.json", 'r') as outfile:
                    json_data = json.load(outfile)
                    self.min = json_data['min']
                    self.max = json_data['max']
            else:
                raise Warning("Cannot find info.json")

        if self.max - self.min == 0:
            raise Warning("max = min!")

        return (data - self.min) / (self.max - self.min)

    def scale(self, data):
        if self.min is None or self.max is None:
            with open("data/info.json", 'r') as outfile:
                data = json.load(outfile)
                self.min = data['min']
                self.max = data['max']

        return data * (self.max - self.min) + self.min

if __name__ == '__main__':
    # stockDataset = StockBuilderDataset()
    stockDataset = StockTFRecordDataset()