# Bliss 'Em All — repository publication checkpoint

**Date:** 2026-07-20  
**State:** New repositories published; no releases, tags, packages, or deployment

The repository-publication gate identified in
[Phase 1](IMPLEMENTATION_CHECKPOINT_1.md) is complete.

## Published repositories

| Repository | Published `main` | Initial verification |
| --- | --- | --- |
| [`chrober/bliss-mixer-core`](https://github.com/chrober/bliss-mixer-core) | `c3a146c0afcf1efb51bbe772ea2f092b98f23d91` | CI passed |
| [`chrober/bliss-playlist-optimizer`](https://github.com/chrober/bliss-playlist-optimizer) | `cecf06cd2c2b70348b29df919b64be97d1c80775` | CI passed |
| [`chrober/lms-bliss-em-all`](https://github.com/chrober/lms-bliss-em-all) | `da07c822f6fc213498f3ebce14502dd05894d247` | Non-installable scaffold; no workflow yet |

All three repositories are public, use `main` as their default branch, and the
corresponding local branch tracks an identical `origin/main` commit.

No pull request, tag, release, extension-feed entry, plugin package, executable
bundle, or Lyrion server change was created as part of publication.

## Next implementation gate

The native applications can now consume a CI-resolvable core dependency. The
next work should:

1. choose and record an immutable core revision for development integration;
2. replace `bliss-mixer`'s internal adaptive helper with the published core
   while preserving its characterized algorithm labels, matrices, means, and
   HTTP contracts;
3. replace matrix and database behavior incrementally, with API parity tests;
4. add the same reviewed core revision to `bliss-playlist-optimizer`; and
5. implement the optimizer `validate` command before route optimization.

A prerelease tag should be created only after the first permanent consumers
pass CI. Until then, consumers should pin the full reviewed Git commit rather
than follow `main`.
