import yfinance as yf
import pandas as pd

# Function to fetch historical BTC data and save it to a CSV file
def fetch_btc_data(start_date, end_date, filename):
    # Fetch Bitcoin historical data from Yahoo Finance
    btc_data = yf.download('BTC-USD', start=start_date, end=end_date)

    # Keep only the 'Close' column and reset the index to have a 'Date' column
    btc_data = btc_data[['Close']].reset_index()

    # Save the data to a CSV file
    btc_data.to_csv(filename, index=False)
    print(f"Data successfully saved to {filename}")

# Define parameters
start_date = '2024-01-01'  # Start date for fetching historical data
end_date = '2024-12-31'    # End date for fetching historical data
filename = 'btc_prices.csv' # Name of the CSV file to save data

# Fetch BTC data and save to CSV
fetch_btc_data(start_date, end_date, filename)


