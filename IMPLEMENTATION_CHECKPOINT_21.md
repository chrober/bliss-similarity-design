# Bliss 'Em All - live exact-count extension checkpoint

**Date:** 2026-07-26
**State:** Strict per-job exact-count extension is deployed and verified end to
end on ARM64 Lyrion Music Server

## Published implementation revision

| Repository | Revision | Result |
| --- | --- | --- |
| [chrober/lms-bliss-em-all](https://github.com/chrober/lms-bliss-em-all/tree/feature/first-ux-preview) | `ed246e92e8deef8f1ca3871ef50303d04008c8fe` | Version `0.6.0` exact-count job option, strict native request/result validation, result UX, safe copy persistence, and live ARM64 evidence |

No native optimizer or shared-core change was required. The deployed optimizer
already contained the checkpoint-10 exact-count engine and later bounded-gap
and endpoint capabilities.

## Connected contract

The Extras editor now enables **Add exactly N tracks** and exposes a positive
integer owned by the current job. For `S` source tracks, this first connected
slice permits one addition inside each optimized source transition and therefore
validates `1 <= N <= S - 1`. Opening and closing slots are explicitly disabled.
The page updates the limit and calculated final size when the selected playlist
or N changes.

The plugin invokes the native `bridge` command with:

```text
mode=exact_count
additional_track_count=N
max_tracks_per_gap=1
allow_opening_track=false
allow_closing_track=false
```

An exact-count result is accepted only when its mode and requested count match
the job, it declares itself feasible, it carries the normal subsequence and
unique-membership proofs, and the resolved final sequence contains exactly N
unique local bridge tracks. A native infeasibility artifact becomes a failed
Preview with requested/found/structural-capacity details. It can never become a
partial playlist.

## Verification

The native optimizer's full local test suite passed:

```text
31 passed; 0 failed
```

This includes deterministic exact-count selection, infeasibility without
partial output, endpoint/multi-gap boundaries, request/result contracts, and
published-fixture parity.

The deployed plugin reported:

```text
ready=1
problem_count=0
ux_contract=extras-job-editor-v7
working_mode=per-job-adaptive/reorder-auto-or-exact-extend/create-copy
```

A live read-only Preview used an anonymized 13-track single-artist playlist,
requested one addition, and disabled artist and album look-back for that job.
The captured request contained the exact-count fields above. The result used
Adaptive-arc routing, contained one bridge and 14 final tracks, passed both
membership proofs, reported a maximum of one feasible addition found and an
internal structural upper bound of 12, and rendered its addition and gap
decisions. No saved playlist was created by Preview.

A two-track request for two additions was rejected before native execution with
a concise maximum-of-one message and no leaked Perl path. A final two-track,
one-addition smoke run created and verified a three-track saved copy. An
independent LMS query found both source URLs exactly once, one additional URL,
three unique URLs, and three total tracks. The test removed only this newly
created smoke playlist by its returned LMS ID through Lyrion's core playlist
deletion API and confirmed it was gone.

All modified deployed package files matched their local source SHA-256 values.
The pre-deployment plugin backup remains outside the scanned plugin tree under
`Cache/BlissEmAll-backups`.

## Next gate

Connect **One bridge per source-track transition** as a preset over the strict
exact-count path. It should calculate `N = S - 1`, show the resulting
`2S - 1` total before Preview, reuse all exact-count failure and persistence
invariants, and remain distinct from the later Double length preset (`N = S`).
