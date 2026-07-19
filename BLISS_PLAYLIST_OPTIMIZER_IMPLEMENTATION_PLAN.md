# Bliss Playlist Optimizer productization and implementation plan

**Status:** Proposed  
**Date:** 2026-07-19  
**Primary objective:** Productize the proven fixed-set playlist sequencing and
bridge-insertion workflow as a separately maintained Lyrion plugin without
requiring Python on the server and without modifying `lms-blissmixer`.  
**Reference implementation:** The untracked Python tools and the 2025/2026
execution reports in this repository remain the behavioral oracle until the
Rust implementation reaches declared parity.

## Decision summary

Build a companion Lyrion plugin, provisionally named **Bliss Playlist
Optimizer**, with its own native Rust helper. Extract the scoring, database,
matrix, and filtering behavior currently embedded in `bliss-mixer` into a
versioned `bliss-mixer-core` Rust library used by both native applications.

The product boundary is:

```text
lms-blissmixer (unchanged)
  owns analysis, bliss.db, learned matrix, and mixer preferences
                       |
                       v
lms-bliss-playlist-optimizer (new Perl plugin)
  owns LMS integration, LastMix integration, jobs, UX, reports, and playlists
                       |
                       v
bliss-playlist-optimizer (new native Rust program)
  owns route optimization and bridge selection
                       |
                       v
bliss-mixer-core (new shared Rust library)
  owns database access, feature order, filtering, and similarity scoring
```

This architecture results in two installed native programs, but not two
independently maintained implementations of Adaptive similarity. The existing
`lms-blissmixer` plugin neither loads code from the new plugin nor exposes
private process state to it.

## Scope

The first product release must support:

- reordering every track of an existing saved playlist exactly once;
- preserving the source playlist by default and writing a new optimized copy;
- the strict sliding Adaptive seed context used by the current BlissMixer;
- dynamic variance weights and learned-matrix blending;
- the configured track, artist, and album look-back windows;
- directional open-path optimization with aggregate and worst-leg objectives;
- automatic bridge insertion and an exact additional-track count;
- endpoint-local LastMix artist evidence with original-collection fallback only
  when the local artist pool is empty;
- reproducible JSON and human-readable reports;
- playlist context-menu, Applications/My Apps, and classic Extras entry points;
- safe LMS-native playlist creation and M3U serialization; and
- native packages for the server platforms declared by a plugin release.

The following are not required for the first release:

- changing the current `lms-blissmixer` implementation;
- replacing `/api/mix` or `/api/list`;
- modifying `bliss.db` or its schema;
- publishing raw playlists, private music metadata, server details, or Last.fm
  responses;
- intro/outro audio decoding or boundary-anchor analysis;
- optimizing the unsaved current player queue; or
- automatically overwriting a source playlist.

## Repository plan

Repository names are provisional but should be settled before code is split so
package names, plugin identifiers, release URLs, and documentation do not churn.

| Repository | State | Responsibility | Release artifact |
| --- | --- | --- | --- |
| `chrober/bliss-mixer-core` | New | Reusable Rust library for Bliss database access, shared models, matrices, filters, and similarity scoring | Tagged Rust library source; optional crates.io package later |
| `chrober/bliss-playlist-optimizer` | New | Headless fixed-set ordering and bridge-selection engine | Native executables and checksums per supported platform |
| `chrober/lms-bliss-playlist-optimizer` | New | Perl Lyrion plugin, UI, jobs, LastMix adapter, playlist persistence, and bundled optimizer executables | Platform-specific LMS plugin ZIP files |
| `chrober/lms-plugins` | Existing; reuse | Lyrion extension repository listing the new plugin alongside BlissMixer | `repo.xml` served from the existing raw GitHub URL |
| `chrober/bliss-mixer` | Existing | Refactor the maintained fork to consume `bliss-mixer-core` without changing `/api/mix` or `/api/list` behavior | Existing mixer binaries |
| `chrober/lms-blissmixer` | Existing; unchanged by this project | Produces and maintains the analysis artifacts and preferences consumed by the companion plugin | Existing LMS plugin ZIP files |
| `chrober/bliss-similarity-design` | Existing | Canonical design, prototype evidence, parity fixtures policy, and cross-repository decisions | Documentation site |

The existing local `D:\LMS\lms-plugins` checkout already points to
`chrober/lms-plugins` and contains a valid `repo.xml`. It should be committed and
extended rather than replaced by another extension-index repository. A separate
index repository is warranted only if different ownership, availability, or
release permissions are later required.

