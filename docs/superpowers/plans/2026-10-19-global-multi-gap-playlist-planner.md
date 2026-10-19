# Global Multi-Gap Playlist Planner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a capability-gated Better Call Bliss mode that inserts exactly `N` generated bridge tracks into every internal source gap through one globally constrained native plan.  
**Architecture:** `bliss-playlist-optimizer` generalizes its shared anchored A-to-B search to contextual scoring, then adds one global beam planner that combines exact-depth alternatives across all gaps. Better Call Bliss owns request normalization, conditional UX, preview rendering, and accepted output while the native optimizer owns acoustic search and whole-route validation.  
**Tech Stack:** Rust 2021, Rayon, Serde/JSON Schema, Perl/Lyrion plugin templates and tests.  
**Spec:** `../specs/2026-10-19-global-multi-gap-playlist-planner-design.md`

**Implementation status (2026-10-19):** The vertical slice is implemented on
`feature/global-multi-gap-planner` in both product repositories. Optimizer
commits through `0ddc68a` provide contextual anchored scoring, the global beam
planner, request/result contracts, projected-repeat preflight, a dedicated
proof-carrying artifact, and deterministic regression coverage. Better Call
Bliss commits through `b22e889` provide capability gating, job normalization,
conditional Extras controls, request/report integration, and independent host
validation of exact per-gap layout. Native and plugin CI plus the ARM64 build
are green. The build is deployed to the Pi's official `InstalledPlugins` path
without restarting LMS; live UI/output smoke testing remains pending activation.

## Global Constraints

- The mode is named `fixed_gap_count`; the request field is `tracks_per_gap` with range `1..8`.
- For `S` source tracks and `B` bridges per gap, return exactly `B * (S - 1)` additions or no route.
- Do not add opening or closing tracks, omit a gap, duplicate source/generated tracks, or return a partial route.
- Support both preserved source order and a source-only optimized order frozen before gap planning.
- Preserve static, extended-isolation-forest, learned-matrix, Frozen Adaptive, and Rolling Adaptive scoring semantics.
- Bliss defines candidate eligibility; optional guidance remains bounded and advisory.
- Enforce artist, album, and track windows across gap boundaries and validate the complete final route independently.
- Preserve deterministic results across thread counts for a fixed request and seed.
- Keep the existing 500-track final limit and eight-track per-gap limit.
- Do not expose the feature unless the native version response advertises `fixed_gap_count_v1`.
- Preserve existing destination-route, automatic, exact-total, extension, logging, output, and progress behavior.

## Review Focus

- A later source anchor must never be consumed as a generated bridge; the global-planner membership test in Task 2 pins this.
- A locally best early gap may block a later gap; Task 2 proves the planner retains and selects a globally viable alternative.
- Source artists/albums that remain impossible after exact spacing must fail before expensive search; Task 3 pins the projected-anchor preflight.
- Rolling Adaptive must score the evolving prefix while Frozen Adaptive keeps one matrix per original gap; Tasks 1 and 2 exercise both paths.
- Parallel expansion must not change selected tracks or ordering; Task 2 compares one-thread and multi-thread results.

---

### Task 1: Context-aware shared A-to-B scoring

**Files:**
- Modify: `D:/LMS/bliss-playlist-optimizer/src/anchored_path.rs`
- Modify: `D:/LMS/bliss-playlist-optimizer/src/preview.rs`

**Interfaces:**
- Produces: `AnchoredPathScorer::score_leg(&self, route_prefix: &[usize], next: usize) -> f64`.
- Produces: `FixedAdjacentScorer<F>` adapter preserving pairwise callers.
- Consumes: existing `AnchoredPathRequest`, `AnchoredPathOption`, and deterministic ordering.

- [ ] **Step 1: Add failing anchored-path tests**

Add tests proving that a scorer observes each evolving prefix, that the final right-anchor leg uses the completed intermediate prefix, and that a fixed-adjacent adapter returns the existing route and scores.

- [ ] **Step 2: Run the targeted tests and verify RED**

Run: `cargo test --locked anchored_path -- --nocapture`  
Expected: compilation or assertion failure because contextual scoring and its adapter do not exist.

- [ ] **Step 3: Implement the scorer abstraction**

Change `search_anchored_paths` to accept a shared `AnchoredPathScorer`; build candidate and lower-bound prefixes explicitly before scoring. Add the fixed adapter and update destination callers without changing their result ordering.

- [ ] **Step 4: Run targeted and full optimizer tests**

Run: `cargo test --locked anchored_path -- --nocapture`  
Expected: PASS.  
Run: `cargo test --locked`  
Expected: all existing tests PASS.

