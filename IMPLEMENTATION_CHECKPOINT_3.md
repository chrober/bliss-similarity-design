# Better Call Bliss - first shared-core consumer checkpoint

**Date:** 2026-07-20
**State:** Shared core consumed by two native applications; validation only, no playlist mutation or server deployment

This checkpoint completes the first permanent, reproducible cross-repository
integration slice from [the implementation plan](BLISS_PLAYLIST_OPTIMIZER_IMPLEMENTATION_PLAN.md).

## Immutable revisions

| Repository | Revision | Result |
| --- | --- | --- |
| [`chrober/bliss-mixer-core`](https://github.com/chrober/bliss-mixer-core) | `0f6fd80c04d6f4448d5d58ba98112c1e7099ade1` | Added usable-track, exact-artist, and normalized-genre read-only queries; CI passed |
| [`chrober/bliss-mixer`](https://github.com/chrober/bliss-mixer/tree/feature/shared-core-extraction) | `b344f586cf50ee10866c92348fc81af07991a0fe` | Feature branch delegates adaptive scoring and learned-matrix parsing to the pinned core; 9 tests passed |
| [`chrober/bliss-playlist-optimizer`](https://github.com/chrober/bliss-playlist-optimizer) | `641470cb00cf67131ac63241a214d39db19c67b6` | `validate --request` implemented against the same pinned core; local and GitHub format, strict Clippy, contract tests, and runtime fixture validation passed |

The consumer manifests pin the full core Git revision. They do not follow a
branch or an unreviewed moving target. The direct `bliss-audio` dependency in
the mixer was pinned to the core's existing upstream revision as well, so the
dependency graph contains one compatible `bliss-audio` package.

## Shared-core contract added

`bliss-mixer-core` now exposes these additional read-only `TracksV2` queries:

- exact usable row lookup, excluding `Ignore = 1` rows;
- exact artist metrics in stable row-ID order, intentionally including ignored
  rows to preserve the existing mixer's artist-tree behavior; and
- normalized semicolon-separated genres from usable rows.

The core continues to open production databases read-only, validates required
columns, and supports SQLite `quick_check` without changing the database.

## Existing mixer integration

The mixer feature branch now uses the shared core for:

- variance-derived, learned, and dynamically blended adaptive matrix
  selection;
- arithmetic seed means; and
- wrapped or direct learned-matrix parsing.

The mixer's existing algorithm labels, endpoint behavior, HTTP-facing calls,
and nine characterization tests remain unchanged. `cargo test` passes.

`cargo clippy --all-targets -- -D warnings` is not yet a valid gate for the
whole upstream mixer: Rust 1.97.1 reports 19 pre-existing warnings outside this
integration. This checkpoint does not mix those unrelated cleanups into the
shared-core branch.

## Optimizer validation command

The optimizer now accepts:

```text
bliss-playlist-optimizer validate --request <request.json>
```

Before any future route optimization is allowed, this command:

1. validates the request and frozen semantic-evidence JSON against embedded v1
   schemas;
2. reads artifacts and verifies every declared SHA-256 digest;
3. opens `bliss.db` read-only, validates `TracksV2`, and runs `quick_check`;
4. parses any supplied learned matrix through `bliss-mixer-core`;
5. requires a matrix for explicit `learned_matrix` scoring; and
6. resolves every source track by its exact `TracksV2.File` identity and
   rejects missing or ignored tracks.

Success is one JSON object on stdout and includes the database schema identity,
artifact digests, job ID, and source-track count. Expected validation failures
are one JSON object on stderr with a stable error code and exit status 1.
Invalid CLI usage exits with status 2. Relative artifact paths are resolved
against the process working directory; the Lyrion plugin should pass absolute
paths.

The anonymized example request was corrected to use the exact identities in
the synthetic database. The successful fixture report contains these digests:

- database: `f5c3ebb9822310455621e696b15a16efb8176b746e6d7fd1882ea04ad5a59d3e`;
- learned matrix: `4023a86c9588df60ec2bc63e886248f7699f46980ae2e78cf6b1dd835933fbc7`;
- semantic evidence: `50fb96d017e3a158274763e7e908ede45cebeb85dca2591cdae5752c8570a711`.

## Non-actions and next gate

No tag, release, pull request, plugin package, extension-feed entry, playlist
write, or Lyrion server change was made.

The next implementation gate is a read-only native scoring/oracle command. It
should load validated source vectors, materialize the selected dynamic scoring
context, calculate deterministic contextual transition costs (or a pairwise
matrix only for fixed scoring modes), and compare that artifact with the
checked-in Python oracle before route search or playlist writing is
implemented. Database-wrapper migration in the existing mixer can continue
incrementally after this consumer seam has stabilized.