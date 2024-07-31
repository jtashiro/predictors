import yfinance as yf
import pandas as pd
import argparse
from datetime import datetime
from collections import defaultdict

def fetch_yfinance_data(ticker, period, interval):
    df = yf.download(ticker, period=period, interval=interval)
    df.index = pd.to_datetime(df.index)
    return df

def find_optimal_time(df):
    avg_prices_by_hour = df.groupby(df.index.hour)['Close'].mean()
    optimal_hour = avg_prices_by_hour.idxmin()
    return optimal_hour

def simulate_single_purchase(df, optimal_hour):
    df_optimal = df[df.index.hour == optimal_hour]
    avg_price = df_optimal['Close'].mean()
    return avg_price

def simulate_dca_strategy(df, price_levels, amounts):
    base_price = df['Close'].iloc[-1]
    orders = [(base_price * (1 - level / 100), amount) for level, amount in zip(price_levels, amounts)]
    fulfilled_orders = defaultdict(float)

    for price, amount in orders:
        fulfilled = df[df['Close'] <= price]
        if not fulfilled.empty:
            fulfilled_orders[fulfilled.index[0]] += amount / fulfilled['Close'].iloc[0]

    return fulfilled_orders

def main():
    parser = argparse.ArgumentParser(description='Simulate DCA strategy for a given ticker.')
    parser.add_argument('--ticker', type=str, default='BTC-USD', help='Ticker symbol (default: BTC-USD)')
    parser.add_argument('--period', type=str, choices=['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'], default='1mo', help='Data period (default: 1mo)')
    parser.add_argument('--interval', type=str, choices=['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'], default='1h', help='Data interval (default: 1h)')
    parser.add_argument('--price_levels', nargs='+', type=float, default=[0.01, 1, 2, 3, 4], help='Price levels below market price for placing orders (default: [0.01, 1, 2, 3, 4])')
    parser.add_argument('--amounts', nargs='+', type=float, default=[100, 200, 300, 400, 500], help='USD amounts for each price level (default: [100, 200, 300, 400, 500])')
    
    args = parser.parse_args()

    df = fetch_yfinance_data(args.ticker, args.period, args.interval)
    optimal_hour = find_optimal_time(df)
    avg_price_single_purchase = simulate_single_purchase(df, optimal_hour)
    fulfilled_orders = simulate_dca_strategy(df, args.price_levels, args.amounts)

    total_invested = sum(args.amounts)
    total_btc_purchased = sum(fulfilled_orders.values())
    avg_price_dca = total_invested / total_btc_purchased if total_btc_purchased != 0 else float('nan')

    print(f"Optimal Time: {optimal_hour}:00")
    print(f"Single Purchase Avg Price: {avg_price_single_purchase:.2f} USD")
    print(f"DCA Avg Price: {avg_price_dca:.2f} USD")

    print("\nFulfilled Orders:")
    for time, btc in fulfilled_orders.items():
        print(f"Time: {time}, BTC Purchased: {btc:.6f}")

if __name__ == '__main__':
    main()
