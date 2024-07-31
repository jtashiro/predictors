import numpy as np
import matplotlib.pyplot as plt

# Parameters
initial_investment = 10000
margin_rate = 0.07
historical_returns = np.random.normal(0.095, 0.15, 10000)  # mean return, std deviation, number of simulations

# Simulate returns
portfolio_returns = []
for r in historical_returns:
    net_return = r - margin_rate
    portfolio_value = initial_investment * (1 + net_return)
    portfolio_returns.append(portfolio_value)

# Plot results
plt.hist(portfolio_returns, bins=50, alpha=0.75, color='blue')
plt.title('Simulated Portfolio Values')
plt.xlabel('Portfolio Value')
plt.ylabel('Frequency')
plt.axvline(x=initial_investment, color='r', linestyle='--', label='Initial Investment')
plt.legend()
plt.show()
