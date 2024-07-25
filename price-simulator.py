import numpy as np
import pandas as pd

# Parameters
initial_price_btc = 67000  # Example initial price
initial_price_bch = 390    # Example initial price
drift_btc = 0.01  # Example drift (historical average return)
volatility_btc = 0.02  # Example volatility (historical standard deviation)
drift_bch = 0.02  # Example drift (historical average return)
volatility_bch = 0.03  # Example volatility (historical standard deviation)
num_paths = 2000
num_days = 200  # Approximate number of days to December 2024

np.random.seed(42)  # For reproducibility

def simulate_price(initial_price, drift, volatility, num_paths, num_days):
    prices = np.zeros((num_paths, num_days))
    prices[:, 0] = initial_price
    for i in range(1, num_days):
        rand = np.random.normal(0, 1, num_paths)
        prices[:, i] = prices[:, i-1] * np.exp((drift - 0.5 * volatility**2) + volatility * rand)
    return prices[:, -1]

# Simulate BTC and BCH prices
btc_prices = simulate_price(initial_price_btc, drift_btc, volatility_btc, num_paths, num_days)
bch_prices = simulate_price(initial_price_bch, drift_bch, volatility_bch, num_paths, num_days)

# Calculate confidence intervals
btc_ci_95 = np.percentile(btc_prices, [2.5, 97.5])
bch_ci_95 = np.percentile(bch_prices, [2.5, 97.5])
btc_ci_99 = np.percentile(btc_prices, [0.5, 99.5])
bch_ci_99 = np.percentile(bch_prices, [0.5, 99.5])

btc_ci_99, bch_ci_99

btc_ci_95, bch_ci_95

print(f"BTC 95%: {btc_ci_95}")
print(f"BCH 95%: {bch_ci_95}")

print(f"BTC 99%: {btc_ci_99}")
print(f"BCH 99%: {bch_ci_99}")
