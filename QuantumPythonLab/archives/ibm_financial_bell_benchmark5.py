# ibm_financial_bell_benchmark3.py

import numpy as np
import pandas as pd
import yfinance as yf

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
# 3️⃣ Build Large Financial Circuit (6 Qubits)
# ==========================================================
def build_large_circuit(encoded_vals):

    n = len(encoded_vals)
    qc = QuantumCircuit(n)

    # Rotation encoding
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
# 4️⃣ Simulate Statevector
# ==========================================================
def simulate_circuit(qc):

    state = Statevector.from_instruction(qc)
    return state


# ==========================================================
# 5️⃣ Safe Circuit Drawing (No Crash)
# ==========================================================
def draw_circuit_safe(qc):

    print("\nText Circuit Diagram:\n")
    print(qc.draw("text"))

    # Try to save matplotlib image safely
    try:
        fig = qc.draw(output="mpl")
        fig.savefig("financial_large_circuit.png")
        print("\nCircuit saved as financial_large_circuit.png")
    except Exception as e:
        print("\nMatplotlib drawing skipped (environment issue).")
        print("Reason:", e)


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
    print("Number of qubits:", qc.num_qubits)

    draw_circuit_safe(qc)
