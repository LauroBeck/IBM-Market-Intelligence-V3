import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# INITIAL CONDITIONS
# -----------------------------

initial_debt = 4.4e12        # 4.4 trillion yuan issuance
initial_gdp = 120e12         # example GDP level
initial_fx = 6.88            # USD/CNY
years = 5
simulations = 10000

# Assumptions (mean & volatility)
mean_gdp_growth = 0.05
gdp_volatility = 0.02

mean_rate = 0.03
rate_volatility = 0.015

fx_volatility = 0.03


# -----------------------------
# MONTE CARLO SIMULATION
# -----------------------------

debt_to_gdp_results = []

for _ in range(simulations):
    
    debt = initial_debt
    gdp = initial_gdp
    fx = initial_fx
    
    for _ in range(years):
        
        # Random shocks
        gdp_growth = np.random.normal(mean_gdp_growth, gdp_volatility)
        rate_shock = np.random.normal(mean_rate, rate_volatility)
        fx_shock = np.random.normal(0, fx_volatility)
        
        # Update GDP
        gdp *= (1 + gdp_growth)
        
        # Debt grows with interest rate
        debt *= (1 + rate_shock)
        
        # FX shock impact (external debt sensitivity)
        fx *= (1 + fx_shock)
    
    debt_to_gdp = debt / gdp
    debt_to_gdp_results.append(debt_to_gdp)


# -----------------------------
# RESULTS
# -----------------------------

results = np.array(debt_to_gdp_results)

print("---- Sovereign Stress Results ----")
print("Mean Debt/GDP:", np.mean(results))
print("95% Worst Case:", np.percentile(results, 95))
print("5% Best Case:", np.percentile(results, 5))

# Plot distribution
plt.hist(results, bins=50)
plt.title("Monte Carlo Debt-to-GDP Distribution")
plt.xlabel("Debt-to-GDP Ratio")
plt.ylabel("Frequency")
plt.show()
