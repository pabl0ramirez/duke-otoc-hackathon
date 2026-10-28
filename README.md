# Duke Quantum Echoes hackathon, October 2026

We estimated out-of-time-order correlators, the quantity behind Google's Quantum Echoes
experiment, at the 24-hour BlueQubit x DuQuantum hackathon hosted at Duke University (October 24
and 25, 2026). There were seven circuits of 4 to 38 qubits. Every circuit has the same echo
shape. A random unitary U runs, a butterfly qubit is flipped, U is undone, qubit q is probed,
and the echo runs again. The answer for circuit `<problem>_q` is <Z_q> at the end. Each problem
is scored as corr^2 between our values and the organizers' exact ones, so the pattern across
qubits matters more than any single value.

The graded circuits were hidden and could only be run by id on BlueQubit's cloud simulators
(MPS and Pauli path, each on CPU or GPU). The three sample circuits were open.

## Results

| Problem | Circuit | Score | How |
|---|---|---|---|
| S1 | 4 qubits | 100 / 100 | exact statevector |
| S2 | 16-qubit chain, butterfly 0 | 100 / 100 | exact statevector |
| S3 | 30-qubit grid, Clifford + Rz | 100 / 100 | Pauli path, threshold 1e-4 |
| G1 | 30-qubit chain, butterfly 0, 32 layers | 235 / 300 | MPS, bond dimension up to 1024 |
| G2 | 36-qubit chain, butterfly 18, 18 layers | 564 / 600 | MPS, bond dimension up to 1024 |
| G3 | 36-qubit grid, Clifford + Rz, 24 layers | 0 / 800 | unsolved |
| G4 | 38-qubit grid, Haar random, 16 layers | 1 / 1000 | unsolved |

Samples 300 of 300. Graded 800 of 2700. Total 1100 of 3000. Every attempt and the source of
each number below is in [results/RECEIPTS.md](results/RECEIPTS.md).

## What worked

**Checking methods on known answers.** The samples can be computed exactly (`otoc/exact.py`),
so we checked the cloud methods against exact sample values before relying on them for graded
circuits. Pauli path matched on the 16-layer Clifford grid sample (S3 scored 100) and MPS on
the 16-qubit chain.

**Ladders of bond dimension.** Each chain circuit ran at increasing bond dimension (64, 128,
256, 512, 1024), and we submitted the value from the largest one that completed. G2 went 426,
then 545, then 564 as the ladder climbed, and G1 went 157, then 235. The platform refused bond
dimension 2048 as over its runtime limit. At submission 12 of 30 G1 circuits and 8 of 36 G2
circuits had converged, and the G2 score was still rising at the top rung, so more bond
dimension would likely have helped. As bond dimension rose, values on the slopes fell. Our
reading is that low bond dimension under-spreads the butterfly's effect.

**The geometry sets the shape.** A perturbation spreads from the butterfly at a finite speed.
Qubits it has not reached stay at 1, and qubits it has reached fall toward 0. A two-parameter
front (`otoc/front.py`) fitted to the exact S2 answers matches them at corr^2 0.963, and fitted
to our final G1 and G2 values matches them at 0.977 and 0.956. The fitted speed differs by
circuit (0.85, 0.60 and 0.75 sites per layer), so it has to be fitted for each circuit.

**Engineering for the platform.** The hackathon allowed five jobs in flight and refused some
requests outright (thresholds too small for a circuit, runtimes over its limit, a balance too
low). `otoc/queue.py` keeps the slots full, resubmits a job the cap bounced, drops a request the
server refused as sent, and skips any job that already completed, so it can be stopped and
restarted.

## What did not work

**G3 (36-qubit Clifford grid, 24 layers).** Pauli path returned exactly 0 for most qubits at
every threshold the platform accepted. On CPU 1e-4 ran and anything finer was refused. On GPU
2e-5 was refused on 19 of the 32 circuits we tried, and 11 of the 13 that ran returned exactly 0. Our reading is
that each non-Clifford rotation scales the main Clifford path by a factor below one, so a deep
enough circuit pushes it under the cutoff and it is dropped. Each U in the 16-layer sample has 71
non-Clifford gates, applied four times; G3 is deeper and its count is hidden. MPS did not help
on this family. On the 30-qubit sample, MPS at bond dimension 512 gave 0.0002 where the answer
is -0.538.

**G4 (38-qubit Haar grid).** MPS at the bond dimensions we ran (64 to 512) produced a strong
distance pattern that carried no signal. It scored 0 as is, 0 extrapolated in 1/chi, and 1
sign-flipped.

**What we would do differently.** After the event, [another participant's public
write-up](https://lnkd.in/ejPfFhY5) showed the move we missed on G4. Use the geometry to split
the qubits. Predict 0 for the interior, treated as fully scrambled, and spend Pauli path at a
fine threshold only on the edge qubits, with a correction per qubit type fitted against exact
sample answers. We had both pieces, the front fit and the calibration, and used the front only
as a check. We also probed G4 with Pauli path on two qubits, saw zeros, and stopped. Two qubits
was too small a probe to rule it out.

## Reproduce

    pip install -r requirements.txt
    python -m otoc.exact SAMPLE_DIR Duke_S2 16 > s2_exact.csv
    python -m otoc.front results/Duke_S2_exact.csv 0 12     # v=0.85, corr^2 0.963
    python -m otoc.front results/Duke_G2_final.csv 18 18    # v=0.75, corr^2 0.956
    read -rs BLUEQUBIT_API_TOKEN && export BLUEQUBIT_API_TOKEN
    python -m otoc.queue tasks.txt results.jsonl
    python -m otoc.submission results.jsonl Duke_G2 36 mps.cpu best > Duke_G2.csv

`read -rs` keeps the token out of shell history. The sample and graded circuits belong to the
organizers and are not included. `results/` holds our final submitted values for G1 and G2, the
exact S2 answers and the S3 Pauli path values.

## Credits

Thanks to the organizers at BlueQubit and DuQuantum for a hard, well-built challenge, and for
the benchmark paper they shared during the event, "Benchmarking Zero-Setup Quantum Circuit
Simulators" (arXiv 2607.09882).

Matrix CR Studio, Costa Rica. Copyright 2026 Pablo Ramirez. All rights reserved.
