"""How much of the answer is set by distance from the butterfly qubit?

    python -m otoc.front VALUES.csv BUTTERFLY LAYERS

A perturbation on the butterfly qubit spreads at a finite speed. Qubits it has not reached
keep <Z> = 1; qubits it has reached scramble toward 0. On a 1D chain a front at distance v*t
gives the shape

    value(d) = 1 / (1 + exp(-(d - v * layers) / w))

This fits v and w to a set of values and reports corr^2, the hackathon's score. The fits we measured are below.

    S2 exact answers (16-qubit chain, 12 layers)   v = 0.85   corr^2 0.963
    G2 final MPS values (36 qubits, 18 layers)      v = 0.75   corr^2 0.956
    G1 final MPS values (30 qubits, 32 layers)      v = 0.60   corr^2 0.977

The shape fits all three chains we tried, but the speed differs from circuit to circuit, so v has to be
fitted, not assumed. Use the fit to check simulated values, or to decide which qubits deserve
compute (the ones on the front), not as the answer by itself.
"""
from __future__ import annotations

import csv
import sys

import numpy as np


def main() -> None:
    path, butterfly, layers = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    rows = list(csv.DictReader(open(path)))
    q = np.array([int(r["circuit_id"].rsplit("_", 1)[1]) for r in rows])
    y = np.array([float(r["value"]) for r in rows])
    d = np.abs(q - butterfly)
    best = (-1.0, 0.0, 0.0)
    for v in np.arange(0.3, 1.21, 0.05):
        for w in (0.5, 1.0, 1.5, 2.0):
            shape = 1 / (1 + np.exp(-(d - v * layers) / w))
            if np.std(shape) == 0:
                continue
            r = np.corrcoef(shape, y)[0, 1]
            if r > best[0]:
                best = (r, v, w)
    r, v, w = best
    print(f"best front: v={v:.2f} sites/layer, width={w}, corr^2={max(r, 0) ** 2:.3f}")


if __name__ == "__main__":
    main()
