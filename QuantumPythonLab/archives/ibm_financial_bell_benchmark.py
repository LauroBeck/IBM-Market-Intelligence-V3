import numpy as np
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit_aer import AerSimulator


# ==========================================================
# 1️⃣ Create Bell Stabilizer Circuit (EDC-style)
# ==========================================================
def create_bell_stab(initial_layouts):
    bell_circuits = []

    for initial_layout in initial_layouts:
        assert len(initial_layout) % 4 == 0
        num_pairs = len(initial_layout) // 4

        qc = QuantumCircuit(4 * num_pairs, 4 * num_pairs)

        for pair_idx in range(num_pairs):
            q0, q1, q2, q3 = pair_idx*4, pair_idx*4+1, pair_idx*4+2, pair_idx*4+3
            ca0, ca1 = pair_idx*4+1, pair_idx*4+2

            qc.h(q0)
            qc.h(q1)
            qc.cx(q1, q2)
            qc.cx(q0, q1)
            qc.cx(q2, q3)
            qc.h(q2)

        qc.barrier()

        # Middle measurements
        for pair_idx in range(num_pairs):
            q1, q2 = pair_idx*4+1, pair_idx*4+2
            qc.measure(q1, q1)
            qc.measure(q2, q2)

        # Conditional corrections
        for pair_idx in range(num_pairs):
            q0, q3 = pair_idx*4, pair_idx*4+3
            ca0, ca1 = pair_idx*4+1, pair_idx*4+2

            with qc.if_test((ca0, 1)):
                qc.x(q3)
            with qc.if_test((ca1, 1)):
                qc.z(q0)
                qc.id(q0)

        bell_zz = qc.copy()
        bell_xx = qc.copy()

        bell_zz.barrier()
        bell_xx.barrier()

        # XX basis rotation
        for pair_idx in range(num_pairs):
            q0, q3 = pair_idx*4, pair_idx*4+3
            bell_xx.h(q0)
            bell_xx.h(q3)

        bell_xx.barrier()

        # Final edge measurements
        for pair_idx in range(num_pairs):
            q0, q3 = pair_idx*4, pair_idx*4+3
            bell_zz.measure(q0, q0)
            bell_zz.measure(q3, q3)

            bell_xx.measure(q0, q0)
            bell_xx.measure(q3, q3)

        bell_circuits.append(bell_zz)
        bell_circuits.append(bell_xx)

    return bell_circuits


# ==========================================================
# 2️⃣ Execute on IBM Runtime
# ==========================================================
def run_on_ibm(circuits, backend_name="ibm_fez", shots=4000):
    service = QiskitRuntimeService()
    backend = service.backend(backend_name)

    pass_manager = generate_preset_pass_manager(
        backend=backend,
        optimization_level=1
    )

    transpiled = pass_manager.run(circuits)

    sampler = SamplerV2(backend)
    job = sampler.run(transpiled, shots=shots)
    result = job.result()

    return result


# ==========================================================
# 3️⃣ Local Simulator Fallback
# ==========================================================
def run_local(circuits, shots=4000):
    sim = AerSimulator()
    transpiled = transpile(circuits, sim)
    job = sim.run(transpiled, shots=shots)
    return job.result()


# ==========================================================
# 4️⃣ Compute Financial MSE vs Target Correlation
# ==========================================================
def compute_mse(result, initial_layouts, target_corr=1.0):
    layout_mse = {}

    for layout_idx, initial_layout in enumerate(initial_layouts):
        layout_mse[tuple(initial_layout)] = {}
        num_pairs = len(initial_layout) // 4

        counts_zz = result[2*layout_idx].data.c.get_counts()
        counts_xx = result[2*layout_idx+1].data.c.get_counts()

        total_zz = sum(counts_zz.values())
        total_xx = sum(counts_xx.values())

        for pair_idx in range(num_pairs):
            exp_zz = 0
            exp_xx = 0

            for bitstr, shots in counts_zz.items():
                bitstr = bitstr[::-1]
                b1, b0 = bitstr[pair_idx*4], bitstr[pair_idx*4+3]
                z0 = 1 if b0 == "0" else -1
                z1 = 1 if b1 == "0" else -1
                exp_zz += z0 * z1 * shots
            exp_zz /= total_zz

            for bitstr, shots in counts_xx.items():
                bitstr = bitstr[::-1]
                b1, b0 = bitstr[pair_idx*4], bitstr[pair_idx*4+3]
                x0 = 1 if b0 == "0" else -1
                x1 = 1 if b1 == "0" else -1
                exp_xx += x0 * x1 * shots
            exp_xx /= total_xx

            mse = ((exp_zz - target_corr)**2 +
                   (exp_xx - target_corr)**2) / 2

            layout_mse[tuple(initial_layout)][
                tuple(initial_layout[pair_idx*4:pair_idx*4+4])
            ] = mse

            print(f"Layout {initial_layout[pair_idx*4:pair_idx*4+4]}")
            print(f"  ⟨ZZ⟩={round(exp_zz,4)} ⟨XX⟩={round(exp_xx,4)}")
            print(f"  Financial MSE={round(mse,6)}\n")

    return layout_mse


# ==========================================================
# 5️⃣ Main Execution
# ==========================================================
if __name__ == "__main__":

    # Example financial correlation target (SP500-Nasdaq ≈ 0.94)
    target_corr = 0.94

    initial_layouts = [
        [0,1,2,3],
        [4,5,6,7]
    ]

    circuits = create_bell_stab(initial_layouts)

    # Choose execution mode
    USE_IBM = True

    if USE_IBM:
        result = run_on_ibm(circuits, backend_name="ibm_oslo")
    else:
        result = run_local(circuits)

    compute_mse(result, initial_layouts, target_corr=target_corr)
