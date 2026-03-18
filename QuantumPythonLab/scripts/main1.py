import numpy as np
import pandas as pd
import yfinance as yf
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


# ==========================================
# 1️⃣ Robust Market Data Loader
# ==========================================
def get_prices(tickers, period="3mo"):
    data = yf.download(
        tickers,
        period=period,
        auto_adjust=True,
        progress=False
    )

    # Handle MultiIndex (new yfinance behavior)
    if isinstance(data.columns, pd.MultiIndex):
        prices = data["Close"]
    else:
        prices = data

    return prices.dropna()


# ==========================================
# 2️⃣ Normalize Latest Market State
# ==========================================
def encode_market_state(returns):
    latest = returns.iloc[-1]
    norm = (latest - latest.mean()) / latest.std()
    return norm.fillna(0)


# ==========================================
# 3️⃣ Build Financial Entanglement Circuit
# ==========================================
def build_circuit(encoded_vector):
    n = len(encoded_vector)
    qc = QuantumCircuit(n)

    # Encode values into qubit rotations
    for i, val in enumerate(encoded_vector):
        qc.ry(float(val), i)

    # Basic macro entanglement structure
    if n >= 2:
        qc.cx(0, 1)
    if n >= 3:
        qc.cx(0, 2)
    if n >= 4:
        qc.cz(1, 3)

    qc.save_statevector()
    return qc


# ==========================================
# 4️⃣ Execute Locally (Aer Simulator)
# ==========================================
def run_local_simulation(qc):
    sim = AerSimulator()
    result = sim.run(qc).result()
    return result.get_statevector()


# ==========================================
# 5️⃣ Classical Benchmark
# ==========================================
def compute_classical_correlation(returns):
    return returns.corr()


# ==========================================
# 🚀 MAIN PIPELINE
# ==========================================
if __name__ == "__main__":

    tickers = ["^GSPC", "^IXIC", "^FTSE", "^VIX"]

    print("\nDownloading market data...")
    prices = get_prices(tickers)

    returns = prices.pct_change().dropna()

    print("Encoding market state...")
    encoded = encode_market_state(returns)

    print("Building quantum circuit...")
    qc = build_circuit(encoded)

    print("Running local quantum simulation...")
    statevector = run_local_simulation(qc)

    print("\nQuantum Statevector:")
    print(statevector)

    print("\nClassical Correlation Matrix:")
    print(compute_classical_correlation(returns))
