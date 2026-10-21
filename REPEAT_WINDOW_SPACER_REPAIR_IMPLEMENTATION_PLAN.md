# Repeat-window spacer repair implementation plan

**Date:** 2026-10-20  
**Status:** Implemented on feature branches; release and live deployment pending  
**Primary owners:** `bliss-playlist-optimizer`, `lms-better-call-bliss`  

## Goal

Make the existing **Add spacing tracks as needed** workflow insert the smallest
number of local analyzed tracks that makes the complete final route satisfy the
selected artist, album, and track repeat windows. Source tracks remain an
ordered subsequence, additions occur only inside source gaps, and candidate
selection remains Bliss-first with optional bounded guidance.

The plugin keeps only safe, cheap preflights. Preserve order uses the exact
positional minimum implied by its fixed source anchors; Optimize uses only an
order-independent membership lower bound until the native source-only route is
known. Neither preflight may dictate the result size or feed the generic
fixed-source extension placer. The native global planner decides the feasible
per-gap counts and the final minimum total.

## Fixed decisions

- **Preserve source order** keeps the input source order. **Optimize source
  order** first produces and freezes the source-only route; repair then operates
  on that frozen order.
- A gap may receive zero or more additions. No opening or closing additions are
  permitted.
- The job's existing maximum-additions value is a hard global budget, not a
  target.
- The global objective is lexicographic:
  1. satisfy every hard membership and repeat constraint;
  2. minimize the total number of additions;
  3. minimize the worst accepted adjacent transition;
  4. minimize the transition sum;
  5. prefer bounded guidance support;
  6. apply Variation only inside the minimum-count quality band.
- Search retains separate beams for each cumulative addition count. A cheap
  zero-addition partial route must not prune a more expensive partial route
  that is required to satisfy a later source repeat.
- The existing acoustic leg acceptance, candidate-library, genre, virtual
  library, uniqueness, repeat-identity, and guidance rules remain authoritative.
- If the source is already repeat-safe, the workflow retains an explicit no-op
  response instead of producing an unchanged preview. Preserve can establish
  this in the plugin; Optimize establishes it natively after freezing its
  source-only route.
- Failure is all-or-nothing and returns no partial route.
- Existing user-facing labels and controls remain unchanged. Result details may
  add gap/count proof, but established Better Call Bliss log bodies must not be
  reformatted.

## Implementation record

The implementation follows the design without adding another user-facing mode:

- `bliss-playlist-optimizer` branch
  `feature/repeat-window-spacer-repair` adds capability
  `repeat_window_repair_v1`, a dedicated request/result contract, source-only
  lower-bound preflight, and a shared inner global planner used by both exact
  fixed-gap and minimum-total repair policies.
- `lms-better-call-bliss` branch `feature/repeat-window-spacer-repair` maps the
  existing **Add spacing tracks as needed** choice to that native mode, keeps
  the existing maximum-additions control as its global ceiling, and validates
  the returned variable per-gap proof before Preview acceptance.
- Pure planner, JSON contract, end-to-end native, request typing, option
  normalization, result validation, diagnostics, and metadata tests cover the
  new path. One- and four-worker Rayon executions produce the same route.
- Optimized source routing deliberately ignores final repeat windows while it
  chooses the source-only order; the global repair owns final repeat-window
  enforcement. Trusted requests reject fields belonging to other modes, and
  the plugin binds each selected candidate identity to its physical source gap.
- Local Windows validation retains two pre-existing fixture-hash failures caused
  by CRLF differences; route and scoring payloads remain identical. Linux CI is
  still required before release.

No GitHub build, release, Pi deployment, or Lyrion restart is part of this
implementation checkpoint.

## File map

### `bliss-playlist-optimizer`

- `src/multi_gap.rs`: generalized count policy and minimum-total global search.
- `src/preview.rs`: per-gap candidate/scoring adapter for repeat repair.
- `src/main.rs`: request dispatch, preflight, progress, result proof, and stable
  error mapping.
- `schemas/optimizer-request-v1.schema.json`: `repeat_window_repair` request.
- `schemas/bridge-analysis-artifact-v1.schema.json`: repair preview proof.
- `tests/multi_gap.rs`: pure global-planner behavior.
- `tests/contracts.rs`: JSON request-contract behavior.
- `fixtures/synthetic/`: deterministic end-to-end request and expected result.
- `docs/ERROR_CODES.md`, `docs/ARCHITECTURE.md`, `README.md`: owned behavior.

### `lms-better-call-bliss`

- `BetterCallBliss/RequestBuilder.pm`: map `satisfy_constraints` to the new
  native mode while preserving the existing maximum-additions job control.
- `BetterCallBliss/Plugin.pm` and `BetterCallBliss/BlissCompatibility.pm`:
  capability detection and compatibility status.
