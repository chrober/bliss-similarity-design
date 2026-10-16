# MBID-aware Repeat Identity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enforce artist repeat windows with structured Lyrion artist identities in Bliss Mixer Lab and Better Call Bliss while retaining explicit legacy text-credit compatibility.

**Architecture:** Lyrion hosts publish an immutable `lyrion-track-identities-v1` SQLite snapshot keyed by the exact Bliss `database_file`. `bliss-mixer-core` loads and compares canonical artist identity sets; `bliss-mixer` and `bliss-playlist-optimizer` apply that shared hard constraint before optional guidance. Host UIs expose the same three-value artist-repeat policy and preserve existing logging.

**Tech Stack:** Rust, rusqlite, serde, Perl, DBI/DBD::SQLite, Lyrion contributor metadata, JSON/SQLite artifacts.

**Spec:** `../../../MBID_REPEAT_IDENTITY_DESIGN.md`

**Implementation status (2026-10-16):** The shared core, both native hosts,
both Lyrion hosts, request/schema plumbing, settings, and focused regression
tests are implemented on isolated feature branches/worktrees. Core, mixer, and
optimizer Rust suites pass; changed non-DBI Perl contract suites pass. The
remaining gates are the DBI-backed plugin integration tests in LMS/CI, the
200,000-track performance fixture, dependency pinning/builds, and live Pi
verification. Optimizer artifact failures now produce an explicit fallback
state instead of aborting the job, and Better Call Bliss's preserved-order and
spacing prechecks use the selected structured identity policy. Current
Optimizer and Better Call Bliss `main` changes are integrated, and the shared
Better Call Bliss Perl identity helper prevents the inventory, request builder,
and preserved-order checks from drifting apart.  

## Global Constraints

- MusicBrainz artist ID is preferred, followed by snapshot-local Lyrion contributor ID, followed by normalized artist name.
- Shared mode uses only complete track-level `ARTIST` and `TRACKARTIST` relations plus primary-artist fallback; album artist and Various Artists never become shared artist keys.
- `shared_artist`, `primary_artist`, and `exact_bliss_credit` have identical meanings in every host.
- Repeat constraints remain hard; guidance cannot re-admit a blocked candidate.
- Existing Better Call Bliss and Bliss Mixer Lab log bodies remain byte-for-byte unchanged; new repeat diagnostics use separate lines or structured fields.
- Missing or invalid identity data falls back per track and must not crash or disable the complete mix/preview.
- Warm requests reuse a snapshot/cache and must not query Lyrion once per candidate.

## Review Focus

- A collaboration with multiple contributor rows where only one artist overlaps must be rejected in shared mode but not necessarily in primary mode.
- A composite-only display credit must remain one conservative fallback key and must not be punctuation-split.
- A stale, incomplete, corrupt, or differently bound snapshot must degrade to exact Bliss credit without admitting an otherwise detected stable-identity repeat.
- Snapshot generation must remain bounded for 200,000-track libraries and must not block every warm DSTM request.
- Cue tracks, filename case, virtual-library candidates, and source/history tracks must resolve to the same exact `database_file` identity as Bliss.

---

### Task 1: Shared Rust repeat-identity contract

**Files:**
- Create: `D:/LMS/bliss-mixer-core/src/repeat_identity.rs`
- Modify: `D:/LMS/bliss-mixer-core/src/lib.rs`
- Modify: `D:/LMS/bliss-mixer-core/Cargo.toml`

**Interfaces:**
- Produces: `ArtistRepeatMode`, `ArtistIdentitySet`, `TrackIdentitySnapshot::open_read_only`, `artist_repeat_matches`, and `canonical_name_key`.
- Consumes: `lyrion-track-identities-v1` SQLite tables from the spec.

- [ ] Write tests for MBID precedence, contributor fallback, normalized-name fallback, shared intersection, primary-only behavior, exact-credit compatibility, missing rows, Various Artists exclusion, and malformed snapshots.
- [ ] Run the focused tests and verify they fail because the module/API is absent.
- [ ] Implement the transport-neutral types, comparison helpers, schema validation, and batched read-only snapshot loader.
- [ ] Run `cargo fmt --check`, `cargo clippy --locked --all-targets --all-features -- -D warnings`, and `cargo test --locked --all-features`.

### Task 2: Native mixer repeat filtering

**Files:**
- Modify: `D:/LMS/bliss-mixer/Cargo.toml`
- Modify: `D:/LMS/bliss-mixer/src/api.rs`
- Modify: `D:/LMS/bliss-mixer/API.md`

**Interfaces:**
- Consumes: Task 1 repeat identity types and snapshot loader.
- Produces: optional `artist_identity_snapshot` and `artist_repeat_mode` mix request fields with legacy behavior when absent/invalid.

- [ ] Add API tests reproducing `Queen & David Bowie` versus `Queen` with a shared Queen MBID, all three modes, candidate-batch self-repeats, and invalid-snapshot fallback.
- [ ] Run the focused test and observe exact-text filtering admit the false negative.
- [ ] Replace artist-string membership checks with shared identity keys while preserving all existing album/title/ID filtering and response/log formats.
- [ ] Pin the Task 1 core revision locally for verification and run the full locked Rust suite.

### Task 3: Bliss Mixer Lab snapshot and policy

