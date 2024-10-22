import pandas as pd
from datetime import datetime

# Load BTC price data from a CSV file
btc_data = pd.read_csv('btc_prices.csv', parse_dates=['Date'])
btc_data.set_index('Date', inplace=True)

# Function to calculate BTC accumulated for a given strategy
def calculate_btc_accumulated(btc_data, amount_per_purchase, purchase_dates=None, strategy="daily"):
    total_btc = 0
    total_cost = 0

    if strategy == "daily":
        # Purchase every day
        for date, price in btc_data['Close'].items():
            total_btc += amount_per_purchase / price
            total_cost += amount_per_purchase
    elif strategy == "twice_per_month":
        # Purchase 15x the daily amount on 1st and 15th of each month
        twice_amount = amount_per_purchase * 15
        for date, price in btc_data['Close'].items():
            if date.day == 1 or date.day == 15:
                total_btc += twice_amount / price
                total_cost += twice_amount

    return total_btc, total_cost

# Define parameters
amount_per_purchase = 100  # The amount of USD to spend per daily purchase
start_date = '2024-01-01'
end_date = '2024-12-31'

# Filter data for the selected date range
btc_data = btc_data.loc[start_date:end_date]

# Calculate BTC accumulated with daily purchases
btc_daily, cost_daily = calculate_btc_accumulated(btc_data, amount_per_purchase, strategy="daily")

# Calculate BTC accumulated with purchases on 1st and 15th (15x daily amount)
btc_twice_per_month, cost_twice_per_month = calculate_btc_accumulated(btc_data, amount_per_purchase, strategy="twice_per_month")

# Output results
print(f"Daily Purchase Strategy:")
print(f"Total BTC accumulated: {btc_daily:.8f}")
print(f"Total cost spent: ${cost_daily:.2f}")

print(f"\nTwice-Per-Month Purchase Strategy (15x daily amount):")
print(f"Total BTC accumulated: {btc_twice_per_month:.8f}")
print(f"Total cost spent: ${cost_twice_per_month:.2f}")

# Calculate and compare
btc_difference = btc_daily - btc_twice_per_month
cost_difference = cost_daily - cost_twice_per_month

print(f"\nDifference in BTC accumulated: {btc_difference:.8f}")
print(f"Difference in total cost spent: ${cost_difference:.2f}")


