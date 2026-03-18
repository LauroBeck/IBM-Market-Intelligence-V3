import numpy as np
import matplotlib.pyplot as plt

# Example Chinese-style yield curve (approximation)
maturities = np.array([1, 2, 5, 10, 20, 30])
yields = np.array([2.1, 2.3, 2.6, 2.8, 3.1, 3.3])

# Fit polynomial curve
coefficients = np.polyfit(maturities, yields, 3)
curve = np.poly1d(coefficients)

x = np.linspace(1, 30, 100)

plt.scatter(maturities, yields)
plt.plot(x, curve(x))
plt.title("Sovereign Yield Curve Fit")
plt.xlabel("Maturity (Years)")
plt.ylabel("Yield (%)")
plt.show()