- `BetterCallBliss/BridgeResolver.pm`: validate and resolve variable per-gap
  additions from the native proof.
- `BetterCallBliss/Web.pm` and the existing Extras template: render the current
  workflow with minimum-total/per-gap proof, without adding controls.
- `BetterCallBliss/Jobs.pm` and `BetterCallBliss/LogDiagnostics.pm`: preserve
  established messages and add only structured repair diagnostics where needed.
- `tests/request_json_types.t`, `tests/job_options.t`,
  `tests/fixed_gap_count.t`, plus a focused repair-result test: host contract and
  rendering regression coverage.
- `ALGORITHMS.md`, `docs/UX_STATUS.md`, `README.md`,
  `BetterCallBliss/README.md`, `IMPROVEMENT_BACKLOG.md`: update only after the
  implementation and verification gates pass.

## Task 1: Generalize the pure global planner

### Tests first

Extend `tests/multi_gap.rs` with hand-derived fixtures that fail against the
current exact-count-only API:

- `repair_uses_zero_tracks_in_safe_gaps_and_two_where_required`: preserve three
  source gaps, add nothing to safe gaps, and place exactly two tracks in the one
  conflicting gap.
- `repair_minimizes_total_additions_before_acoustic_score`: prove that a
  better-sounding three-track solution loses to a valid two-track solution.
- `repair_keeps_separate_total_count_beams_for_later_source_conflicts`: prove
  that an early higher-count state survives when the lower-count local winner
  makes a later repeated source anchor infeasible.
- `repair_respects_global_budget_without_returning_a_partial_route`: one fewer
  permitted addition returns a typed failure and no plan.
- `repair_is_deterministic_across_one_and_four_rayon_workers`: identical seed
  and inputs produce identical route, proof, and stats.
- `repair_variation_never_selects_a_larger_valid_total`: non-zero Variation may
  choose among minimum-count quality-band routes only.

Run the focused test and confirm that it fails because the variable-count API
does not exist:

```powershell
cargo test --locked --test multi_gap repair_ -- --nocapture
```

### Minimal implementation

In `src/multi_gap.rs`:

- retain `plan_fixed_gap_count*` as the compatibility wrapper used by the
  released fixed-gap feature;
- add a shared internal planner with an explicit count policy;
- add public `plan_repeat_window_repair` and
  `plan_repeat_window_repair_with_progress` entry points;
- extend each global state with its cumulative addition count;
- enumerate anchored alternatives from zero through the remaining global
  budget and retain a bounded beam independently for each cumulative count;
- after all gaps, validate the complete route and select the first non-empty
  total-count bucket, then apply the existing acoustic/guidance/Variation
  ordering within that bucket;
- return per-gap intermediate lists and search statistics in the existing
  planner-neutral structures where possible; do not duplicate the anchored-path
  kernel or repeat checker.

Re-run the focused test, then the complete pure-planner test:

```powershell
cargo test --locked --test multi_gap
```

## Task 2: Add the native request/result contract

### Tests first

In `tests/contracts.rs`, add a request using:

```json
{
  "mode": "repeat_window_repair",
  "candidate_limit": 16,
  "shortlist_limit": 256,
  "max_added_tracks": 20,
  "gap_context_mode": "rolling"
}
```

Assert that this mode requires `max_added_tracks`, rejects fixed-count and
target-count fields, accepts rolling/frozen gap context, and preserves numeric
and boolean JSON types. Confirm the new tests fail against the current schema.

Add a deterministic synthetic fixture whose source has both a safe gap and a
repeat-deficient gap. Its expected result must prove:

- source order is preserved;
- no endpoint additions exist;
- each source occurs exactly once;
- additions are unique and LMS-eligible;
- the total is no greater than the global budget;
- the final route satisfies every repeat window;
- the preview reports each gap's actual addition count and the minimum-total
  global search statistics.

### Minimal implementation

- Add `repeat_window_repair` to the request schema with only the fields above.
- Add a dedicated selection-preview variant rather than overloading
  `fixed_source_extension` or claiming `every_gap_exact_count`.
- Reuse the existing fixed-gap candidate preparation, frozen/rolling contextual
  scorer, anchored-path kernel, and guidance adjustments in `src/preview.rs`.
- Dispatch the new mode in `src/main.rs` after the source-only route has been
  selected and frozen.
- Keep the existing plugin-side minimum-size check as a lower-bound preflight;
  add native fail-fast checks for zero budget, final-size limit, insufficient
  unique inventory, and a lower bound above the global budget.
- Publish structured progress for candidate preparation, each gap, cumulative
  count buckets, evaluated states, and retained states.