- [ ] **Step 5: Commit**

Commit message: `refactor: support contextual anchored path scoring`

### Task 2: Reusable global fixed-gap planner

**Files:**
- Create: `D:/LMS/bliss-playlist-optimizer/src/multi_gap.rs`
- Modify: `D:/LMS/bliss-playlist-optimizer/src/lib.rs`
- Modify: `D:/LMS/bliss-playlist-optimizer/src/preview.rs`

**Interfaces:**
- Consumes: Task 1 `AnchoredPathScorer` and exact-depth `AnchoredPathOption` alternatives.
- Produces: internal `MultiGapPolicy` and `plan_multi_gap` machinery for allowed per-gap depths and final-count acceptance.
- Produces: `FixedGapPlanConfig`, `FixedGapPlanRequest`, `FixedGapPlan`, `FixedGapPlanStats`, and `FixedGapPlanError`.
- Produces: `plan_fixed_gap_count(request, scorer) -> Result<FixedGapPlan, FixedGapPlanError>` as the strict exact-depth policy wrapper.

- [ ] **Step 1: Add failing global-planner unit tests**

Cover literals for: three sources with `B=2` yielding four additions; no endpoints; every gap exactly two; later anchors unavailable; cross-gap uniqueness; a locally best first gap blocking the second; artist/album/track windows across boundaries; no partial result; seeded variation; and deterministic equality under one versus multiple Rayon threads.

- [ ] **Step 2: Run the new module tests and verify RED**

Run: `cargo test --locked multi_gap -- --nocapture`  
Expected: compilation failure because the module and planner interfaces do not exist.

- [ ] **Step 3: Implement compact global beam state and exact-depth expansion**

Carry the complete prefix, used identities, per-gap bridge lists, worst transition, transition sum, guidance adjustment, and accumulated stats. Expand each retained state through the shared A-to-B engine, merge in stable order, deduplicate by route membership/order, and prune deterministically.

- [ ] **Step 4: Add final proof and stable planner errors**

Validate source preservation, exact per-gap counts, generated uniqueness, source-anchor exclusion, and all repeat windows independently after selection. Return no `FixedGapPlan` on failure.

- [ ] **Step 5: Replace duplicate exact-total expansion with a policy adapter**

Refactor `select_exact_count_multi_gap_bridges` to consume the common global state/expansion machinery while retaining exact-total distribution semantics and all existing artifact shapes.

- [ ] **Step 6: Run module and full optimizer suites**

Run: `cargo test --locked multi_gap -- --nocapture`  
Expected: PASS.  
Run: `cargo test --locked`  
Expected: all tests PASS, including unchanged exact-count and destination fixtures.

- [ ] **Step 7: Commit**

Commit message: `feat: add global multi-gap route planner`

### Task 3: Native fixed-gap request, result, progress, and failures

**Files:**
- Modify: `D:/LMS/bliss-playlist-optimizer/src/main.rs`
- Modify: `D:/LMS/bliss-playlist-optimizer/schemas/optimizer-request-v1.schema.json`
- Modify: `D:/LMS/bliss-playlist-optimizer/schemas/bridge-analysis-artifact-v1.schema.json`
- Modify: `D:/LMS/bliss-playlist-optimizer/tests/contracts.rs`
- Create: `D:/LMS/bliss-playlist-optimizer/fixtures/synthetic/fixed-gap-count-request.json`
- Create: `D:/LMS/bliss-playlist-optimizer/fixtures/synthetic/expected-native-fixed-gap-count-v1.json`

**Interfaces:**
- Consumes: Task 2 `plan_fixed_gap_count`.
- Produces: request `extension.mode=fixed_gap_count`, `tracks_per_gap`, capability `fixed_gap_count_v1`, and a schema-valid fixed-gap selection preview.
- Produces: stable failures `FIXED_GAP_COUNT_INVALID`, `FIXED_GAP_COUNT_TOO_LARGE`, `FIXED_GAP_SOURCE_REPEAT_CONFLICT`, `FIXED_GAP_INSUFFICIENT_CANDIDATES`, and `FIXED_GAP_ROUTE_NOT_FOUND`.

- [ ] **Step 1: Add failing schema and capability tests**

Assert acceptance of a valid `tracks_per_gap=2` request, rejection of `0`, `9`, contradictory count/endpoint fields, and presence of `fixed_gap_count_v1` in `version --json`.

- [ ] **Step 2: Run contract tests and verify RED**

Run: `cargo test --locked --test contracts -- --nocapture`  
Expected: failures because the mode, result shape, and capability are absent.

