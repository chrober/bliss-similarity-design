# Shared Rust guidance semantics and Better Call Bliss parity Implementation Plan

> **Delivery status (2026-10-03): Delivered.** The shared policy semantics,
> Library Signals observations, Last.fm artist-policy capability, optimizer
> aggregation, Better Call Bliss controls and provenance, and cross-repository
> Raspberry Pi verification were completed. The first native `bliss-mixer`
> Library Signals host endpoint and `selection_trace_v1` followed in version
> 0.11.4. This document remains the implementation record; later provider
> acquisition and provider-specific Lab DSTM parity are tracked separately;
> Lab already uses the endpoint for enabled native providers.

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the playlist optimizer and Better Call Bliss the same bounded Last.fm and local-library reranking semantics already validated in BlissMixerLab, while keeping Bliss eligibility and acoustic ranking authoritative.

**Architecture:** Keep provider processes responsible for source-specific observation and normalized signals. Add a host-neutral, pure-Rust policy module to `bliss-playlist-guidance-spi`; the optimizer consumes that module while selecting candidates and routes. Better Call Bliss snapshots effective per-job policy, supplies trusted Last.fm/Lyrion inputs, and renders provenance; it does not implement ranking formulas in Perl.

**Tech Stack:** Rust 2021, `bliss-playlist-guidance-spi` JSONL v2,
`bliss-guidance-lastfm`, `bliss-guidance-library-signals`,
`bliss-playlist-optimizer`, `bliss-mixer`, and Perl/Lyrion Better Call Bliss.

**Spec:** `D:\LMS\lms-blissmixer-lab\RUST_GUIDANCE_MIGRATION.md`; `D:\LMS\lms-better-call-bliss\docs\superpowers\specs\2026-09-19-guidance-spi-migration-design.md`

## Global Constraints

- Bliss remains responsible for candidate admission, acoustic scoring, route validity, repeat windows, genre filtering, and all hard constraints.  
- Guidance is advisory: disabled, unavailable, malformed, timed-out, or identity-incomplete providers yield neutral guidance, never a failed mix or route.  
- Provider processes receive only bounded candidate batches; no full-library JSON artifact or unbounded SQLite preload is introduced.  
- Capture one immutable `as_of` timestamp and effective policy at job start; later clock, setting, and database changes must not alter the run.  
- Preserve deterministic tie-breaking and existing Rayon parallelism; aggregate provider output in a deterministic order.  
- This slice excludes Lyrion provider discovery, provider settings-page ownership, direct Last.fm acquisition, and the future native `bliss-mixer` host.  

## Review Focus

- Zero-valued controls are explicit disables, not absent defaults or inherited values.  
- A never-played track and an unknown/absent database row remain distinguishable and follow Lab semantics.  
- Date signals use the Lab exponential saturation curve, including future timestamps and horizon boundaries.  
- Target-share applies only to declared host policy channels and cannot make an ineligible or acoustically rejected candidate selectable.  
- Provider failures, missing identity coverage, and empty support sets leave the exact Bliss-only decision path intact.  

---

## File structure

| Repository | Files | Responsibility |
| --- | --- | --- |
| `bliss-playlist-guidance-spi` | `src/policy.rs`, `src/lib.rs`, `SPI.md`, `README.md` | Pure shared policy types, channel-policy capability declarations, and mathematical transforms; no process, LMS, or network I/O. |
| `bliss-guidance-playcounts` | `src/main.rs`, `README.md` | Rename/document as library-signals provider where required; emit frozen raw play-count/date signals using explicit prepare options. |
| `bliss-guidance-lastfm` | `src/main.rs`, `README.md` | Advertise strategy-neutral artist/track observations and supported host policies; preserve source-artifact-only acquisition during the hybrid migration. |
| `bliss-playlist-optimizer` | `src/guidance.rs`, `src/lib.rs`, `tests/contracts.rs`, fixture requests/results, `README.md` | Replace private aggregation math with the shared policy module and report effective policy/provenance. |
| `lms-better-call-bliss` | `BetterCallBliss/{Defaults,JobOptions,RequestBuilder,CandidateGuidance,GuidanceReporting,Settings,Web,strings.txt}.pm`, settings/Extras templates, tests | Capture per-job controls, map them to provider policy/options, and present effective guidance decisions. |

