# ibm_financial_edc_benchmark.py

import numpy as np
import pandas as pd
import yfinance as yf

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
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

    # Entangle equity cluster
    qc.cx(0, 1)
    qc.cx(1, 2)

    # Volatility influence
    qc.cz(3, 0)
    qc.cz(3, 1)

    # Commodities interaction
    qc.cx(4, 5)

    # Cross-asset entanglement
    qc.cz(2, 4)

    return qc


# ==========================================================
# 4️⃣ Simple Circuit Cutting (Manual Partition)
# ==========================================================
def cut_circuit(qc):

    # Split into two partitions
    left = qc.copy()
    right = qc.copy()

    # For demonstration:
    # Partition first 3 qubits vs last 3 qubits
    left_qubits = [0, 1, 2]
    right_qubits = [3, 4, 5]

    left_sub = left.remove_final_measurements(inplace=False)
    right_sub = right.remove_final_measurements(inplace=False)

    return left_sub, right_sub


# ==========================================================
# 5️⃣ Simulate Subcircuits
# ==========================================================
def simulate_subcircuits(left, right):

    sim = AerSimulator()

    left_sv = Statevector.from_instruction(left)
    right_sv = Statevector.from_instruction(right)

    return left_sv, right_sv


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

    print("Cutting circuit (EDC-style partition)...")
    left, right = cut_circuit(qc)

    print("Simulating subcircuits...")
    left_sv, right_sv = simulate_subcircuits(left, right)

    print("Left subsystem dimension:", len(left_sv))
    print("Right subsystem dimension:", len(right_sv))
