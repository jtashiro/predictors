import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# Define a function to fetch historical intraday data
def fetch_intraday_data(ticker, interval='5m', period='7d'):
    data = yf.download(tickers=ticker, interval=interval, period=period)
    return data

# Define a function to determine the best time of day to buy
def best_time_to_buy(data):
    # Convert index to datetime
    data.index = pd.to_datetime(data.index)

    # Extract time of day from the index
    data['Time'] = data.index.time

    # Group by time of day and calculate the average close price
    avg_price_by_time = data.groupby('Time')['Close'].mean()

    # Find the time of day with the lowest average close price
    best_time = avg_price_by_time.idxmin()
    lowest_avg_price = avg_price_by_time.min()

    return best_time, lowest_avg_price

# Fetch intraday BTC data
btc_data = fetch_intraday_data('BTC-USD', interval='5m', period='7d')

# Determine the best time of day to buy BTC
best_time, lowest_avg_price = best_time_to_buy(btc_data)

print(f"The best time of day to buy BTC-USD is at {best_time} with an average close price of ${lowest_avg_price:.2f}")
