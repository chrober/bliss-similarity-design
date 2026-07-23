# Analysis delivery, risks, and open questions

**Status:** Living research and design proposal  
**Primary scope:** Phased bliss-rs research and API evolution  
**Last reviewed:** 2026-07-23

## Delivery phases

### Phase 0: baseline and API discovery

- document current intermediate measurements and allocation;
- benchmark Version 2 extraction;
- identify reusable transforms and public/private API constraints;
- verify current consumer contracts in both `blissify-rs`/MPD and the
  LMS-oriented analyzer/mixer stack;
- define representation schema identity;
- assemble small audio and judgment fixtures;
- define aspect-specific evaluation tasks, leakage controls, and promotion
  criteria before descriptor tuning.

### Phase 1: experimental frame API

- expose one minimal, typed frame representation;
- preserve exact Version 2 results;
- attach timestamps and confidence where already available;
- retain enough tonal evidence for fixed-window multi-scale experiments;
- implement serialization round trips outside the stable
  [`Analysis`](https://github.com/Polochon-street/bliss-rs/blob/master/src/song/mod.rs#L240) type;
- benchmark retention and streaming.

### Phase 2: high-value descriptor prototypes

- prototype tempo confidence/stability and onset density;
- prototype dynamics and bass-energy summaries;
- prototype lightweight vocal-activity, coverage, and temporal-profile evidence;
- compare current chroma with a perceptually motivated TIV or equivalent tonal
  representation;
- prototype tonal dispersion, harmonic-change rate/magnitude, and
  short/long-term harmonic relationships;
- compare soft harmonic transitions with any hard-label baseline;
- prototype repetition/change-point summaries from retained frames;
- use named Essentia or librosa measurements as external cross-checks where
  useful, without importing an undifferentiated extractor vector;
- run independent ablations.

### Phase 3: structure and anchors

- expose novelty/change-point primitives;
- compare fixed windows with context-sensitive segmentation;
- represent structural scale and alternative hypotheses where available;
- define configurable intro/outro anchors;
- add key-sensitive tonal evidence only for justified tasks;
- test short-input validity and confidence-aware fallback.

### Phase 4: optional learned-representation benchmarks

- select at least one reproducible lightweight music embedding, such as a
  musicnn or compact Essentia model, and, if practical, one larger MAEST or
  MERT research baseline;
- record exact model, input, pooling, objective, and augmentation provenance;
- evaluate frame/segment and whole-track pooling independently;
- probe vocal delivery and extreme-technique classifiers or audio-language models
  as identified research baselines, not assumed production dependencies;
- compare learned, interpretable, and fused representations on the same held-out
  tasks;
- measure CPU, memory, artifact size, licensing, and platform constraints;
- keep the learned backend optional unless it demonstrates sufficient value.

### Phase 5: stable API review

- retain only descriptors with demonstrated value;
- decide base crate, feature-gated module, or companion crate ownership;
- stabilize manifests and serialization contracts;
- document MPD, LMS, and generic downstream migration paths.

### Phase 6: Version 3 decision

- select any scalar candidates that meet promotion criteria;
- define default normalization/weights;
- coordinate MPD and LMS reanalysis, database, forest, mixer, and learner
  changes;
- preserve Version 2 comparison and compatibility paths.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| More descriptors degrade similarity | Require family ablations and held-out listener benefit. |
| Published classification gains are mistaken for mixing gains | Treat literature as candidate evidence and require target-task validation. |
| One generic similarity score hides incompatible musical aspects | Evaluate and expose aspect-conditioned views; keep fusion in consumers. |
| Structured API makes simple use expensive | Make products explicit and opt-in; preserve [`Song::analyze`](https://github.com/Polochon-street/bliss-rs/blob/master/src/song/mod.rs#L386). |
| Public intermediates freeze poor abstractions | Expose typed products and manifests, not every internal buffer. |
| Temporal storage becomes excessive | Use shaped BLOBs, hot/cold retention, and avoid quadratic intermediates. |
| Different cadences are forced into false alignment | Permit typed series or declare resampling explicitly. |
| Short excerpts yield confident nonsense | Define minimum support and return validity/confidence. |
| Version 3 breaks downstream models | Coordinate schema identity, migrations, and explicit rejection. |
| New features dominate by scale or redundancy | Define normalization and baseline weights before promotion. |
| Instrument classifiers introduce bias and deployment burden | Keep optional and lower priority; expose probabilities and model identity. |
| Hard vocal categories erase mixed techniques and encode unsupported identity claims | Prefer temporal, multi-label evidence; use continuous register measures and describe binary presentation models as model-relative perception only. |
| Vocal source separation adds compute and can introduce artifacts | Keep separation optional; compare mixture-based detection first and measure incremental value on target hardware. |
| Learned embeddings hide task-incompatible invariances | Record objective/augmentations and test transformation behavior per task. |
| Learned-model artifacts disappear or change | Store immutable identity and reject incompatible data; retain non-model baselines. |
| A full-system comparator wins through lyrics, metadata, clustering, or UX rather than better audio evidence | Report audio-only and multimodal configurations separately; do not call a system comparison a descriptor ablation. |
| A broad external extractor becomes an accidental unversioned feature dump | Select named hypotheses, record exact versions and configuration, and ablate each retained family. |
| An experimental dependency creates incompatible licensing or deployment requirements | Keep external baselines separable and review redistribution, model, and service licenses before adoption. |
| A comparison system works on a high-end Pi 5 but is assumed suitable for every Lyrion appliance | Benchmark representative Pi generations, memory sizes, and storage classes while playback is active. |
| Segmentation labels are treated as musical truth | Prefer boundaries and confidence; keep named sections out of the initial contract. |
| One segmentation is treated as uniquely correct | Preserve level/viewpoint and permit alternative hypotheses. |
| Experimental DB policy leaks into the library | Keep persistence consumer-owned and specify only serialization contracts. |

## Open questions

1. Should structured analysis live in the base crate, behind a Cargo feature, or
   in a companion crate?
2. Which intermediate spectral, loudness, onset, tempo, and chroma calculations
   can be shared without destabilizing current results?
3. Should temporal descriptor families retain separate cadences or align to one
   common frame sequence?
4. What minimum frame cadence supports useful structure and anchors at acceptable
   storage cost?
5. Should callers receive retained vectors, iterators, sinks, or multiple API
   styles?
6. How should representation schema IDs be generated and compared?
7. Which confidence values are available from current dependencies, and which
   require calibration?
8. Which descriptor family gives the strongest first improvement over Version 2?
9. Can repetition and change-point summaries remain stable across track duration
   and alternate masters?
10. Which anchor features remain valid at 15, 20, and 30 seconds?
11. Is a general segmentation primitive mature enough for `bliss-rs`, or should
    it remain in a companion experimental crate initially?
12. Which products should be serializable under the existing `serde` feature?
13. Should `f32le-row-major-v1` be standardized by `bliss-rs` or left to each
    consumer with a shared manifest?
14. What evidence threshold justifies Version 3 and a full library reanalysis?
15. How should Version 2 and Version 3 coexist in library and playlist APIs?
16. Which fixed-window scales best separate chord-scale change, harmonic rhythm,
    and large-scale tonal movement?
17. Does a TIV representation add held-out value beyond the existing chroma
    intermediates on the target contemporary library?
18. Can soft harmonic-transition evidence be exposed without taking a hard
    dependency on one chord-recognition model?
19. Which reproducible learned embedding is small and portable enough to serve
    as the first optional benchmark?
20. Which consented passive signals can reduce `bliss-learner` survey effort,
    and how should active questions be selected and evaluated?
21. Which declared audio-only AudioMuse-AI configuration is reproducible enough
    to serve as the first end-to-end comparison baseline?
22. Which Essentia descriptor subset and which MAEST, musicnn, or MERT pooling
    policies provide fair component baselines without defining the proposed API
    around one external toolkit or model?
23. On which Raspberry Pi configurations does AudioMuse-AI provide acceptable
    initial analysis, incremental analysis, clustering, idle, and concurrent
    playback performance compared with the Bliss pipeline?
24. What is the lightest vocal-activity detector that remains calibrated across
    the target library and provides useful temporal coverage?
25. Which continuous register, activity, or timbral measurements add similarity
    value beyond vocal-versus-instrumental detection?
26. Can clean, spoken, shouted, screamed, growled, and other overlapping delivery
    evidence generalize beyond small or genre-specific annotated corpora?
27. Does optional vocal-source separation improve the retained descriptors enough
    to justify its compute, artifact, licensing, and deployment costs?
