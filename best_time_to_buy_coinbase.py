import requests
import pandas as pd
import argparse
from datetime import datetime, timedelta

def fetch_intraday_data(ticker, interval, period):
    base_url = "https://api.pro.coinbase.com"
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=int(period[:-1]))

    granularity_map = {
        '1m': 60,
        '5m': 300,
        '15m': 900,
        '30m': 1800,
        '60m': 3600,
        '6h': 21600,
        '1d': 86400
    }
    
    granularity = granularity_map.get(interval, 300)

    # Ensure granularity and period combination does not exceed 300 data points
    total_seconds = (end_time - start_time).total_seconds()
    max_data_points = 300
    
    while total_seconds / granularity > max_data_points:
        interval, granularity = next((k, v) for k, v in granularity_map.items() if v > granularity)
    
    url = f"{base_url}/products/{ticker}/candles"
    params = {
        'start': start_time.isoformat(),
        'end': end_time.isoformat(),
        'granularity': granularity
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

    data = response.json()

    if not data:
        raise Exception("No data returned from API.")

    df = pd.DataFrame(data, columns=['time', 'low', 'high', 'open', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    
    return df

def best_time_to_buy(data):
    # Extract time of day from the index
    data['Time'] = data.index.time

    # Group by time of day and calculate the average close price
    avg_price_by_time = data.groupby('Time')['close'].mean()

    if avg_price_by_time.empty:
        raise Exception("No average price data available to determine the best time to buy.")

    # Find the time of day with the lowest average close price
    best_time = avg_price_by_time.idxmin()
    lowest_avg_price = avg_price_by_time.min()

    return best_time, lowest_avg_price

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Determine the best time of day to buy a given ticker based on historical intraday data.")
    parser.add_argument('--ticker', type=str, default='BTC-USD', help='Ticker symbol (default: BTC-USD)')
    parser.add_argument('--interval', type=str, default='5m', help='Data interval (default: 5m)')
    parser.add_argument('--period', type=str, default='7d', help='Data period (default: 7d)')
    
    args = parser.parse_args()

    try:
        # Fetch intraday data based on command line arguments
        data = fetch_intraday_data(args.ticker, args.interval, args.period)

        # Determine the best time of day to buy
        best_time, lowest_avg_price = best_time_to_buy(data)

        print(f"The best time of day to buy {args.ticker} is at {best_time} with an average close price of ${lowest_avg_price:.2f}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

