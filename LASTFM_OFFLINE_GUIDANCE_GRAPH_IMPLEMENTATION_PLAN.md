# Last.fm offline guidance graph implementation plan

**Date:** 2026-10-22  
**Status:** Core graph, provider controls and maintenance implemented and released; see current status below
**Primary owners:** `bliss-guidance-lastfm`, `lms-guidance-lastfm`  

> **For agentic workers:** REQUIRED SUB-SKILL: use
> `superpowers:executing-plans` to implement this plan task by task.

**Goal:** Replace the direct API-key path's whole-file JSON cache with a
provider-owned SQLite similarity graph, add API-key-only read-through and
library-artist synchronization, and preserve LastMix behavior exactly.

**Architecture:** `lms-guidance-lastfm` owns the API key, provider preferences,
Lyrion artist-root snapshot and background-job UI. `bliss-guidance-lastfm` owns
the SQLite repository, direct HTTP acquisition, frozen per-job reads and the
maintenance CLI. Compatible hosts remain source-agnostic and Bliss-first.
LastMix continues to supply its existing resolved job artifact and never opens
or modifies the SQLite graph.

**Tech stack:** Rust 2021, `rusqlite` with bundled SQLite, `ureq`, Serde/JSONL,
Perl/Lyrion plugin APIs, Test::More, GitHub Actions cross-platform builds.

**Specification:**
[`LASTFM_OFFLINE_GUIDANCE_GRAPH_DESIGN.md`](LASTFM_OFFLINE_GUIDANCE_GRAPH_DESIGN.md)

## Current implementation status (2026-11-02)

The native and Lyrion provider main branches contain the released API-key-only
artist graph and maintenance workflow. Provider `0.3.6` and native `0.2.5`
record later persistence-notification work; check the actual package pin and
published artifacts before using these as deployment evidence. Real Pi library
updates and host lookups have been exercised, but individual rate-limit,
recovery and cross-platform scenarios below are not all established as tested.
Track observations remain in a separate short-lived JSON cache. Online results
serve the current job before asynchronous persistence completes; database
membership refresh is low-priority and does not initiate a bulk Last.fm scan.
The configurable retained-data budget defaults to 100 decimal MB.

The table and detailed task checklist below preserve the 2026-10-23 planning
snapshot; they are historical, not the current release gate.

## Historical implementation snapshot (2026-10-23)

| Area | State | Remaining gate |
| --- | --- | --- |
| Native SQLite graph, MBID-first identity, migration, freshness, read-through, limits and policies | Implemented, committed and locally tested on `feature/offline-lastfm-graph` | Cross-platform release build and Pi acceptance |
| Native maintenance CLI and JSONL progress | Implemented and locally tested | Long-running real-library, cancellation, rate-limit and storage-budget verification on the Pi |
| Provider-owned paths, settings, library-root snapshot and background job | Implemented, committed and locally tested on `feature/offline-lastfm-graph` | Material/Lyrion live UI and restart-recovery verification |
| Manual settings-page update | Implemented with JSON-RPC start/status/pause/resume/cancel polling; normal Save remains explicit | Real API-key synchronization test on the Pi |
| LastMix isolation | Covered by source gating and existing artifact-path tests | Filesystem-open proof on packaged Pi build |
| Generic host cleanup | Old Last.fm JSON-cache paths removed in local main-branch commits for Better Call Bliss and Bliss Mixer Lab | Complete host suites and released package verification |
| Documentation and release | In progress | Version bumps, GitHub binaries, package/feed inspection and deployment require a later explicit release/deploy request |

## Global constraints

- The graph path is reachable only when the resolved source is **API Key**.
- LastMix must not open, read, populate, refresh, migrate, delete, compact, or
  report the graph. Its artifact behavior and established logs stay unchanged.
- The API key remains process-environment-only. It must not enter requests,
  files, SQLite, command arguments, progress JSONL, diagnostics, fixtures, or
  logs.
- `prepare` may read stored observations and perform bounded direct HTTP work;
  `score` remains network-free and uses a frozen in-memory snapshot.
- A later offline job can rely on an online miss only after its independent
  persistence succeeds; the current job need not wait for the commit.
