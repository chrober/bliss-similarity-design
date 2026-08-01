# Implementation and comparison evidence

**Status:** Descriptive evidence inventory
**Primary scope:** Existing code, project documentation, and related implementations  
**Last reviewed:** 2026-08-01

## Historical, implementation, and comparison evidence

- Bliss [`Analysis`](https://docs.rs/bliss-audio/latest/bliss_audio/struct.Analysis.html)
  and [`AnalysisIndex`](https://docs.rs/bliss-audio/latest/bliss_audio/enum.AnalysisIndex.html)
  document the versioned 23-feature representation. The analysis research pages
  summarize its scientific rationale and candidate extensions without proposing
  upstream code changes.
- The Bliss [changelog](https://docs.rs/crate/bliss-audio/0.11.2/source/CHANGELOG.md)
  records the Version 2 chroma additions, and the [chroma
  source](https://docs.rs/bliss-audio/latest/src/bliss_audio/chroma.rs.html)
  shows pitch-rotation-based, transposition-invariant templates.
- The [MusicIP patent](https://patents.google.com/patent/WO2005038666A1/en)
  is evidence for described acoustic attributes, fingerprints, group profiles,
  and ordering methods, but not proof that every embodiment shipped or that the
  inferred population-weighting formula is correct.
- The deployed [MusicIP HTTP
  API](https://github.com/LMS-Community/slimserver/blob/public/9.2/Slim/Plugin/MusicMagic/HTML/EN/plugins/MusicMagic/html/docs/httpprotocol.html)
  and [LMS plugin
  source](https://github.com/LMS-Community/slimserver/blob/public/9.2/Slim/Plugin/MusicMagic/Plugin.pm)
  corroborate user-visible seed, mood, recipe, style, variety, and filtering
  behavior.
- The public [`libofa` source
  package](https://sources.debian.org/src/libofa/0.9.3-15/) is fingerprinting
  code; it is not treated here as the MusicIP similarity implementation.
- [`AudioMuse-AI`](https://github.com/NeptuneHub/AudioMuse-AI) documents the
  closest current open-source self-hosted comparison system, while its
  [configuration reference](https://neptunehub.github.io/AudioMuse-AI/PARAMETERS/)
  shows why audio-only and multimodal modes must be evaluated separately.
  Its [main documentation](https://neptunehub.github.io/AudioMuse-AI/) and
  [FAQ](https://neptunehub.github.io/AudioMuse-AI/FAQ/) document current Lyrion
  support, ARM operation, and the tested Raspberry Pi 5 8 GB/NVMe profile.
- [`Essentia`](https://github.com/MTG/essentia), its
  [`MusicExtractor`](https://essentia.upf.edu/tutorial_extractors_musicextractor.html),
  and its [model catalogue](https://essentia.upf.edu/models.html) provide
  current descriptor and learned-representation baselines, not a prescribed
  mixer contract.
- [librosa feature extraction](https://librosa.org/doc/latest/feature.html) and
  [`musicnn`](https://github.com/jordipons/musicnn) provide research building
  blocks whose pooling, schema, distance, and deployment policy remain the
  responsibility of the experiment.
- [Plex Sonic
  Analysis](https://support.plex.tv/articles/sonic-analysis-music/) documents a
  closed current product reference for similar tracks, radio, and mixes.

## Related documents

- [Bliss Analysis Evolution](../index.md)
  - research synthesis for descriptor hypotheses, temporal representations,
  confidence, evaluation, and analysis cost; it is not an upstream code design.
- [ALGORITHMS.md](https://github.com/chrober/lms-blissmixer/blob/master/ALGORITHMS.md) - current candidate-generation algorithms and
  shared filtering behavior.
- [METRIC_LEARNING.md](https://github.com/chrober/lms-blissmixer/blob/master/METRIC_LEARNING.md) - learned Mahalanobis matrix and
  existing listener survey.
- [PATH_INTERPOLATION.md](https://github.com/chrober/lms-blissmixer/blob/master/PATH_INTERPOLATION.md) - multi-track paths toward a
  known destination, a related but distinct feature.

## Related implementations

- [`bliss-learner`](https://github.com/chrober/bliss-learner) - this project's
  public but experimental standalone Rust port, adapted to the LMS survey,
  `TracksV2` schema, JSON artifacts, and progress notifications; it is not an
  upstream Bliss component.
- [`chrober/bliss-mixer`](https://github.com/chrober/bliss-mixer) - the fork
  that adds variance-based Adaptive Weighting and learned-matrix support to the
  upstream mixer. It loads `bliss-learner` output through `--matrix`, applies
  its Mahalanobis metric directly for a single seed, and can blend it with
  seed-variance weighting for multiple seeds.
- [`bliss-metric-learning`](https://github.com/Polochon-street/bliss-metric-learning)
  - the `bliss-rs` author's explicitly experimental Python survey and metric
  trainer from which `bliss-learner` ports the core algorithm.
- [`blissify-rs`](https://github.com/Polochon-street/blissify-rs) - the
  `bliss-rs` author's MPD application and the original database, playlist, and
  Mahalanobis-matrix consumption context for `bliss-metric-learning`.
- [`AudioMuse-AI`](https://github.com/NeptuneHub/AudioMuse-AI) - current
  self-hosted end-to-end comparison system with sonic analysis, similarity,
  clustering, paths, and LMS/Lyrion integration; it is a separate application
  stack rather than a `bliss-rs` consumer.
