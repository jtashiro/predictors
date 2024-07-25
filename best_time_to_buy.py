import requests
import yfinance as yf
import pandas as pd
import argparse
from datetime import datetime, timedelta
from prettytable import PrettyTable

# Mapping of common ticker symbols to CoinGecko identifiers
COINGECKO_TICKER_MAP = {
    'BTC-USD': 'bitcoin',
    'ETH-USD': 'ethereum',
    'LTC-USD': 'litecoin',
    'XRP-USD': 'ripple',
    'BCH-USD': 'bitcoin-cash',
    'ADA-USD': 'cardano',
    'DOT-USD': 'polkadot',
    'LINK-USD': 'chainlink',
    'DOGE-USD': 'dogecoin',
    # Add more mappings as needed
}

def fetch_coinbase_data(ticker, interval, period):
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
    df.rename(columns={"close": "price"}, inplace=True)

    print(f"Coinbase Data:\n{df.head()}")  # Debug print

    return df[['price']]

def fetch_coingecko_data(ticker, interval, period):
    base_url = "https://api.coingecko.com/api/v3"
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=int(period[:-1]))

    if ticker in COINGECKO_TICKER_MAP:
        coingecko_ticker = COINGECKO_TICKER_MAP[ticker]
    else:
        raise ValueError(f"Unknown ticker symbol: {ticker}")

    url = f"{base_url}/coins/{coingecko_ticker}/market_chart/range"
    params = {
        'vs_currency': 'usd',
        'from': int(start_date.timestamp()),
        'to': int(end_date.timestamp())
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if 'prices' not in data:
            raise ValueError("No price data returned from API.")
        
        prices = data['prices']
        df = pd.DataFrame(prices, columns=['time', 'price'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        df.set_index('time', inplace=True)

        # Adjust for intervals
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

        print(f"CoinGecko Data:\n{df.head()}")  # Debug print

        return df[['price']]
    
    except requests.RequestException as e:
        raise Exception(f"Error fetching data: {e}")
    except ValueError as e:
        raise Exception(f"Data processing error: {e}")

def fetch_cryptocompare_data(ticker, interval, period):
    base_url = "https://min-api.cryptocompare.com/data/v2/histoday"
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=int(period[:-1]))

    params = {
        'fsym': ticker.split('-')[0],
        'tsym': 'USD',
        'limit': int(period[:-1]),
        'toTs': int(end_time.timestamp())
    }

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

    data = response.json()
    if 'Data' not in data:
        raise Exception("No data returned from API.")

    df = pd.DataFrame(data['Data']['Data'])
    df['time'] = pd.to_datetime(df['time'], unit='s')  # Convert Unix time to datetime
    df.set_index('time', inplace=True)
    df.rename(columns={"close": "price"}, inplace=True)

    # Handle interval logic
    if interval == '1d':
        df = df.resample('H').mean()  # Treat daily data as hourly to find best time of day

    print(f"CryptoCompare Data:\n{df.head()}")  # Debug print

    return df[['price']]

def fetch_yfinance_data(ticker, interval, period):
    period_map = {
        '1d': '1d',
        '5d': '5d',
        '1mo': '1mo',
        '3mo': '3mo',
        '6mo': '6mo',
        '1y': '1y',
        '2y': '2y',
        '5y': '5y',
        '10y': '10y',
        'ytd': 'ytd',
        'max': 'max'
    }

    period = period_map.get(period, '5d')
    data = yf.download(ticker, period=period, interval=interval)
    if data.empty:
        raise Exception("No data returned from API.")
    
    data = data[['Close']].rename(columns={'Close': 'price'})

    # Adjust for intervals
    if interval == '1d':
        data = data.resample('H').mean()  # Treat daily data as hourly to find best time of day

    print(f"YFinance Data:\n{data.head()}")  # Debug print

    return data

def best_time_to_buy(df, interval):
    if df.empty:
        raise ValueError("DataFrame is empty. Cannot calculate the best time to buy.")

    if interval == '1d':
        if 'hour' not in df.columns:  # Check if hourly data is not available
            return "N/A", df['price'].min()  # Return N/A if hourly granularity is not available

        df = df.resample('H').mean()  # Ensure data is hourly for daily interval data
        best_time = df['price'].idxmin()
        lowest_avg_price = df['price'].min()
        return f"{best_time.hour}:{best_time.minute:02}", lowest_avg_price

    df['hour'] = df.index.hour
    df['minute'] = df.index.minute
    df = df.groupby(['hour', 'minute']).mean()  # Group by both hour and minute if available

    avg_price_by_time = df['price']
    if avg_price_by_time.empty:
        raise ValueError("No price data available for calculating best time to buy.")
    
    best_time = avg_price_by_time.idxmin()
    lowest_avg_price = avg_price_by_time.min()
    
    return f"{best_time[0]}:{best_time[1]:02}", lowest_avg_price

def main():
    parser = argparse.ArgumentParser(description="Find the best time to buy cryptocurrency.")
    parser.add_argument('--source', choices=['yfinance', 'coinbase', 'coingecko', 'cryptocompare', 'all'], required=True, help='Data source')
    parser.add_argument('--ticker', type=str, default='BTC-USD', help='Cryptocurrency ticker symbol')
    parser.add_argument('--period', type=str, default='5d', help='Time period for the data (e.g., 5d, 1mo)')
    parser.add_argument('--interval', type=str, default='1d', help='Data interval (e.g., 1m, 5m, 15m, 30m, 60m, 1d)')
    args = parser.parse_args()

    sources = {
        'yfinance': fetch_yfinance_data,
        'coinbase': fetch_coinbase_data,
        'coingecko': fetch_coingecko_data,
        'cryptocompare': fetch_cryptocompare_data
    }

    results = []

    if args.source == 'all':
        for source, func in sources.items():
            print(f"Fetching data from {source} with parameters:")
            print(f"  Ticker: {args.ticker}")
            print(f"  Interval: {args.interval}")
            print(f"  Period: {args.period}")

            try:
                df = func(args.ticker, args.interval, args.period)
                best_time, lowest_avg_price = best_time_to_buy(df, args.interval)
                results.append({
                    'Source': source,
                    'Best Time to Buy (Hour:Minute)': best_time,
                    'Lowest Average Price (USD)': f"{lowest_avg_price:.2f} USD"
                })
            except Exception as e:
                results.append({
                    'Source': source,
                    'Best Time to Buy (Hour:Minute)': 'Error',
                    'Lowest Average Price (USD)': str(e)
                })

    else:
        print(f"Fetching data from {args.source} with parameters:")
        print(f"  Ticker: {args.ticker}")
        print(f"  Interval: {args.interval}")
        print(f"  Period: {args.period}")

        try:
            df = sources[args.source](args.ticker, args.interval, args.period)
            best_time, lowest_avg_price = best_time_to_buy(df, args.interval)
            results.append({
                'Source': args.source,
                'Best Time to Buy (Hour:Minute)': best_time,
                'Lowest Average Price (USD)': f"{lowest_avg_price:.2f} USD"
            })
        except Exception as e:
            results.append({
                'Source': args.source,
                'Best Time to Buy (Hour:Minute)': 'Error',
                'Lowest Average Price (USD)': str(e)
            })

    table = PrettyTable()
    table.field_names = ["Source", "Best Time to Buy (Hour:Minute)", "Lowest Average Price (USD)"]
    for result in results:
        table.add_row([result['Source'], result['Best Time to Buy (Hour:Minute)'], result['Lowest Average Price (USD)']])

    print(table)

if __name__ == '__main__':
    main()