- Artist edges are directional. A response for `A` must never synthesize
  `B -> A`.
- MBIDs are authoritative; normalized names are only controlled fallbacks.
- Library synchronization is manually started and never enters preview or DSTM
  latency paths.
- Normal operation must remain bounded on Raspberry Pi hardware and on a
  200,000-track library.
- Existing Better Call Bliss preview wording and Bliss Mixer Lab selection-log
  formatting are compatibility contracts.
- Intentional Markdown line breaks use two trailing spaces.

## Review focus

- Verify every source switch before a store object is constructed.
- Verify that no host-specific graph implementation leaks into Better Call
  Bliss or Bliss Mixer Lab.
- Verify transaction boundaries, WAL size accounting and cancellation between
  roots.
- Verify that the result-limit setting records requested and actual counts
  instead of assuming Last.fm honored `25`, `50`, or `100`.
- Verify LastMix with a filesystem-open spy, not only by comparing output.

---

## Task 1: Establish native store contracts and schema

**Repository:** `D:\LMS\bliss-guidance-lastfm`  
**Files:**

- Modify: `Cargo.toml`
- Modify: `Cargo.lock`
- Modify: `src/main.rs`
- Create: `src/store/mod.rs`
- Create: `src/store/schema.rs`
- Create: `src/store/repository.rs`
- Create: `tests/store_repository.rs`

**Steps:**

1. Add failing repository tests for schema creation, schema-version rejection,
   WAL mode, busy timeout, positive and empty observations, transactional edge
   replacement, and rollback on failure.
2. Add `rusqlite` with bundled SQLite so GitHub can build every target without
   relying on system development headers.
3. Implement the design's artist, artist-alias, artist-query,
   artist-similarity-edge, library-snapshot, library-membership, track,
   track-query and track-similarity-edge tables plus required indexes.
4. Keep timestamps as UTC Unix seconds and make repository calls accept an
   explicit clock value for deterministic tests.
5. Expose typed repository operations; do not let `direct.rs` issue ad-hoc SQL.
6. Run:

   ```powershell
   cargo test --test store_repository
   cargo fmt --all -- --check
   cargo clippy --all-targets --all-features -- -D warnings
   ```

7. Commit: `feat: add Last.fm guidance SQLite repository`.

## Task 2: Implement MBID-first graph identity

**Repository:** `D:\LMS\bliss-guidance-lastfm`  
**Files:**

- Modify: `src/store/repository.rs`
- Create: `src/store/identity.rs`
- Modify: `tests/store_repository.rs`
- Create: `tests/graph_identity.rs`

**Steps:**

1. Add failing tests for MBID precedence, safe name-to-MBID promotion,
   ambiguous same-name artists, name-only fallbacks, Recording MBIDs, and
   independent reverse edges.
2. Implement normalized artist/title keys in one shared module and remove
   duplicated normalization from callers.
3. Resolve or create source and target nodes before replacing one source's
   directed outgoing edges.
4. Store aliases without merging two distinct non-empty MBIDs.
5. Add indexed batched lookups for all anchors needed by one prepare call.
6. Run the focused tests, then the complete `cargo test --all-features` suite.
7. Commit: `feat: add MBID-first Last.fm graph identity`.

## Task 3: Preserve and migrate the legacy API-key JSON cache

**Repository:** `D:\LMS\bliss-guidance-lastfm`  
**Files:**

- Rename: `src/cache.rs` to `src/legacy_cache.rs`
- Modify: `src/main.rs`
- Modify: `src/store/repository.rs`
- Create: `tests/legacy_cache_migration.rs`
- Create: `tests/fixtures/lastfm-cache-v1.json`
- Create: `tests/fixtures/lastfm-cache-v1-corrupt.json`

**Steps:**

1. Add failing tests for one-time import, positive and negative entries,
   timestamp retention, idempotence, corrupt-file preservation and no
   migration when acquisition mode is `artifact`.
2. Turn the old cache code into a read-only schema-v1 parser.
3. Acquire its existing lock, import in one transaction, verify counts, record
   migration metadata and only then remove the valid legacy JSON.
