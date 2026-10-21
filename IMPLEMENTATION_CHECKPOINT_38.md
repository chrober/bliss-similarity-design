# Implementation checkpoint 38: released repeat-window spacer repair

**Date:** 2026-10-21  
**Status:** Released  
**Releases:** Better Call Bliss `0.22.9`; `bliss-playlist-optimizer` v0.2.6  

## Outcome

The existing **Add spacing tracks as needed** workflow now uses the shared
native global multi-gap planner. It freezes either the preserved source order or
a source-only optimized order, then finds the repeat-safe result with the
smallest feasible total number of additions inside the job's global ceiling.
Different gaps may receive different counts; no track is added before the first
or after the last source track.

The final resolver accepts the complete multi-leg repair only when every
adjacent transition satisfies its configured maximum-leg percentile and the
whole route satisfies the artist, album, and track repeat proof. It no longer
rejects one selected spacing track by incorrectly reapplying the isolated
single-bridge detour test. Local difficult-transition workflows retain that
separate bridge rule.

## Search and UX boundaries

- **Additional route-search attempts** affects only the preliminary source-only
  route when **Optimize source order** is selected.
- **Preserve source order** does not use route restarts.
- The subsequent global spacing repair uses its own bounded beam; route-search
  restarts do not widen it.
- **Maximum additional tracks** is a ceiling, not a target.
- Queue output now defaults to the selected player, **Replace queue**, and
  **Start playback** when the listener accepts a preview.

## Published implementation

| Component | Main revision | Release |
| --- | --- | --- |
| `bliss-playlist-optimizer` | `adad000` | v0.2.6 |
| `lms-better-call-bliss` | `92bb85b` | 0.22.9 |

The optimizer's final repair correction is revision `743cdfd`. The host's final
queue-output default change is revision `fc861b8`. The Better Call Bliss release
pins and packages the v0.2.6 optimizer binaries.

## Verification

- Native formatting, Clippy, unit, integration, multi-gap, and JSON contract
  suites passed with all features enabled.
- Better Call Bliss tests and its release workflow passed.
- The optimizer release contains all supported platform binaries and checksums.
- The plugin release contains the pinned binaries, versioned ZIP/checksum
  artifacts, and an updated private extension-feed entry.
- The ARM64 development binary was deployed to the Pi during implementation.
  The published packages remain the authoritative install source.

## Remaining work

This checkpoint completes minimum-total repeat-window spacing. It does not yet
provide a global budget allocator for optional difficult-transition bridges, or
joint preserved-order placement for already selected fixed-source extension
membership. Those remain separate outer-planner tasks because their user intent
and membership semantics differ from mandatory repeat repair.
