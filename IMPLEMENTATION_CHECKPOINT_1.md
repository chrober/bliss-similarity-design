# Bliss 'Em All — Phase 1 shared-core extraction checkpoint

**Date:** 2026-07-20  
**State:** Locally committed and parity-tested; nothing pushed or deployed

This checkpoint establishes a reproducible Rust environment and extracts the
first transport-independent behavior into `bliss-mixer-core`. It does not yet
make `bliss-mixer` or `bliss-playlist-optimizer` permanently depend on the core.

## Commits

| Repository | Commit | Responsibility |
| --- | --- | --- |
| `bliss-mixer-core` | `4622600` | Pin Rust 1.97.1 and add the standalone Dev Container |
| `bliss-mixer-core` | `c3a146c` | Extract read-only TracksV2 access, learned-matrix parsing, and adaptive scoring |
| `bliss-playlist-optimizer` | `cecf06c` | Pin Rust 1.97.1 and add the standalone Dev Container |
| `bliss-mixer` | `5d31bc6` | Pin Rust 1.97.1, add its Dev Container, and add Windows/Linux test CI |
| `bliss-mixer` | `24c678d` | Isolate and characterize adaptive matrix selection and seed means |

## Reproducible development environment

Each Rust repository now contains:

- `rust-toolchain.toml`, pinned to Rust 1.97.1 with rustfmt and Clippy;
- a standalone `.devcontainer` using Microsoft's supported Rust 1.x Debian
  Bookworm image line;
- SQLite development/CLI tools and Python inside the container; and
- repository-specific fetch and test configuration.

The image form follows the official
[Dev Containers Rust image documentation](https://github.com/devcontainers/images/tree/main/src/rust).
Docker is not installed on the current workstation, so the JSON definitions
were validated locally but an actual container build remains a CI, Codespaces,
or Docker-enabled-machine check. The pinned local Rust toolchain is the tested
development path in this checkpoint.

## Shared-core API now implemented

`bliss-mixer-core` exposes:

- the canonical 23-dimensional `FeatureVector` and feature names;
- read-only opening of an existing SQLite database;
- explicit `TracksV2` schema validation and optional `PRAGMA quick_check`;
- exact file-to-row identity, metadata lookup, raw metrics, and full usable-row
  scans with the existing `Ignore IS NOT 1` rule;
- learned-matrix loading from either the blissify `m` wrapper or the direct
  `dim`/`data` object, with exact 23×23 validation;
- adaptive matrix selection for zero, one, and multiple seeds;
- variance-only, learned-only, and blended behavior, including exact 0% and
  100% endpoints and learned fallback;
- arithmetic seed means and the existing Bliss Mahalanobis distance; and
- caller-visible effective algorithm identity and variance-failure diagnostics.

The extraction record identifies `bliss-mixer` source commit
`60a39c46d189604914f4aa39c1632bf496e226fe` and pins `bliss-audio` commit
`010a5dcb111242eda2113834fd2b288605dd1ce7`.

## Verification

- `bliss-mixer-core`: formatting and warnings-denied Clippy passed; 10 tests
  passed, including read-only enforcement, schema rejection, matrix formats,
  ignored rows, adaptive blend endpoints, means, and distances.
- `bliss-playlist-optimizer`: formatting and warnings-denied Clippy passed; its
  unit and schema-contract tests passed under the pinned toolchain.
- `bliss-mixer`: 9 committed tests passed. The existing linker and legacy
  dependency future-compatibility warnings remain unchanged.
- A temporary local-path parity harness linked `bliss-mixer` to the new core and
  compared variance-only and 0%, 20%, and 100% learned blends. Algorithm labels,
  matrices, and means matched exactly. The temporary dependency and test were
  removed after success, and the mixer worktree is clean.

## Boundary still in force

The core contains no LMS, HTTP, logging, provider, playlist, route-search, or
filesystem-persistence policy. The optimizer remains network-free, and optional
semantic-provider orchestration remains owned by the future LMS plugin.

## Next gate

Permanent consumption of the shared core needs a reproducible dependency that
CI can resolve. The planned route is to create and push the new
`chrober/bliss-mixer-core` repository, then depend on a reviewed Git revision or
prerelease tag from both native applications. Until publication is explicitly
authorized, local path dependencies must remain temporary and uncommitted.

After that gate:

1. replace `bliss-mixer`'s internal adaptive helper and matrix/database calls
   incrementally with core APIs while keeping every HTTP contract unchanged;
2. add API-level parity fixtures for `/api/mix`, `/api/list`, and `/api/ready`;
3. add the core dependency to `bliss-playlist-optimizer`; and
4. implement the optimizer's `validate` command with request deserialization,
   artifact hashing, read-only database checks, track resolution, and stable
   error codes.
