# Bliss 'Em All - automatic bridge-selection preview checkpoint

**Date:** 2026-07-20
**State:** Read-only Phase 3 automatic selection published; no exact-count
selection, provider adapter, network request, preview application, playlist
write, plugin deployment, or Lyrion server mutation

## Published revision

| Repository | Revision | Result |
| --- | --- | --- |
| [chrober/bliss-playlist-optimizer](https://github.com/chrober/bliss-playlist-optimizer) | 9fae3c3d8fbf7c4542508fdac8de4e02c9f280f1 | Deterministic automatic bridge-selection preview with explicit trigger and budget, sequential contextual rescoring, complete per-gap reasons, and reproducible one-worker/four-worker output; [CI](https://github.com/chrober/bliss-playlist-optimizer/actions/runs/29778912091) passed |

## Read-only selection contract

The existing `bridge` command still performs no persistence. For an automatic
extension request, its versioned `contextual-bridge-analysis-v1` artifact now
contains a `selection_preview` with the proposed final sequence and one
decision for every original internal gap.

Automatic requests declare both `trigger_percentile` and
`max_added_tracks`. A gap is eligible only when its frozen direct-transition
percentile is strictly greater than the trigger. The budget limits successful
insertions, not candidate analysis, and at most one bridge is proposed for an
original gap.

Every decision has exactly one stable reason:

- `selected`;
- `below_threshold`;
- `budget_exhausted`;
- `no_eligible_candidate`;
- `repeat_conflict`;
- `acoustic_rejected`; or
- `no_improvement`.

The schema requires `selected_bridge` for `selected` and requires it to be
null for every skip reason. This makes partial or contradictory reports fail
contract validation.

## Contextual order and objective

Original gaps are processed from left to right. This sequencing is intentional
for Adaptive scoring: a proposed bridge becomes part of the preceding seed
context seen by later gaps, while a later insertion cannot retrospectively
change an already reported decision. Candidate evaluation within the current
gap remains deterministic indexed-Rayon work.

The frozen semantic pool and its recording-before-artist,
endpoint-before-collection precedence remain mandatory. Each candidate is
rescored on both affected legs against the evolving route. Unique membership,
the full-route artist and album look-back windows, and frozen acoustic leg and
detour gates remain hard constraints.

Among accepted candidates, selection retains the semantic priority and stable
acoustic tie-break order. A candidate must also strictly improve the local
bottleneck-then-sum objective used by native route search:

```text
direct   = direct_distance + 2 * direct_distance
inserted = left_distance + right_distance
           + 2 * max(left_distance, right_distance)
```

Equal or worse candidates are reported as `no_improvement`; the preview never
adds a bridge merely to consume the available budget.

## Privacy and structural proofs

The preview exposes source request IDs and database-bound opaque
`bliss-row-N` candidate identities, not filesystem paths. It reports and tests
that:

- every source track occurs exactly once;
- source tracks remain an identical ordered subsequence;
- every bridge identity is unique in the final sequence; and
- the number of bridge entries equals `added_track_count` and never exceeds
  `max_added_tracks`.

Applying the preview, resolving opaque candidates back to LMS tracks, and
serializing an extended M3U remain responsibilities of later native/plugin
slices.

## Triggering fixture and gates

The private-data-free automatic-preview fixture uses four source anchors, one
genuinely triggering middle gap, an empty semantic graph, and a one-track
budget. It proposes `bliss-row-3` between `track-02` and `track-11`, producing:

```text
track-01, track-02, bliss-row-3, track-11, track-12
```

The request SHA-256 is
`4686db917b1356005aca1c950decc19098da98662e0cfd8da2d231f0463b4f12` and the
exact preview artifact SHA-256 is
`4256a14250ef1c44cae1fcc2cd6e0bbe196ab0e2c3a342c3f3c4066d97b02292`.
The generator reproduces all automatic and semantic requests byte-for-byte,
and all eight declared manifest hashes verify.

The local and GitHub gates pass formatting, warning-free Clippy, 11 library
tests, two binary tests, four schema-contract tests, exact one-worker and
four-worker bridge snapshots, and documentation tests. Negative contracts
cover missing automatic budgets/triggers and both invalid combinations of a
decision reason with `selected_bridge`.

## Next gate

Implement an exact-count selection preview that either proposes exactly the
requested number of additional tracks or reports infeasibility without a
partial result. It must search beyond the greedy automatic policy when needed,
preserve deterministic contextual scoring and all hard constraints, expose the
complete decision/search rationale, and remain read-only. Provider adapters,
applying previews, and LMS playlist persistence remain later slices.