### Repository creation checklist

For each new repository:

1. add a concise README, license, security policy, contribution notes, and
   release policy;
2. enable protected default branches and required CI checks;
3. use issues and milestones matching the phases in this plan;
4. add Dependabot or an equivalent dependency-update process;
5. prohibit real `bliss.db`, learned matrices, playlists, artist profiles, and
   run artifacts through `.gitignore` and fixture-review rules; and
6. record the upstream/fork relationship and copyright provenance before
   moving existing GPL code.

Because `bliss-mixer` is GPL-3.0-only, code extracted from it must retain its
copyright and compatible GPL licensing. License choices for original new code
must be reviewed before the initial public commits; using GPL-3.0-only across
the shared core and native optimizer is the simplest compatibility choice.

## `bliss-mixer-core` design

### Responsibilities

The shared crate should own behavior that must remain identical between the
mixer and playlist optimizer:

- the `TracksV2` feature order and raw track representation;
- read-only SQLite opening and supported-schema validation;
- path lookup and track metadata loading;
- learned-matrix loading, dimensions, finiteness, symmetry, and compatibility
  validation;
- static Bliss distance primitives;
- population-variance calculation and inverse-variance normalization;
- Adaptive matrix construction and learned-matrix blending;
- single-seed learned-matrix behavior;
- mean-seed construction and Mahalanobis distance;
- genre, duration, ignored-track, Christmas, BPM, duplicate, artist, album, and
  track filtering primitives that are genuinely shared;
- normalized diagnostics describing the active algorithm and effective matrix;
  and
- stable typed errors rather than process exits or HTTP responses.

The crate must not own:

- Actix routes or daemon lifecycle;
- LMS preferences or playlist persistence;
- Last.fm network access;
- route search, energy arcs, or bridge-position policy;
- HTML, OPML, JSON-RPC, or other Lyrion UI concerns; or
- audio decoding and feature extraction already owned by `bliss-rs`.

### Proposed crate modules

```text
src/
  lib.rs
  error.rs
  schema.rs
  db.rs
  track.rs
  matrix.rs
  scoring/
    mod.rs
    static.rs
    adaptive.rs
  filtering.rs
  diagnostics.rs
```

The library should continue using the appropriate `bliss_audio::playlist`
primitives instead of copying Mahalanobis and variance implementations already
provided by `bliss-rs`.

### Compatibility and versioning

- Start at `0.1.0` and use semantic versioning.
- Pin consumers to a released tag and commit through `Cargo.lock`; do not track
  a mutable branch in release builds.
- Expose a core library version and supported database/schema identities.
- Treat feature ordering, population-versus-sample variance, epsilon,
  normalization total, matrix blend, and single-seed behavior as part of the
  compatibility contract.
- Require a golden parity test before any change to those semantics.
- Publish to crates.io only after the API has stabilized enough to support an
  external consumer; Git tags are sufficient initially.

## Refactoring `bliss-mixer`

The first consumer of the core must be the existing `chrober/bliss-mixer` fork.
This proves that the extraction is genuinely shared rather than a new copy made
only for the optimizer.

Refactor in behavior-preserving steps:

1. freeze representative `/api/mix` and `/api/list` requests and results;
2. add unit tests for database mapping, static scoring, Adaptive scoring,
   learned blending, and single-seed fallback;
3. move one cohesive unit at a time into `bliss-mixer-core`;
4. retain HTTP payload parsing, response formatting, server startup, tree/forest
   selection, and mixer-specific orchestration in `bliss-mixer`;
5. compare old and refactored binaries against the same sanitized database;
6. require identical accepted candidates and rankings, or document and approve
   any intentional numerical tolerance; and
7. release the refactored mixer only after the existing API regression suite
   passes.

This source refactor does not require a corresponding change to
`lms-blissmixer` for the optimizer project to proceed. Already released mixer
binaries naturally contain their historical implementation; maintained source
must no longer duplicate it.

## `bliss-playlist-optimizer` design

### Responsibilities

The native optimizer builds on `bliss-mixer-core` and owns:

- parsing and validating an explicit fixed track set;
- deterministic directional route construction;
- strict sliding-context rescoring at every proposed position;
- open-path nearest-neighbour, insertion, randomized greedy, 2-opt, swap, and
  relocation search;
