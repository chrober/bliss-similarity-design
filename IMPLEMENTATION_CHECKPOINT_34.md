# Implementation checkpoint 34 - Shared anchored A-to-B path engine

Date: 2026-09-01

This checkpoint extracts the bounded inner search used by destination routes
into a pure, outer-planner-neutral optimizer module. It is the architectural
prerequisite for **Fill every gap with N bridge tracks** and later convergence
between live destination routes and playlist gap planning.

## What changed

- The optimizer now exposes an anchored-path request containing distinct left
  and right anchors, a returned route prefix, immutable listening history,
  unavailable outer-plan membership, frozen candidate evidence, repeat windows,
  search breadth, Variation, and the caller's adjacent-distance function.
- The engine returns complete route alternatives and their bottleneck, distance
  sum, and bounded-search statistics without mutating a playlist or player
  queue.
- Callers can retain multiple alternatives for each intermediate count. Current
  destination adapters deliberately retain one for behavioral compatibility;
  the future multi-gap planner can request several so a locally best gap does
  not make later gaps impossible under global repeat or membership constraints.
- Existing one-way destination and waypoint-and-rejoin workflows now call the
  shared kernel through Preview adapters. Their request schema, result schema,
  decision reconstruction, progress behavior, and queue-facing contract remain
  unchanged.
- Artist/album repeat checks remain one shared implementation rather than being
  duplicated inside the new engine. Immutable history is considered for new
  candidates but its pre-existing duplicates remain tolerated.

## Deliberate boundary

The kernel answers only: "Which complete paths can connect A to B under this
frozen evidence and local budget?" It does not decide which playlist gaps need
work, allocate a global bridge budget, commit candidate membership across gaps,
or persist an output. Those responsibilities remain in feature-specific outer
planners.

Playlist preserved-order and fixed-source placement have not yet migrated. The
next implementation slice should request several alternatives per original gap
and select a globally compatible combination before exposing strict per-gap
filling in the plugin UX.

## Validation

- New unit tests cover direct and bounded multi-track paths, immutable-history
  handling, unavailable membership, generated-track repeat enforcement, and
  retaining multiple alternatives for a future outer planner.
- Existing automatic destination, exact/minimum-count, Adaptive fallback,
  immutable-history, and waypoint-and-rejoin regressions pass unchanged.
- `cargo fmt --all -- --check` and `cargo clippy --all-targets -- -D warnings`
  pass.
- The complete optimizer suite passes: 28 library tests, 23 binary tests, and
  14 contract tests.

## Release boundary

Optimizer revisions `84e2d8b` and `57f4d8a` are published as standalone
optimizer release `v0.1.10`. The release workflow passed formatting, Clippy,
and the complete test suite, then published macOS, Windows, x86_64 Linux,
ARMHF Linux, and AArch64 Linux binaries with checksums.

This extraction does not require a Better Call Bliss schema or plugin change.
Better Call Bliss `0.16.2` therefore remains pinned to optimizer `v0.1.9` until
a later plugin release deliberately adopts the new binary. Live ARM64
integration verification remains a separate follow-up.
