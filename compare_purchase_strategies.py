import yfinance as yf
import pandas as pd
import argparse

VALID_PERIODS = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
VALID_INTERVALS = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
MAX_DAYS = 730

def fetch_yfinance_data(ticker, period='1mo', interval='1h'):
    df = yf.download(ticker, period=period, interval=interval)
    df.index = pd.to_datetime(df.index)
    return df

def calculate_avg_price_at_time(df, hour):
    df_time = df[df.index.hour == hour]
    avg_price_time = df_time['Close'].mean()
    return avg_price_time

def calculate_avg_price_multiple_purchases(df):
    df_4hour = df[df.index.hour % 4 == 0]
    avg_price_4hour = df_4hour['Close'].mean()
    return avg_price_4hour

def find_optimal_purchase_time(df):
    df['Hour'] = df.index.hour
    avg_price_by_hour = df.groupby('Hour')['Close'].mean()
    optimal_hour = avg_price_by_hour.idxmin()
    optimal_price = avg_price_by_hour.min()
    return optimal_hour, optimal_price

def validate_period(period):
    if period == '1d':
        days = 1
    elif period == '5d':
        days = 5
    elif period == '1mo':
        days = 30
    elif period == '3mo':
        days = 90
    elif period == '6mo':
        days = 180
    elif period == '1y':
        days = 365
    elif period == '2y':
        days = 730
    elif period in ['5y', '10y', 'ytd', 'max']:
        days = MAX_DAYS + 1  # Beyond the max limit for simplicity
    else:
        raise ValueError("Invalid period provided.")

    if days > MAX_DAYS:
        raise ValueError(f"The requested range for period '{period}' must be within the last {MAX_DAYS} days.")
    return period

def validate_interval(interval):
    if interval not in VALID_INTERVALS:
        raise ValueError(f"Invalid interval provided. Valid intervals: {', '.join(VALID_INTERVALS)}")
    return interval

def main():
    parser = argparse.ArgumentParser(description='Compare purchase strategies for a given ticker.')
    parser.add_argument('--ticker', type=str, default='BTC-USD', help='Ticker symbol (default: BTC-USD)')
    parser.add_argument('--period', type=str, choices=VALID_PERIODS, default='1mo', help='Data period (default: 1mo)')
    parser.add_argument('--interval', type=str, choices=VALID_INTERVALS, default='1h', help='Data interval (default: 1h)')
    
    args = parser.parse_args()
    
    try:
        validated_period = validate_period(args.period)
        validated_interval = validate_interval(args.interval)
    except ValueError as e:
        print(e)
        return
    
    print(f"Fetching historical data for {args.ticker} for the past {validated_period} with {validated_interval} interval.")
    df = fetch_yfinance_data(args.ticker, validated_period, validated_interval)
    
    print(f"Data fetched. First few rows:\n{df.head()}")

    avg_price_at_optimal_time = calculate_avg_price_at_time(df, find_optimal_purchase_time(df)[0])
    avg_price_4hour = calculate_avg_price_multiple_purchases(df)
    optimal_hour, optimal_price = find_optimal_purchase_time(df)
    
    print("\nComparison of Strategies:")
    print(f"Average Price for Single Purchase at Optimal Time ({optimal_hour}:00): {avg_price_at_optimal_time:.2f} USD")
    print(f"Average Price for Multiple Purchases Every 4 Hours: {avg_price_4hour:.2f} USD")
    print(f"Optimal Time to Purchase: {optimal_hour}:00 with Average Price: {optimal_price:.2f} USD")
    
    if avg_price_at_optimal_time < avg_price_4hour:
        print("Single Purchase at Optimal Time is the better strategy.")
    else:
        print("Multiple Purchases Every 4 Hours is the better strategy.")

if __name__ == '__main__':
    main()
