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

class Transformer(object):
    def __init__(self):
        pass


