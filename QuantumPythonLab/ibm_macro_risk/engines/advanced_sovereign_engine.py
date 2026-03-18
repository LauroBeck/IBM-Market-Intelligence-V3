import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# -----------------------------
# INITIAL CONDITIONS
# -----------------------------

initial_debt = 4.4e12
initial_gdp = 120e12
initial_fx = 6.88
years = 5
simulations = 10000

# Scenario selection
scenario = "soft"  # change to "hard"

# -----------------------------
# SCENARIO PARAMETERS
# -----------------------------

if scenario == "soft":
    mean_gdp = 0.05
    mean_rate = 0.03
    commodity_factor = 0.01
    semicon_factor = 0.01
elif scenario == "hard":
    mean_gdp = 0.01
    mean_rate = 0.06
    commodity_factor = -0.02
    semicon_factor = -0.03

vol_gdp = 0.02
vol_rate = 0.015
vol_fx = 0.03

# -----------------------------
# CORRELATION MATRIX
# GDP, RATE, FX
# -----------------------------

corr_matrix = np.array([
    [1.0, -0.4, -0.3],
    [-0.4, 1.0, 0.5],
    [-0.3, 0.5, 1.0]
])

chol_matrix = np.linalg.cholesky(corr_matrix)

# -----------------------------
# MONTE CARLO
# -----------------------------

debt_gdp_results = []
cds_spreads = []
default_probs = []

for _ in range(simulations):

    debt = initial_debt
    gdp = initial_gdp
    fx = initial_fx
    capital_pressure = 0

    for _ in range(years):

        # Generate correlated shocks
        random_vector = np.random.normal(size=3)
        correlated_shocks = chol_matrix @ random_vector

        gdp_shock = mean_gdp + vol_gdp * correlated_shocks[0]
        rate_shock = mean_rate + vol_rate * correlated_shocks[1]
        fx_shock = vol_fx * correlated_shocks[2]

        # Add commodity & semiconductor influence
        gdp_shock += commodity_factor + semicon_factor

        # Update macro variables
        gdp *= (1 + gdp_shock)
        debt *= (1 + rate_shock)
        fx *= (1 + fx_shock)

        # Capital flow pressure (FX + rate sensitivity)
        capital_pressure += abs(fx_shock) + rate_shock

    debt_gdp = debt / gdp
    debt_gdp_results.append(debt_gdp)

    # CDS spread approximation (simple risk proxy)
    cds = 100 * debt_gdp + 50 * capital_pressure
    cds_spreads.append(cds)

    # Default probability using logistic model
    pd = 1 / (1 + np.exp(-5 * (debt_gdp - 1)))
    default_probs.append(pd)

# -----------------------------
# RESULTS
# -----------------------------

print("Scenario:", scenario.upper())
print("Mean Debt/GDP:", np.mean(debt_gdp_results))
print("95% Worst Case Debt/GDP:", np.percentile(debt_gdp_results, 95))
print("Mean CDS Spread (bps):", np.mean(cds_spreads))
print("Mean Default Probability:", np.mean(default_probs))

# Plot distribution
plt.hist(debt_gdp_results, bins=50)
plt.title(f"Debt/GDP Distribution ({scenario} landing)")
plt.xlabel("Debt-to-GDP")
plt.ylabel("Frequency")
plt.show()