- total-cost and worst-leg route objectives;
- hard artist, album, and track repeat windows;
- optional start/end locks and forbidden adjacencies;
- energy-arc evaluation as a secondary selector;
- bridge candidate generation from the analyzed local library;
- contextual two-leg bridge evaluation;
- frozen cross-context reference distributions;
- endpoint artist-evidence tiers supplied by the caller;
- automatic and exact-count bridge policies; and
- structured progress, warnings, results, and reproducibility diagnostics.

The optimizer must not call Last.fm directly. It receives a frozen semantic
profile from the LMS plugin so that LastMix remains the network-policy owner and
the optimizer is usable outside LMS.

### Initial command-line contract

Prefer a non-daemon one-process-per-job interface for the first release:

```text
bliss-playlist-optimizer version --json
bliss-playlist-optimizer validate --request request.json
bliss-playlist-optimizer optimize --request request.json --result result.json
```

The Perl plugin must invoke the executable with an argument array, never a
shell-composed command. Results should be written to an atomic temporary file
and renamed only after success. Optional JSON-lines progress may be written to
a separate file that the plugin polls.

Each request includes an explicit `schema_version` and, at minimum:

- database and learned-matrix locations;
- the ordered source track identities;
- the captured BlissMixer algorithm settings;
- route objective and deterministic search settings;
- look-back windows;
- extension mode and bridge budget/count;
- the frozen LastMix artist graph and coverage/failure metadata; and
- output/report policy.

Each result includes:

- result schema and executable/core versions;
- input artifact hashes and schema identities;
- complete output ordering and original/bridge classification;
- per-leg seed context, raw cost, normalized cost, and effective algorithm;
- repeat validation;
- route candidates and selection reason;
- every accepted bridge's two-leg costs and semantic evidence tier;
- rejected/fallback counts and warnings;
- deterministic seed, restart count, timings, and termination state; and
- a success, partial-capability, validation-error, cancelled, or internal-error
  outcome with stable machine-readable codes.

### Database safety

- Open `bliss.db` read-only and never migrate it.
- Validate the schema before loading tracks.
- Use a busy timeout and fail clearly if a consistent read cannot be obtained.
- Prefer postponing optimization while Bliss analysis is active.
- Record database identity at the beginning and end of a job.
- Consider an optimizer-owned snapshot for long jobs if live read consistency
  cannot be guaranteed; snapshots must live in the plugin cache and never Git.

## `lms-bliss-playlist-optimizer` design

### Dependency model

Lyrion does not provide a general `install.xml` dependency mechanism that can
be relied on to install and version-check another plugin automatically. The new
plugin must load safely and perform runtime capability checks in
`postinitPlugin`.

Check:

1. `Plugins::BlissMixer::Plugin` is enabled;
2. the supported BlissMixer version range;
3. the current preferences directory contains readable `bliss.db`;
4. the database schema is supported;
5. `learned_matrix.json` is present when the captured mode requires it;
6. the bundled optimizer matches the current platform and passes
   `version --json`;
7. the selected playlist has sufficient analysis coverage;
8. Bliss analysis is not currently writing the database; and
9. LastMix availability when semantic bridge assistance is requested.

The plugin should remain enabled when a capability is missing, but hide or
disable execution and show a precise remediation message. Avoid compile-time
imports, direct calls to underscore-prefixed BlissMixer functions, access to its
lexical process/port variables, or reliance on the running `/api/mix` process.

Keep all observed BlissMixer compatibility assumptions in one module, for
example:

```text
Plugins::BlissPlaylistOptimizer::BlissCompatibility
```

That adapter derives the current preferences directory, reads
`preferences('plugin.blissmixer')`, validates artifact names and schemas, and
maps supported preference versions into the optimizer request. It reads but
never changes BlissMixer preferences.

### Proposed plugin modules

```text
BlissPlaylistOptimizer/
  install.xml
  Plugin.pm
  Settings.pm
  Jobs.pm
  OptimizerProcess.pm
  BlissCompatibility.pm
  LastMixAdapter.pm
  PlaylistWriter.pm
  Report.pm
  strings.txt
  HTML/EN/plugins/BlissPlaylistOptimizer/
  Bin/<platform>/bliss-playlist-optimizer[.exe]
```

### LMS command surface

Register a namespaced command family such as:

```text
blissplaylistoptimizer capabilities
blissplaylistoptimizer optimize
blissplaylistoptimizer status
blissplaylistoptimizer cancel
blissplaylistoptimizer result
blissplaylistoptimizer history
```

Commands should accept a playlist ID for the immediate request but resolve and
record its URL/path because a playlist database ID is not stable across scanner
recreation. Only one write phase may run for a target output name at a time.

