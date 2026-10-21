# Better Call Bliss - verified optimized-copy persistence checkpoint

**Date:** 2026-07-22
**State:** Reorder-only Preview can now be explicitly persisted as a new,
verified LMS playlist without modifying the source

## Published implementation revision

| Repository | Revision | Result |
| --- | --- | --- |
| [chrober/lms-better-call-bliss](https://github.com/chrober/lms-better-call-bliss/tree/feature/first-ux-preview) | `cddda95997adf919f609ea062fcf511a7c018957` | Version `0.4.0` create-copy writer, post-Preview UX action, verification, failure cleanup, logging, and updated feature contract |

## Connected workflow

The safe writable vertical slice is now:

```text
Extras > Better Call Bliss
  -> select saved playlist
  -> configure per-job Adaptive and repeat settings
  -> Run read-only preview
  -> review the complete proposed order
  -> Create optimized copy
  -> verify LMS catalog and extended-M3U order
```

Preview remains non-mutating. Creation is a distinct action available only for
a completed job whose output disposition was **Create optimized copy**.
Selecting **Overwrite source** never reaches the writer.

## Persistence contract implemented

The plugin retains the source track-ID-to-URL mapping with the in-memory job and
requires the native result to contain every source ID exactly once. It resolves
those URLs back to local LMS track objects immediately before writing, rejects
missing or remote tracks, cleans the requested name with Lyrion's filename
helper, and rejects both filesystem and catalog collisions.

Lyrion's core M3U formatter writes a private same-directory temporary file. The
plugin reads it back and compares exact URL order, atomically publishes the new
file, creates the LMS playlist object, sets the ordered tracks, commits it, and
then independently verifies both catalog and final-file order. On failure it
removes only the temporary file, newly created catalog object, and newly
published output belonging to that attempt. It never edits the source.

This deliberately does not start a playlist scan. Lyrion's own playlist-save
path updates the playlist object directly; this implementation follows that
model and adds immediate catalog/file verification, avoiding dependence on an
eventual scanner cache refresh.

## Live ARM64 verification

Version `0.4.0` was deployed to LMS 9.1.1 on ARM64. System status reported:

```text
ready=1
problem_count=0
ux_contract=extras-job-editor-v2
working_mode=per-job-adaptive/reorder-only/create-copy
```

An anonymized 13-track single-artist playlist completed Preview with artist and
album look-back disabled for that job. **Create optimized copy** produced a new
13-track LMS playlist. Independent JSON-RPC inspection confirmed that its URL
order exactly matched the optimizer's selected IDs, while the source URL-list
fingerprint and track count remained unchanged. Its M3U contained exactly 13
`#EXTURL:file:///` lines and 13 `#EXTINF` lines plus decoded paths in Lyrion's
native format.

Reusing the same output name returned stable `OUTPUT_EXISTS`, left both source
and existing output unchanged, and left no `.bettercallbliss-*` temporary file.
Lifecycle records correlated `Creating`, `CreatedAndVerified`, and rejected
creation with the Preview job ID. The final restart loaded one LMS process with
the version `0.4.0` plugin and no capability problems.

## Remaining boundary

The plugin still keeps jobs and reports only in process memory. Source
overwrite, bridge/extension modes, semantic providers, cancellation, durable
history/export, complete localization, packaging, and the wider client matrix
remain visibly unavailable. The next product slice should connect one extension
mode end to end while preserving Preview-before-persistence and the same writer
verification contract.
