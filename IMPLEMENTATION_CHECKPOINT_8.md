# Better Call Bliss - provider-neutral semantic bridge-ranking checkpoint

**Date:** 2026-07-20
**State:** Read-only Phase 3 semantic ranking published; no provider adapter, network request, bridge selection, playlist write, plugin deployment, or Lyrion server mutation

## Published revision

| Repository | Revision | Result |
| --- | --- | --- |
| [chrober/bliss-playlist-optimizer](https://github.com/chrober/bliss-playlist-optimizer) | 2338d38602056667421017abe148483c5d54e91a | Frozen provider-neutral semantic evidence, deterministic gap pools and tier-first ranking, provider-failure tolerance, versioned provenance output, and reproducible mixed-evidence snapshot; [CI](https://github.com/chrober/bliss-playlist-optimizer/actions/runs/29776324068) passed |

## Implemented evidence boundary

The native optimizer now consumes the already frozen
`semantic-evidence-v1` graph. It does not contact Last.fm, ListenBrainz, or any
other service. Every edge must name exactly one declared provider state, and the
schema rejects recording-to-artist relationships and recording-level
collection fallback.

Source recordings bind by request track ID or recording MBID. Candidate
recordings bind to the opaque `bliss-row-N` identity associated with the
recorded database hash. Artists bind by MBID, canonical local artist identity,
or normalized name at the confidence supplied by the upstream resolver. The
Lyrion plugin remains responsible for resolving an external result to exactly
one analyzed local track before freezing the graph.

## Gap-local precedence and ranking

For each selected-route gap, the optimizer constructs exactly one candidate
pool:

1. endpoint-local recording and artist evidence, when any usable local
   candidate exists;
2. collection-artist evidence from the complete original source set, only when
   that endpoint-local pool is empty; or
3. every otherwise eligible analyzed local candidate under Bliss-only operation when
   neither semantic pool resolves locally.

Within the endpoint-local pool, a recording supported by both endpoints
precedes a recording supported by one endpoint, which precedes local artist
support. Collection evidence and Bliss-only candidates cannot silently replace
an existing local pool when its candidates later fail repeat or acoustic gates.

Accepted candidates are ordered by semantic tier, identity confidence, the
best available provider-local ordinal rank, worst acoustic leg, total acoustic
detour, and stable row identity. Raw provider scores remain visible but are not
compared across providers. Both affected Adaptive legs are still rescored and
all repeat and acoustic acceptance gates remain mandatory.

Provider states such as disabled, partial, unavailable, and failed are report
data rather than optimizer failures. Cached or stale edges from another
provider remain usable, and a failed provider with no usable edges falls
through to Bliss-only analysis.

## Parallelism, fixture, and gates

Semantic candidate resolution uses immutable indexed Rayon inputs, followed by
the existing parallel acoustic candidate evaluation. Tests prove one-worker and
four-worker semantic results are identical.

The private-data-free fixture retains 18 usable rows, 6 non-curated candidates,
102 frozen contextual reference scores, and 11 internal gaps. It records a
failed LastMix/Last.fm provider beside partial cached ListenBrainz evidence.
The selected gaps demonstrate `recording_both`, `recording_one`,
`artist_local`, and `artist_collection`; collection fallback is absent where
the local pool exists.

The evidence SHA-256 is
`7089e68e3ce3270e9f8916abc4ffa39e5d76954d5f9b3726ff2144cc353a8599`, the
request SHA-256 is
`6c5bacde6d6af934c459832106dabaf88edbb3d4ee1ca96e9a89b45e4c6cbc07`, and the
one-worker semantic artifact SHA-256 is
`39ad5a3c2e05bd6c1774a133730a6edee23e326d5557344a27de243eb8f907ca`.
The generator reproduces both semantic inputs byte-for-byte and all seven
manifest hashes verify.

The local and GitHub gates pass formatting, warning-free Clippy, nine library
tests, two binary tests, two schema-contract tests, exact empty and semantic
bridge snapshots, and documentation tests. Negative contracts cover mixed
recording/artist edges and forbidden recording-level collection fallback.

## Next gate

Implement a deterministic automatic bridge-selection preview over a synthetic
route containing at least one genuinely triggering gap. Selection must respect
the frozen semantic pool, contextual rescoring, global membership and repeat
constraints, bridge budget, and stable tie-breaking. The preview artifact must
show the proposed final sequence and why each bridge was chosen or skipped,
while still performing no playlist persistence. Exact-count and destination
modes remain later slices.