### LastMix adapter

- Build the artist profile from every distinct artist in the original input.
- Prefer MBID and normalized name identities.
- Keep per-source similar-artist results for local edge evidence.
- Build the global original-collection pool separately.
- Freeze the profile before optimization; inserted tracks never become seeds.
- Pass successful results and failed lookup coverage to the optimizer.
- Treat LastMix as optional for reorder-only mode and configurable for bridge
  mode; never silently describe a Bliss-only fallback as artist-assisted.

### Playlist persistence

Use LMS playlist objects and core persistence APIs instead of manually editing
M3U files over SSH:

1. create a new saved playlist with an unused, cleaned output name;
2. resolve every returned path to exactly one local LMS track object;
3. set the tracks in the returned order;
4. write through `Slim::Formats::Playlists->writeList` or the corresponding
   supported playlist command path;
5. rely on the core M3U writer for `#EXTURL`, `#EXTINF`, and path formatting;
6. commit and invalidate LMS caches through supported APIs;
7. verify the persisted playlist track-for-track; and
8. report, rather than conceal, any scanner/catalog mismatch.

Default to `<source> (Optimized)` and `<source> (Extended)`. Source replacement
is an explicitly confirmed advanced action and should be deferred until copy
creation and recovery behavior have been proven.

### UX

The primary entry point is one playlist context-menu provider:

> Optimize with Bliss…

It opens a workflow rather than changing the playlist immediately. Provide:

- **Reorder only**;
- **Extend automatically**;
- **Add exactly N tracks**;
- **One bridge per transition**; and
- **Target length / double length** presets.

The workflow displays source size, analysis coverage, inherited BlissMixer
settings, output name, LastMix availability, and a collapsed advanced section.
It runs Preview before Create and summarizes moved tracks, added bridges,
repeat compliance, mean/worst transition change, warnings, and semantic evidence
tiers.

Also expose one management dashboard through both:

- Applications/My Apps via `Slim::Control::Jive::registerPluginMenu`; and
- classic Extras via `Slim::Web::Pages->addPageLinks('plugins', ...)`.

The dashboard owns playlist selection, active jobs, progress, cancellation,
reports, history, and dependency status. The Settings page contains durable
defaults only, not individual jobs.

## Testing and parity strategy

### Sanitized fixtures

Create small synthetic or explicitly sanitized fixtures containing:

- a minimal supported `bliss.db` subset;
- known raw feature vectors and metadata;
- learned matrices including valid, missing, invalid, and single-seed cases;
- playlists with feasible and infeasible repeat windows;
- frozen artist graphs with both-endpoint, one-endpoint, empty-local-pool, and
  partial-failure cases; and
- expected route/report outputs for fixed deterministic settings.

Do not commit a subset of the real music library unless every field has been
reviewed and approved for publication.

### Differential parity

The existing Python tools remain the oracle during migration:

1. run Python and Rust against the same frozen fixtures;
2. compare feature ordering, matrices, centroids, per-leg costs, route
   objectives, repeat results, bridge evidence, and final ordering;
3. declare tolerances for floating-point diagnostics while requiring identical
   eligibility and deterministic selection where ties are fully specified;
4. compare shared scorer behavior against the existing native mixer debug
   output; and
5. retire Python as a production dependency only after all required parity
   suites pass.

### Repository CI

`bliss-mixer-core`:

- formatting, clippy with warnings denied, unit tests, schema fixtures,
  property tests, and minimum-supported-Rust checks;
- dependency and license audit; and
- public-API and semantic-version review on tags.

`bliss-mixer`:

- existing tests plus old-versus-refactored API differential tests;
- matrix and candidate-ranking parity; and
- unchanged `/api/mix`, `/api/list`, and `/api/ready` contracts.

`bliss-playlist-optimizer`:

- unit, property, golden, cancellation, malformed-input, and determinism tests;
- Python differential tests during development;
- build jobs for every release target; and
- smoke execution of `version`, `validate`, and a small optimization fixture on
  each runnable CI platform.

`lms-bliss-playlist-optimizer`:

- Perl compile checks and focused unit tests with mocked LMS objects;
- capability-state, path-validation, command, job-lifecycle, and LastMix tests;
- plugin ZIP structure and executable-presence validation;
- LMS-native playlist writer and exact-order integration tests; and
- installation, upgrade, disable, uninstall, and server-restart tests on a
  disposable LMS instance.

`lms-plugins`:

