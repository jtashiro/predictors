import requests

# Function to fetch all available coins from CoinGecko
def list_all_coins():
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url)
    
    if response.status_code == 200:
        coins = response.json()
        print(f"Total coins available: {len(coins)}\n")
        
        # Print the list of coins (ID, Symbol, and Name)
        for coin in coins:
            print(f"ID: {coin['id']}, Symbol: {coin['symbol']}, Name: {coin['name']}")
    else:
        print(f"Error: {response.status_code}, unable to fetch data from CoinGecko API")

if __name__ == "__main__":
    list_all_coins()
