# Better Call Bliss — Phase 0 bootstrap checkpoint

**Date:** 2026-07-20  
**State:** Locally committed; nothing pushed, published, packaged, or deployed

This checkpoint turns the implementation plan into buildable repository and
contract boundaries without claiming that playlist optimization is functional.
It intentionally makes no production-server changes.

## Local repository state

| Repository | Branch | Commit | Bootstrap responsibility |
| --- | --- | --- | --- |
| `bliss-mixer-core` | `main` | `65be970` | GPL Rust library scaffold, canonical 23-feature identity, extraction provenance policy, CI |
| `bliss-playlist-optimizer` | `main` | `16576d5` | Native command scaffold, v1 JSON Schema drafts, examples, stable codes, sanitized parity fixture, CI |
| `lms-better-call-bliss` | `main` | `da07c82` | Deliberately non-installable LMS plugin scaffold and fixed project identities |
| `lms-plugins` | `main` | `cb8a513` | Validated extension-feed repository; Better Call Bliss remains unlisted until real releases exist |
| `bliss-mixer` | `feature/shared-core-extraction` | `2a6b674` | Six behavior-preserving database and matrix-loader characterization tests |

The fixed plugin identities are display name `Better Call Bliss`, Perl namespace
`Plugins::BetterCallBliss`, plugin directory `BetterCallBliss`, command prefix
`bettercallbliss`, UUID `5ff183ce-3d88-4aa1-8fa5-28fed965af76`, and native command
`bliss-playlist-optimizer`.

## Contract decisions established here

- The optimizer is network-free. The LMS plugin resolves optional Last.fm,
  ListenBrainz, or later provider evidence before invoking it.
- Frozen semantic evidence is a separate, independently validated and hashable
  JSON artifact referenced by the optimizer request.
- Request v1 captures source identities, database and matrix artifacts,
  BlissMixer scoring settings, deterministic route search, ordering policy,
  repeat windows, extension policy, semantic evidence, and report policy.
- Result v1 exposes complete membership/order, original-versus-bridge identity,
  per-leg context and costs, semantic tier/provenance, repeat verification,
  stable warnings/errors, search termination, and timings.
- Progress is JSON Lines friendly and separate from diagnostics or server logs.
- The native application commits `Cargo.lock`; the reusable core library does
  not. Both projects use GPL-3.0-only.
- No production logic has been copied into the core yet. Future extraction must
  identify its source commit, preserve notices, and land only behind source-side
  characterization tests.

## Reproducible validation completed

- Rust toolchain: stable `rustc 1.97.1`, with rustfmt and Clippy.
- Existing Python oracle: 11 unit tests passed.
- Synthetic fixture generation: a second generation produced identical SHA-256
  hashes for the SQLite database, extended M3U, learned matrix, and manifest.
- Python oracle on the fixture: selected the recorded `adaptive-arc` result; the
  portable expectation verifier passed with no repeat-window violations.
- `bliss-mixer-core`: formatting and warnings-denied Clippy passed; 1 unit test
  passed.
- `bliss-playlist-optimizer`: formatting and warnings-denied Clippy passed; 1
  unit test and 1 contract test passed. The contract test validates all four
  published examples against their v1 schemas.
- `bliss-playlist-optimizer version --json` returned schema version 1,
  executable version `0.1.0`, and core API `0.1`.
- `bliss-mixer`: all 6 new characterization tests passed. They freeze TracksV2
  feature order, metadata/row identity, ignored-row filtering, and wrapped and
  unwrapped learned-matrix inputs.
- `lms-plugins/repo.xml` parses successfully.
- Public-facing bootstrap files contain none of the private playlist name,
  server address, credentials, production music path, or workstation path.

The upstream `bliss-mixer` tree is neither rustfmt-clean nor warnings-denied
Clippy-clean before this extraction work. A full formatting run would rewrite
unrelated code, and strict Clippy currently reports 25 existing findings.
Those are recorded as baseline debt rather than folded into the characterization
commit. Ordinary compilation and all new tests pass.

## Not implemented yet

- No shared database, matrix, scorer, or adaptive code has been extracted.
- The native optimizer supports only `version`; `validate` and `optimize` are
  contract placeholders.
- There is no route search, bridge insertion, repeat solver, result writer,
  cancellation, or progress stream in Rust.
- The LMS scaffold has no `plugin.xml`, Perl runtime, settings, menus, jobs,
  provider adapters, packages, or executable bundles and is not installable.
- The extension feed deliberately contains no Better Call Bliss entry.
- No GitHub repository, release, pull request, or Lyrion server was changed.

## Next implementation checkpoint

1. Add focused characterization for current adaptive-score construction and
   fixed API behavior without refactoring it yet.
2. Extract feature models, read-only TracksV2 access, and learned-matrix loading
   into `bliss-mixer-core`, preserving the characterized `bliss-mixer` behavior.
3. Make `bliss-mixer` consume the local core during development, then repeat its
   test and API parity checks.
4. Implement optimizer request deserialization, schema/version checks, artifact
   hashing, supported-database validation, and the `validate` command.
5. Port reorder-only adaptive scoring against the synthetic fixture. Do not
   begin bridge modes or LMS integration until Python/Rust parity is measured
   and documented.
