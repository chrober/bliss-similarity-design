# Current system and ecosystem

**Status:** Descriptive baseline and research context
**Primary scope:** Existing analysis, mixer, and consumer architecture  
**Last reviewed:** 2026-08-01

The existing architecture is described in [ALGORITHMS.md](https://github.com/chrober/lms-blissmixer/blob/master/ALGORITHMS.md):

- `bliss-analyser` decodes audio and stores the current Bliss Version 2 vector
  in SQLite: tempo; zero-crossing rate; mean and standard deviation of spectral
  centroid, rolloff, and flatness; mean and standard deviation of loudness; and
  13 chroma-derived features. Version 1 contained 20 features; Version 2 added
  three chroma features. The vector contains both means and dispersions, but no
  MFCCs and no temporal ordering. See the public
  [`AnalysisIndex`](https://docs.rs/bliss-audio/latest/bliss_audio/enum.AnalysisIndex.html),
  [`Analysis`](https://docs.rs/bliss-audio/latest/bliss_audio/struct.Analysis.html),
  and [changelog](https://docs.rs/crate/bliss-audio/0.11.2/source/CHANGELOG.md).
- The upstream
  [`CDrummond/bliss-mixer`](https://github.com/CDrummond/bliss-mixer) reads
  those precomputed features and exposes the HTTP mixing API used by this
  design.
- The [`chrober/bliss-mixer`](https://github.com/chrober/bliss-mixer) fork
  retains that upstream behavior and adds variance-based weighting plus
  learned-matrix loading, direct use, and blending support.
- `lms-blissmixer` selects seeds, starts and calls the mixer fork, applies LMS
  integration behavior, and adds returned tracks to the queue. It already
  exposes the user-facing **Create bliss mix** / **Bliss Mix erstellen** action
  for immediate Bliss-based mix generation; newer playlist-optimizer work should
  credit that feature and define itself as a companion preview/persistence
  workflow rather than a replacement.
- Static Weights and Extended Isolation Forest are inherited mixer strategies.
  The fork's variance-based Adaptive Weighting is a third strategy, with the
  learned matrix available as an optional metric extension rather than a fourth
  candidate-search algorithm.
- The integrated similarity survey and `bliss-learner` are a project-specific
  experiment added to `lms-blissmixer`, not an upstream `bliss-rs` capability.
  The learner is a standalone Rust port of the upstream
  `bliss-metric-learning` experiment. It learns a 23x23 Mahalanobis matrix from
  personal odd-one-out judgments. The `chrober/bliss-mixer` fork loads the
  resulting JSON artifact through `--matrix`; it can use the matrix directly
  for a single seed or blend it with seed-variance weighting for multiple
  seeds. See [METRIC_LEARNING.md](https://github.com/chrober/lms-blissmixer/blob/master/METRIC_LEARNING.md).

These components and fallbacks define the baseline against which enhanced
analysis and scoring ideas are evaluated. This site does not require them to
change or prescribe how any successful experiment would be integrated.