- Map infeasibility to stable errors such as
  `REPEAT_WINDOW_REPAIR_INSUFFICIENT_CANDIDATES` and
  `REPEAT_WINDOW_REPAIR_NOT_FOUND`, with the budget and blocking gap in
  diagnostics.
- Advertise `repeat_window_repair_v1` in `capabilities`.

Run:

```powershell
cargo test --locked --test contracts
cargo test --locked
cargo fmt --check
cargo clippy --locked --all-targets --all-features -- -D warnings
```

## Task 3: Switch Better Call Bliss request generation

### Tests first

Update `tests/request_json_types.t` and `tests/job_options.t` so the existing
**Add spacing tracks as needed** selection expects:

- native `extension.mode = repeat_window_repair`;
- the exact per-job `max_added_tracks` budget;
- no derived exact `target_track_count` in the native extension object;
- the selected ordering policy and existing Adaptive gap-context option;
- unchanged plugin-side no-op and obvious insufficient-budget messages;
- capability rejection when the installed optimizer lacks
  `repeat_window_repair_v1`.

Run the focused tests and observe the expected old
`fixed_source_extension` payload failure:

```powershell
prove -l tests/request_json_types.t tests/job_options.t
```

### Minimal implementation

- Preserve the listener-facing `addition_purpose = satisfy_constraints`.
- Normalize the internal job mode to `repeat_window_repair` so status,
  diagnostics, and result parsing describe the command truthfully.
- Retain `_minimum_repeat_safe_target` only for cheap no-op and impossible-budget
  preflight; do not use it as the requested final size.
- Emit the new native request and gate this workflow on the new capability.
- Keep every unrelated extension and destination-route payload byte-for-byte
  stable in the canonical request tests.

## Task 4: Validate and render the native repair proof

### Tests first

Add a focused Perl fixture test that supplies a successful repair artifact with
different counts in several gaps. Assert:

- additions resolve in their exact native positions;
- no opening/closing addition is accepted;
- the source subsequence, total count, per-gap counts, uniqueness, and repeat
  proof are mandatory;
- malformed, over-budget, partial, or fixed-count-masquerading artifacts fail
  before Preview acceptance;
- the existing workflow label and controls are unchanged;
- the Preview summary says that the minimum feasible total was selected and
  lists additions under their actual left/right anchors;
- existing complete information/debug log fixtures are unchanged, except for
  additional repair-specific lines explicitly asserted by the new fixture.

Run the focused host tests and observe the unsupported-mode/result failures:

```powershell
prove -l tests/request_json_types.t tests/job_options.t tests/fixed_gap_count.t tests/repeat_window_repair.t tests/log_diagnostics.t
```

### Minimal implementation

- Extend `BridgeResolver.pm` with a dedicated repair-result validator using the
  same invariant helpers as fixed-gap mode.
- Update `Jobs.pm`, `Web.pm`, and `LogDiagnostics.pm` only where their mode
  switch requires the new internal identifier.
- Reuse the existing Extras controls and conditional sections. Add no duplicate
  setting, template block, or parallel formatter.
- Render per-gap placement and total-budget proof from the native artifact;
  keep Perl authoritative for labels and wording.

Run the focused set again, then:

```powershell
prove -l tests
```

Run the repository's Python/feed checks if its current workflow declares any.
Record missing local LMS/DBI dependencies by test name instead of treating them
as passing.

## Task 5: Cross-component verification and documentation

- Run the synthetic native request twice with Variation zero and compare the
  complete result artifacts.
- Run with Rayon worker counts one and four and compare the complete result.
- Exercise preserved and optimized source order, artist-only, album-only,
  combined repeat windows, insufficient budget, no eligible candidates,
  provider disabled, and neutral provider failure.
- Benchmark a warm and cold synthetic/library-sized request; confirm bounded
  memory, live progress, and no nested unbounded parallelism.
- Run `cargo build --locked --release` only as a local verification artifact;
  do not commit binaries.
- Update the owned READMEs, architecture, error catalogue, Algorithms, UX
  status, improvement backlog, productization plan, and a new implementation
  checkpoint only after code and tests prove the status.
- Commit optimizer, plugin, and design documentation separately. Do not push,
  build on GitHub, release, deploy, or restart Lyrion without a later explicit
  request.

## Review focus

- A source artist repeated across more than one source gap must be repairable by
  additions distributed across those gaps; adjacent-pair-only math is
  insufficient.
- Shared/collaboration artist identities must use the configured MBID-aware
  repeat mode and not fall back to display-credit equality accidentally.
- A minimum-count bucket must survive pruning even when its locally best route
  consumes a candidate required by a later gap.
- Variation and optional guidance must never increase the chosen minimum total
  or weaken a repeat/membership/acoustic gate.
- Failure, cancellation, and malformed-result paths must remain read-only and
  must not expose a partial playlist for acceptance.
