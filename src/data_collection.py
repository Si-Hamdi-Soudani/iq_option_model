import pandas as pd
from iqoptionapi.stable_api import IQ_Option
import time
import logging

class DataCollector:
    def __init__(self, email, password, asset, timeframe):
        self.email = email
        self.password = password
        self.asset = asset
        self.timeframe = timeframe
        self.api = IQ_Option(email, password)
        self.connect()

    def connect(self):
        logging.info("Connecting to IQ Option API...")
        self.api.connect()
        while not self.api.check_connect():
            logging.error("Failed to connect. Retrying...")
            time.sleep(5)
            self.api.connect()

    def reconnect(self):
        self.api.disconnect()
        self.connect()

    def collect_initial_data(self, num_candles):
        try:
            self.api.start_candles_stream(self.asset, self.timeframe, 100)
            data = self.api.get_candles(self.asset, self.timeframe, num_candles, time.time())
            self.api.stop_candles_stream(self.asset, self.timeframe)
        except Exception as e:
            logging.error(f"Error collecting initial data: {e}")
            self.reconnect()
            return self.collect_initial_data(num_candles)

        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['from'], unit='s')
        df.set_index('timestamp', inplace=True)
        return df

    def collect_new_candle(self):
        try:
            now = time.time()
            seconds_to_next_minute = 60 - (now % 60)
            time.sleep(seconds_to_next_minute)
            timestamp = int(time.time())
            self.api.start_candles_stream(self.asset, self.timeframe, 1)
            data = self.api.get_candles(self.asset, self.timeframe, 1, timestamp)
            self.api.stop_candles_stream(self.asset, self.timeframe)
        except Exception as e:
            logging.error(f"Error collecting new candle: {e}")
            self.reconnect()
            return self.collect_new_candle()

        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['from'], unit='s')
        df.set_index('timestamp', inplace=True)
        logging.info(f"New candle collected: {df}")
        return df
