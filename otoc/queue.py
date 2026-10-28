"""Run BlueQubit jobs by circuit id under a hackathon's in-flight cap.

    python -m otoc.queue TASKS RESULTS.jsonl [--slots 5]

TASKS has one job per line, in priority order, in this form.

    <circuit-prefix> <n_qubits> <qubit q> <device> <param> [level=3,wcut=12]

e.g. `Duke_G2 36 5 mps.cpu 128` measures <Z_5> on circuit Duke_G2_5 at bond dimension 128.
Each finished job appends one JSON line to RESULTS. A job already COMPLETED there with the same
settings is skipped, so a restart does not rerun finished work. A job still running when the
process stops is not recorded and runs again on restart.

The job's state is read from the SDK's structured run_status. A job bounced by the cap or a GPU
cooldown goes back to the front and is retried later. A refused job (FAILED_VALIDATION,
NOT_ENOUGH_FUNDS) is logged once and dropped, since the same request cannot succeed as sent.

The API token is read from BLUEQUBIT_API_TOKEN.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

BOUNCE = {"HACKATHON_PARALLEL_JOBS_LIMIT", "HACKATHON_GPU_QUOTA_COOLDOWN"}
REFUSED = {"FAILED_VALIDATION", "NOT_ENOUGH_FUNDS"}
RUNNING = {"PENDING", "QUEUED", "RUNNING", "NOT_STARTED", "TRANSPILING"}


def z_label(n: int, q: int) -> str:
    """Pauli label for Z on qubit q, Qiskit order (rightmost character is qubit 0)."""
    lab = ["I"] * n
    lab[n - 1 - q] = "Z"
    return "".join(lab)


def options(device: str, param: float, extra: dict) -> dict:
    if device.startswith("pauli-path"):
        opts = {"pauli_path_truncation_threshold": param,
                "pauli_path_circuit_transpilation_level": int(extra.get("level", 2))}
        if "wcut" in extra:
            opts["pauli_path_weight_cutoff"] = int(extra["wcut"])
        return opts
    return {"mps_bond_dimension": int(param)}


def parse_tasks(path: Path, done: set) -> list:
    tasks = []
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        prefix, n, q, device, param, *rest = line.split()
        extra = rest[0] if rest else ""
        key = (f"{prefix}_{q}", device, float(param), extra)
        if key not in done:
            tasks.append(key + (int(n), int(q)))
    return tasks


def completed(results: Path) -> set:
    done = set()
    if results.exists():
        for line in results.read_text().splitlines():
            d = json.loads(line)
            if d.get("run_status") == "COMPLETED":
                done.add((d["cid"], d["device"], float(d["param"]), d.get("extra", "")))
    return done


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tasks", type=Path)
    ap.add_argument("results", type=Path)
    ap.add_argument("--slots", type=int, default=5, help="jobs in flight (the hackathon allowed 5)")
    a = ap.parse_args()

    import bluequbit

    client = bluequbit.init(os.environ["BLUEQUBIT_API_TOKEN"])
    tasks = parse_tasks(a.tasks, completed(a.results))
    print(f"{len(tasks)} jobs to run, {a.slots} slots", flush=True)
    inflight: dict = {}
    with a.results.open("a") as out:

        def record(t, **fields) -> None:
            cid, device, param, extra = t[:4]
            out.write(json.dumps({"cid": cid, "device": device, "param": param, "extra": extra,
                                  "ts": time.time(), **fields}, default=str) + "\n")
            out.flush()

        while tasks or inflight:
            while tasks and len(inflight) < a.slots:
                t = tasks[0]
                cid, device, param, extra, n, q = t
                kv = dict(x.split("=") for x in extra.split(",") if x)
                try:
                    job = client.run(cid, device=device, pauli_sum=[(z_label(n, q), 1.0)],
                                     options=options(device, param, kv), job_name=cid, asynchronous=True)
                    inflight[job.job_id] = tasks.pop(0)
                except Exception as e:
                    status = getattr(e, "run_status", None)
                    if status in BOUNCE:
                        break                       # wait for a slot, then try the same job again
                    tasks.pop(0)
                    record(t, run_status=status or "SUBMIT_ERROR", error_message=str(e)[:300])
                    print("refused", cid, device, param, extra, status, flush=True)
            time.sleep(4)
            for job_id in list(inflight):
                try:
                    r = client.get(job_id)
                except Exception as e:
                    print("status check failed", job_id, str(e)[:120], flush=True)
                    continue
                if r.run_status in RUNNING:
                    continue
                t = inflight.pop(job_id)
                if r.run_status in BOUNCE:
                    tasks.insert(0, t)
                    continue
                record(t, job_id=job_id, run_status=r.run_status, expectation_value=r.expectation_value,
                       cost=getattr(r, "cost", None), run_time_ms=getattr(r, "run_time_ms", None),
                       error_message=getattr(r, "error_message", None))
                print(t[0], t[1], t[2], t[3], r.run_status, r.expectation_value, flush=True)
    print("queue empty", flush=True)


if __name__ == "__main__":
    main()
