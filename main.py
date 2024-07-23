import threading
import time
import os
import pandas as pd
import logging
from src.data_collection import DataCollector
from src.feature_engineering import FeatureEngineer
from src.model_training import ModelTrainer
from src.trade_signal_analysis import TradeSignalAnalyzer
from src.trade_evaluation import TradeEvaluator
from src.utils import check_and_create_files

logging.basicConfig(level=logging.INFO)


def main():
    # Initialize configuration
    config = {
        'email': 'hamdizeby1999@gmail.com',
        'password': 'AaBb@1999',
        'asset': 'EURUSD-OTC',
        'timeframe': 1,
        'num_candles': 100000  # Increase number of candles for startup
    }

    # Check and create necessary files
    check_and_create_files()

    # Initialize components
    collector = DataCollector(config['email'], config['password'],
                              config['asset'], config['timeframe'])
    engineer = FeatureEngineer()
    trainer = ModelTrainer()
    evaluator = TradeEvaluator(config['email'], config['password'],
                               config['asset'], config['timeframe'])

    # Step 1: Check if the dataset file has actual data points
    dataset_path = 'data/historical_data.csv'
    try:
        initial_data = pd.read_csv(dataset_path)
        if initial_data.shape[0] <= 1:  # If only headers or insufficient data
            raise ValueError("Dataset contains insufficient data")
    except (pd.errors.EmptyDataError, ValueError) as e:
        logging.info(
            "Dataset is empty or insufficient, collecting initial data from IQ Option..."
        )
        initial_data = collector.collect_initial_data(config['num_candles'])
        logging.info(f"Collected {len(initial_data)} initial data points")
        initial_data = engineer.add_technical_indicators(initial_data)
        initial_data.to_csv(dataset_path, index=False)
        logging.info(
            f"Initial data collected and saved with columns: {initial_data.columns}"
        )

    # Ensure the data is sufficient
    if len(initial_data) < 100:  # Ensure sufficient data points
        logging.error(
            "Insufficient data points after adding technical indicators. Collect more data."
        )
        return

    # Step 2: Train initial model if it doesn't exist
    model_path = 'models/trained_model.pkl'
    if not os.path.exists(model_path) or os.stat(model_path).st_size == 0:
        X_train, X_test, y_train, y_test = trainer.prepare_data(initial_data)
        if X_train.empty or y_train.empty:
            logging.error(
                "Insufficient data for training. Ensure the dataset is populated correctly."
            )
            return
        trainer.train(X_train, y_train)
        trainer.evaluate(X_test, y_test)

    analyzer = TradeSignalAnalyzer()

    # Step 3: Start real-time data collection and analysis
    def real_time_data_collection():
        while True:
            try:
                new_candle = collector.collect_new_candle()
                logging.info(f"New candle collected: {new_candle}")
                new_candle = engineer.add_technical_indicators(new_candle)
                if not new_candle.empty:
                    new_candle.to_csv(dataset_path,
                                      mode='a',
                                      header=False,
                                      index=False)
                    logging.info(
                        f"New candle added with columns: {new_candle.columns}")
                else:
                    logging.warning("No new candle data collected.")
            except Exception as e:
                logging.error(f"Error in real-time data collection: {e}")

    def real_time_analysis():
        while True:
            try:
                realtime_data = pd.read_csv(dataset_path)
                if 'SMA20' not in realtime_data.columns:
                    realtime_data = engineer.add_technical_indicators(
                        realtime_data)
                trade_signal = analyzer.analyze(realtime_data)
                if trade_signal:
                    logging.info(f"Trade Signal: {trade_signal}")
                    evaluator.add_trade(trade_signal)
            except Exception as e:
                logging.error(f"Error in real-time analysis: {e}")
            time.sleep(60)

    def trade_evaluation():
        while True:
            try:
                evaluator.evaluate_trades()
            except Exception as e:
                logging.error(f"Error in trade evaluation: {e}")
            time.sleep(60)

    # Start threads for real-time data collection, analysis, and trade evaluation
    data_thread = threading.Thread(target=real_time_data_collection)
    analysis_thread = threading.Thread(target=real_time_analysis)
    evaluation_thread = threading.Thread(target=trade_evaluation)

    data_thread.start()
    analysis_thread.start()
    evaluation_thread.start()


if __name__ == '__main__':
    main()
