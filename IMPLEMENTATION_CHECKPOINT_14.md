# Bliss 'Em All - first live Lyrion preview checkpoint

**Date:** 2026-07-21
**State:** First usable read-only reorder UX deployed and verified on LMS 9.1.1
ARM64; playlist creation, bridge-mode UI, context actions, semantic providers,
destination routing, cancellation, and durable history remain disabled

## Published revisions

| Repository | Revision | Result |
| --- | --- | --- |
| [chrober/lms-bliss-em-all](https://github.com/chrober/lms-bliss-em-all/tree/feature/first-ux-preview) | `01c598641f1b2e81d5d4d96b254749460300bee7` | Installable read-only Applications UX, LMS capability and Unicode playlist mapping, native background job, proposed-order review, and structured failure diagnostics |
| [chrober/bliss-playlist-optimizer](https://github.com/chrober/bliss-playlist-optimizer) | `93bb3960cd0ce66bc7a60a9a01470bc656a2915a` | Reproducible ARM64 GitHub Actions artifact carrying optimizer `0.1.0` and core API `0.1`; [workflow](https://github.com/chrober/bliss-playlist-optimizer/actions/runs/29828872943) passed |

The bundled executable SHA-256 is
`172a6ea8a37383b2b1e78965af938a14a90049b4d114367bdf1c0d8041866a00`.

## Visible workflow

LMS now exposes **Bliss 'Em All** under Applications/My Apps. The hierarchy is:

```text
Bliss 'Em All
|- Optimize a saved playlist
|  `- playlist -> Reorder only -> review -> Run preview
|- Active previews
|- Recent results
|- System status
|- Settings
`- Help and about
```

The review screen displays the source and proposed counts, Adaptive seed and
learned blend, and inherited artist/album/track repeat windows. A completed
result displays the selected strategy, objective, worst transition,
repeat-window validation, and a numbered proposed order.

**Preserve order and fill gaps** is visible but marked as the next mode.
**Create playlist** is visibly disabled. The source playlist is never modified.

## Runtime ownership

The Perl plugin resolves saved playlists and local track identities through LMS
objects, maps tracks against LMS 9.1's multi-root `getAudioDirs()` result, and
writes versioned private JSON beneath the LMS cache. It captures the current
BlissMixer Adaptive settings and hard repeat windows for each job.

The native optimizer is invoked with an argument array through
`Proc::Background`. Because LMS ties `STDERR` to its logger, the launcher uses
the same safe untie/fork/re-tie pattern as the LMS scanner and redirects output
to private per-job handles. A timer polls without blocking the LMS event loop.

The learned matrix is optional. Capability discovery and request construction
include it only when readable; Adaptive scoring otherwise falls back to its
shared-core baseline behavior. No provider or network request exists in this
slice.

## Live verification

An anonymized nine-track saved playlist was previewed end to end on the live
ARM64 server. The plugin captured three Adaptive seeds, a 20% learned blend,
and repeat windows of 5/10/100. The completed result reported:

- selected strategy `adaptive`;
- objective `2.273`;
- worst transition `0.299`;
- all repeat constraints satisfied; and
- all nine unique source tracks exactly once in the proposed order.

The live status command returned ready with zero problems. Active and Recent
screens were separately verified, the native binary reported the expected
version contract, and the original saved playlist remained untouched.

A subsequent anonymized 52-track playlist containing a non-ASCII filesystem
identity completed with all tracks and repeat constraints after the native-path
boundary was corrected. With 50 configured restarts it took 204 seconds, so the
review and job screens now disclose restart effort and elapsed time rather than
implying immediate completion for larger fixed sets.

An anonymized 13-track playlist containing only one artist was also exercised.
Its artist look-back window of five is structurally impossible for reorder-only:
60 other-artist separators are required and none exist. The native
`ROUTE_SEARCH_FAILED` envelope now survives LMS child reaping, appears in the
server log with job ID and elapsed time, and is augmented in the UI with the
capacity explanation. The plugin did not weaken the inherited constraint.

Runtime defects found by the first deployment were corrected and retained as
compatibility rules: Lyrion strings require tab-separated locale rows; LMS 9.1
uses `getAudioDirs()` instead of the legacy `audiodir`; the bundled JSON
compatibility module exports functions rather than an object constructor; JSON
schema booleans require `JSON::XS::true`/`false`; and tied log handles require
the scanner-style child launch. Native filesystem paths must remain locale
bytes while the LMS media root is stripped and be decoded exactly once before
JSON output. Structured stderr must also be parsed even if LMS reaped the child
first and `Proc::Background` consequently reports a lost status as zero.

## UX safety discovered by the vertical slice

OPML navigation may replay ancestor callbacks when a deeper item is queried.
The state-changing **Run preview** action is therefore terminal. It never owns
a nested Refresh action that could start a duplicate job. Users return to the
side-effect-free Active or Recent screens, where status and results can be
opened repeatedly. Active and Recent also filter their job sets independently.

## Current boundary and next gates

Jobs live only for the LMS process lifetime, cannot yet be cancelled from the
UI, and retain no durable index. Reports are private native artifacts rather
than exported user-facing audit reports. Only Linux ARM64 is bundled.

The shortest route to a safely useful playlist feature is now:

1. add Preview-confirmed LMS-native creation of a new playlist while preserving
   the source and exact `#EXTURL`/`#EXTINF` serialization;
2. persist minimal job/report metadata and add cancellation/restart recovery;
3. expose the already implemented Preserve order and bridge-selection native
   modes through the same wizard; and
4. implement the fixed-destination native route and **Bliss me there...** UX.

Provider adapters, package ZIPs, extension-repository publication, and the full
client compatibility matrix remain later gates.
