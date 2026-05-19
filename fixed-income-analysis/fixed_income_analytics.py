"""
Fixed Income Analytics
Author: Mohamed Lamkadmi
Description: Bond yield trend analysis, yield curve visualization, 
and duration/convexity calculations for a sample bond portfolio.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Step 1: Download yield data for different maturities
# ^IRX = 13-week T-bill, ^FVX = 5-year, ^TNX = 10-year, ^TYX = 30-year
tickers = ['^IRX', '^FVX', '^TNX', '^TYX']
labels = ['3-Month', '5-Year', '10-Year', '30-Year']
data = yf.download(tickers, start='2023-01-01', end='2026-05-01')['Close']
data.columns = labels

# Step 2: Plot yield curve over time
plt.figure(figsize=(12, 6))
for col in labels:
    plt.plot(data.index, data[col], label=col)
plt.title('US Treasury Yields by Maturity (2023-2026)')
plt.xlabel('Date')
plt.ylabel('Yield (%)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('yield_curve_time_series.png', dpi=150)
plt.show()

# Step 3: Yield curve snapshot (most recent vs 1 year ago)
latest = data.iloc[-1]
year_ago = data.iloc[-252] if len(data) > 252 else data.iloc[0]

maturities = [0.25, 5, 10, 30]
plt.figure(figsize=(8, 5))
plt.plot(maturities, year_ago.values, 'o-', label='1 Year Ago', color='gray')
plt.plot(maturities, latest.values, 'o-', label='Current', color='blue', linewidth=2)
plt.xlabel('Maturity (Years)')
plt.ylabel('Yield (%)')
plt.title('Yield Curve Comparison')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('yield_curve_snapshot.png', dpi=150)
plt.show()

# Step 4: Calculate yield curve slope (10Y - 2Y) using available maturities
slope = data['10-Year'] - data['5-Year']
plt.figure(figsize=(10, 4))
plt.plot(slope.index, slope, color='purple')
plt.axhline(y=0, color='red', linestyle='--', alpha=0.5)
plt.title('Yield Curve Slope (10Y - 5Y)')
plt.xlabel('Date')
plt.ylabel('Spread (%)')
plt.grid(True, alpha=0.3)
plt.savefig('yield_curve_slope.png', dpi=150)
plt.show()

# Step 5: Simplified duration and convexity for a sample bond
print("=== Hypothetical Bond Analysis ===")
face_value = 1000
coupon_rate = 0.05
coupon = face_value * coupon_rate
maturity = 10  # years
ytm = latest['10-Year'] / 100  # current 10Y yield as discount rate

# Calculate bond price
def bond_price(ytm, coupon, face, years):
    cf = [coupon] * years
    cf[-1] += face
    t = np.arange(1, years + 1)
    pv = np.array(cf) / ((1 + ytm) ** t)
    return np.sum(pv)

price = bond_price(ytm, coupon, face_value, maturity)
print(f"Bond: {coupon_rate*100:.0f}% coupon, {maturity}yr maturity, Face=${face_value}")
print(f"Current YTM: {ytm*100:.2f}%")
print(f"Calculated Price: ${price:.2f}")

# Duration (Macaulay)
def macaulay_duration(ytm, coupon, face, years):
    cf = [coupon] * years
    cf[-1] += face
    t = np.arange(1, years + 1)
    pv = np.array(cf) / ((1 + ytm) ** t)
    weighted_time = np.sum(t * pv)
    return weighted_time / np.sum(pv)

duration = macaulay_duration(ytm, coupon, face_value, maturity)
modified_duration = duration / (1 + ytm)
print(f"Macaulay Duration: {duration:.2f} years")
print(f"Modified Duration: {modified_duration:.2f}")
print(f"Price change per 1% yield increase: -${modified_duration * price * 0.01:.2f}")

# Convexity
def convexity(ytm, coupon, face, years):
    cf = [coupon] * years
    cf[-1] += face
    t = np.arange(1, years + 1)
    pv = np.array(cf) / ((1 + ytm) ** t)
    return np.sum(t * (t + 1) * pv) / ((1 + ytm) ** 2 * np.sum(pv))

conv = convexity(ytm, coupon, face_value, maturity)
print(f"Convexity: {conv:.2f}")
print(f"Convexity adjustment for 1% yield increase: +${0.5 * conv * price * (0.01**2):.2f}")
print(f"Estimated total price change for +1% yield: -${(modified_duration * price * 0.01 - 0.5 * conv * price * (0.01**2)):.2f}")

print("\nAnalysis complete. Charts saved.")
