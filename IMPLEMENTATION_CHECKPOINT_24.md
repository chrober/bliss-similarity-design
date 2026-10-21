# Better Call Bliss - preserve source order and fill gaps

**Date:** 2026-07-26  
**State:** Preserve-order automatic and exact-count workflows deployed and verified on ARM64 Lyrion Music Server  
**Plugin version:** `0.9.0`

## Outcome

The native immutable-anchor capability is now connected as a complete
user-facing Lyrion workflow. A user can choose **Preserve source order and fill
gaps**, then either add tracks automatically or request exactly `N` additions.

- Every original track remains in its input order.
- This first connected slice permits at most one addition in each internal gap.
- Opening and closing additions remain disabled.
- Preserve order with no additions, or automatic mode with a zero budget, is
  rejected as a guaranteed no-op in both the browser and Perl validator.
- Additional route-search attempts are disabled because the source route is
  immutable.
- Automatic mode may legitimately return zero additions while still producing
  a successful preserved-order Preview.
- Exact-count mode remains all-or-nothing and is bounded to `1 <= N <= S - 1`.
- Successful results explicitly display **Source order preserved** and mark
  inserted bridges in the numbered sequence.

## Repository commits

| Repository | Commit | Change |
| --- | --- | --- |
| `lms-better-call-bliss` | `c562fa2` | Preserve-order validation, enabled UX, artifact proofs, logging, version `0.9.0`, public contract docs |
| `lms-better-call-bliss` | `da4e99f` | Capability contract `extras-job-editor-v8` and explicit optimized-or-preserved working mode |
| `lms-better-call-bliss` | `636f771` | Reproducible live-validation report |

The native optimizer remains `b6d3d10`; no Rust change was required because its
preserved-order automatic, exact-count, and immutable-subsequence contracts were
already implemented and covered by native tests.

## Defensive result boundary

The plugin now rejects an addition artifact unless:

1. its published `ordering_policy` equals the submitted job policy;
2. source and selected base-route membership are identical and unique;
3. for `preserve_order`, selected base-route IDs equal source IDs in exact order;
4. original entries in the final route equal that selected base route;
5. the native original-subsequence and unique-membership proofs are true;
6. automatic budget or exact-count requirements are satisfied;
7. every proposed bridge resolves through the unchanged `bliss.db` to a unique
   current local LMS track.

Playlist persistence remains a separate explicit action and consumes only the
normalized, proof-checked final sequence.

## Live verification

After the final restart, the server at `192.168.1.112` reported:

```text
ready=1
problem_count=0
ux_contract=extras-job-editor-v8
working_mode=per-job-adaptive/optimize-or-preserve/none-auto-exact/create-copy
```

The live Extras page exposed the enabled
**Preserve source order and fill gaps [Working]** option. Three read-only
Previews were exercised:

| Source | Mode | Result | Native | Wall |
| ---: | --- | --- | ---: | ---: |
| 13 tracks | Preserve + Add exactly 1 | 14 tracks, one resolved bridge | 10,658 ms | 11,026 ms |
| 13 tracks | Preserve + Add automatically, budget 1 | 14 tracks, one resolved bridge | 10,418 ms | 10,531 ms |
| 2 tracks | Preserve + automatic, 100th-percentile trigger | 2 tracks, zero additions | 3,163 ms | 3,510 ms |

For both real additions, native source IDs, selected base-route IDs, and the
original-only final subsequence were identical in exact order. The result page
showed the preserved-order banner, and both selected bridge rows resolved to
current local LMS tracks. The zero-addition path also preserved exact order and
showed its explicit no-bridge explanation.

A direct Preserve plus no-additions form submission was rejected before job
creation, proving the server does not rely on JavaScript relevance rules.

## Known membership boundary

A separate two-track exact-one request produced a valid native preserved-order
artifact but selected `bliss-row-8`, which was not present as a current local LMS
track. The plugin failed closed with `BRIDGE_TRACK_NOT_IN_LMS`; no persistence
action was available. This is the same pre-search LMS-candidate inventory gap
recorded in checkpoint 23, not a preserve-order failure.

## Verification completed

- static XML and form-enablement checks: passed;
- server ordering-policy enum and no-op validation: passed;
- LMS restart and Perl plugin loading: passed;
- final status contract v8 and plugin version `0.9.0`: passed;
- preserve automatic with one addition: passed;
- preserve automatic with zero additions: passed;
- preserve exact-one with one resolved addition: passed;
- exact source-order and final-subsequence comparisons: passed;
- known non-LMS bridge candidate: rejected safely;
- no Preview invoked playlist persistence.

## Next user-facing slice

The **One bridge per source-track transition** preset can now be implemented as
a thin preserved-order exact-count wrapper with `N = S - 1`. Before enabling it
for large playlists, the UI should gain cancellation/resource bounds, and the
pre-search LMS-local candidate inventory should prevent stale Bliss rows from
wasting the longer search.