### Task 1: Add the shared, pure-Rust guidance policy module

**Files:**

- Create: `D:\LMS\bliss-playlist-guidance-spi\src\policy.rs`
- Modify: `D:\LMS\bliss-playlist-guidance-spi\src\lib.rs`
- Modify: `D:\LMS\bliss-playlist-guidance-spi\SPI.md`
- Modify: `D:\LMS\bliss-playlist-guidance-spi\README.md`

**Interfaces:**

- Produces `GuidancePolicyEntry`, `AppliedGuidanceContribution`, `bounded_multiplier`, `target_share_multiplier`, and `saturating_time_signal`.  
- `GuidancePolicyEntry` is keyed by `(provider_id, channel)` and carries signed bounded influence plus optional host-owned `target_percent`; it does not contain source credentials.  
- `ChannelDescriptor` declares supported host policy kinds. `lastfm_artist` may declare `bounded_influence` and `target_share`; `lastfm_track`, play count, last played, and library age declare bounded influence only.  
- `saturating_time_signal(timestamp, as_of, horizon_days, zero_means_never)` exactly matches Lab's `exp(-age/horizon)` transformation and returns `None` for unknown library-added values.  

- [ ] **Step 1: Write failing unit tests for the policy module**

Cover bounded contribution clamping, deterministic contribution ordering, Lab-equivalent exponential date signals, never-played handling, future timestamps, zero influence, and target-share multipliers for sparse support.

- [ ] **Step 2: Run the SPI tests and verify the new tests fail for missing policy APIs**

Run: `cargo test --locked` in `D:\LMS\bliss-playlist-guidance-spi`  
Expected: compile failure naming the new policy module/functions.

- [ ] **Step 3: Implement the pure policy APIs**

Keep all operations deterministic and free of host I/O. Use `exp(ln(10) * influence * signal)` for Lab-compatible bounded multipliers. Document that target share is host policy, not a Last.fm-provider behavior, and validate requested policies against the provider's declared channel capability.

- [ ] **Step 4: Run the SPI suite and commit**

Run: `cargo test --locked`  
Expected: PASS.  
Commit: `feat: add shared guidance policy semantics`

### Task 2: Make the library-signals provider emit Lab-compatible frozen observations

**Files:**

- Modify: `D:\LMS\bliss-guidance-playcounts\src\main.rs`
- Modify: `D:\LMS\bliss-guidance-playcounts\README.md`
- Modify: `D:\LMS\bliss-guidance-playcounts\Cargo.toml`

**Interfaces:**

- Consumes prepare `options`: `as_of_unix_seconds`, `last_played_horizon_days`, and `library_age_horizon_days`.  
- Produces `playcount`, `last_played`, and `library_age` signals with provider diagnostics declaring frozen timestamp, horizons, row coverage, and cache/batch counts.  
- Uses `saturating_time_signal` from the shared SPI policy module; play-count keeps its existing stable percentile observation.  

- [ ] **Step 1: Write failing provider tests against a fixture `tracks_persistent` database**

Assert that a 0 `lastPlayed` value means never played, unknown rows emit no signal, added=0 emits no library-age signal, and dates at/after the fixed `as_of` time receive the newest-track signal. Assert that scoring the same candidate after an external SQLite update uses the prepared snapshot.

- [ ] **Step 2: Run the provider tests and verify the semantic tests fail**

Run: `cargo test --locked` in `D:\LMS\bliss-guidance-playcounts`  
Expected: date expectations fail because the current implementation uses global rank percentiles.

- [ ] **Step 3: Parse and validate frozen prepare options; use shared date transforms**

Validate horizons at the Lab-compatible host range and retain the current bounded SQLite batching/cache behavior. Do not add a full-catalog preload.

- [ ] **Step 4: Update provider documentation, run tests, and commit**

Run: `cargo test --locked`  
Expected: PASS.  
Commit: `feat: align library signal observations with Lab semantics`

### Task 3: Make Last.fm artist policy capability explicit without moving policy into the provider

**Files:**

- Modify: `D:\LMS\bliss-guidance-lastfm\src\main.rs`
- Modify: `D:\LMS\bliss-guidance-lastfm\README.md`
- Test: `D:\LMS\bliss-guidance-lastfm\tests\*` or the existing unit-test module

**Interfaces:**

