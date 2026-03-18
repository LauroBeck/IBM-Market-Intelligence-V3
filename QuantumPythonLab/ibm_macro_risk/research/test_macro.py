import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Simulated GDP growth & bond issuance
years = np.arange(2015, 2025)
gdp_growth = np.array([6.5, 6.7, 6.2, 5.9, 5.5, 2.3, 3.1, 4.8, 5.0, 5.2])
bond_issuance = np.array([2.1, 2.3, 2.5, 2.8, 3.0, 3.5, 3.8, 4.0, 4.2, 4.4])

df = pd.DataFrame({
    "Year": years,
    "GDP_Growth": gdp_growth,
    "Bond_Issuance_Trillion": bond_issuance
})

# Regression: Does bond issuance respond to GDP?
X = df[["GDP_Growth"]]
y = df["Bond_Issuance_Trillion"]

model = LinearRegression()
model.fit(X, y)

print("Regression Coefficient:", model.coef_[0])
print("Intercept:", model.intercept_)

# Plot
plt.scatter(gdp_growth, bond_issuance)
plt.plot(gdp_growth, model.predict(X))
plt.xlabel("GDP Growth (%)")
plt.ylabel("Bond Issuance (Trillion)")
plt.title("GDP vs Sovereign Bond Issuance")
plt.show()
