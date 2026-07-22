# Bliss 'Em All - live automatic extension checkpoint

**Date:** 2026-07-22
**State:** Extend automatically is connected end to end from per-job Extras UX
through native bridge selection, local LMS resolution, reviewed Preview, and
verified create-copy persistence

## Published implementation revision

| Repository | Revision | Result |
| --- | --- | --- |
| [chrober/lms-bliss-em-all](https://github.com/chrober/lms-bliss-em-all/tree/feature/first-ux-preview) | `9f5a66366e7e21d69f9c8612b426078db1fdb99a` | Version `0.5.0` automatic-extension job contract, read-only bridge resolver, additions/decisions UX, verified extended persistence, and updated defaults/logging/docs |

No native optimizer change was required. This checkpoint consumes the already
published deterministic `contextual-bridge-analysis-v1` and automatic
`selection_preview` contracts.

## Connected workflow

```text
Extras > Bliss 'Em All
  -> select saved playlist
  -> Optimize order
  -> Extend automatically
  -> set per-job Adaptive, repeat, search, bridge-budget, and trigger values
  -> Run read-only preview
  -> review final order, additions, evidence mode, and every gap decision
  -> Create optimized copy
  -> verify LMS catalog and extended-M3U order
```

Automatic mode may legitimately add zero tracks. The budget caps successful
insertions, not candidate analysis. A transition is eligible only when its
direct distance is strictly above the declared frozen contextual percentile;
the selected candidate must additionally pass native acoustic improvement,
unique-membership, and full-route repeat gates.

## LMS bridge resolution

The native artifact deliberately exposes database-bound `bliss-row-N`
identities instead of private paths. The plugin now:

1. proves that the selected base route is an exact permutation of the source;
2. requires the native subsequence and unique-membership proofs;
3. validates contiguous positions, sequence kinds, added count, budget, and
   one-to-one correspondence between final bridges and selected decisions;
4. rejects the result if the database device/inode/size/mtime identity changed
   while the native job was running;
5. opens `bliss.db` with SQLite read-only flags and resolves each row through
   `TracksV2`;
6. maps its database file identity to a current local LMS track, including CUE
   identities, and rejects missing, remote, or duplicate URLs; and
7. freezes the resolved URLs, labels, provenance, and final track IDs in the
   in-memory reviewed job.

Create-copy then uses the same Lyrion-native writer as reorder-only, with exact
source and bridge membership verification before serialization.

## Semantic boundary

This slice writes the versioned empty semantic-evidence artifact and therefore
uses the native `bliss-only-empty-graph` fallback. The result and server log
state that fact explicitly. Last.fm and ListenBrainz remain optional and
unconnected; no network request is made, and their absence cannot fail the
job. When connected later, transition-local evidence must precede the full
source-artist collection fallback without changing this native result shape.

## Live ARM64 verification

The final `0.5.0` build was exercised on LMS 9.1.1 ARM64 against 63,822 usable
Bliss rows. A seven-track anonymized playlist used Adaptive 3/20,
artist/album/track windows 5/10/100, zero restarts, a one-track budget, and a
0th-percentile trigger. Native bridge analysis completed in about 20 seconds
and proposed one local bridge.

The Preview rendered an eight-track order, marked the addition, showed its
original endpoints, percentile and Bliss-only provenance, exposed all gap
decisions, and retained the explicit Create action. Creation produced LMS
playlist ID 723639 for the development run. Independent comparison of request
source mappings, native `final_sequence`, and catalog URLs proved exact order
equality with exactly one non-source URL. The source still exactly matched the
seven URLs captured before the job and had URL-list SHA-256
`e85f20d212a21823d60cf6d733ba7e288a076dd2065692e93b66bd26b77b2b6a`.
The output M3U contained eight `#EXTURL:file:///` and eight `#EXTINF`
records, and no private temporary file remained.

Post-restart status was:

```text
ready=1
problem_count=0
ux_contract=extras-job-editor-v3
working_mode=per-job-adaptive/reorder-or-auto-extend/create-copy
```

## Deployment rule corrected

A rollback directory initially created beneath `Cache/Plugins` was itself
scanned by Lyrion and shadowed the new web template while the live Perl job code
continued to run. This produced a hybrid result view and made the failure easy
to misdiagnose as ordinary template caching.

Rollback copies must live outside every scanned plugin root. The verified
rollback is now beneath `Cache/BlissEmAll-backups`; the stale derived template
was removed, Lyrion regenerated it from the live plugin, and the final page
contains the working automatic controls without diagnostic residue.

## Next gate

Connect **Add exactly N tracks** next. The native exact-count and infeasibility
contracts already exist, so the plugin work is bounded: add the per-job count,
normalize feasible/infeasible artifacts, reuse the same row resolver and writer,
and render explicit search/infeasibility diagnostics without creating a partial
playlist.
