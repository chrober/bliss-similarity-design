# Bliss 'Em All - multi-track preserved-gap routing checkpoint

**Date:** 2026-07-21
**State:** Read-only Phase 3 exact-count multi-track internal-gap routing
published for immutable anchors; no endpoint insertion, destination route,
dynamic provider request, preview application, playlist write, plugin
deployment, or Lyrion server mutation

## Published revision

| Repository | Revision | Result |
| --- | --- | --- |
| [chrober/bliss-playlist-optimizer](https://github.com/chrober/bliss-playlist-optimizer) | eff16c37583a04970413d74505acc5060aa9f815 | Deterministic bounded routes with multiple bridges inside one preserved internal gap, final-context diagnostics, explicit safety limits, reproducible over-gap-count fixture, and one-worker/four-worker byte parity; [CI](https://github.com/chrober/bliss-playlist-optimizer/actions/runs/29824428835) passed |

## Request and compatibility contract

Exact-count requests still default to one bridge per original internal gap.
A preserve-order request may opt into
`extension.max_tracks_per_gap` from 1 through 8. The effective value is
recorded in `selection_preview.search.max_tracks_per_gap`.

The cross-field contract is strict:

- the option is valid only for `extension.mode = exact_count`;
- a value above one currently requires
  `route.ordering_policy = preserve_order`;
- automatic extension remains one bridge per gap;
- values below one or above eight are rejected by both the request schema and
  native API boundary; and
- omitting the option selects one and preserves checkpoint-10/11 search
  behavior.

The three earlier exact-count artifacts changed only by the effective
`max_tracks_per_gap = 1` provenance field.

## Bounded deterministic search

The proven one-bridge implementation remains a separate compatibility path.
For a larger per-gap bound, the optimizer processes original gaps left to
right. Within one gap it appends candidates immediately before the right anchor;
candidate choice order therefore defines a small route between the anchors.

Every expansion:

- is drawn from the semantic pool frozen for the original anchor endpoints;
- excludes identities already present in the evolving route;
- passes full-route artist and album repeat windows;
- passes the two affected contextual acoustic gates;
- recomputes the complete Adaptive bottleneck-then-sum route objective; and
- remains bounded by candidate limit, local gap depth, local beam, global beam,
  and requested total count.

Local states are reduced deterministically at every depth. Global states remain
bucketed by total addition count so cheaper short routes cannot crowd the
requested count out. Stable objective and route-identity tie-breaking makes the
result independent of Rayon worker count.

The structural upper bound is:

```text
min(unique frozen candidates, internal gaps * max_tracks_per_gap)
```

Exact-count failure still exposes no partial route.

## Final-context diagnostics

Adding a later bridge changes the earlier bridge's outgoing neighbor. Publishing
the earlier insertion-time evaluation would therefore be stale. After the final
route is selected, the optimizer removes each inserted bridge in turn and
virtually reinserts it at its final position. Its reported incoming and outgoing
distances, percentiles, repeat result, and acoustic acceptance consequently
reflect the actual final neighbors and Adaptive context.

A final bridge that does not pass this reconstruction fails the preview instead
of producing an inconsistent artifact.

## Reproducible fixture

The private-data-free fixture keeps these four anchors:

```text
track-01, track-11, track-02, track-12
```

It requests four additions with a per-gap bound of two. Four is greater than the
three available internal gaps, so the result is possible only through
multi-track gap routing:

```text
track-01,
track-11, bliss-row-5, bliss-row-6,
track-02, bliss-row-8, bliss-row-7,
track-12
```

The request SHA-256 is
`b43ecd7ede10ce412a57ef09c49bdbe971541f14b96faf61df9064f910a8857c`.
The exact artifact SHA-256 is
`3c6ead8dbce76d969be3911dc1346c6cd2d9461dd72e5d55a28bf00266ef29cf`.

The artifact records a beam width of 64, candidate limit of 3, per-gap bound of
2, 168 evaluated states, 160 retained states, maximum addition count of 4, and
structural upper bound of 6. All 13 generated-input hashes verify.

## Verification

The local and GitHub gates pass:

- formatter and compiler checks;
- warning-free Clippy across all targets and features;
- 13 library tests, including a one-gap/two-bridge API case;
- two binary tests with exact one-worker/four-worker artifact parity;
- nine schema and artifact contract tests;
- exact requested membership with no partial result;
- immutable source-anchor subsequence and unique membership;
- at least one gap containing more than one selected bridge; and
- semantic compatibility audits for every earlier exact snapshot.

## Current boundary and next gate

Candidate semantic eligibility is frozen from the original anchor endpoints.
This checkpoint does not perform dynamic semantic chaining between inserted
tracks. It also keeps the conservative
`PRESERVED_ANCHOR_REPEAT_CONFLICT` behavior for source orders that violate a
look-back window before insertion.

Opening and closing slots are still excluded. The next native gate is explicit,
opt-in endpoint insertion for strict target counts, with separate limits and
diagnostics so tracks are never silently added outside the original anchors.
Destination routing for **Bliss me there…** remains the subsequent route
variant.
