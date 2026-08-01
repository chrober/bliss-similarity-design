# Analysis research roadmap, risks, and open questions

**Status:** Living research and design proposal  
**Primary scope:** Phased evaluation of potential analysis enhancements
**Last reviewed:** 2026-08-01

## Scope

The phases below organize research, not `bliss-rs` implementation or release
work. They do not prescribe a public API, module layout, feature gate, companion
crate, feature version, storage schema, or upstream ownership. A research
prototype may use whichever reproducible tools are suitable for testing a
hypothesis.

## Research phases

### Phase 0: baseline and evaluation design

- document Version 2 extraction, ranges, cost, and known behavior;
- collect reproducible examples of suspected representation failures;
- assemble small audio, transformation, and listener-judgment fixtures;
- define aspect-specific retrieval and playlist tasks;
- define leakage controls, comparison baselines, and rejection criteria before
  tuning descriptors; and
- record the target library and hardware scope.

### Phase 1: temporal evidence experiments

- construct one minimal, identified frame or window representation in a
  research environment;
- retain exact timestamps and validity information;
- compare aligned and family-specific cadences;
- retain enough tonal evidence for fixed-window multi-scale experiments;
- compare summary-only calculation with retained temporal evidence; and
- measure bounded-input validity, storage, memory, and analysis cost.

### Phase 2: high-value descriptor prototypes

- prototype tempo confidence and stability, onset density, and rhythmic
  regularity;
- prototype dynamics, perceived-energy, and bass-energy summaries;
- prototype lightweight vocal activity, coverage, and temporal profile;
- compare current chroma with a perceptually motivated TIV or equivalent tonal
  representation;
- prototype tonal dispersion, harmonic-change rate and magnitude, and
  short/long-term harmonic relationships;
- compare soft harmonic transitions with any hard-label baseline;
- prototype repetition and change-point summaries; and
- use named Essentia or librosa measurements as external cross-checks without
  importing an undifferentiated extractor vector.

Each family receives an independent ablation against Version 2 and against the
simplest plausible alternative.

### Phase 3: structure and local context

- compare conventional novelty and change-point baselines;
- compare fixed windows with content-sensitive segmentation;
- retain structural scale and alternative hypotheses where available;
- compare fixed-duration and structure-aligned intro/outro anchors;
- evaluate key-sensitive tonal evidence only for justified tasks; and
- test short-input validity and confidence-aware fallback.

### Phase 4: learned-representation benchmarks

- select at least one reproducible lightweight music embedding and, if
  practical, one larger research baseline;
- record exact model, input, pooling, objective, augmentation, license, and
  artifact identity;
- evaluate frame, segment, and whole-track pooling independently;
- probe vocal-delivery and extreme-technique classifiers or audio-language
  models as identified research baselines;
- compare learned, interpretable, and fused representations on the same held-out
  tasks; and
- measure CPU, memory, artifact size, platform, and accelerator constraints.

### Phase 5: evidence synthesis

- retain only candidates with demonstrated task value;
- publish negative results and unsupported domains;
- compare compact and dense variants of every retained family;
- report quality, uncertainty, licensing, and resource cost together; and
- state which conclusions generalize beyond the evaluated library and which do
  not.

Any later implementation or upstream discussion begins only after this research
phase and is outside the present document.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| More descriptors degrade similarity | Require family ablations and held-out listener benefit. |
| Published classification gains are mistaken for mixing gains | Treat literature as candidate evidence and require target-task validation. |
| One generic similarity score hides incompatible musical aspects | Evaluate aspect-conditioned views independently. |
| Temporal evidence becomes expensive without adding value | Compare compact summaries with dense representations and report cost. |
| Different cadences are forced into false alignment | Compare typed series with declared resampling. |
| Short excerpts yield confident nonsense | Define minimum support and evaluate validity as a function of duration. |
| New features dominate through scale, redundancy, or multiplicity | Normalize explicitly and compare family-level ablations. |
| Instrument classifiers introduce bias and deployment burden | Treat them as optional model-relative evidence and expose probabilities. |
| Hard vocal categories erase mixed techniques or imply unsupported identities | Prefer temporal, multi-label evidence and continuous register measures. |
| Vocal source separation adds compute and artifacts | Compare mixture-based detection first and measure incremental value. |
| Learned embeddings hide task-incompatible invariances | Record objectives and augmentations and test transformations directly. |
| Learned artifacts disappear or change | Record immutable artifact identity and retain non-model baselines. |
| A full system wins through metadata, lyrics, clustering, or UX | Separate component, audio-only, hybrid, and full-system comparisons. |
| A broad toolkit becomes an accidental feature dump | Select named hypotheses and ablate every retained family. |
| Licensing or packaging invalidates an attractive result | Include license and deployment review in the experiment. |
| High-end Raspberry Pi results are generalized to all servers | Benchmark representative hardware and storage classes during playback. |
| Segmentation labels are treated as musical truth | Prefer boundaries, confidence, scale, and alternative hypotheses. |
| Structural variance becomes a genre proxy | Treat it as evidence about aggregation reliability, not a genre label. |

## Open research questions

1. Which specific shortcomings of the current 23 features can be demonstrated
   reproducibly?
2. Which descriptor family gives the strongest first improvement over Version 2?
3. Should temporal families retain separate cadences or align to a shared one?
4. What minimum cadence supports useful structure and anchors at acceptable cost?
5. Which confidence values can be calibrated reliably across the target library?
6. Can repetition and change-point summaries remain stable across duration and
   alternate masters?
7. Which anchor measurements remain valid at 15, 20, and 30 seconds?
8. Which fixed-window scales best separate chord-scale change, harmonic rhythm,
   and large-scale tonal movement?
9. Does a TIV representation add held-out value beyond the current chroma
   representation on a contemporary heterogeneous library?
10. Does soft harmonic-transition evidence outperform hard decoded labels?
11. Which reproducible learned embedding is small enough to be a fair
    lightweight benchmark?
12. Which consented passive signals can reduce explicit survey effort, and how
    should active questions be selected?
13. Which audio-only AudioMuse-AI configuration is reproducible enough to serve
    as an end-to-end baseline?
14. Which Essentia descriptors and MAEST, musicnn, or MERT pooling policies make
    fair component baselines?
15. On which Raspberry Pi configurations do comparison systems provide
    acceptable analysis and playback performance?
16. What is the lightest vocal-activity detector that remains calibrated across
    the target library?
17. Which register, activity, or timbral measurements add similarity value
    beyond vocal-versus-instrumental detection?
18. Can clean, spoken, shouted, screamed, growled, and overlapping delivery
    evidence generalize beyond small genre-specific corpora?
19. Does vocal-source separation improve retained descriptors enough to justify
    its artifacts and cost?
20. What evidence would justify moving any result from a research condition to
    a discussion with relevant project maintainers?
