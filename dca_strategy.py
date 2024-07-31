import argparse
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import DateOffset

VALID_PERIODS = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
VALID_INTERVALS = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']

def fetch_data(ticker, period, interval):
    data = yf.download(ticker, period=period, interval=interval)
    return data

def calculate_avg_price_single_purchase(df, optimal_time):
    df.index = pd.to_datetime(df.index)  # Ensure the index is datetime
    df_optimal = df.between_time(optimal_time, optimal_time)
    return df_optimal['Close'].mean()

def calculate_avg_price_multiple_purchases(df, intervals):
    df.index = pd.to_datetime(df.index)  # Ensure the index is datetime
    prices = []
    for interval in intervals:
        df_interval = df.between_time(interval, interval)
        if not df_interval.empty:
            prices.append(df_interval['Close'].mean())
    return sum(prices) / len(prices) if prices else None

def distribute_orders(market_order_amount, total_amount, num_orders, start_price, price_step):
    remaining_amount = total_amount - market_order_amount
    per_order_amount = remaining_amount / num_orders
    orders = []
    
    for i in range(num_orders):
        price_level = start_price - (i + 1) * price_step
        orders.append({'price': price_level, 'amount': per_order_amount})
    
    return orders

def main():
    parser = argparse.ArgumentParser(description="Compare purchase strategies")
    parser.add_argument('--ticker', type=str, default='BTC-USD', help='Ticker symbol')
    parser.add_argument('--period', type=str, choices=VALID_PERIODS, default='1mo', help='Data period (default: 1mo)')
    parser.add_argument('--interval', type=str, choices=VALID_INTERVALS, default='1h', help='Data interval (default: 1h)')
    parser.add_argument('--market_order', type=float, default=250, help='Amount for the market order')
    parser.add_argument('--total_amount', type=float, required=True, help='Total amount to invest per day')
    parser.add_argument('--num_orders', type=int, default=4, help='Number of orders below market price')
    parser.add_argument('--start_price', type=float, required=True, help='Current market price')
    parser.add_argument('--price_step', type=float, default=0.01, help='Step percentage below market price (e.g., 0.01 for 1%)')
    
    args = parser.parse_args()
    
    market_order_amount = args.market_order
    total_amount = args.total_amount
    num_orders = args.num_orders
    start_price = args.start_price
    price_step = args.price_step * start_price
    
    print(f"Fetching data from yfinance with parameters:")
    print(f"  Ticker: {args.ticker}")
    print(f"  Interval: {args.interval}")
    print(f"  Period: {args.period}")
    
    df = fetch_data(args.ticker, args.period, args.interval)
    
    if df.empty:
        print("No data fetched, please check the ticker symbol and internet connection.")
        return
    
    # Find the optimal time to purchase
    optimal_time = '07:00'  # Example optimal time, you might calculate this based on historical analysis
    avg_price_single = calculate_avg_price_single_purchase(df, optimal_time)
    intervals = ['07:00', '11:00', '15:00', '19:00', '23:00']
    avg_price_multiple = calculate_avg_price_multiple_purchases(df, intervals)
    
    orders = distribute_orders(market_order_amount, total_amount, num_orders, start_price, price_step)
    
    print(f"Market order: ${market_order_amount} at market price {start_price}")
    for i, order in enumerate(orders):
        print(f"Order {i + 1}: ${order['amount']} at price {order['price']} (expires in 24 hours)")
    
    print(f"Average price for single purchase at optimal time ({optimal_time}): {avg_price_single}")
    print(f"Average price for multiple purchases: {avg_price_multiple}")

if __name__ == "__main__":
    main()
