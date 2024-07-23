import pandas as pd
from datetime import datetime, timedelta
import pytz
from iqoptionapi.stable_api import IQ_Option
import time

class TradeEvaluator:
    def __init__(self, email, password, asset, timeframe):
        self.trades = []
        self.tz = pytz.timezone('Africa/Tunis')
        self.asset = asset
        self.timeframe = timeframe
        self.api = IQ_Option(email, password)
        self.connect()

    def connect(self):
        self.api.connect()
        while not self.api.check_connect():
            print("Failed to connect. Retrying...")
            time.sleep(5)
            self.api.connect()

    def add_trade(self, trade_signal):
        self.trades.append(trade_signal)

    def evaluate_trades(self):
        now = datetime.now(self.tz)
        for trade in self.trades:
            if now >= trade['entry_time'] + timedelta(minutes=trade['timeframe']):
                self.evaluate_trade(trade)
                self.trades.remove(trade)

    def evaluate_trade(self, trade):
        # Capture the actual price at the entry time and the exit time
        entry_time = int(trade['entry_time'].timestamp())
        exit_time = int((trade['entry_time'] + timedelta(minutes=trade['timeframe'])).timestamp())

        # Fetch historical data around the entry and exit time
        self.api.start_candles_stream(self.asset, self.timeframe, 3, entry_time)
        candles = self.api.get_candles(self.asset, self.timeframe, 3, entry_time)
        self.api.stop_candles_stream(self.asset, self.timeframe)

        entry_price = candles[0]['close']  # Assuming the first candle includes the entry time
        exit_price = candles[-1]['close']  # Assuming the last candle includes the exit time

        # Determine if the trade was successful
        if trade['action'] == 'buy' and exit_price > entry_price:
            result = 'win'
        elif trade['action'] == 'sell' and exit_price < entry_price:
            result = 'win'
        else:
            result = 'lose'

        # Log or store the result for further analysis
        trade_result = {
            'entry_time': trade['entry_time'],
            'exit_time': trade['entry_time'] + timedelta(minutes=trade['timeframe']),
            'entry_price': entry_price,
            'exit_price': exit_price,
            'action': trade['action'],
            'result': result
        }

        # Save trade result for training the model
        self.save_trade_result(trade_result)

    def save_trade_result(self, trade_result):
        # Append the trade result to a CSV file for later analysis and model training
        df = pd.DataFrame([trade_result])
        df.to_csv('data/trade_results.csv', mode='a', header=not os.path.exists('data/trade_results.csv'), index=False)
