# Implementation checkpoint 35 - Complete album destination routes

Date: 2026-09-07

This checkpoint extends all three **Bliss me there...** context actions from a
single selected track to a complete selected album while preserving the album
as listener-owned, immutable route membership.

## What changed

- Better Call Bliss registers the three sibling actions in album context menus
  in the same order as their track equivalents.
- The plugin resolves every local audio track of the selected album and orders
  the immutable destination block by disc and track number. It rejects an album
  rather than silently omitting a remote, non-audio, missing, or Bliss-unresolved
  member.
- The optimizer request retains the legacy destination entrance and adds an
  optional ordered `destination_track_ids` block. Older single-track requests
  remain wire-compatible.
- The shared anchored A-to-B engine searches only the boundary from the route
  start to the album's first track and, for **and back again**, the boundary
  from the album's last track to the locked queue rejoin.
- Album tracks cannot become generated candidates. Internal album transitions
  remain untouched and do not participate in bridge acceptance or quality
  reporting. Repeat windows continue to constrain generated bridges without
  rejecting repeats intentionally contained in the selected album.
- The plugin registers album actions only when the optimizer advertises the
  `destination_blocks` capability.

## Queue behavior

- **Bliss me there...** keeps the current song and replaces its later queue
  entries with the approach route and complete album.
- **Bliss me there... and back again!** inserts the approach, complete album,
  and return route before the unchanged first upcoming track.
- **Bliss me there... when we're through!** keeps the existing queue and appends
  the approach route and complete album after its captured end.

The queue writer omits the captured start and rejoin anchors, so each album
track and generated bridge is emitted exactly once.

## Validation

- The optimizer suite passes 30 library tests, 23 binary tests, and 14 contract
  tests, plus formatting and strict Clippy gates.
- The complete plugin suite passes on the Raspberry Pi in the LMS Perl
  environment: 12 test files and 397 assertions.
- Two live album round-trip smoke tests exercised 17-track and 4-track albums.
  Both retained the complete canonical album sequence, inserted only boundary
  bridges, preserved the queue anchors, and applied the result successfully.

## Release boundary

Optimizer commits `8c5bfc4` and `f5fcaed` are released as `v0.1.11`. Better
Call Bliss commits `8c80580` and `693d6a6` package that optimizer and expose
the album actions in `0.17.4`. The Better Call Bliss release workflow
publishes platform-specific plugin archives and updates the Lyrion extension
repository.