- [ ] **Step 3: Extend request/result types and JSON Schemas**

Add `tracks_per_gap: Option<usize>` to extension settings and a `FixedGapCountSelectionArtifact` carrying source/gap counts, bridge count, derived counts, final sequence, per-gap decisions, global stats, and proof summaries.

- [ ] **Step 4: Implement cheap preflight and error mapping**

Use checked arithmetic, final size `<=500`, unique-candidate capacity, and projected source-anchor positions spaced `B+1` apart. Map invalid structure, inventory shortage, and bounded-search exhaustion to their distinct stable codes.

- [ ] **Step 5: Integrate scoring modes, guidance, progress, and cancellation**

Construct one fixed matrix per gap for Frozen Adaptive and a prefix-sensitive scorer for Rolling Adaptive. Prepare providers once, publish gap/state progress with heartbeats, and honor cancellation within bounded expansion.

- [ ] **Step 6: Generate and verify deterministic fixtures**

Run the fixed fixture twice and compare bytes; validate request and result artifacts through `tests/contracts.rs`. Add a negative fixture or unit test proving no partial final sequence on an infeasible request.

- [ ] **Step 7: Run native quality gates**

Run: `cargo fmt --check`  
Run: `cargo clippy --locked --all-targets --all-features -- -D warnings`  
Run: `cargo test --locked --all-features`  
Expected: all commands exit `0` without warnings or failures.

- [ ] **Step 8: Commit**

Commit message: `feat: expose fixed bridges per playlist gap`

### Task 4: Better Call Bliss capability, options, and request contract

**Files:**
- Modify: `D:/LMS/lms-better-call-bliss/BetterCallBliss/Plugin.pm`
- Modify: `D:/LMS/lms-better-call-bliss/BetterCallBliss/BlissCompatibility.pm`
- Modify: `D:/LMS/lms-better-call-bliss/BetterCallBliss/JobOptions.pm`
- Modify: `D:/LMS/lms-better-call-bliss/BetterCallBliss/RequestBuilder.pm`
- Modify: `D:/LMS/lms-better-call-bliss/tests/job_options.t`
- Modify: `D:/LMS/lms-better-call-bliss/tests/request_json_types.t`
- Modify: `D:/LMS/lms-better-call-bliss/tests/metadata_hygiene.t`

**Interfaces:**
- Consumes: native `fixed_gap_count_v1`, `fixed_gap_count`, and `tracks_per_gap` from Task 3.
- Produces: normalized `addition_purpose=fixed_gap_count`, integer `tracks_per_gap`, derived source/gap/addition/final counts, and the native request extension.

- [ ] **Step 1: Add failing option and request tests**

Test `1` and `8`, reject `0` and `9`, derive `B*(S-1)`, reject final size above 500, retain both ordering policies, serialize strict JSON integers, omit endpoint/count fields, and hide/disable the option when capability is absent.

- [ ] **Step 2: Run targeted Perl tests and verify RED**

Run: `prove -l tests/job_options.t tests/request_json_types.t tests/metadata_hygiene.t`  
Expected: failures for missing capability, normalization, and request fields.

- [ ] **Step 3: Add capability probing and option normalization**

Parse `fixed_gap_count_v1` from native `version --json`, expose it in the compatibility snapshot, and normalize the new purpose/value without reusing exact-total fields.

- [ ] **Step 4: Build the fixed-gap request**

Emit `extension.mode=fixed_gap_count`, `tracks_per_gap`, and Adaptive gap context only where applicable. Keep candidate-library, guidance, scoring, repeat-window, and output contracts unchanged.

- [ ] **Step 5: Run targeted and full plugin tests**

Run: `prove -l tests/job_options.t tests/request_json_types.t tests/metadata_hygiene.t`  
Expected: PASS.  
Run: `prove -l tests`  
Expected: all plugin tests PASS or any environment dependency failure is reported by exact test name.

- [ ] **Step 6: Commit**

Commit message: `feat: request fixed bridges for every gap`

### Task 5: Better Call Bliss job UX, progress, and preview reporting

**Files:**
- Modify: `D:/LMS/lms-better-call-bliss/BetterCallBliss/Web.pm`
- Modify: `D:/LMS/lms-better-call-bliss/BetterCallBliss/Jobs.pm`
- Modify: `D:/LMS/lms-better-call-bliss/BetterCallBliss/LogDiagnostics.pm`
- Modify: `D:/LMS/lms-better-call-bliss/BetterCallBliss/HTML/EN/plugins/BetterCallBliss/index.html`
- Modify: `D:/LMS/lms-better-call-bliss/tests/log_diagnostics.t`
- Create or modify: `D:/LMS/lms-better-call-bliss/tests/fixed_gap_count.t`

