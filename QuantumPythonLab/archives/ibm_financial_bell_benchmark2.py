# ibm_financial_bell_benchmark.py

import numpy as np
import pandas as pd
import yfinance as yf

from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler


# ==========================================================
# 1️⃣ Download Financial Returns (MultiIndex Safe)
# ==========================================================
def get_financial_returns():

    tickers = ["^GSPC", "^IXIC"]

    data = yf.download(
        tickers,
        period="3mo",
        auto_adjust=True,
        progress=False
    )

    # Handle MultiIndex columns (new yfinance behavior)
    if isinstance(data.columns, pd.MultiIndex):
        prices = data["Close"]
    else:
        prices = data

    returns = prices.pct_change().dropna()

    return returns


# ==========================================================
# 2️⃣ Encode Financial State → NumPy Array
# ==========================================================
def encode_financial_state(returns):

    latest = returns.iloc[-1]

    norm = (latest - latest.mean()) / latest.std()

    # Convert to pure NumPy array for quantum layer
    return norm.fillna(0).to_numpy()


# ==========================================================
# 3️⃣ Build Financial Bell Circuit
# ==========================================================
def build_financial_bell(encoded_vals):

    qc = QuantumCircuit(2)

    qc.ry(float(encoded_vals[0]), 0)
    qc.ry(float(encoded_vals[1]), 1)

    qc.cx(0, 1)

    qc.measure_all()

    return qc


# ==========================================================
# 4️⃣ Run on IBM Hardware (Runtime V2 Safe)
# ==========================================================
def run_on_ibm(qc):

    service = QiskitRuntimeService(instance="open-instance")

    backend = service.least_busy(simulator=False)
    print("Using backend:", backend)

    qc_t = transpile(
        qc,
        target=backend.target,   # CRITICAL FIX
        optimization_level=1
    )

    sampler = Sampler(mode=backend)

    job = sampler.run([qc_t])
    print("Job ID:", job.job_id())

    result = job.result()

    counts = result[0].data.meas.get_counts()

    return counts


# ==========================================================
# 5️⃣ Analyze Bell Fidelity
# ==========================================================
def analyze_results(counts):

    total = sum(counts.values())

    p00 = counts.get("00", 0) / total
    p11 = counts.get("11", 0) / total

    fidelity = p00 + p11

    print("\nMeasurement Counts:", counts)
    print("Bell Fidelity:", round(fidelity, 4))


# ==========================================================
# 🚀 MAIN
# ==========================================================
if __name__ == "__main__":

    print("Downloading financial data...")
    returns = get_financial_returns()

    print("Encoding financial state...")
    encoded = encode_financial_state(returns)

    print("Building financial Bell circuit...")
    qc = build_financial_bell(encoded)

    print("Running on IBM hardware...")
    counts = run_on_ibm(qc)

    analyze_results(counts)
