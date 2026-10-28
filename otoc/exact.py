"""Exact reference values for the open sample circuits, on a laptop.

    python -m otoc.exact SAMPLE_DIR Duke_S2 16 > Duke_S2_exact.csv

For circuit `<prefix>_q` the score is <Z_q> at the end of the circuit. Up to about 26 qubits
this is a plain statevector; at 30 qubits (S3) it needs about 8 GB in single precision and
43 minutes per circuit on our 8-core machine, which is why the cloud methods exist.
"""
from __future__ import annotations

import sys

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


def z_expectation(path: str, q: int) -> float:
    qc = QuantumCircuit.from_qasm_file(path)
    p = np.abs(Statevector(qc).data) ** 2
    bit = (np.arange(len(p)) >> q) & 1          # in Qiskit order qubit 0 is the lowest bit
    return float(np.sum(p * (1 - 2 * bit)))


def main() -> None:
    folder, prefix, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
    print("circuit_id,value")
    for q in range(n):
        print(f"{prefix}_{q},{z_expectation(f'{folder}/{prefix}_{q}.qasm', q):.6f}", flush=True)


if __name__ == "__main__":
    main()
