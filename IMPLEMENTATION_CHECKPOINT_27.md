# Better Call Bliss - finalized Grow from these seeds

**Date:** 2026-07-29  
**State:** Exact-target seed growth implemented, published, deployed, and accepted on ARM64  
**Plugin version:** `0.11.1`  

## Outcome

**Grow from these seeds** is now an end-to-end user feature. It treats every original source track as an immutable relevance seed, selects exactly enough unique current LMS-local analyzed songs to reach the requested total, and optimizes the complete membership for fluent playback under the job's repeat windows.

Preview distinguishes the two objectives instead of presenting one opaque score:

- fixed-seed relevance reports the best, mean, and furthest selected Adaptive distance; and
- final-route flow reports strategy, transition sum, worst transition, objective, and arc error.

The native artifact carries explicit acceptance proofs for exact target size, every source retained once, local candidate membership, unique membership, and artist/album/track repeat compliance. The plugin refuses to normalize or persist a result unless every proof passes.

## CI correction and build provenance

Optimizer run `30457329083` failed only at strict Clippy because `select_seed_growth` returned an unnamed complex tuple. Commit `8396d0b` introduced the named `SeedGrowthResult`; replacement CI run `30463443162` passed formatting, strict Clippy, and the complete test suite.

Native commit `0c4f119` adds the diagnostics and versioned proof contract. CI run `30464031982` passed, and ARM64 workflow run `30464031228` produced the deployed binary:

```text
6299aa46c5e1b9411e31ea77d8d41be6a49033d3d053157cd4aeff9ab64be77b
```

Plugin commit `22ab304` adds proof enforcement, Preview rendering, INFO-log summaries, and UX contract `extras-job-editor-v12`. Commit `7b16ec5` bundles the exact ARM64 artifact and provenance.

## Saved-copy acceptance

The earlier accepted Preview for the two-track saved playlist `Test` was persisted through the existing explicit **Create optimized copy** action as `Test Seed Growth Validation`, LMS playlist ID `2515545`.

The saved M3U and LMS catalog were independently checked:

- 25 `#EXTURL`, 25 `#EXTINF`, and 25 filesystem-path lines;
- 25 LMS catalog tracks and 25 unique URLs;
- both original seed IDs present exactly once; and
- no source playlist overwrite.

This proves that seed growth uses the same verified, non-overwriting publication boundary as the other connected workflows.

## Final live validation

Version `0.11.1` was deployed to `192.168.1.111` only after playback became idle. The previous live tree is recoverable at:

```text
/mnt/mmcblk0p2/tce/slimserver/Cache/BetterCallBliss-backups/BetterCallBliss-0.11.0-pre-7b16ec5-20260729
```

After activation, `bettercallbliss status` reported `ready=1`, no compatibility problems, and `extras-job-editor-v12`.

Read-only job `preview-1785338076-0001` grew the two seeds to exactly 25 tracks with 23 local additions. It completed in 4,869 ms total and 4,690 ms native on a warm database cache. Preview showed the new relevance, route, and acceptance sections plus the explicit copy action. The result reported:

| Diagnostic | Value |
| --- | ---: |
| Best / mean / furthest fixed-seed distance | 0.1190 / 0.1633 / 0.1835 |
| Selected route | `adaptive-arc` |
| Transition sum | 3.4328 |
| Worst transition | 0.3537 |
| Route objective | 4.1402 |
| Arc error | 3.1451 |

All seven machine-readable proofs were true: exact target, every source once, every addition local, unique membership, artist window, album window, and track uniqueness. The final validation was Preview-only and created no additional playlist.

## Remaining enhancements

Last.fm/LastMix and ListenBrainz evidence may later enrich candidate relevance and diversity, but they remain optional, failure-tolerant refinements. Bliss-only offline seed growth is the completed baseline. Preserving seed relative order and user-tunable relevance/diversity tradeoffs are also separate future policies rather than blockers for this feature.
