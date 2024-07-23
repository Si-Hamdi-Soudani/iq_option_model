import os


def check_and_create_files():
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists('models'):
        os.makedirs('models')
    if not os.path.exists('data/historical_data.csv'):
        with open('data/historical_data.csv', 'w') as f:
            f.write(
                'id,from,at,to,open,close,min,max,volume,timestamp,open,high,low,close,SMA20,EMA50,RSI,MACD,MACD_Signal,Bollinger_High,Bollinger_Low\n'
            )
    if not os.path.exists('data/trade_results.csv'):
        with open('data/trade_results.csv', 'w') as f:
            f.write(
                'entry_time,exit_time,entry_price,exit_price,action,result\n')
