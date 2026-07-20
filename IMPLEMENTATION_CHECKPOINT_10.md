# Bliss 'Em All - exact-count bridge-selection preview checkpoint

**Date:** 2026-07-20
**State:** Read-only Phase 3 exact-count selection published; no immutable
anchor multi-track gap route, endpoint insertion, provider adapter, network
request, preview application, playlist write, plugin deployment, or Lyrion
server mutation

## Published revision

| Repository | Revision | Result |
| --- | --- | --- |
| [chrober/bliss-playlist-optimizer](https://github.com/chrober/bliss-playlist-optimizer) | 43e2d1a7d265f7f112dd70d2c06d330d8625f311 | Deterministic exact-count bridge preview with bounded search, strict no-partial output, honest infeasibility evidence, reproducible feasible/infeasible fixtures, and one-worker/four-worker byte parity; [CI](https://github.com/chrober/bliss-playlist-optimizer/actions/runs/29781608818) passed |

## Exact-count contract

The read-only `bridge` command now accepts `extension.mode = exact_count`
with a required `additional_track_count`. For the current
`optimize_order` slice, it considers at most one bridge in each original
internal transition. It does not apply the preview or write a playlist.

A successful artifact is explicit:

- `feasible` is true;
- `added_track_count` equals the requested count;
- the final sequence contains exactly that many unique bridge identities;
- every source track remains an identical ordered subsequence;
- every selected bridge passes the frozen semantic, unique-membership, repeat,
  and acoustic gates; and
- each original gap records either `selected` with a candidate or
  `not_selected` with a null candidate.

An unsuccessful artifact cannot look like a usable partial result:

- `feasible` is false;
- `added_track_count` is zero;
- structural proofs and `final_sequence` are null;
- `decisions` is empty; and
- `infeasibility` contains the stable failure code and search evidence.

The JSON schema enforces both tagged shapes and the selected-candidate
relationship. Contract tests additionally count bridge entries and compare
them with the request.

## Deterministic bounded search

The optimizer processes original gaps left to right so every later Adaptive
context includes earlier tentative bridges. For each retained state it creates
a skip branch and up to the declared candidate limit of accepted insertion
branches. Every insertion is contextually rescored against the evolving route.
Its complete tentative sequence is then scored with the same
bottleneck-then-sum objective as native route search.

States are bucketed by number of additions before pruning. This prevents
shorter, naturally cheaper routes from crowding the requested count out of the
beam. Each count bucket retains up to 64 states ordered by full route objective
and stable route identity. State expansion and candidate evaluation use
indexed Rayon inputs; sorting and reduction are stable.

The search is heuristic rather than a claim of global optimality. Its artifact
therefore separates:

- `maximum_additions_found`, the largest count retained by this search;
- `structural_upper_bound`, the smaller of the original internal-gap count
  and the number of unique frozen candidates;
- `EXACT_COUNT_INFEASIBLE`, used only when the request exceeds that structural
  upper bound; and
- `EXACT_COUNT_NOT_FOUND_WITHIN_SEARCH_BOUNDS`, used when the request is
  structurally possible but no complete state survives the declared candidate
  and beam bounds.

This distinction keeps the preview useful without overstating a bounded
heuristic as a proof.

## Reproducible fixtures and gates

The feasible private-data-free fixture uses four source anchors and requests
two additional tracks. It returns:

```text
track-01, bliss-row-3, track-02, bliss-row-8, track-11, track-12
```

Its request SHA-256 is
`be2fcbeb912b50814939b59710c680eaf3cd82d11683e97a43e7dbc3f72b2e9f` and
its exact artifact SHA-256 is
`3cd729dad03a8c29ee97e48a30f4c1799a0966b3a060d1aeed6e7a50e0d268ac`.

The infeasible fixture requests seven additions from a six-candidate library.
Only three additions are found under the acoustic and repeat gates, while the
structural upper bound is six. It therefore returns
`EXACT_COUNT_INFEASIBLE` with no partial sequence. Its request SHA-256 is
`35d1bd966f73aed3b1bbe2139184e4e0f4d11c965d22e76cb19195a2afe33980`
and its exact artifact SHA-256 is
`d4d660b4e72927e500544242d76c9096dbaa090cee1cc413f9f68ce2a156df47`.

Fixture generation is byte-stable and all ten declared manifest hashes verify.
The local and GitHub gates pass formatting, warning-free Clippy, 12 library
tests, two binary tests, six schema-contract tests, exact feasible/infeasible
snapshots under one and four workers, and documentation tests.

## Current boundary and next gate

This checkpoint deliberately covers one bridge per original internal gap after
`optimize_order`. It does not yet implement the canonical endpoint slots
needed when an optimized playlist requests more additions than internal gaps,
or multiple inserted tracks forming a small route inside one immutable-anchor
gap.

The next gate is **Preserve order and fill gaps**: accept an immutable ordered
anchor sequence, keep it byte-for-byte as the original subsequence, and search
one or more contextual bridge tracks inside selected gaps without moving an
anchor. Automatic and exact-count outcomes must retain the same strict
membership, repeat, semantic, acoustic, determinism, and no-partial contracts.