- XML parsing and schema/content validation;
- URL reachability after release publication;
- SHA-1 verification of every listed ZIP, because Lyrion requires it;
- duplicate plugin/version/target detection; and
- validation that plugin names match package directories and `install.xml`.

## Build and release pipeline

Use independent semantic versions for core, optimizer, and LMS plugin. A plugin
release records the exact optimizer and core versions it contains.

Release order:

1. tag and release `bliss-mixer-core`;
2. pin the core tag and commit in `bliss-playlist-optimizer`;
3. build native optimizer artifacts for the declared targets;
4. publish optimizer artifacts plus SHA-256 checksums and provenance;
5. update the LMS plugin's pinned artifact manifest;
6. package separate Linux, macOS, and Windows plugin ZIPs containing only the
   applicable native binaries;
7. verify ZIP root layout, permissions, `install.xml`, and executable smoke
   tests;
8. publish the plugin GitHub release;
9. calculate the plugin ZIP SHA-1 values required by Lyrion;
10. update `chrober/lms-plugins/repo.xml` only after every asset is publicly
    reachable and verified; and
11. install the release through Lyrion's extension manager on at least one clean
    server before announcing it.

Do not use mutable `latest` URLs. Keep the previous plugin release available so
rolling `repo.xml` back is sufficient to recover from a bad release. Preserve
executable bits for Unix artifacts and test on piCorePlayer rather than assuming
a generic ARM64 CI binary is ABI-compatible.

The existing `lms-blissmixer` `mkrel.py` and multi-platform packaging layout are
useful references, but the new release workflow should be automated in GitHub
Actions and should use an artifact manifest rather than downloading whichever
workflow artifact happens to be newest.

## Security, privacy, and failure behavior

- Treat playlist names, paths, JSON requests, and helper output as untrusted.
- Pass process arguments without a shell and validate all resolved paths.
- Restrict job files to the plugin-owned cache directory.
- Use unpredictable job IDs and atomic request/result writes.
- Never log SSH credentials, LMS authorization values, full artist profiles,
  complete private playlists, or raw analysis databases by default.
- Bind any future helper HTTP service to loopback and require an unguessable
  per-process token; the initial CLI design avoids this surface.
- Never write `bliss.db` or `learned_matrix.json`.
- Cancel and clean up child processes during plugin shutdown.
- Leave incomplete output playlists clearly marked or remove them through
  supported LMS APIs; never replace the source after a failed job.
- Make LastMix failure explicit and distinguish semantic, collection-level, and
  Bliss-only fallbacks in reports.

## Implementation phases

### Phase 0: bootstrap and contracts

- Create the three new repositories.
- Commit or otherwise establish the existing `chrober/lms-plugins` repository.
- Choose final package, plugin, command, and UUID names.
- Freeze request/result schema version 1 drafts.
- Prepare sanitized parity fixtures and Python oracle commands.
- Decide licenses and preserve extracted-code attribution.

**Exit gate:** repository ownership, artifacts, schemas, and release order are
documented; no production logic has been forked without provenance.

### Phase 1: extract `bliss-mixer-core`

- Add characterization tests to `bliss-mixer`.
- Extract models, database access, matrices, and scorers incrementally.
- Refactor the mixer fork to consume the tagged core.
- Prove existing API and binary behavior within declared tolerances.

**Exit gate:** `bliss-mixer` uses the new core and all baseline API/scoring tests
pass without an intentional behavior change.

### Phase 2: reorder-only native optimizer

- Implement request validation and result schemas.
- Port the dynamic directional scorer and deterministic route search.
- Enforce exact membership and repeat windows.
- Generate JSON diagnostics and progress.
- Establish Python/Rust parity on 2025/2026-shaped sanitized cases.

**Exit gate:** deterministic reorder-only output passes exact membership,
matrix, per-leg, objective, and repeat parity.

### Phase 3: bridges and semantic evidence

- Port frozen reference distributions and two-leg bridge scoring.
- Implement automatic and exact-count modes.
- Accept and validate the frozen artist-evidence graph.
- Enforce the endpoint-local fallback policy and full-route repeat constraints.
- Add detailed acceptance/rejection reporting.

**Exit gate:** bridge fixtures cover every evidence tier, impossible exact-count
requests fail visibly, and Python/Rust parity passes.

### Phase 4: headless LMS plugin backend

- Implement capability checks and preference capture.
- Add job creation, status, cancellation, and report commands.
- Implement LastMix profile collection.
- Invoke the native optimizer safely.
- Create and positionally verify new playlists through LMS APIs.