4. Keep corrupt or unknown files and emit a structured warning.
5. Add a filesystem-open regression test proving artifact/LastMix prepare does
   not touch either the JSON cache or SQLite path.
6. Run focused migration tests and all native tests.
7. Commit: `feat: migrate direct Last.fm cache into SQLite`.

## Task 4: Add HTTP freshness, validators and configurable limits

**Repository:** `D:\LMS\bliss-guidance-lastfm`  
**Files:**

- Modify: `src/lastfm_api.rs`
- Create: `src/freshness.rs`
- Modify: `src/store/repository.rs`
- Create: `tests/http_freshness.rs`

**Steps:**

1. Add mock-server tests for `Cache-Control`, `Expires`, `ETag`,
   `Last-Modified`, conditional requests, `304`, unchanged `200`, changed
   `200`, empty results, HTTP 429 and transport errors.
2. Return a typed response envelope from `lastfm_api.rs`: parsed results,
   requested limit, actual count, relevant headers and response status.
3. Make artist requests accept `25`, `50`, or `100`; retain the current bounded
   track lookup limit.
4. Compute the canonical ordered-result hash over method, source identity,
   target identity, rank and normalized score.
5. Apply the design's fallback freshness windows only when HTTP metadata does
   not give a usable lifetime.
6. Ensure failures never replace the last complete observation.
7. Run focused tests, all native tests, format and Clippy.
8. Commit: `feat: persist Last.fm freshness and validators`.

## Task 5: Replace direct prepare with API-key-only SQLite read-through

**Repository:** `D:\LMS\bliss-guidance-lastfm`  
**Files:**

- Modify: `src/direct.rs`
- Modify: `src/main.rs`
- Modify: `src/store/repository.rs`
- Create: `tests/direct_read_through.rs`

**Steps:**

1. Add failing end-to-end tests for `online_with_cache`, `offline_preferred`
   and `offline_only`; warm-cache network blocking; stale fallback; missing
   neutral guidance; result-limit expansion; and persistence failure.
2. Replace `cache_path`/TTL internals with trusted `store_path`, retrieval
   policy, artist result limit and storage scope.
3. Open the SQLite store only after `acquisition_mode == direct` has been
   validated and the API key has been obtained from the environment.
4. Batch-read all source observations, fetch only required misses or
   revalidations, persist complete responses transactionally and then freeze
   the relations in `DirectPrepared`.
5. Preserve existing `lastfm_track` and `lastfm_artist` scoring semantics.
6. Extend structured diagnostics with `fresh`, `cached`, `stale_offline`,
   `missing`, `partial`, `rate_limited` and `persistence_failed` counts without
   changing established host-rendered message bodies.
7. Add a test that runs `prepare`, blocks network, runs a new process and gets
   the same signals from SQLite.
8. Run all native checks.
9. Commit: `feat: use offline graph for direct Last.fm guidance`.

## Task 6: Add the native graph-maintenance CLI

**Repository:** `D:\LMS\bliss-guidance-lastfm`  
**Files:**

- Modify: `src/main.rs`
- Create: `src/maintenance.rs`
- Create: `src/root_snapshot.rs`
- Create: `src/progress.rs`
- Create: `tests/maintenance_cli.rs`
- Create: `tests/fixtures/library-artist-roots-v1.json`

**Steps:**

1. Add failing CLI tests for `graph status`, `graph sync`, `graph compact` and
   `graph delete` with trusted request files and no credential arguments.
2. Define `lastfm-library-artist-roots-v1` with snapshot identity, generation
   time and distinct `{lms_contributor_id, name, artist_mbids[]}` roots.
3. Make `graph sync` validate the snapshot, store membership, skip sufficient
   observations and process only missing or refresh-eligible roots.
4. Emit versioned JSONL progress containing phase, current/total roots,
   request/cache/change/failure counts and database bytes.
5. Default to one request worker and at most one request per second; implement
   bounded retry/backoff and stop on rate-limit retry time.
6. Check the 80 MB main/WAL/legacy/provider-backup budget before a batch and
   after a deliberate checkpoint.
