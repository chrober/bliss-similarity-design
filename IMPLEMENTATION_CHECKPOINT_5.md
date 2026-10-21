# Better Call Bliss - deterministic native route-search checkpoint

**Date:** 2026-07-20
**State:** Read-only reorder-only route search implemented and published; no bridge insertion, playlist write, plugin deployment, or Lyrion server mutation

## Published revisions

| Repository | Revision | Result |
| --- | --- | --- |
| [chrober/bliss-mixer-core](https://github.com/chrober/bliss-mixer-core) | 3297d83213c831daef84dc93aa9f2c8ec866f457 | Pinned shared learned/adaptive scoring contract |
| [chrober/bliss-playlist-optimizer](https://github.com/chrober/bliss-playlist-optimizer) | aef1a7d038d9919a927b4bef80d3965a429dcdbd | Deterministic route command, schema, snapshot, tests, and documentation; local gates and [CI](https://github.com/chrober/bliss-playlist-optimizer/actions/runs/29751087939) passed |

The optimizer pins the full core revision. No consumer follows a moving branch.

## Blueprint and ownership boundary

The learned-matrix-enabled D:\LMS\bliss-mixer fork is the behavioral blueprint
for matrix loading and Adaptive scoring. The shared core preserves its one-seed
learned-matrix behavior, multi-seed variance blend, learned-percent semantics,
labels, validation, and fallbacks. The optimizer does not duplicate those
calculations.

The optimizer-owned code begins at the fixed-set problem: seeded route
construction, hard repeat constraints, local route improvement, objective and
energy-arc evaluation, deterministic reduction, and route reporting. These
capabilities do not exist in bliss-mixer and remain outside the shared scorer.

## Implemented route contract

The read-only route command validates unique source and database identities,
loads features and artist/album metadata from TracksV2, and recomputes every
transition from its actual preceding Adaptive seed window. It minimizes the
transition sum plus twice the worst transition while treating artist and album
look-back windows as hard constraints. Exact unique membership proves the
track-repeat window without weakening it.

Deterministic fixed starts and seeded greedy restarts are improved with reversal
and relocation moves. A separately searched energy-arc candidate is selected
only within the frozen 8% primary-cost and 10% arc-improvement gates. The
versioned adaptive-route-v1 artifact records both candidates, the selected
membership and order, input hashes, settings, and repeat validation.

Start and destination locks, time-budget termination, preserve-order routing,
and all membership-changing extension modes fail with explicit unsupported
errors in this slice.

## Parallelization and performance

Independent restart tasks use an indexed Rayon range. Each restart receives a
stable derived random seed and a private contextual transition cache, avoiding
locks and cross-job state. Final reduction uses the complete search score and a
lexical route tie-break.

The 12-track, 50-restart debug fixture completed in approximately 22 seconds
with four workers and approximately 72 seconds with one worker. Exact output is
identical across those counts. The executable still defaults to one fewer
logical worker than available so Lyrion retains CPU capacity; the
RAYON_NUM_THREADS environment variable remains the explicit override.

## Parity and reproducibility evidence

The native route selects the same adaptive-arc order as the Python oracle.
Aggregate values agree within 1e-5:

| Metric | Python | Native Rust |
| --- | ---: | ---: |
| Transition sum | 7.464628568112724 | 7.464628517627716 |
| Worst transition | 0.7095845442163404 | 0.7095845341682434 |
| Objective | 8.883797656545404 | 8.883797585964203 |

The checked-in native artifact SHA-256 is
18c06308e57159ff7d3552084ffad6de336b1626cd8ec549cd65765340a0fc32.
Strict formatting, Clippy with warnings denied, unit tests, JSON-schema
validation, exact snapshot comparison, Python tolerance comparison, membership
checks, infeasible-repeat coverage, and one/four-worker determinism all pass.

## Next gate

Begin the bridge kernel as another read-only and reproducible slice. Enumerate
eligible analyzed library candidates, freeze the cross-context reference
distribution, rescore both sides of each proposed insertion with the bridge in
the outgoing seed context, enforce full-route uniqueness and repeat windows,
and emit accepted and rejected proposal evidence. Start with Bliss-only
behavior. Provider-neutral Last.fm or ListenBrainz evidence remains optional
input and must never be required for an acoustically feasible result.
