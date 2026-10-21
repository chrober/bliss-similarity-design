# Implementation checkpoint 33 - Lyrion virtual-library candidate scope

Date: 2026-08-25

This checkpoint adds a user-selectable Lyrion virtual library as a hard
candidate boundary for every Better Call Bliss workflow that generates tracks.
It complements BlissMixer's genre policy: the virtual library controls *where*
new music may come from, while the genre policy further filters that allowed
set.

## What changed

- Extras now shows a per-job **Candidate library** dropdown containing **All
  tracks** plus every registered Lyrion virtual library and its track count.
- A newly opened editor initially follows Material Skin's active library. If
  that browser state is unavailable, it uses the library assigned to the active
  player; **All tracks** is the final fallback.
- Playlist and track context actions propagate Material's current
  `library_id`, including all three **Bliss me there...** shortcuts.
- The plugin freezes the selected `library_track` membership into the existing
  checksum-protected local candidate inventory. Its membership digest
  invalidates both memory and disk caches after a library rebuild even when the
  LMS scan timestamp did not change.
- Tracks known to LMS but outside the selected virtual library are counted
  separately. They are not written to the persistent non-LMS Bliss-row audit,
  because their exclusion is intentional rather than a catalog defect.
- The selected library, eligible row count, outside-library count, and cache
  state appear in job diagnostics and the namespaced status command.
- The optimizer now treats the local candidate inventory strictly as an
  allowlist for generated additions. Existing source tracks, listening history,
  mandatory destinations, waypoints, and queue-rejoin anchors need usable Bliss
  rows but may remain outside the selected virtual library.
- Optimizer `version --json` advertises
  `candidate_library_scope=true`; the plugin refuses an older binary rather
  than silently ignoring the user's library selection.

## Why anchors are outside the candidate boundary

A virtual library is a selection policy for music Better Call Bliss may add. It
must not rewrite the user's input. Unioning input anchors into the candidate
allowlist would also be unsafe: an anchor or history track could then become
eligible as a generated addition when its repeat window is disabled. Keeping
route members and candidate membership separate preserves both intentions.

## Validation

- The complete optimizer test suite passed: 26 library tests, 23 binary tests,
  and 14 contract tests.
- A new optimizer regression uses an empty candidate allowlist and proves that
  source anchors still validate while the eligible generated-candidate count is
  zero.
- Plugin regression coverage verifies active-library discovery, stable-ID
  normalization, dropdown ordering, context propagation, per-job normalization,
  capability gating, and metadata contracts.
- A DBI/SQLite integration test creates synthetic LMS and Bliss databases and
  verifies selected membership, outside-library reporting, genuine stale-row
  auditing, and cache invalidation after a membership-only change. The GitHub
  workflows install the added DBI/SQLite test dependencies; this test cannot run
  in the bundled Windows Git Perl environment because those modules are absent.

## Release boundary

Optimizer commit `2029a0d` was published as `v0.1.9` after the complete native
test, clippy, formatting, and five-platform build workflow passed. Better Call
Bliss commits `67f2372` and `a3ffdde` were published as `0.16.2`; its release
workflow passed all 325 plugin tests, downloaded and verified the `v0.1.9`
platform artifacts, packaged the plugin ZIP and checksums, and updated the
private Lyrion extension feed. Deployment to the ARM64 test server is outside
this checkpoint.
