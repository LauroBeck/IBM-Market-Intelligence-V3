import numpy as np
import yfinance as yf
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector

# -------------------------
# STEP 1 — Load Market Data
# -------------------------
tickers = ["^GSPC", "^IXIC", "^FTSE", "^VIX"]
data = yf.download(tickers, period="3mo")["Adj Close"]
returns = data.pct_change().dropna()
latest = returns.iloc[-1]

# -------------------------
# STEP 2 — Normalize
# -------------------------
norm = (latest - latest.mean()) / latest.std()

# -------------------------
# STEP 3 — Build Circuit
# -------------------------
qc = QuantumCircuit(4)

for i, val in enumerate(norm):
    qc.ry(float(val), i)

qc.cx(0, 1)
qc.cx(0, 2)
qc.cz(1, 3)

# -------------------------
# STEP 4/5 — Local Execution
# -------------------------
sim = AerSimulator()
qc.save_statevector()
result = sim.run(qc).result()
state = result.get_statevector()

# -------------------------
# STEP 6 — Classical Benchmark
# -------------------------
corr = returns.corr()

print("\nQuantum Statevector:")
print(state)

print("\nClassical Correlation Matrix:")
print(corr)
