# Bliss 'Em All - parallel contextual scoring checkpoint

**Date:** 2026-07-20
**State:** Read-only native contextual scoring implemented; no route mutation, playlist write, or server deployment

## Published revisions

| Repository | Revision | Result |
| --- | --- | --- |
| [`chrober/bliss-mixer-core`](https://github.com/chrober/bliss-mixer-core) | `3297d83213c831daef84dc93aa9f2c8ec866f457` | Deterministic Rayon batch for contextual adaptive transitions; 12 tests and CI passed |
| [`chrober/bliss-playlist-optimizer`](https://github.com/chrober/bliss-playlist-optimizer) | `1f9c0ff1e7a51380bfa373ea35b142df8f3d2f25` | Versioned `score --request` artifact, synthetic snapshot, and Python parity; CI passed |
| [`chrober/bliss-playlist-optimizer`](https://github.com/chrober/bliss-playlist-optimizer) | `37d0bd571d6f18eb7f5341d6ba3df97a5f8e0661` | Resource-aware Rayon configuration: one logical CPU reserved for Lyrion unless explicitly overridden; CI passed |

The optimizer pins the full core revision. No consumer follows a moving branch.

## Parallelization audit and policy

The existing `bliss-mixer` already uses Rayon for independent forest and
candidate operations and configures its global pool to leave one CPU unused.
The shared core's single-transition matrix selection, short 23-value mean, and
one Mahalanobis calculation are too small and interdependent to parallelize
profitably.

The new shared-core batch scores the independent transitions of a fixed route
with `rayon::prelude::*`. Each task receives an immutable route, its exact
preceding seed window, the learned matrix, and blend percentage. Collection
uses an indexed parallel range, so output order and floating-point operations
inside each leg do not depend on scheduling or worker count.

The optimizer defaults to `max(1, logical_cpus - 1)` Rayon workers so a
background optimization does not consume every Lyrion CPU. Operators and the
future plugin may override this with `RAYON_NUM_THREADS`. SQLite access,
schema validation, artifact reads, hash calculation, and serialized output
remain sequential. SQLite is deliberately not shared across workers.

Future route-search restarts and independent bridge-gap searches should be
parallelized. Each unit must receive a deterministic derived random seed, and
the final reduction must use an explicit objective and stable tie-break key.
Playlist writes, LMS calls, logging order, cancellation state, and final report
assembly remain single-owner operations.

## Correct adaptive cost model

The previous checkpoint described a pairwise cost matrix as the next artifact.
That is correct for Euclidean, statically weighted, and fixed learned-matrix
modes, but not for the selected adaptive mode. Adaptive weights are recomputed
from the preceding route seed window; the cost of `A -> B` can therefore change
when earlier tracks change.

The native `score --request` command consequently emits a
`contextual-adaptive-scoring-v1` artifact containing:

- the ordered source track identities;
- every seed window and candidate identity;
- the effective algorithm for each leg;
- each dynamic transition distance;
- transition sum, worst transition, and the current bottleneck-then-sum
  objective; and
- SHA-256 identities for the request, database, learned matrix, and frozen
  semantic evidence.

The adaptive request contract now requires both `seed_limit` and
`learned_percent`, avoiding an implicit static or default weight choice.

## Parity and determinism evidence

The 12-track private-data-free fixture is generated together with its adaptive
scoring request. Rust and the Python oracle agree within `1e-5`:

| Metric | Python | Native Rust |
| --- | ---: | ---: |
| Transition sum | `17.743305682757974` | `17.743305817246437` |
| Worst transition | `4.745354934880446` | `4.745355129241943` |
| Objective | `27.234015552518866` | `27.234016075730324` |

The small difference is the expected consequence of the native Bliss `f32`
feature and matrix contract versus the Python oracle's `f64` arithmetic.
Executions with one and four Rayon workers were byte-for-byte identical and
matched the checked-in JSON snapshot. The compact artifact SHA-256 was
`421c4ceec77df43022f17fa3211eebeef72f0ebe7f3c8307cf2193e900f33c54`.

## Next gate

Implement deterministic route search over the contextual scoring primitive.
Parallelize independent restarts with stable per-restart seeds and deterministic
tie-breaking, enforce artist/album/track repeat windows during construction and
validation, and compare the selected synthetic route with the Python oracle.
Playlist serialization and bridge insertion remain out of scope until route
parity passes.