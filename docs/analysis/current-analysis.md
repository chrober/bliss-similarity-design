# Current bliss-rs analysis

**Status:** Living research and design proposal  
**Primary scope:** Stable Version 2 representation and existing experiments  
**Last reviewed:** 2026-07-14

## Stable representation

At Version 2, [`Analysis`](https://github.com/Polochon-street/bliss-rs/blob/master/src/song/mod.rs#L240) contains:

- tempo;
- zero-crossing rate;
- mean and standard deviation of spectral centroid;
- mean and standard deviation of spectral rolloff;
- mean and standard deviation of spectral flatness;
- mean and standard deviation of loudness;
- 13 chroma-derived interval and triad features.

[`FeaturesVersion`](https://github.com/Polochon-street/bliss-rs/blob/master/src/lib.rs#L147) declares the expected feature count,
[`Analysis::new`](https://github.com/Polochon-street/bliss-rs/blob/master/src/song/mod.rs#L326) rejects the wrong dimension, and
[`AnalysisIndex`](https://github.com/Polochon-street/bliss-rs/blob/master/src/song/mod.rs#L103) gives the Version 2 ordering. Version 1
has 20 features; Version 2 added and corrected chroma-derived features.

This is a sound compatibility model for a canonical vector. A new incompatible
vector would require a new feature version and library reanalysis.

## Existing temporal computation

The implementation already observes more information than
[`Analysis`](https://github.com/Polochon-street/bliss-rs/blob/master/src/song/mod.rs#L240) returns:

- tempo estimation consumes overlapping windows;
- spectral descriptors collect window measurements before returning summary
  statistics;
- loudness is processed in chunks;
- chroma builds a time-dependent chromagram before deriving aggregate interval
  features.

That makes `bliss-rs` the natural location for reusable temporal extraction.
An external analyzer should not need to duplicate decoding, resampling, FFTs,
onset processing, or chroma calculation merely to preserve intermediate data.

## Fixed-dimension dependencies

[`NUMBER_FEATURES`](https://github.com/Polochon-street/bliss-rs/blob/master/src/song/mod.rs#L222) is used beyond
[`Analysis`](https://github.com/Polochon-street/bliss-rs/blob/master/src/song/mod.rs#L240), including storage, matrix defaults, tests,
and the fixed-dimension extended isolation forest adapter. Increasing the
canonical vector therefore affects more than the extractor:

- all stored analyses become version-sensitive;
- default distance behavior changes unless weights are controlled;
- matrices and learned metrics become incompatible;
- consumers with explicit columns require migrations;
- fixed-size algorithms and fixtures must be rebuilt.

This is why experimental descriptors should not immediately become Version 3.

## Existing application and personalization experiments

Three related repositories provide concrete implementation precedent, but they
must not be conflated with one another or treated as scientific validation:

1. [`blissify-rs`](https://github.com/Polochon-street/blissify-rs) is the
   `bliss-rs` author's MPD application. It analyzes an MPD library through
   Bliss, persists the library in SQLite, handles feature-version upgrades and
   reanalysis, and generates several kinds of playlists. It exposes Euclidean,
   cosine, extended-isolation-forest, and Mahalanobis distance choices. For the
   last of these it reads a learned matrix from its configuration and supplies
   it to Bliss's Mahalanobis distance builder.
2. [`bliss-metric-learning`](https://github.com/Polochon-street/bliss-metric-learning)
   is a separate upstream Python experiment built around a `blissify-rs`
   library. A local web survey collects personal odd-one-out triplets; an
   offline trainer fits a positive-semidefinite Mahalanobis matrix over the
   fixed Bliss feature vector and writes that matrix into the `blissify-rs`
   configuration. Its own documentation labels the process heavily
   experimental.
3. [`bliss-learner`](https://github.com/chrober/bliss-learner) is a later public
   but experimental Rust port integrated into the
   [`chrober/lms-blissmixer`](https://github.com/chrober/lms-blissmixer) fork.
   Neither the learner nor this integration is part of the upstream Bliss
   projects. It reads filename-based triplets from JSON, loads the 23 named
   Version 2 columns from the LMS Bliss database, ports the probabilistic
   triplet-learning and cross-validation workflow, and writes a JSON matrix for
   the
   [`chrober/bliss-mixer`](https://github.com/chrober/bliss-mixer) fork.

`blissify-rs` is important to this design because it demonstrates the intended
division between intrinsic analysis, persisted library state, distance choice,
and playlist policy in a real application maintained alongside Bliss. The two
learning projects additionally demonstrate that a stable Bliss vector can be
used as the basis of a personalized metric without putting survey collection or
model training in `bliss-rs` itself.

They also expose constraints that an analysis evolution must address:

- learned matrices depend on exact feature definitions, ordering, dimension,
  scaling, and preprocessing, not just a nominal matrix size;
- adding descriptors or changing normalization requires a new learned-artifact
  schema and normally retraining, while old Version 2 matrices must remain
  usable with Version 2 data;
- a learned metric can reweight or combine captured evidence but cannot recover
  rhythm, structure, boundaries, or other information absent from the input
  representation;
- filenames are useful identities across database rebuilds but need explicit
  handling for moves, aliases, and duplicate content;
- application code is a compatibility and workflow precedent, not proof that a
  representation or learned metric improves perceived playlist quality.

The appropriate `bliss-rs` responsibility is therefore to produce stable,
identified, confidence-aware analysis evidence and composable distance hooks.
Survey UX, personal data, model fitting, and playlist-specific policy should
remain downstream.
