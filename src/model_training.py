import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

class ModelTrainer:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)

    def prepare_data(self, data):
        data['next_move'] = data['close'].shift(-5) > data['close']
        data = data.dropna()
        X = data[['SMA20', 'EMA50', 'RSI', 'MACD', 'MACD_Signal', 'Bollinger_High', 'Bollinger_Low']]
        y = data['next_move']
        return train_test_split(X, y, test_size=0.2, random_state=42)

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def evaluate(self, X_test, y_test):
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f'Accuracy: {accuracy:.2f}')
        joblib.dump(self.model, 'models/trained_model.pkl')
