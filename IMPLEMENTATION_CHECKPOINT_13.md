# Bliss 'Em All - explicit endpoint insertion checkpoint

**Date:** 2026-07-21
**State:** Read-only Phase 3 exact-count opening and closing insertion slots
published; no destination route, dynamic provider request, preview application,
playlist write, plugin deployment, or Lyrion server mutation

## Published revision

| Repository | Revision | Result |
| --- | --- | --- |
| [chrober/bliss-playlist-optimizer](https://github.com/chrober/bliss-playlist-optimizer) | 288b1ae3a04d1c589ab33bed26b76a9e8c74523f | Independent opt-in opening and closing slots, one-sided contextual and semantic evidence, complete-route diagnostics, deterministic bounded search, and one-worker/four-worker byte parity; [CI](https://github.com/chrober/bliss-playlist-optimizer/actions/runs/29827780178) passed |

## Request and compatibility contract

Exact-count requests may independently set:

- `extension.allow_opening_track = true`; and
- `extension.allow_closing_track = true`.

Each enabled slot has hard capacity one. The properties are valid only for
`extension.mode = exact_count`; endpoint tracks are never silently enabled to
make an otherwise impossible count feasible. Omitting both properties delegates
to the checkpoint-10/12 internal-gap implementation and preserves all earlier
artifacts byte-for-byte.

The exact-count contract remains strict: a successful preview contains exactly
the requested additions, while failure exposes no final sequence and no partial
decisions.

## One-sided scoring and evidence

An endpoint is not represented as a fabricated ordinary gap:

- an opening candidate is scored only into the first source anchor, using the
  candidate itself as the one-track Adaptive context;
- a closing candidate is scored only from the complete preceding route into
  that candidate; and
- both pass unique membership, complete-route artist and album windows, and the
  existing frozen max-leg percentile gate.

The endpoint evidence pool also has one real anchor. Recording support therefore
produces `recording_one`, never `recording_both`. Endpoint-local artist
support follows recording support, then collection fallback, then Bliss-only
operation. Opening evidence identifies its anchor as the right endpoint;
closing evidence identifies its anchor as the left endpoint. Provider
provenance and failure-tolerant frozen evidence behavior are unchanged.

## Bounded deterministic search

The optimizer enumerates the allowed opening/closing-use combinations. For each
combination it requests the remaining count from the bounded internal-gap
search, retains endpoint candidates under the same candidate limit, recomputes
the complete Adaptive route objective, and applies stable route-identity
tie-breaking.

This is deliberately documented as a bounded staged search, not a proof of
joint global optimality: each endpoint-count allocation starts from the best
internal route retained by the existing bounded search. Candidate scoring uses
indexed Rayon iteration and deterministic reduction.

The structural upper bound is:

```text
min(
  unique frozen candidates,
  internal gaps * max_tracks_per_gap + enabled endpoint slots
)
```

After a winning route is selected, every internal bridge diagnostic is
reconstructed in the completed route. An opening insertion therefore shifts the
reported internal positions and changes early Adaptive contexts without leaving
stale insertion-time diagnostics. Endpoint decisions have their own policy,
anchor, semantic pool, reason, selected track, distance, and percentile fields.

## Reproducible fixture

The fixture keeps these immutable anchors:

```text
track-01, track-11, track-02, track-12
```

It requests four additions with one track per internal gap. The three internal
slots alone are insufficient. Explicit opening and closing flags raise the
structural upper bound to five, and the selected exact route is:

```text
bliss-row-3,
track-01,
track-11, bliss-row-5,
track-02, bliss-row-8,
track-12,
bliss-row-7
```

The request SHA-256 is
`31727e9f39415b177892367705b8174ecdc0a20bc0791fb6db6fb1dd3b83060a`.
The exact artifact SHA-256 is
`57f1453add34e3d2fbaf9719e7e2c3179395f14e1df9572d2919bb47a855d2cc`.

The artifact records a beam width of 64, candidate limit of 3, one track per
internal gap, 90 evaluated states, 90 retained states, maximum addition count
of 4, and structural upper bound of 5. All 14 generated-input hashes verify.

## Verification

The local gate passes:

- formatter and warning-free Clippy across all targets and features;
- 16 library tests, including one-sided scoring, repeat rejection, semantic
  provenance, structural feasibility, and one/four-worker determinism;
- three binary tests with exact one-worker/four-worker artifact parity;
- 12 schema and artifact contract tests;
- explicit endpoint-only exact-count feasibility with no partial result;
- immutable source-anchor subsequence and unique membership;
- final-route internal positions after opening insertion; and
- all earlier compatibility snapshots.

No provider request, network access, playlist write, LMS mutation, plugin
deployment, or server access occurred.

## Current boundary and next gate

Endpoint candidates have capacity one per side. Multi-track endpoint chains and
dynamic semantic chaining are not implemented. Internal semantic pools remain
frozen from their original anchor pair, and the conservative
`PRESERVED_ANCHOR_REPEAT_CONFLICT` behavior remains.

The next native route variant is fixed-destination routing for **Bliss me
there...**. The learned-matrix baseline fallback remains required before plugin
release so a personal learned matrix can become optional without silently
changing scoring semantics.
