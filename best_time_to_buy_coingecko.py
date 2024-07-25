import requests
import pandas as pd
import argparse
from datetime import datetime, timedelta

def fetch_intraday_data(ticker, interval, period):
    base_url = "https://api.coingecko.com/api/v3"
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=int(period[:-1]))

    url = f"{base_url}/coins/{ticker}/market_chart/range"
    params = {
        'vs_currency': 'usd',
        'from': int(start_date.timestamp()),
        'to': int(end_date.timestamp())
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

    data = response.json()

    if 'prices' not in data:
        raise Exception("No price data returned from API.")

    prices = data['prices']
    df = pd.DataFrame(prices, columns=['time', 'price'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df.set_index('time', inplace=True)

    # Resample to the specified interval
    if interval == '1m':
        df = df.resample('1T').mean()
    elif interval == '5m':
        df = df.resample('5T').mean()
    elif interval == '15m':
        df = df.resample('15T').mean()
    elif interval == '30m':
        df = df.resample('30T').mean()
    elif interval == '60m':
        df = df.resample('H').mean()
    elif interval == '1d':
        df = df.resample('D').mean()
    else:
        raise ValueError(f"Unsupported interval: {interval}")

    df.dropna(inplace=True)
    return df

def best_time_to_buy(data):
    # Extract time of day from the index
    data['Time'] = data.index.time

    # Group by time of day and calculate the average price
    avg_price_by_time = data.groupby('Time')['price'].mean()

    if avg_price_by_time.empty:
        raise Exception("No average price data available to determine the best time to buy.")

    # Find the time of day with the lowest average price
    best_time = avg_price_by_time.idxmin()
    lowest_avg_price = avg_price_by_time.min()

    return best_time, lowest_avg_price

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Determine the best time of day to buy a given ticker based on historical intraday data.")
    parser.add_argument('--ticker', type=str, default='bitcoin', help='Ticker symbol (default: bitcoin)')
    parser.add_argument('--interval', type=str, default='5m', help='Data interval (default: 5m)')
    parser.add_argument('--period', type=str, default='7d', help='Data period (default: 7d)')
    
    args = parser.parse_args()

    try:
        # Fetch intraday data based on command line arguments
        data = fetch_intraday_data(args.ticker, args.interval, args.period)

        # Determine the best time of day to buy
        best_time, lowest_avg_price = best_time_to_buy(data)

        print(f"The best time of day to buy {args.ticker} is at {best_time} with an average price of ${lowest_avg_price:.2f}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
