"""
Portfolio Risk Analysis
Author: Mohamed Lamkadmi
Description: Portfolio optimization tool analyzing 5 stocks — 
calculates Sharpe ratios, volatility, and efficient frontier.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Step 1: Download stock data (Canadian + US)
tickers = ['BNS.TO', 'TD.TO', 'CNR.TO', 'SHOP.TO', 'BCE.TO']
data = yf.download(tickers, start='2023-01-01', end='2026-05-01')['Close']

# Step 2: Calculate daily returns
returns = data.pct_change().dropna()

# Step 3: Calculate annualized return and volatility
annual_return = returns.mean() * 252
annual_vol = returns.std() * np.sqrt(252)
sharpe_ratio = annual_return / annual_vol

print("=== Portfolio Metrics ===")
metrics = pd.DataFrame({
    'Return': annual_return,
    'Volatility': annual_vol,
    'Sharpe Ratio': sharpe_ratio
})
print(metrics.round(4))

# Step 4: Monte Carlo simulation for efficient frontier
num_portfolios = 10000
results = np.zeros((3, num_portfolios))
weights_record = []

for i in range(num_portfolios):
    weights = np.random.random(len(tickers))
    weights /= np.sum(weights)
    weights_record.append(weights)
    
    port_return = np.dot(weights, annual_return)
    port_vol = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
    sharpe = port_return / port_vol
    
    results[0, i] = port_return
    results[1, i] = port_vol
    results[2, i] = sharpe

# Step 5: Find optimal portfolio (highest Sharpe ratio)
max_sharpe_idx = np.argmax(results[2])
optimal = {
    'Return': results[0, max_sharpe_idx],
    'Volatility': results[1, max_sharpe_idx],
    'Sharpe': results[2, max_sharpe_idx]
}
print("\n=== Optimal Portfolio (Max Sharpe) ===")
for k, v in optimal.items():
    print(f"{k}: {v:.4f}")

print("\nOptimal Weights:")
opt_weights = weights_record[max_sharpe_idx]
for t, w in zip(tickers, opt_weights):
    print(f"{t}: {w:.2%}")

# Step 6: Plot efficient frontier
plt.figure(figsize=(10, 6))
plt.scatter(results[1, :], results[0, :], c=results[2, :], 
            cmap='viridis', alpha=0.6, s=10)
plt.colorbar(label='Sharpe Ratio')
plt.scatter(optimal['Volatility'], optimal['Return'], 
            c='red', marker='*', s=300, label='Optimal Portfolio')
plt.xlabel('Volatility (Risk)')
plt.ylabel('Expected Return')
plt.title('Efficient Frontier - Portfolio Optimization')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('efficient_frontier.png', dpi=150)
plt.show()

print("\nEfficient frontier chart saved as 'efficient_frontier.png'")
