import threading
import time
import os
import pandas as pd
from src.data_collection import DataCollector
from src.feature_engineering import FeatureEngineer
from src.model_training import ModelTrainer
from src.trade_signal_analysis import TradeSignalAnalyzer
from src.utils import check_and_create_files

def main():
    # Initialize configuration
    config = {
        'email': 'dinzaisgod@yopmail.com',
        'password': 'AaBb@1999',
        'asset': 'EURUSD-OTC',
        'timeframe': 1,
        'num_candles': 5000  # Optimal number of candles for startup
    }

    # Check and create necessary files
    check_and_create_files()

    # Initialize components
    collector = DataCollector(config['email'], config['password'], config['asset'], config['timeframe'])
    engineer = FeatureEngineer()
    trainer = ModelTrainer()

    # Step 1: Collect initial data
    initial_data = collector.collect_initial_data(config['num_candles'])
    initial_data = engineer.add_technical_indicators(initial_data)
    initial_data.to_csv('data/historical_data.csv', index=False)

    # Step 2: Train initial model if it doesn't exist
    model_path = 'models/trained_model.pkl'
    if not os.path.exists(model_path):
        X_train, X_test, y_train, y_test = trainer.prepare_data(initial_data)
        trainer.train(X_train, y_train)
        trainer.evaluate(X_test, y_test)

    analyzer = TradeSignalAnalyzer()

    # Step 3: Start real-time data collection and analysis
    def real_time_data_collection():
        while True:
            new_candle = collector.collect_new_candle()
            new_candle = engineer.add_technical_indicators(new_candle)
            with open('data/realtime_data.csv', 'a') as f:
                new_candle.to_csv(f, header=False)
            time.sleep(60)

    def real_time_analysis():
        while True:
            realtime_data = pd.read_csv('data/realtime_data.csv')
            trade_signal = analyzer.analyze(realtime_data)
            if trade_signal:
                print(f"Trade Signal: {trade_signal}")
            time.sleep(60)

    # Start threads for real-time data collection and analysis
    data_thread = threading.Thread(target=real_time_data_collection)
    analysis_thread = threading.Thread(target=real_time_analysis)

    data_thread.start()
    analysis_thread.start()

if __name__ == '__main__':
    main()
