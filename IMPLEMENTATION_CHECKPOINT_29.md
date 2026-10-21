# Implementation checkpoint 29 - Accept-time output targets and release packaging

Date: 2026-08-08

This checkpoint records the current Better Call Bliss product boundary after the private-beta packaging work and the `extras-job-editor-v18` UX update.

## What changed

- Preview generation is now output-neutral in the Extras workflow. Users run a read-only preview first and choose the output target only after reviewing the completed result.
- Completed previews expose **Accept this preview** with three connected targets:
  - create a verified optimized copy;
  - overwrite the source playlist after explicit confirmation; and
  - send the result to a selected player queue as Replace queue, Append to queue, or Play next, with optional playback start.
- Accept-time output fields can be changed without rerunning the optimizer. Failed accept attempts keep the same preview available for adjustment and retry.
- The plugin can now use Static BlissMixer-weighted routing and can run Adaptive without a learned matrix by falling back to variance weighting for multi-track contexts and Static BlissMixer weights for one-track contexts.
- Optional Last.fm evidence through LastMix now covers similar tracks as well as similar artists. It remains advisory, per-job controllable, and failure-tolerant; local Bliss similarity remains authoritative.
- The plugin release workflow now packages the plugin without committing native binaries. It downloads pinned `bliss-playlist-optimizer` release artifacts for aarch64, armhf, x86_64 Linux, macOS, and Windows, verifies checksums, creates versioned ZIP/checksum artifacts, publishes GitHub releases, and updates the Lyrion extension repository feed.

## Current deployment and release distinction

The latest public/private-beta package line is `0.14.3`, using optimizer release `v0.1.0`. The newest output-neutral accept UX is recorded as `extras-job-editor-v18` and has been hot-deployed for live testing on the ARM64 server. A later version bump/release should package this UX contract for normal Lyrion extension-manager updates.

## Remaining important gaps

- **Bliss me there…** remains an informational context action; fixed-destination routing and queue append from a selected destination are still open.
- Player queue as an input source remains a proposed workflow, not a connected source type.
- One-per-transition, target-length, double-length, endpoint insertion controls, cancellation, durable result history/export, ListenBrainz, plugin-owned durable semantic caches, and complete localization remain roadmap items.
- Private-beta release artifacts exist, but clean install/upgrade/uninstall, outage, scanner, restart, and recovery testing still need a systematic matrix.

## Plan impact

The roadmap counts move to **46 implemented**, **17 partial**, and **10 not implemented or later-roadmap** rows. This is a feature-row inventory, not a release percentage.
