# ibm_financial_bell_benchmark3.py

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


# ==========================================================
# 1️⃣ Download Multi-Asset Data
# ==========================================================
def get_financial_returns():

    tickers = [
        "^GSPC",   # S&P 500
        "^IXIC",   # Nasdaq
        "^FTSE",   # FTSE 100
        "^VIX",    # VIX
        "BZ=F",    # Brent Oil
        "GC=F"     # Gold
    ]

    data = yf.download(
        tickers,
        period="3mo",
        auto_adjust=True,
        progress=False
    )

    if isinstance(data.columns, pd.MultiIndex):
        prices = data["Close"]
    else:
        prices = data

    returns = prices.pct_change().dropna()

    return returns


# ==========================================================
# 2️⃣ Encode Market State
# ==========================================================
def encode_market_state(returns):

    latest = returns.iloc[-1]
    norm = (latest - latest.mean()) / latest.std()

    return norm.fillna(0).to_numpy()


# ==========================================================
# 3️⃣ Build Large Financial Circuit
# ==========================================================
def build_large_circuit(encoded_vals):

    n = len(encoded_vals)
    qc = QuantumCircuit(n)

    # Encode macro rotations
    for i, val in enumerate(encoded_vals):
        qc.ry(float(val), i)

    # Entanglement structure
    qc.cx(0, 1)
    qc.cx(1, 2)

    qc.cz(3, 0)
    qc.cz(3, 1)

    qc.cx(4, 5)
    qc.cz(2, 4)

    return qc


# ==========================================================
# 4️⃣ Simulate Circuit
# ==========================================================
def simulate_circuit(qc):

    state = Statevector.from_instruction(qc)
    return state


# ==========================================================
# 🚀 MAIN
# ==========================================================
if __name__ == "__main__":

    print("Downloading multi-asset data...")
    returns = get_financial_returns()

    print("Encoding macro state...")
    encoded = encode_market_state(returns)

    print("Building large entangled circuit...")
    qc = build_large_circuit(encoded)

    print("Simulating circuit...")
    state = simulate_circuit(qc)

    print("Hilbert space dimension:", len(state))

    # ======================================================
    # Draw Circuit (Text)
    # ======================================================
    print("\nText Diagram:\n")
    print(qc.draw("text"))

    # ======================================================
    # Draw Circuit (Matplotlib)
    # ======================================================
    print("\nOpening graphical circuit window...")
    qc.draw("mpl")
    plt.show()

    # ======================================================
    # Save Circuit as PNG
    # ======================================================
    qc.draw("mpl", filename="financial_large_circuit.png")
    print("Circuit saved as financial_large_circuit.png")
