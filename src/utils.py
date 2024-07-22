import os

def check_and_create_files():
    if not os.path.exists('data/historical_data.csv'):
        with open('data/historical_data.csv', 'w') as f:
            f.write('timestamp,open,high,low,close\n')
    if not os.path.exists('data/realtime_data.csv'):
        with open('data/realtime_data.csv', 'w') as f:
            f.write('timestamp,open,high,low,close\n')
