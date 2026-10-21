# Implementation checkpoint 37: minimum-total repeat-window spacer repair

**Date:** 2026-10-21  
**Scope:** Native global repeat-window repair and Better Call Bliss integration
for **Add spacing tracks as needed**.  
**Release state:** Implemented and locally verified on feature branches; GitHub
build, release, Pi deployment, and live Lyrion validation remain pending.  

## Delivered behavior

- The existing listener-facing workflow now uses native
  `repeat_window_repair` instead of deriving an exact fixed-source-extension
  target.  
- Preserve keeps the input order. Optimize first selects and freezes a
  source-only route. Repair never moves those frozen anchors.  
- Every internal gap may receive a different count, including zero. No opening
  or closing track is added.  
- The configured maximum additions is a hard global ceiling. The planner first
  minimizes the complete result's total additions, then worst transition,
  transition sum, guidance, and seeded Variation inside the minimum-count
  quality band.  
- Exact fixed-gap filling and variable-count repeat repair share one internal
  global planning core and the same anchored A-to-B path kernel. Their distinct
  count policies remain explicit.  
- Search retains a bounded beam for every cumulative addition count, preventing
  a locally cheaper early route from eliminating a larger partial route needed
  by a later repeated source anchor.  
- Preserve-order preflight calculates the exact positional spacing minimum;
  Optimize uses only the order-independent membership lower bound until its
  source-only route is frozen. Both reject clearly insufficient budgets before
  candidate search without mistaking a local conflict for a safe playlist.  
- Optimized source-only routing does not require the incomplete route to obey
  final repeat windows; the global repair owns that enforcement. Failure
  remains atomic.  
- The result carries per-gap selections and independent proofs for source
  subsequence, unique membership, endpoint exclusion, addition budget, and
  complete artist, album, and track repeat-window compliance. Better Call Bliss
  validates those proofs and each selected candidate's physical gap before
  enabling output actions. It also checks the reported source anchors and
  zero-based final-route position for every selected bridge. Trusted native
  requests enforce the same dedicated field contract as schema-validated
  requests.  
- Existing controls and labels remain unchanged; the result now explains the
  selected minimum total and its actual gap placements. The established
  `Spacing target: start at ...` information-log body remains unchanged.  

## Implementation revisions

| Component | Branch | Revisions |
| --- | --- | --- |
| `bliss-playlist-optimizer` | `feature/repeat-window-spacer-repair` | `d4dc59b`, `ea9c6a9`, `006f3db`, `ff76e72`, `ffd09a8` |
| `lms-better-call-bliss` | `feature/repeat-window-spacer-repair` | `e5f4c6d`, `999c926`, `392b5bb`, `593bbcd` |

## Verification evidence

- `cargo test --locked --test multi_gap`: 14 passed.  
- `cargo test --locked --test contracts`: 18 passed.  
- Focused native end-to-end repair test passed and produced identical output
  with one and four Rayon workers.  
- `cargo fmt --check` and
  `cargo clippy --locked --all-targets --all-features -- -D warnings` passed.  
- Better Call Bliss focused tests passed: `job_options.t` 75/75,
  `request_json_types.t` 92/92, `repeat_window_repair.t` 8/8,
  `metadata_hygiene.t` 162/162, and `log_diagnostics.t` 41/41.  
- Two existing Windows full-suite tests still differ only in fixture hashes
  because checkout line endings change request artifacts; numerical and route
  content is identical. Linux CI remains the release gate.  

## Remaining boundaries

- **Improve difficult transitions** still decides which optional gaps to repair
  under its existing local workflow; it does not yet allocate one global budget
  across several merely awkward transitions.  
- **Extend playlist** still chooses an exact whole-source-relevant membership
  before placement. It is intentionally not conflated with repeat-window
  repair.  
- Release packaging, live Pi validation, and performance measurement against a
  large real candidate library remain future gates.  

## Next useful step

Run Linux CI for both repositories, build and package the native optimizer,
then exercise preserved and optimized repair on the Pi with a known repeated-
artist source. Verify minimum additions, per-gap placement, live progress,
repeat proofs, and output persistence before publishing the feature.  