**Files:**
- Create: `D:/LMS/lms-blissmixer-lab/BlissMixerLab/RepeatIdentitySnapshot.pm`
- Modify: `D:/LMS/lms-blissmixer-lab/BlissMixerLab/Plugin.pm`
- Modify: `D:/LMS/lms-blissmixer-lab/BlissMixerLab/Settings.pm`
- Modify: `D:/LMS/lms-blissmixer-lab/BlissMixerLab/HTML/EN/plugins/BlissMixerLab/settings/blissmixerlab.html`
- Modify: `D:/LMS/lms-blissmixer-lab/BlissMixerLab/strings.txt`
- Test: `D:/LMS/lms-blissmixer-lab/tests/repeat_identity_snapshot.t`
- Test: `D:/LMS/lms-blissmixer-lab/tests/settings_contract.t`
- Test: `D:/LMS/lms-blissmixer-lab/tests/plugin_contract.t`

**Interfaces:**
- Consumes: Task 2 request fields and the shared SQLite schema.
- Produces: cached snapshot path and `artist_repeat_mode` in every DSTM mix request.

- [ ] Capture current released Lab log fixtures and add failing tests for snapshot rows, Queen contributor identity, settings normalization, request fields, cache reuse, and fallback.
- [ ] Build snapshots atomically from Lyrion `tracks`, `contributors`, and `contributor_track`, keyed by exact `_trackToPath`/Bliss path identity and scan identity.
- [ ] Add the three-value setting under existing mix settings without changing unrelated layout or established log bodies.
- [ ] Run `prove -l tests` and repository validators.

### Task 4: Optimizer identity-aware repeat engine

**Files:**
- Modify: `D:/LMS/bliss-playlist-optimizer/Cargo.toml`
- Modify: `D:/LMS/bliss-playlist-optimizer/schemas/optimizer-request-v1.schema.json`
- Modify: `D:/LMS/bliss-playlist-optimizer/src/main.rs`
- Modify: `D:/LMS/bliss-playlist-optimizer/src/route.rs`
- Modify: `D:/LMS/bliss-playlist-optimizer/src/bridge.rs`
- Modify: `D:/LMS/bliss-playlist-optimizer/src/anchored_path.rs`
- Modify: `D:/LMS/bliss-playlist-optimizer/src/preview.rs`
- Test: `D:/LMS/bliss-playlist-optimizer/tests/contracts.rs`

**Interfaces:**
- Consumes: Task 1 comparison helpers and `artifacts.track_identities`.
- Produces: identity-aware route tracks and the same artist-repeat semantics across reorder, spacing, extension, gap, and destination routes.

- [ ] Add failing schema/core tests for the Queen case, shared collaboration intersections, primary mode, exact-credit mode, history-versus-generated behavior, and malformed/missing artifact fallback.
- [ ] Load the shared snapshot once, enrich library/source/history route tracks, and route every artist comparison through the shared helper.
- [ ] Preserve current result schemas; add only structured repeat-identity provenance where backward-compatible.
- [ ] Run formatting, clippy, all locked tests, and the existing synthetic contract suite.

### Task 5: Better Call Bliss snapshot, source identities, and job policy

**Files:**
- Modify: `D:/LMS/lms-better-call-bliss/BetterCallBliss/CandidateInventory.pm`
- Modify: `D:/LMS/lms-better-call-bliss/BetterCallBliss/RequestBuilder.pm`
- Modify: `D:/LMS/lms-better-call-bliss/BetterCallBliss/JobOptions.pm`
- Modify: `D:/LMS/lms-better-call-bliss/BetterCallBliss/Defaults.pm`
- Modify: `D:/LMS/lms-better-call-bliss/BetterCallBliss/Settings.pm`
- Modify: `D:/LMS/lms-better-call-bliss/BetterCallBliss/Web.pm`
- Modify: `D:/LMS/lms-better-call-bliss/BetterCallBliss/HTML/EN/plugins/BetterCallBliss/index.html`
- Modify: `D:/LMS/lms-better-call-bliss/BetterCallBliss/HTML/EN/plugins/BetterCallBliss/settings/bettercallbliss.html`
- Modify: `D:/LMS/lms-better-call-bliss/BetterCallBliss/strings.txt`
- Test: `D:/LMS/lms-better-call-bliss/tests/candidate_inventory_library.t`
- Test: `D:/LMS/lms-better-call-bliss/tests/job_options.t`
- Test: `D:/LMS/lms-better-call-bliss/tests/request_json_types.t`

**Interfaces:**
- Consumes: Task 4 request/schema contract.
- Produces: complete track-level source/candidate artist identities, snapshot artifact descriptor, global default, and per-job override.

- [ ] Add failing tests for multi-artist contributor capture, primary fallback, virtual-library filtering, exact path identity, three policy values, normalized request typing, and preservation across retry/result forms.
- [ ] Extend the existing inventory pass and identity lookup instead of adding a second whole-library scan.
- [ ] Capture complete source/history artist relations and bind the shared snapshot to the exact Bliss database/cache identity.
- [ ] Add the same localized policy control to settings and Extras, defaulting to `shared_artist`.
- [ ] Run `prove -l tests` and repository validators.

### Task 6: Documentation and cross-repository verification

**Files:**
- Modify: `D:/LMS/bliss-similarity-design/MBID_REPEAT_IDENTITY_DESIGN.md`
- Modify: affected component READMEs/architecture docs only where they own the new contract.

**Interfaces:**
- Consumes: all implemented request/artifact/config names.
- Produces: status-accurate docs and verification evidence.

- [ ] Update the proposed design with exact implemented schema/API names and status, without copying host/provider details into unrelated READMEs.
- [ ] Run every repository's full test/validation commands and inspect all diffs for generated binaries, private fixtures, log-format changes, and unrelated files.
- [ ] Run deterministic synthetic 200,000-track snapshot/load checks and record cold/warm timing and peak-size evidence.
- [ ] Perform a whole-change review against the design, especially the five Review Focus cases.
