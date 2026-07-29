# Better Call Bliss - preserve-order gap-filling preview checkpoint

**Date:** 2026-07-21
**State:** Read-only Phase 3 immutable-anchor preview published for automatic
and exact-count extension with at most one bridge per original internal gap; no
multi-track gap route, endpoint insertion, provider adapter, network request,
preview application, playlist write, plugin deployment, or Lyrion server
mutation

## Published revision

| Repository | Revision | Result |
| --- | --- | --- |
| [chrober/bliss-playlist-optimizer](https://github.com/chrober/bliss-playlist-optimizer) | 6ae252f1c600ea0e20b66f5ac0cfaaf789d22c23 | Deterministic preserve-order automatic and exact-count previews, explicit ordering provenance, immutable-anchor and repeat-conflict contracts, reproducible fixtures, and one-worker/four-worker byte parity; [CI](https://github.com/chrober/bliss-playlist-optimizer/actions/runs/29821853754) passed |

## Immutable-anchor contract

The read-only `bridge` command now accepts
`route.ordering_policy = preserve_order`. The source tracks are immutable
ordered anchors:

- source indices are used directly instead of running fixed-set route search;
- `source_track_ids` and `selected_track_ids` are recorded separately and
  are identical in this mode;
- filtering the proposed final sequence to `original` entries reproduces the
  source IDs exactly;
- bridge candidates still pass the same provider-neutral semantic narrowing,
  unique-membership, artist/album repeat, and two-sided contextual acoustic
  gates; and
- the existing automatic and exact-count selection policies operate over the
  preserved internal gaps without writing a playlist.

The artifact identifies `preserve_order`, reports
`selected_strategy = preserve-order`, and records
`parallel_execution = rayon-candidates-indexed`. Route restart search is
intentionally absent because no anchor may move.

## Repeat-window behavior

An immutable source order can already violate a captured artist or album
look-back window before any bridge is considered. The current bounded
one-bridge-per-gap search cannot honestly claim to repair several interacting
anchor conflicts. It therefore fails early with the stable code
`PRESERVED_ANCHOR_REPEAT_CONFLICT` rather than moving an anchor, weakening a
constraint, or returning a misleading partial preview.

This is deliberately conservative. A later multi-track gap-route search may
prove that selected conflicts can be separated while preserving every anchor,
but that capability needs its own whole-sequence search and contract.

## Reproducible fixtures

Both private-data-free fixtures use the deliberately unsorted source anchors:

```text
track-01, track-11, track-02, track-12
```

The automatic fixture has a one-track budget and returns:

```text
track-01, track-11, track-02, bliss-row-5, track-12
```

Its request SHA-256 is
`64321710acbf4bda9ff99a7a19b42103d5d9b8854b1a691628b0642e9983acd3` and
its exact artifact SHA-256 is
`1942905ee95334b5d3cabe58e7d0a857137ad6091ac18acce4e24ec84a32f0d0`.

The exact-count fixture requests two tracks and returns:

```text
track-01, track-11, bliss-row-5, track-02, bliss-row-8, track-12
```

Its request SHA-256 is
`b6d03a6f78a1858b07e1a251b56dcb44aab4f4fba05381738245312b4692d5b0` and
its exact artifact SHA-256 is
`8e8c215a17f4cd55b775a2d205908869c4378b85bea29fa1fb7f439e9896a169`.

Fixture regeneration is byte-stable and all 12 manifest hashes verify. A
semantic snapshot audit also proves that the five earlier bridge artifacts
changed only by the required `ordering_policy` and `source_track_ids`
provenance fields.

## Verification

The local and GitHub gates pass:

- formatter and compiler checks;
- warning-free Clippy across all targets and features;
- 12 library tests;
- two binary tests, including exact snapshot parity under one and four Rayon
  workers;
- seven schema-contract tests;
- immutable original-subsequence assertions for both preserve modes;
- exact selected bridge identities and requested counts; and
- the negative preserved-anchor repeat-conflict path.

## Current boundary and next gate

This checkpoint establishes the first usable **Preserve order and fill gaps**
native preview, but it permits at most one bridge in each original internal gap.
It does not add opening or closing tracks and does not form a small multi-track
route between two anchors.

The next native gate is bounded multi-track routing inside preserved gaps so
strict target-length requests can add more than one bridge where needed without
moving anchors. That search must rescore from the earliest affected position,
validate the complete final route, remain deterministic across worker counts,
and preserve the existing exact-count no-partial contract.
