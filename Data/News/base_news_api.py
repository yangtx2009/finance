import pandas as pd
import pathlib
import requests

class BaseNewsApi:
    def __init__(self):
        self.token = ""
        self.api_keys_df = None
        self._read_api_keys_file()

    def _read_api_keys_file(self):
        local_path = pathlib.Path(__file__)
        parent_path = local_path.parent
        api_key_file = parent_path.joinpath("apikeys.csv")

        assert(api_key_file.exists())
        self.api_keys_df = pd.read_csv(api_key_file)

    def _read_token(self, key):
        return self.api_keys_df.loc[self.api_keys_df['api_name'] == key].token.iloc[0]
    
    def _read_base_url(self, key):
        return self.api_keys_df.loc[self.api_keys_df['api_name'] == key].address.iloc[0]