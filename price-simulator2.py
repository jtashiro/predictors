import numpy as np
import yfinance as yf
from datetime import datetime

# Download historical data
def get_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data['Close']

# Calculate returns
def calculate_returns(prices):
    returns = prices.pct_change().dropna()
    return returns

# Calculate average return and standard deviation
def calculate_metrics(returns):
    average_return = returns.mean()
    std_deviation = returns.std()
    return average_return, std_deviation

# Define simulation function
def simulate_price(initial_price, drift, volatility, num_paths, num_days):
    dt = 1 / 365  # Using calendar days
    prices = np.zeros((num_paths, num_days))
    prices[:, 0] = initial_price
    for i in range(1, num_days):
        rand = np.random.normal(0, 1, num_paths)
        prices[:, i] = prices[:, i-1] * np.exp((drift - 0.5 * volatility**2) * dt + volatility * np.sqrt(dt) * rand)
    return prices[:, -1]

# Define parameters
start_date = '2023-01-01'
end_date = '2024-07-01'

# Get data for BTC and BCH
btc_prices = get_data('BTC-USD', start_date, end_date)
bch_prices = get_data('BCH-USD', start_date, end_date)

# Calculate returns
btc_returns = calculate_returns(btc_prices)
bch_returns = calculate_returns(bch_prices)

# Calculate metrics
btc_avg_return, btc_std_dev = calculate_metrics(btc_returns)
bch_avg_return, bch_std_dev = calculate_metrics(bch_returns)

# Convert metrics to annualized return and volatility based on 365 days
days_per_year = 365
btc_drift = btc_avg_return * days_per_year
btc_volatility = btc_std_dev * np.sqrt(days_per_year)

bch_drift = bch_avg_return * days_per_year
bch_volatility = bch_std_dev * np.sqrt(days_per_year)

# Calculate number of days to target date
start_date = datetime(2024, 7, 20)
end_date = datetime(2024, 12, 31)
num_days = (end_date - start_date).days

# Parameters for simulation
initial_price_btc = btc_prices.iloc[-1]  # Using the most recent closing price
initial_price_bch = bch_prices.iloc[-1]  # Using the most recent closing price
num_paths = 50000

# Simulate BTC and BCH prices
btc_prices_simulated = simulate_price(initial_price_btc, btc_drift, btc_volatility, num_paths, num_days)
bch_prices_simulated = simulate_price(initial_price_bch, bch_drift, bch_volatility, num_paths, num_days)

# Calculate 95% and 99% confidence intervals
btc_ci_95 = np.percentile(btc_prices_simulated, [2.5, 97.5])
btc_ci_99 = np.percentile(btc_prices_simulated, [0.5, 99.5])
bch_ci_95 = np.percentile(bch_prices_simulated, [2.5, 97.5])
bch_ci_99 = np.percentile(bch_prices_simulated, [0.5, 99.5])

# Format results for better readability
def format_number(num):
    return "{:,.2f}".format(num)

btc_ci_95_formatted = [format_number(x) for x in btc_ci_95]
btc_ci_99_formatted = [format_number(x) for x in btc_ci_99]
bch_ci_95_formatted = [format_number(x) for x in bch_ci_95]
bch_ci_99_formatted = [format_number(x) for x in bch_ci_99]

# Print results
print(f"BTC 95% Confidence Interval: [{btc_ci_95_formatted[0]}, {btc_ci_95_formatted[1]}]")
print(f"BTC 99% Confidence Interval: [{btc_ci_99_formatted[0]}, {btc_ci_99_formatted[1]}]")
print(f"BCH 95% Confidence Interval: [{bch_ci_95_formatted[0]}, {bch_ci_95_formatted[1]}]")
print(f"BCH 99% Confidence Interval: [{bch_ci_99_formatted[0]}, {bch_ci_99_formatted[1]}]")


