# Better Call Bliss - strict-rank bridge shortlist and live scaling

**Date:** 2026-07-26  
**State:** Native bridge-search performance gate deployed and measured on ARM64 Lyrion Music Server  
**Plugin version:** `0.8.0`

## Outcome

The high-recall bridge-candidate shortlist is implemented, published, deployed,
and measured. It bounds repeated evolving-route work without substituting a
cheaper musical model for the production scoring contract.

- Native requests may declare `extension.shortlist_limit`. Omitting it preserves
  exhaustive behavior for parity and diagnosis.
- The plugin supplies a conservative fixed limit of 256 for its connected
  automatic and exact-count addition jobs.
- Endpoint-local semantic candidates are reserved before acoustic filling, so
  optional semantic evidence cannot be displaced merely by collection size.
- Each original internal gap uses the existing strict dynamic two-leg Adaptive
  rank over the full frozen eligible pool. The rank includes accepted status,
  semantic priority, worst-leg percentile, detour percentile, and stable
  identity.
- Only the retained candidates enter repeated evolving-route rescoring and
  exact-count beam expansion.
- Per-gap artifacts report the original semantic count, retained count, and
  acoustic-shortlist exclusion count.
- Native timing separates candidate preparation, initial ranking/shortlisting,
  shortlisted scoring, and final selection.
- Candidate work remains deterministic across Rayon worker counts.

## Repositories and commits

| Repository | Commit | Change |
| --- | --- | --- |
| `bliss-playlist-optimizer` | `f89e5e6` | Optional shortlist contract, diagnostics, semantic reserve, prepared Adaptive context, deterministic tests |
| `bliss-playlist-optimizer` | `b6d3d10` | Final production-rank-preserving shortlist after rejecting two weaker live proxies |
| `lms-better-call-bliss` | `d55e1c7` | Version `0.8.0`, fixed 256-candidate job contract, logging, final ARM64 binary, provenance |
| `lms-better-call-bliss` | `6053871` | Reproducible live-validation report |

Both final optimizer GitHub Actions workflows passed:

- CI run `30207143940`;
- ARM64 build run `30207143926`.

The deployed binary was built from
`b6d3d1046612742ebb757bf6dec47f15f207591e` and has SHA-256
`f2c3f8a743072625820ad8f3208f6595d5ee529cdb0232a50819af6c284252a6`.

## Live quality oracle

The same anonymized two-track, one-gap exact-count request used by checkpoint 22
contained 63,820 eligible candidates. The final 256-track shortlist selected
`bliss-row-49`, identical to the exhaustive implementation, and returned one
addition.

| Measurement | Exhaustive | Shortlisted | Change |
| --- | ---: | ---: | ---: |
| Native total | 3,888 ms | 3,174 ms | -18.4% |
| Candidate preparation | 449 ms | 458 ms | Stable |
| Full initial gap rank / shortlist | 693 ms | 613 ms | Stable |
| Repeated shortlisted gap scoring | Included above | 2 ms | Bounded |
| Exact selection and final diagnostics | 688 ms | 2 ms | Bounded |
| Candidates entering evolving search | 63,820 | 256 | -99.6% |

The plugin wall measurement was 5,016 ms. It includes asynchronous process
launch and polling granularity, so the native structured measurement is the
meaningful algorithm comparison.

## Rejected proxy designs

The live oracle prevented two attractive but incorrect shortcuts from becoming
the accepted implementation:

1. a prepared-left plus learned candidate-to-right proxy selected
   `bliss-row-983`;
2. an exact dynamic local-objective proxy selected `bliss-row-764`.

Neither matched the exact-count candidate-retention order. The bounded search
first prioritizes accepted status, semantic tier, worst-leg percentile, and
detour percentile before comparing retained routes. Reusing that production
rank restored `bliss-row-49`. Deterministic worker-count tests, a contextual
synthetic corpus, and an end-to-end exhaustive-versus-shortlisted fixture now
cover this boundary.

## Formerly runaway request

The anonymized 13-track, exact-eight request that previously exceeded four
minutes completed native analysis in 21,142 ms:

| Stage | Elapsed |
| --- | ---: |
| Route search | 247 ms |
| Candidate preparation | 457 ms |
| Rank and shortlist 12 original gaps | 8,113 ms |
| Initial shortlisted rescoring | 37 ms |
| Bounded exact selection | 10,064 ms |

The native artifact was feasible, contained exactly eight unique additions, and
proposed 21 final tracks. Every original gap had 63,809 eligible candidates and
256 retained candidates.

The plugin then rejected the result with `BRIDGE_TRACK_NOT_IN_LMS` because
selected candidate `bliss-row-21660` did not resolve to a current local LMS
track. This occurred before persistence. No playlist was created, overwritten,
or otherwise changed.

## Newly exposed correctness boundary

The optimizer currently treats every usable Bliss database row as a potential
local candidate. The plugin proves LMS membership only after native selection.
That post-result proof is safely fail-closed, but it can waste a successful
search and prevent a usable Preview when `bliss.db` contains a stale or
otherwise non-LMS row.

The next correctness gate is a frozen, database-bound inventory of actual local
LMS candidate identities, or an equivalent bounded exclusion-and-retry
contract. Native bridge preparation must use that membership before ranking.
The result resolver remains a required second proof against database or LMS
changes during the job.

## Verification completed

- optimizer formatting and warning-free Clippy: passed;
- optimizer unit, deterministic, parity, and JSON contract suites: passed;
- final CI and ARM64 cross-build: passed;
- active plugin version, binary checksum, and native version contract: passed;
- live status: `ready=1`, `problem_count=0`;
- exhaustive-winner oracle: identical selected bridge;
- shortlist diagnostics: 63,820 reduced to 256;
- formerly runaway native request: completed in 21.1 seconds with exactly eight
  proposed additions;
- post-result non-LMS candidate: rejected safely before any playlist mutation.

## Next gate

Add and test pre-search LMS-local candidate membership, including CUE identities,
Unicode paths, scanner/database drift, and a second post-result proof. Then add
user-visible cancellation and bounded resource policy before enabling the
one-per-transition, target-length, or double-length presets.

