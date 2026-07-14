# Related bliss-rs resources

**Status:** Living research and design proposal  
**Primary scope:** Implementation sources and companion design material  
**Last reviewed:** 2026-07-14

- `src/song/mod.rs` - current [`Analysis`](https://github.com/Polochon-street/bliss-rs/blob/master/src/song/mod.rs#L240),
  [`AnalysisIndex`](https://github.com/Polochon-street/bliss-rs/blob/master/src/song/mod.rs#L103), and extraction orchestration.
- `src/lib.rs` - [`FeaturesVersion`](https://github.com/Polochon-street/bliss-rs/blob/master/src/lib.rs#L147) and public exports.
- `src/temporal.rs` - current tempo and temporal descriptor implementation.
- `src/timbral.rs` - current spectral descriptor implementation.
- `src/chroma.rs` - current chromagram and aggregate interval features.
- `src/playlist.rs` - distance functions and fixed-dimension playlist consumers.
- `TODO.md` - existing evaluation, metric-learning, and playlist research notes.
- [`blissify-rs`](https://github.com/Polochon-street/blissify-rs) - upstream MPD
  application demonstrating Bliss analysis persistence, feature-version
  migration, playlist generation, and configurable distance metrics.
- [`bliss-metric-learning`](https://github.com/Polochon-street/bliss-metric-learning)
  - upstream experimental survey and Python metric trainer designed around a
  `blissify-rs` library.
- [`bliss-learner`](https://github.com/chrober/bliss-learner) - downstream
  public but experimental Rust port integrated into the
  [`chrober/lms-blissmixer`](https://github.com/chrober/lms-blissmixer) fork;
  neither the learner nor this integration is an upstream Bliss component.
- [`chrober/bliss-mixer`](https://github.com/chrober/bliss-mixer) - LMS-oriented
  fork that adds variance-based Adaptive Weighting and learned-matrix support
  to the upstream mixer; it consumes `bliss-learner` output through `--matrix`
  and applies or blends the learned Mahalanobis metric.
- [`AudioMuse-AI`](https://github.com/NeptuneHub/AudioMuse-AI) - current
  self-hosted end-to-end comparison system for sonic analysis, similarity,
  clustering, paths, and playlist integration, including LMS/Lyrion.
- [`Essentia`](https://github.com/MTG/essentia) - broad C++/Python analysis
  toolkit and model-inference ecosystem suitable for descriptor prototypes and
  external baselines, but not a canonical Bliss representation.
- [librosa feature extraction](https://librosa.org/doc/latest/feature.html) -
  Python research toolkit for spectral, tonal, rhythmic, temporal, and
  segmentation experiments.
- [Plex Sonic
  Analysis](https://support.plex.tv/articles/sonic-analysis-music/) - closed
  product and UX reference for local sonic neighbors, radio, and mixes; not a
  reproducible representation baseline.
- [Enhanced Bliss Similarity and Mixing
  Quality](../index.md)
  - cross-repository feature and mixing-quality design.