7. Treat cancellation as a cooperative stop between roots; committed roots
   remain resumable.
8. Ensure every graph command refuses to run without API-key mode and a
   process-environment API key, except read-only `status` and explicit local
   deletion.
9. Run CLI tests, all native checks and the binary's `version --json` contract.
10. Commit: `feat: add Last.fm graph maintenance commands`.

## Task 7: Move trusted graph configuration into the provider plugin

**Repository:** `D:\LMS\lms-guidance-lastfm`  
**Files:**

- Modify: `LastFmGuidance/Provider.pm`
- Modify: `LastFmGuidance/Settings.pm`
- Modify: `LastFmGuidance/Plugin.pm`
- Modify: `tests/provider_descriptor.t`
- Modify: `tests/settings_contract.t`
- Modify: `tests/plugin_contract.t`

**Steps:**

1. Add failing tests for provider-owned store/root/progress paths, retrieval
   policy, storage scope, result limit and API-key-only visibility.
2. Add provider preferences for retrieval policy, storage scope and artist
   result limit. Do not publish them as host-overridable descriptor controls.
3. Derive all paths from Lyrion's trusted cache directory inside the provider;
   reject web- or host-supplied executable/store/root paths.
4. For direct mode, return trusted native options for store path and policies.
   For LastMix, keep the existing artifact config byte-for-byte and omit every
   graph option.
5. Expand native capability checks so incompatible pre-graph binaries fail
   clearly only when API Key graph behavior is required.
6. Forward maintenance status methods through `Plugin.pm` without exposing the
   API key.
7. Run all Perl tests.
8. Commit: `feat: own API-key graph configuration in Last.fm provider`.

## Task 8: Add Lyrion artist snapshot and background synchronization

**Repository:** `D:\LMS\lms-guidance-lastfm`  
**Files:**

- Create: `LastFmGuidance/LibrarySnapshot.pm`
- Create: `LastFmGuidance/GraphJobs.pm`
- Modify: `LastFmGuidance/Provider.pm`
- Modify: `LastFmGuidance/Plugin.pm`
- Create: `tests/library_snapshot.t`
- Create: `tests/graph_jobs.t`

**Steps:**

1. Add failing tests for distinct contributors, all stored Artist MBIDs,
   stable snapshot ordering, frozen library identity and bounded streaming.
2. Read only local music-library contributors from Lyrion; do not copy track
   rows or Last.fm data into the root snapshot.
3. Write the versioned snapshot atomically beneath the provider cache root.
4. Start the native process asynchronously with the API key only in its
   environment and parse progress JSONL without blocking LMS's event loop.
5. Implement single-job exclusion, start, poll, pause/resume, cancel and stale
   process recovery. Never auto-start from a preview, DSTM request or scan.
6. Persist only lightweight job state needed after a settings-page reload; the
   SQLite repository remains the source of synchronization truth.
7. Add tests for first install, missing key, scan in progress, cancellation,
   rate limit, child failure and restart recovery.
8. Run all Perl tests.
9. Commit: `feat: synchronize Last.fm artist roots in background`.

## Task 9: Implement the API-key-only provider UX

**Repository:** `D:\LMS\lms-guidance-lastfm`  
**Files:**

- Modify: `LastFmGuidance/HTML/EN/plugins/LastFmGuidance/settings/lastfmguidance.html`
- Modify: `LastFmGuidance/strings.txt`
- Modify: `LastFmGuidance/Settings.pm`
- Modify: `tests/settings_contract.t`
- Modify: `tests/strings_format.t`

**Steps:**

1. Add failing template tests proving graph controls/status are rendered for
   API Key and absent for LastMix.
2. Add localized policy, scope and result-limit controls plus database health,
   coverage and synchronization status.
3. Add explicit actions for update, pause/resume, cancel, compact/rebuild and
   confirmed deletion.
4. Update conditional JavaScript immediately when the source selector changes;
   switching to LastMix hides the entire graph section without saving.
5. Keep normal Save explicit. Maintenance buttons may start only their named
   action and must not silently save unrelated form edits.
6. Gate the public **Offline only** option according to the licensing decision
   recorded in the design; keep native behavior covered even while hidden.
