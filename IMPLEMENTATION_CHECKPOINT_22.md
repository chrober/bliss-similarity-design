# Better Call Bliss - prepared-library cache and measured Pi performance

**Date:** 2026-07-26  
**State:** Native timing/cache gate deployed and verified on ARM64 Lyrion Music Server  
**Plugin version:** `0.7.0`

## Outcome

The next performance gate is implemented across the shared core, native
optimizer, and Lyrion plugin. It does not change playlist scoring or selection
semantics.

- `bliss-mixer-core` exposes one ordered query returning every usable row's
  canonical features and metadata. This removes the optimizer's previous
  one-metadata-query-per-track loop.
- `bliss-playlist-optimizer` reads each runtime request once, streams the large
  database hash, loads matrix and semantic artifacts once, and emits optional
  structured native stage timings.
- A versioned, checksum-protected binary cache stores the database SHA-256,
  successful `quick_check` result, and decoded usable-track library.
- Cache reuse requires the exact database path and the plugin-supplied
  `device:inode:size:mtime` identity. Identity mismatch, payload checksum
  failure, format mismatch, oversize input, or decode failure is a safe miss.
- Cache replacement uses a process-specific temporary file followed by rename.
  Only one cache filename exists per database path, preventing unbounded growth
  after Bliss scans.
- The plugin still verifies that the database identity is unchanged after a
  bridge job before resolving any added track. The cache does not weaken the
  prior fail-closed boundary.
- INFO completion records now contain plugin wall time, native time, and cache
  state. DEBUG adds sanitized per-stage milliseconds without track paths.
- A portable Perl benchmark harness runs repeated cold/warm native requests on
  the server without requiring Python.

## Repositories and commits

| Repository | Commit | Change |
| --- | --- | --- |
| `bliss-mixer-core` | `e18bd4d` | Bulk usable-track feature/metadata query and tests |
| `bliss-playlist-optimizer` | `ec8b6a5` | Prepared request path, timing contract, guarded cache, benchmark harness, deterministic cache tests |
| `lms-better-call-bliss` | `12f00e4` | Cache identity/orchestration, timing log relay, ARM64 binary, version `0.7.0` |

Both optimizer GitHub Actions workflows passed. The deployed ARM64 binary was
built by run `30205114070` and has SHA-256
`fde138541697ca21cf32a64f132a8ed0adbc882c78d94feae6cef9052166f64d`.

## Live verification

The live server at `192.168.1.112` returned HTTP 200 for Lyrion and
`bettercallbliss status` reported `ready=1`, `problem_count=0`, and
`extras-job-editor-v7` after restart. Version `0.7.0` and the expected binary
checksum were verified in the active manual-plugin directory. The previous
`0.6.0` plugin remains available beneath the established backup directory
outside Lyrion's scanned plugin tree.

An anonymized 13-track, single-artist playlist was run twice through the live
Extras workflow with identical reorder-only settings:

| Measurement | Cold cache | Warm cache | Change |
| --- | ---: | ---: | ---: |
| Native total | 5,183 ms | 2,065 ms | -60.2% |
| Plugin wall time | 5,510 ms | 2,357 ms | -57.2% |
| Route search | 248 ms | 239 ms | Stable |
| Database cache | miss | hit | Expected |

The selected Adaptive-arc route, objective `5.049`, and worst transition
`0.531` were identical. Cold-only preparation measured:

| Stage | Elapsed |
| --- | ---: |
| Stream database SHA-256 | 749 ms |
| Open and `quick_check` | 288 ms |
| Bulk decode 63,822 usable tracks | 1,926 ms |
| Write 16.9 MiB cache | 883 ms |

The warm cache decoded in 664 ms. The remaining fixed costs were request/schema
validation (805 ms), semantic artifact/schema validation (279 ms), source
resolution (41 ms), and route search (239 ms).

A separate two-track, one-gap exact-count Preview added exactly one track. It
completed in 3,888 ms native and 4,013 ms wall time on a warm cache. The bridge
stages measured candidate preparation at 449 ms, gap candidate scoring at
693 ms, and exact selection/final revalidation at 688 ms.

No benchmark result was persisted. No playlist was created or overwritten.

## Important negative result

An eight-addition Preview over the anonymized 13-track single-artist collection
was intentionally stopped after more than four wall-clock minutes and roughly
12 accumulated CPU-minutes. The native process was healthy and CPU-bound, but
the request was not an acceptable interactive workload. Terminating that one
read-only child produced a visible failed Preview stating that no playlist was
changed.

The preparation cache therefore solves the repeated database work but not the
dominant extension complexity. With `S` source tracks and `C` eligible library
tracks, initial bridge analysis still performs approximately `(S - 1) * C`
two-leg contextual evaluations, and exact selection may perform additional
contextual reranking. Permissive repeat windows can enlarge the accepted search
space further.

## Verification completed

- shared-core unit tests: 12 passed;
- optimizer formatting and warning-free clippy: passed;
- optimizer unit, deterministic parity, and JSON contract suites: passed;
- checksum-corruption cache test: safe miss;
- changed-identity cache test: safe miss;
- cold/warm optimizer output after removing timing metadata: byte-identical;
- ARM64 cross-build and architecture verification: passed;
- live plugin readiness, active version, and binary checksum: passed;
- cold and warm route-only Previews: completed;
- bounded one-gap exact-count Preview: completed with exactly one addition;
- stopped large Preview: failed safely with no playlist mutation.

## Next gate

Implement and measure a high-recall acoustic candidate shortlist before the
existing strict two-leg contextual scorer. The shortlist must be deterministic,
must never replace final Adaptive scoring, and must be evaluated against the
current exhaustive implementation for selected-track recall, feasibility,
objective drift, and worker-count parity. Candidate preparation and exact
selection should also avoid rescoring identical gap/candidate contexts.

Before exposing larger presets, add a user-visible cancellation action and a
bounded resource policy so an unexpectedly expensive read-only job can be
stopped without SSH. The one-bridge-per-transition preset remains behind these
performance and cancellation gates.