**Interfaces:**
- Consumes: Task 4 normalized values and Task 3 selection-preview/progress artifacts.
- Produces: conditional job controls, derived-count summary, capability message, per-gap preview groups, and existing accepted-output compatibility.

- [ ] **Step 1: Capture current complete log bodies and add failing UX/report tests**

Preserve all released non-fixed-gap log message bodies. Test option visibility, irrelevant-control hiding, derived count display, capability-disabled behavior, restored submitted values after errors, per-gap result grouping, and no accepted output for an infeasible preview.

- [ ] **Step 2: Run targeted tests and verify RED**

Run: `prove -l tests/fixed_gap_count.t tests/log_diagnostics.t tests/metadata_hygiene.t`  
Expected: failures because the new controls and artifact rendering are absent.

- [ ] **Step 3: Implement conditional editor controls**

Add **Fill every gap with N bridge tracks** and **Bridge tracks per gap**. Show gap context only for Adaptive; retain source/order/guidance/variation/repeat settings; hide extension amount, automatic budget, and endpoint controls. Scroll and live-job behavior remain unchanged.

- [ ] **Step 4: Render progress, terminal summaries, and per-gap decisions**

Map native progress into the existing running-job UI and show each source pair with exactly its selected bridges, transition details, and optional guidance. Add fixed-gap diagnostics as new lines without changing existing message bodies.

- [ ] **Step 5: Reuse accepted output paths unchanged**

Feed the validated final sequence into existing create-copy, overwrite, and player-queue acceptance. Add tests proving a failed or partial artifact cannot be accepted.

- [ ] **Step 6: Run targeted and full plugin suites**

Run: `prove -l tests/fixed_gap_count.t tests/log_diagnostics.t tests/metadata_hygiene.t`  
Expected: PASS.  
Run: `prove -l tests`  
Expected: all available tests PASS with unchanged baseline log fixtures.

- [ ] **Step 7: Commit**

Commit message: `feat: add fixed bridges per gap workflow`

### Task 6: Product documentation and cross-repository verification

**Files:**
- Modify: `D:/LMS/bliss-playlist-optimizer/README.md`
- Modify: `D:/LMS/bliss-playlist-optimizer/docs/ARCHITECTURE.md`
- Modify: `D:/LMS/lms-better-call-bliss/README.md`
- Modify: `D:/LMS/lms-better-call-bliss/ALGORITHMS.md`
- Modify: `D:/LMS/lms-better-call-bliss/docs/UX_STATUS.md`
- Modify: `D:/LMS/bliss-similarity-design-feature-playlist-optimization/BLISS_PLAYLIST_OPTIMIZER_IMPLEMENTATION_PLAN.md`
- Create: `D:/LMS/bliss-similarity-design-feature-playlist-optimization/IMPLEMENTATION_CHECKPOINT_33.md`

**Interfaces:**
- Consumes: verified native and plugin behavior from Tasks 1-5.
- Produces: status-quo product documentation plus an implementation checkpoint and refreshed roadmap.

- [ ] **Step 1: Update user and architecture documentation**

Explain the exact per-gap contract, both source-order policies, global rather than greedy planning, gap-context modes, all-or-nothing failures, derived counts, constraints, progress, and capability requirement. Keep planned future allocation/repair modes clearly separate.

- [ ] **Step 2: Run documentation checks**

Search for stale claims that the feature is planned or that exact-total extension supplies it. Check Markdown code fences and Mermaid blocks, and retain two trailing spaces for intentional hard line breaks.

- [ ] **Step 3: Run final native and plugin verification**

Optimizer: `cargo fmt --check`, `cargo clippy --locked --all-targets --all-features -- -D warnings`, `cargo test --locked --all-features`, and `cargo build --locked --release`.  
Plugin: `prove -l tests` plus the repository's Python feed test command from its current workflow.  
Plugin feed test: `python -m unittest discover -s tests -p "test_*.py"`.  
Cross-contract: run the plugin-built request through the matching native binary and validate the emitted artifact against both schemas.

- [ ] **Step 4: Review the complete implementation against the spec**

Verify every acceptance criterion, inspect diffs for unrelated changes or committed binaries, and record any unavailable environment-specific gate rather than treating it as passed.

- [ ] **Step 5: Commit documentation**

Optimizer commit message: `docs: explain global fixed-gap planning`  
Plugin commit message: `docs: document fixed bridges per gap`  
Design commit message: `docs: record multi-gap planner implementation`
