# Receipts

Where each number in the README comes from. Scores are the leaderboard's own, read from the
submission page after each upload (October 24 and 25, 2026).

## Placement

41st of 65 on the leaderboard after the event, 1100/3000, last submission 25 October 2026 6:15 AM, as shown in our screenshots of [our row](leaderboard_our_row.png) (sha256 634834ccddc8e4b4...) and of [the last row, 65](leaderboard_last_row_name_blurred.png) (sha256 88027a9f7140d8bb...), taken by us after the event. In the second, only that participant's avatar letter and name are blurred; the rank, score, hours, submission count and date are untouched. We could not find a public copy of the leaderboard, so these screenshots are our receipt for the placement.

## Scores, in submission order

| Problem | Attempts and scores |
|---|---|
| S1 | 100 |
| S2 | 100 |
| S3 | 100 |
| G1 | 157 (bond dimension 64), 235 (ladder to 1024 on 4 circuits), 235 (ladder to 1024 on 12) |
| G2 | 426 (bond dimension 64), 545 (mostly 128 and 256), 564 (14 circuits at 1024) |
| G3 | 0 (Pauli path, threshold 1e-4, 27 of 36 values exactly 0) |
| G4 | 0 (MPS 64 and 128), 0 (MPS extrapolated in 1/chi), 1 (the same values sign-flipped) |

## Ladders at submission (final G1 and G2 files)

Each circuit's value is the one from the largest bond dimension that completed. A ladder stopped
when its value stopped moving or when the platform refused the next rung (bond dimension 2048
was refused as over its runtime limit).

| Problem | Circuits per top rung | Converged (two rungs agree within tolerance) |
|---|---|---|
| G1 | 1024 x 12, 512 x 3, 256 x 8, 128 x 7 | 12 of 30 |
| G2 | 1024 x 14, 512 x 8, 256 x 14 | 8 of 36 |

## Pauli path thresholds on G3

On the CPU device 1e-4 ran and 7e-5, 5e-5, 3e-5 and 1e-5 were refused as too small for the
circuit. On the GPU device, with transpilation level 3, 2e-5 was tried on 32 circuits before we stopped
the run. 19 were refused and 13 ran, and 11 of those 13 returned exactly 0. 1e-5 was refused.

## The Clifford grid sample under MPS

S3 qubit 1, whose Pauli path value is -0.538 (S3 scored 100 with these values), run locally with
Qiskit Aer MPS on an 8-core machine. Exact statevector for S3 qubit 0 is 0.144130 (43 minutes).

| Bond dimension | <Z_1> | Time |
|---|---|---|
| 64 | -0.00000 | 68 s |
| 128 | +0.00011 | 552 s |
| 256 | +0.00657 | 3929 s |
| 512 | +0.00016 | 30564 s |

Each U in S3 contains 71 single-qubit gates that are not Clifford, and the circuit applies U
four times. The count for G3 is unknown, since the graded circuits are hidden.

## The front fits

`python -m otoc.front FILE BUTTERFLY LAYERS` on the files in this folder.

| File | Butterfly | Layers | v (sites per layer) | corr^2 |
|---|---|---|---|---|
| Duke_S2_exact.csv | 0 | 12 | 0.85 | 0.963 |
| Duke_G1_final.csv | 0 | 32 | 0.60 | 0.977 |
| Duke_G2_final.csv | 18 | 18 | 0.75 | 0.956 |
