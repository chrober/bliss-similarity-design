# Bliss 'Em All - contextual bridge-scoring kernel checkpoint

**Date:** 2026-07-20
**State:** First read-only Phase 3 kernel published; no bridge command, semantic ranking, playlist write, plugin deployment, or Lyrion server mutation

## Published revision

| Repository | Revision | Result |
| --- | --- | --- |
| [chrober/bliss-playlist-optimizer](https://github.com/chrober/bliss-playlist-optimizer) | 0a59b6c2ac71a42cb5a7d641d3cc7c534194508c | Public Rust bridge/context/route library boundary and tested contextual bridge kernel; [CI](https://github.com/chrober/bliss-playlist-optimizer/actions/runs/29752925300) passed |

## Implemented semantics

The optimizer now has one shared adapter around bliss-mixer-core for Adaptive
context-to-candidate scoring. Route search and bridge scoring therefore use the
same one-seed learned behavior and multi-seed learned/variance blend; the bridge
code does not copy the mixer calculation.

The bridge kernel builds the frozen reference distribution from every original
candidate under each actual selected-route seed context. It scores a proposed
internal insertion twice: first from the real preceding context into the bridge,
then from a context containing that bridge into the unchanged right anchor.
Both raw distances and empirical percentiles are retained.

Artist and album windows are checked across the complete tentative route.
Existing route members cannot be reused as bridges. Acoustic acceptance uses
the frozen prototype gates: each leg at or below percentile 0.70 and their sum
at or below 1.30. Candidate ranking uses accepted state, worst leg, detour sum,
and a stable candidate-index tie-break.

## Parallelism and gates

Frozen context groups and independent bridge candidates use indexed Rayon
iteration. Inputs are immutable, result collection is ordered, and ranking has
an explicit total order. The tests prove one-worker and four-worker results are
identical.

The fail-fast local gate passes formatting, strict Clippy with all targets and
features, seven unit tests, one schema-contract test, and documentation tests.
Coverage includes frozen-reference size, two-sided outgoing-context rescoring,
accepted acoustic bridges, repeat rejection, original-member rejection,
invalid-index errors without panics, Rayon determinism, and the unchanged exact
native route snapshot.

## Next gate

Connect the kernel to stable TracksV2 candidate enumeration and emit a
versioned read-only bridge-analysis artifact for the synthetic fixture. That
artifact must report gaps, accepted and rejected candidates, contextual costs,
repeat decisions, and hashes before any insertion policy can alter membership.
Then add provider-neutral recording evidence first, endpoint-local artist
evidence second, and collection-wide or Bliss-only fallback only when the local
edge is empty. Provider failure must remain non-fatal.
