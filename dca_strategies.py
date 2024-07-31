import yfinance as yf
import pandas as pd
import argparse
from datetime import datetime

VALID_PERIODS = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
VALID_INTERVALS = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']

# Fetch historical data
def fetch_yfinance_data(ticker, period, interval):
    df = yf.download(ticker, period=period, interval=interval)
    df.index = pd.to_datetime(df.index)
    return df

# Calculate optimal buy levels based on historical dips
def calculate_optimal_dca_levels(df, num_levels=5):
    # Calculate daily percentage drops from the high of the day
    df['High'] = df['High'].shift(1)  # Shift high price to previous day
    df['Drop'] = (df['High'] - df['Low']) / df['High'] * 100  # Calculate drop percentage
    df = df.dropna()  # Drop NA values

    # Get the most frequent drop levels
    drop_percentiles = [df['Drop'].quantile(i / num_levels) for i in range(1, num_levels + 1)]
    return drop_percentiles

# Simulate aggressive DCA strategy
def simulate_dca_strategy(df, drop_levels, daily_amount):
    base_price = df['Close'].iloc[-1]
    orders = [(base_price * (1 - level / 100), daily_amount / len(drop_levels)) for level in drop_levels]

    fulfilled_orders = []

    for price, amount in orders:
        fulfilled = df[df['Close'] <= price]
        if not fulfilled.empty:
            fulfilled_orders.append((fulfilled.index[0], amount / fulfilled['Close'].iloc[0]))

    total_invested = daily_amount * len(drop_levels)
    total_btc_purchased = sum([btc for time, btc in fulfilled_orders])
    avg_price_dca = total_invested / total_btc_purchased if total_btc_purchased != 0 else float('nan')

    return fulfilled_orders, avg_price_dca

# Main function
def main():
    parser = argparse.ArgumentParser(description='Simulate aggressive DCA strategy for a given ticker.')
    parser.add_argument('--ticker', type=str, default='BTC-USD', help='Ticker symbol (default: BTC-USD)')
    parser.add_argument('--period', type=str, choices=VALID_PERIODS, default='1mo', help='Data period (default: 1mo)')
    parser.add_argument('--interval', type=str, choices=VALID_INTERVALS, default='1h', help='Data interval (default: 1h)')
    parser.add_argument('--daily_amount', type=float, default=250, help='Daily amount in USD to invest (default: 250)')
    parser.add_argument('--num_levels', type=int, default=5, help='Number of DCA levels (default: 5)')

    args = parser.parse_args()

    # Check if the period is within the last 730 days
    if args.period not in VALID_PERIODS:
        raise ValueError("Invalid period. Choose from: " + ", ".join(VALID_PERIODS))

    df = fetch_yfinance_data(args.ticker, args.period, args.interval)
    drop_levels = calculate_optimal_dca_levels(df, args.num_levels)
    fulfilled_orders, avg_price_dca = simulate_dca_strategy(df, drop_levels, args.daily_amount)

    # Calculate amounts for each order
    order_amounts = [args.daily_amount / args.num_levels] * args.num_levels

    print(f"Optimal Drop Levels: {drop_levels}")
    print(f"DCA Avg Price: {avg_price_dca:.2f} USD")

    print("\nOrder Amounts:")
    for i, amount in enumerate(order_amounts):
        print(f"Order {i + 1} Amount: {amount:.2f} USD at {drop_levels[i]:.4f}% below market price")

    print("\nFulfilled Orders:")
    for time, btc in fulfilled_orders:
        print(f"Time: {time}, BTC Purchased: {btc:.6f}")

if __name__ == '__main__':
    main()
