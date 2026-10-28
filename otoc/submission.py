"""Build a `circuit_id,value` submission CSV from a queue results file.

    python -m otoc.submission RESULTS.jsonl Duke_G2 36 mps.cpu 128 > Duke_G2.csv
    python -m otoc.submission RESULTS.jsonl Duke_G2 36 mps.cpu best > Duke_G2.csv

With a numeric setting, every circuit must have a COMPLETED value at exactly that setting.
With `best`, each circuit takes its value at the largest bond dimension (MPS) or the smallest
threshold (Pauli path) that completed. A missing circuit is an error, never a silent 0.0,
because a placeholder zero looks like an answer and drags the correlation down.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    results, prefix, n, device, setting = sys.argv[1:6]
    extra = sys.argv[6] if len(sys.argv) > 6 else ""
    n = int(n)
    finer = (lambda a, b: a > b) if device.startswith("mps") else (lambda a, b: a < b)
    best: dict = {}
    for line in Path(results).read_text().splitlines():
        d = json.loads(line)
        if (d.get("run_status") != "COMPLETED" or d["device"] != device or d.get("extra", "") != extra
                or not d["cid"].startswith(prefix + "_")):
            continue
        q, p = int(d["cid"].rsplit("_", 1)[1]), float(d["param"])
        if setting != "best" and p != float(setting):
            continue
        if q not in best or finer(p, best[q][0]):
            best[q] = (p, float(d["expectation_value"]))
    missing = [q for q in range(n) if q not in best]
    if missing:
        sys.exit(f"{prefix}: no value for qubits {missing}")
    print("circuit_id,value")
    for q in range(n):
        print(f"{prefix}_{q},{best[q][1]:.6f}")


if __name__ == "__main__":
    main()
