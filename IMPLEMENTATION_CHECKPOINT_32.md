# Implementation checkpoint 32 - Destination-route maturity and reporting

Date: 2026-08-24

This checkpoint records the post-`0.14.4` work that turned **Bliss me there...**
from an editor-assisted first slice into the current background destination-route
workflow, plus the related optimizer and plugin reporting fixes. The latest
published private-beta plugin package is `0.15.7`, bundling
`bliss-playlist-optimizer` `v0.1.7`. The newest reporting fixes are committed on
the optimizer and plugin `main` branches and have been hot-deployed to the ARM64
test server, but still need the next versioned release package.

## What changed

- **Bliss me there...** now runs as a real quick action from a local track
  context. It captures the selected player, the live queue tail, immutable recent
  listening history, and the selected destination, then starts a background job
  without opening the Extras editor or requiring an Accept button.
- Destination routes append only a validated suffix: zero or more generated
  intermediates plus the selected destination. Existing queue entries are not
  removed, reordered, or replaced by this quick action.
- Automatic destination routing now supports separate minimum and maximum
  intermediate counts. Exact mode uses the same adjacent path objective for one
  fixed count.
- Fast, Balanced, and Thorough search-effort profiles bound candidate shortlist,
  per-state expansion, and beam breadth without weakening repeat or quality
  checks.
- Destination Adaptive routing now follows the BlissMixer-style Adaptive
  context and learned/Static fallback contract, using immutable queue history
  plus the tail as context. The destination itself does not train or fit an
  ad-hoc matrix.
- Adaptive destination jobs with a learned matrix also evaluate the direct
  endpoint jump through the current Static BlissMixer weights. The higher-risk
  view governs bounded candidate discovery, path scoring, and target acceptance;
  artifacts and Preview expose both verdicts.
- The optimizer now distinguishes immutable listening history from generated
  route membership. Repeats already present in history are tolerated, while newly
  generated intermediates remain constrained by track, artist, and album windows.
- Preserve-order bridge jobs expose the Adaptive gap-context policy per job:
  follow the evolving route, or freeze weights per original source gap.
- Variation for destination routes is applied only inside a complete-route
  quality band rather than changing graph reachability before the final route is
  known.
- Direct routes retained after cautious bridge search now report
  `best_effort_reason=no-beneficial-bridge-over-direct` even when the quality
  target was met. Their search statistics now aggregate the bridge search that
  actually ran instead of reporting only the selected zero-bridge option.
- Better Call Bliss Preview text now distinguishes a target-met
  no-beneficial/direct-retained route from a true target-missed best effort.
- Plugin information/debug logging gained native route-quality summaries,
  secondary-model diagnostics, transition-percentile explanations, and
  no-beneficial bridge outcomes.
- The release pipeline published Better Call Bliss `0.15.6` and `0.15.7`;
  `0.15.7` pins optimizer release `v0.1.7`.
- Root planning docs now record the intended long-term convergence between
  **Bliss me there...** and playlist gap filling through a shared inner
  A-to-B route engine, while keeping their outer planners distinct.

## Boundaries

- **Bliss me there...** is still marked partial for musical-quality maturity.
  The current search still uses one bounded endpoint-derived shortlist per
  request depth. Depth-aware frontier/corridor discovery, semantic evidence
  between intermediates, and richer acoustic evidence remain future work.
- The direct-transition trigger and generated-route quality target are still
  represented by one percentile setting in the schema. Splitting those controls
  remains planned.
- The strict **Fill every gap with N bridge tracks** playlist preset is not
  implemented. Its future implementation should reuse the shared A-to-B route
  engine rather than copy either the current destination-route path or the
  current playlist gap logic.
- Material still has no durable, subtle background-task indicator for quick
  actions. The transient notification, job ID, and Extras running/recent list are
  available; a persistent Material task chip remains planned.
- Post-`0.15.7` reporting fixes are not yet in a public versioned package. They
  are committed on `main` and manually deployed to `192.168.1.111`.
- Local Perl tests remain unavailable in the Windows workspace because `perl`
  is not on the local PATH.

## Validation

- Optimizer `cargo test` passed after the destination-route reporting fixes,
  including new regression coverage for searched direct retention and aggregate
  destination search statistics.
- `git diff --check` passed for the optimizer and plugin changes before they
  were committed and pushed.
- The ARM64 optimizer build workflow completed successfully for optimizer
  commit `1f5cf38`; the resulting binary was deployed to
  `192.168.1.111`.
- The deployed ARM64 optimizer checksum matched the downloaded GitHub Actions
  artifact:
  `cd3af602f2353c596774a0d39b63983f783fbe622569ab1983abb8f9c3d5c15e`.
- The updated Better Call Bliss Extras template was deployed to
  `192.168.1.111` and verified to contain the new cautious no-beneficial
  wording.
- The plan was reconciled against recent `lms-better-call-bliss` commits
  `3114845`, `357a3e5`, `5fefe65`, `e72191d`, `fbf0e6f`, `a7bac89`,
  `b527589`, and `6db530d`, and optimizer commits `9d78df5`, `baf626f`,
  `688ac61`, `5731105`, `80bc12d`, `68107eb`, `19d866c`, `3bdb777`, and
  `1f5cf38`.