**Exit gate:** a CLI/JSON-RPC request can create a verified optimized copy on a
test Lyrion server without modifying the source or `lms-blissmixer`.

### Phase 5: user experience

- Register the playlist context-menu provider.
- Implement Preview and Create workflow screens.
- Add Applications/My Apps and Extras dashboard entry points.
- Add dependency status, progress, cancellation, history, and report views.
- Keep advanced algorithm controls collapsed and inherit BlissMixer settings by
  default.

**Exit gate:** the complete workflow is usable from Material and classic web
interfaces and gives actionable failure messages.

### Phase 6: packaging and private beta

- Build platform-specific binaries and plugin ZIPs.
- Test first on Linux ARM64/piCorePlayer and the Windows development server.
- Exercise analysis-running, missing-matrix, unavailable-LastMix, server-restart,
  cancellation, output collision, and scanner-recreation cases.
- Audit reports for private-data leakage.

**Exit gate:** platform smoke tests, install/upgrade tests, and real-server
playlist verification pass.

### Phase 7: extension repository and public release

- Publish versioned plugin ZIPs and checksums.
- Add Linux/macOS/Windows entries to `chrober/lms-plugins/repo.xml` as supported.
- Validate installation through the raw repository URL.
- Publish user documentation, compatibility matrix, known limitations, and
  rollback instructions.

**Exit gate:** a clean Lyrion installation can discover, install, validate, use,
upgrade, and uninstall the plugin through the extension manager.

## Acceptance criteria for the first public release

- `lms-blissmixer` contains no change required solely for this feature.
- The plugin never calls BlissMixer private functions or owns its process.
- No Python interpreter is required on the Lyrion server.
- `bliss-mixer` and `bliss-playlist-optimizer` use the same released core
  scoring implementation.
- Reorder-only mode preserves every original track exactly once.
- Exact bridge count either produces exactly the requested count or fails
  without creating a misleading partial result.
- All outputs satisfy captured repeat windows.
- Adaptive mode ignores static feature sliders and uses the captured dynamic
  matrix and learned blend, including defined single-seed behavior.
- LastMix local evidence and collection fallback semantics are visible in the
  report.
- The source playlist is unchanged by the default workflow.
- New playlists are written through LMS and match the returned result order.
- Jobs are cancellable, survive UI navigation, and clean up on server shutdown.
- Reports contain enough identity and decision data to reproduce a run without
  exposing private server data by default.
- Each advertised platform has an executable smoke test and a real installation
  result.
- Lyrion validates the published ZIP SHA-1 and installs it from
  `chrober/lms-plugins`.

## Open decisions

Resolve these before or during Phase 0:

1. Final names: `BlissPlaylistOptimizer`, `bliss-playlist-optimizer`, and
   `lms-bliss-playlist-optimizer` are clear but long.
2. Whether `bliss-mixer-core` should be public immediately or begin privately
   until extracted-code provenance is reviewed.
3. Whether the first beta targets only Linux ARM64/x86-64 or all platforms
   currently packaged by BlissMixer.
4. Minimum supported Lyrion version; begin with the actually tested release and
   widen only after compatibility testing.
5. Whether LastMix is optional with reduced bridge capability or required for
   every public bridge mode. Reorder-only should remain independent.
6. Whether long jobs read the live database in one transaction or always use an
   optimizer-owned SQLite snapshot.
7. Default route-search effort and a server-class-aware time/memory budget.
8. Report retention duration and whether users can explicitly export a private
   full report.
9. Whether replacing a source playlist is omitted entirely from version 1.
10. Whether to propose a small future public capability API to the
    `lms-blissmixer` maintainer; this must not block the companion plugin.

## Documentation work accompanying implementation

- Keep the design rationale and evaluation model in
  `bliss-similarity-design`.
- Keep the Rust core API and compatibility rules in `bliss-mixer-core`.
- Keep CLI schemas and optimizer algorithm details in
  `bliss-playlist-optimizer`.
- Keep installation, dependency diagnostics, UI, and user workflows in
  `lms-bliss-playlist-optimizer`.
- Keep only extension-repository usage and available-plugin summaries in
  `lms-plugins`.
- Replace references to the untracked Python prototype with stable repository
  links only after the corresponding repositories and releases exist.

The one-shot reports remain historical evidence. They should inform golden
tests and aggregate case studies, but their private paths, credentials, catalog
IDs, track lists, database copies, and run hashes must not migrate into public
product repositories.
