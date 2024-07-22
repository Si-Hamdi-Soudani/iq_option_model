import pandas as pd
from iqoptionapi.stable_api import IQ_Option
import time

class DataCollector:
    def __init__(self, email, password, asset, timeframe):
        self.email = email
        self.password = password
        self.asset = asset
        self.timeframe = timeframe
        self.api = IQ_Option(email, password)
        self.api.connect()

    def collect_initial_data(self, num_candles):
        self.api.start_candles_stream(self.asset, self.timeframe, 100)
        data = self.api.get_candles(self.asset, self.timeframe, num_candles, time.time())
        self.api.stop_candles_stream(self.asset, self.timeframe)
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['from'], unit='s')
        df.set_index('timestamp', inplace=True)
        return df

    def collect_new_candle(self):
        self.api.start_candles_stream(self.asset, self.timeframe, 1)
        data = self.api.get_candles(self.asset, self.timeframe, 1, time.time())
        self.api.stop_candles_stream(self.asset, self.timeframe)
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['from'], unit='s')
        df.set_index('timestamp', inplace=True)
        return df
