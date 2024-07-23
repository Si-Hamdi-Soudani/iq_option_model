import pandas as pd
import joblib
from datetime import datetime, timedelta
import pytz
import os
import logging

class TradeSignalAnalyzer:
    def __init__(self):
        self.model = None
        self.tz = pytz.timezone('Africa/Tunis')
        self.load_model()

    def load_model(self):
        model_path = 'models/trained_model.pkl'
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
        else:
            raise FileNotFoundError("Trained model not found. Please train the model first.")

    def analyze(self, data):
        if self.model is None:
            raise RuntimeError("Model is not loaded.")
        latest_data = data.tail(1)
        features = latest_data[['SMA20', 'EMA50', 'RSI', 'MACD', 'MACD_Signal', 'Bollinger_High', 'Bollinger_Low']]
        prediction = self.model.predict(features)[0]
        action = 'buy' if prediction else 'sell'
        entry_time = datetime.now(self.tz).replace(second=0, microsecond=0) + timedelta(minutes=1)
        entry_time_str = entry_time.strftime('%Y-%m-%d %I:%M:%S %p')
        timeframe = self.predict_timeframe(data)
        trade_signal = {'action': action, 'entry_time': entry_time_str, 'timeframe': timeframe}
        logging.info(f"Trade Signal: {trade_signal}")
        return trade_signal

    def predict_timeframe(self, data):
        latest_data = data.tail(10)  # Use the latest 10 data points for pattern recognition
        # Implement smarter logic here, leveraging historical patterns, technical indicators, and past performance
        if latest_data['RSI'].iloc[-1] < 30 or latest_data['RSI'].iloc[-1] > 70:
            return 5  # Overbought or oversold conditions suggest a longer timeframe
        elif latest_data['MACD'].iloc[-1] > latest_data['MACD_Signal'].iloc[-1]:
            return 3  # Strong bullish trend
        else:
            return 1  # Default to a shorter timeframe
