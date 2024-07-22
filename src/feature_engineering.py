import pandas as pd
import ta

class FeatureEngineer:
    def __init__(self):
        pass

    def add_technical_indicators(self, df):
        df['SMA20'] = ta.trend.sma_indicator(df['close'], window=20)
        df['EMA50'] = ta.trend.ema_indicator(df['close'], window=50)
        df['RSI'] = ta.momentum.rsi(df['close'], window=14)
        df['MACD'] = ta.trend.macd(df['close'])
        df['MACD_Signal'] = ta.trend.macd_signal(df['close'])
        df['Bollinger_High'] = ta.volatility.bollinger_hband(df['close'])
        df['Bollinger_Low'] = ta.volatility.bollinger_lband(df['close'])
        return df.dropna()