- The manifest declares `lastfm_artist` compatible with `bounded_influence` and `target_share`; `lastfm_track` is compatible with `bounded_influence` only.  
- The provider continues to consume Better Call Bliss's immutable LastMix-derived artifact and anchor identities, then returns normalized raw support/confidence/provenance. It does not receive credentials, rank candidates, calculate multipliers, or choose a target share.  
- Identical prepared evidence must produce identical raw artist observations irrespective of the host policy that later consumes them.  

- [ ] **Step 1: Write failing provider contract tests for policy capability and raw-observation independence**

Assert the manifest capability declarations, independent `lastfm_track`/`lastfm_artist` channels, canonical artist identity provenance, and equal raw artist observations for bounded-influence versus target-share host consumption.

- [ ] **Step 2: Run the Last.fm provider tests and verify the capability tests fail**

Run: `cargo test --locked` in `D:\LMS\bliss-guidance-lastfm`  
Expected: missing channel-policy capability metadata or assertions against undocumented behavior.

- [ ] **Step 3: Implement declarations and documentation only at the provider boundary**

Add the channel-policy capability metadata and explain the split of responsibility: the provider owns LastMix artifact interpretation, identity matching, and evidence provenance; the shared host policy owns bounded multipliers and target-share selection. Do not duplicate optimizer policy math in this provider.

- [ ] **Step 4: Run the suite and commit**

Run: `cargo test --locked`  
Expected: PASS.  
Commit: `feat: declare Last.fm artist guidance policy capability`

### Task 4: Extract optimizer aggregation onto the shared policy module

**Files:**

- Modify: `D:\LMS\bliss-playlist-optimizer\src\guidance.rs`
- Modify: `D:\LMS\bliss-playlist-optimizer\src\lib.rs`
- Modify: `D:\LMS\bliss-playlist-optimizer\tests\contracts.rs`
- Modify: `D:\LMS\bliss-playlist-optimizer\fixtures\synthetic\*guidance*.json`
- Modify: `D:\LMS\bliss-playlist-optimizer\README.md`

**Interfaces:**

- Consumes shared `GuidancePolicyEntry` and provider signals from SPI v2.  
- Produces deterministic applied-contribution provenance with signal, effective influence/multiplier, target-share policy where configured, and neutralized-provider diagnostics.  
- Keeps `GuidanceAddonConfig` process lifecycle and bounded score batches intact.
- Rejects or neutralizes a requested policy when the selected provider/channel does not declare support for it; no implicit substitution from target share to bounded influence is permitted.

- [ ] **Step 1: Write failing optimizer fixtures for bounded artist influence, target-share artist policy, and local date channels**

Use an identical Bliss-ranked candidate pool to demonstrate that bounded influence competes with play count/date signals, while target share intentionally seeks supported candidates only within that pool.

- [ ] **Step 2: Run focused contract tests and verify the new fixtures fail**

Run: `cargo test --locked guidance` in `D:\LMS\bliss-playlist-optimizer`  
Expected: assertions fail because the private aggregation path has no Lab-equivalent date policy or shared policy provenance.

- [ ] **Step 3: Replace private policy math with SPI policy helpers**

Retain the optimizer's process session, timeout, candidate-index validation, contribution cap, and deterministic tie breaking. Remove duplicated formulas only after the replacement tests pass.

- [ ] **Step 4: Run the full optimizer suite and commit**

Run: `cargo test --locked`  
Expected: PASS.  
Commit: `refactor: share optimizer guidance policy semantics`

### Task 5: Give Better Call Bliss equivalent effective policy controls

**Files:**

- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\Defaults.pm`
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\JobOptions.pm`
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\RequestBuilder.pm`
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\CandidateGuidance.pm`
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\Settings.pm`
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\Web.pm`
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\strings.txt`
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\HTML\EN\plugins\BetterCallBliss\settings\bettercallbliss.html`
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\HTML\EN\plugins\BetterCallBliss\index.html`
- Test: `D:\LMS\lms-better-call-bliss\tests\{job_options,candidate_guidance,request_json_types,lastfm_evidence,log_diagnostics}.t`

**Interfaces:**

- Captures per-job `lastfm_artist_mode` (`bounded_influence` or `target_share`), signed Last.fm track/artist and local-signal influences, date horizons, and one job-start `as_of_unix_seconds`.  
- Maps these controls to provider-specific `Prepare.options` plus host `GuidancePolicyEntry` values.  
- Preserves LastMix acquisition on the Perl side for this slice; it supplies the immutable Last.fm artifact, while the Rust provider resolves/scales it.  
- Shows only artist-policy choices declared by the installed Last.fm provider; a missing or incompatible provider leaves the corresponding channel neutral with an explicit diagnostic rather than silently applying a different policy.  

- [ ] **Step 1: Write failing Perl contract tests for defaults, explicit zero overrides, JSON types, and request mapping**

Assert that target-share artist mode produces a host target policy, bounded artist mode produces a signed bounded policy, track guidance is a bounded channel, and the two date channels pass one frozen timestamp/horizon set to the library-signals provider.

- [ ] **Step 2: Run the focused Perl tests and verify they fail**

Run: `prove -l tests/job_options.t tests/candidate_guidance.t tests/request_json_types.t tests/lastfm_evidence.t tests/log_diagnostics.t` in `D:\LMS\lms-better-call-bliss`  
Expected: missing option keys and policy entries.

- [ ] **Step 3: Implement setting/job normalization and request construction**

Use source-specific labels: Last.fm artist strategy is host policy; Last.fm acquisition remains a provider-input concern. Keep controls disabled/hidden when no compatible provider binary is available and preserve Bliss-only behavior with all influences at zero.

- [ ] **Step 4: Add effective-policy reporting and update product documentation**

Report each applied addition/bridge contribution plus the frozen policy and neutralized provider causes. Update `README.md`, `ALGORITHMS.md`, and `docs/GUIDANCE_DATA_FLOW.md` with the final current behavior; do not describe future discovery as implemented.

- [ ] **Step 5: Run the full plugin suite and commit**

Run: `prove -l tests` and `python -m unittest discover -s tests -p "test_*.py"`  
Expected: PASS.  
Commit: `feat: add Lab-equivalent guidance policy controls`

### Task 6: Cross-repository parity fixtures, packaging, and Raspberry Pi verification

**Files:**

- Modify: release/version metadata and source manifests only after all prior tests are green.
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\Bin\SOURCE.md`
- Modify: relevant README/release notes in the optimizer and providers.

**Interfaces:**

- Produces platform binaries whose reported SPI/version metadata agree with Better Call Bliss compatibility checks.  
- Produces a frozen parity fixture containing the same candidate observations and expected bounded/target-share decisions as BlissMixerLab.

- [ ] **Step 1: Add an end-to-end parity fixture**

Use fixed candidate IDs, Last.fm artifact, Lyrion SQLite fixture, `as_of`, policy modes, and expected applied contributions. Test Bliss-only fallback, bounded artist influence, target-share artist mode, and both date channels.

- [ ] **Step 2: Build and test each Rust repository from a clean checkout**

Run `cargo test --locked` in SPI, Last.fm guidance, library signals, and optimizer; run Better Call Bliss's full CI-equivalent Perl/Python suite.

- [ ] **Step 3: Publish coordinated provider/optimizer artifacts and package Better Call Bliss**

Update binary source metadata only to released artifact tags. Verify the packaging workflow validates executable metadata and includes all platform-specific binaries.

- [ ] **Step 4: Deploy to `192.168.1.111` and verify with real previews**

Run one Bliss-only baseline and controlled previews for each policy mode. Confirm logs and preview reports show frozen `as_of`, active channels, applied contributions, neutral fallback where applicable, and no change to hard eligibility/repeat/genre behavior.

- [ ] **Step 5: Commit release metadata and record verification evidence**

Commit each repository independently with no generated binaries tracked in source repositories.

## Self-review

- The plan separates provider observation from host policy and leaves discovery out of scope. Last.fm is now an explicit provider deliverable: it advertises artist-policy compatibility, preserves strategy-neutral observations, and proves that target-share behavior is not hidden inside the provider.  
- Every Lab-only semantic has a named Rust destination: exponential date signals in the provider/shared policy module, explicit Last.fm artist capabilities in the Last.fm provider, bounded artist/track influence and target share in shared host policy, plus job-level Better Call Bliss controls.  
- The current migration document's linear-looking pseudocode must be corrected during Task 1: the implementation of record is Lab's exponential `exp(-age/horizon)` curve.  
- Each repository has a test-first task and a focused verification command before its commit.  
