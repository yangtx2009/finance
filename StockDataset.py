import tensorflow_datasets.public_api as tfds

class StockDataset(tfds.core.GeneratorBasedBuilder):
    """
    save stock data in a unified dataset
    """
    VERSION = tfds.core.Version('0.1.0')

    def __init__(self, inputLength=30, targetLength=7):
        super(StockDataset, self).__init__()
        self.inputLength = inputLength
        self.targetLength = targetLength

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
                "input": tfds.features.Tensor(shape=(self.inputLength, 1)),
                "target": tfds.features.Tensor(shape=(self.targetLength, 1))
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
        pass  # TODO

    def _generate_examples(self):
        # 从数据集中产生样本
        yield {
            "input": [],
            "target": []
        }