7. Preserve Lyrion/Material Skin setting wrappers and current source/scoring
   layout.
8. Run all Perl and string-format tests.
9. Commit: `feat: add API-key offline graph controls`.

## Task 10: Remove host-owned Last.fm cache paths without changing host UX

**Repositories:**

- `D:\LMS\lms-better-call-bliss`
- `D:\LMS\lms-blissmixer-lab`

**Files:**

- Modify: `BetterCallBliss/Jobs.pm`
- Modify: relevant Better Call Bliss guidance-context contract test
- Modify: `BlissMixerLab/Plugin.pm`
- Modify: relevant Bliss Mixer Lab guidance-context contract test

**Steps:**

1. Add failing tests showing generic hosts no longer construct or supply a
   Last.fm cache/store path.
2. Remove only the provider-specific `lastfm-guidance-v1.json` context fields.
   Keep candidate identity, anchors, diagnostics and generic provider lifecycle
   unchanged.
3. Run each plugin's complete Perl test suite.
4. Compare rendered Better Call Bliss preview diagnostics and Bliss Mixer Lab
   selection logs with their current golden strings.
5. Commit independently in each repository with
   `refactor: let Last.fm provider own its graph paths`.

## Task 11: Documentation, release contracts and acceptance

**Repositories:**

- `D:\LMS\bliss-guidance-lastfm`
- `D:\LMS\lms-guidance-lastfm`
- `D:\LMS\lms-better-call-bliss`
- `D:\LMS\lms-blissmixer-lab`
- `D:\LMS\bliss-similarity-design`

**Files:**

- Modify: native and plugin `README.md` files where ownership changed
- Modify: `D:\LMS\lms-guidance-lastfm\CHANGELOG.md`
- Modify: native/plugin release-contract and packaging tests
- Modify: `LASTFM_GUIDANCE_ACQUISITION_PLAN.md`
- Modify: `LASTFM_OFFLINE_GUIDANCE_GRAPH_DESIGN.md`
- Modify: `IMPROVEMENT_BACKLOG.md` in Better Call Bliss when the feature is
  operational

**Steps:**

1. Document the API-key-only boundary prominently in both Last.fm repositories.
2. Add a compact Mermaid static view and job/synchronization sequence diagram
   showing every file source and sink.
3. Document storage size accounting, freshness, result limits, migration,
   failure behavior and deletion.
4. Update native `version --json`, plugin binary compatibility, source
   provenance and package checks so graph-capable binaries cannot be confused
   with the old JSON-cache build.
5. Run all native and Perl tests locally; build cross-platform Rust binaries in
   GitHub Actions rather than on the Pi.
6. Inspect each release artifact, checksums, bundled platform binaries and
   extension-feed metadata independently.
7. Deploy only to
   `/usr/local/slimserver/Cache/InstalledPlugins/Plugins/LastFmGuidance` and do
   not use the development `Cache/Plugins` directory.
8. On the Pi, test:
   - first direct lookup and persisted second offline lookup;
   - LastMix with filesystem-open proof of zero graph access;
   - 25/50/100 requested versus actual counts;
   - manual synchronization, cancellation and resume;
   - network outage and stale/missing status;
   - concurrent Better Call Bliss preview and Bliss Mixer Lab DSTM;
   - LMS UI and queue responsiveness;
   - graph size/WAL budget and API-key redaction.
9. Mark the design implemented only after the Pi acceptance evidence exists.
10. Commit documentation/status updates separately from release version bumps.

## Final verification commands

```powershell
Set-Location D:\LMS\bliss-guidance-lastfm
cargo fmt --all -- --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-features

Set-Location D:\LMS\lms-guidance-lastfm
prove -I. -r tests
python -m unittest discover -s tests -p 'test_*.py'

Set-Location D:\LMS\lms-better-call-bliss
prove -I. -r tests

Set-Location D:\LMS\lms-blissmixer-lab
prove -I. -r tests
```

Expected result: every command exits `0`; the direct API-key path can reuse and
synchronize the SQLite graph; LastMix still produces the same resolved
artifact and performs zero graph I/O.
