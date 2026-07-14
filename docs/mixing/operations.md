# Psychoacoustics and operational concerns

**Status:** Living research and design proposal  
**Primary scope:** Research scope, UX, observability, and performance  
**Last reviewed:** 2026-07-14

## Psychoacoustic scope

Psychoacoustics should be treated as a source of hypotheses for the general
audio representation, not only for transition anchors, and not as a separate
runtime layer or a promise to reproduce MusicIP.

### Reasonable early work

- document the perceptual assumptions already present in spectral and chroma
  processing before adding another feature family;
- use a standards-based loudness implementation with correctly named outputs;
- test level normalization choices before comparing timbre;
- evaluate whether very low and very high frequency energy should influence
  perceived similarity as strongly as mid-band content;
- compare candidate perceptual descriptors with the current timbre, loudness,
  chroma, and tempo groups through feature-family ablations.

### Research work, not MVP assumptions

- simultaneous masking and spreading functions;
- temporal masking around transients;
- Bark-scale replacement of existing timbre features;
- learned perceptual embeddings;
- claims that a particular preprocessing chain models "what a human hears."

Bliss does not currently extract MFCCs. Applying A-weighting before hypothetical
MFCC extraction would therefore be a new pipeline rather than a correction to
the existing one. A-weighting is designed for particular sound-level
measurement contexts and is not automatically the correct preprocessing for a
new musical timbre descriptor. Any such experiment must be evaluated against
unweighted and loudness-normalized baselines.

## User experience and configuration

The development version should expose as little configuration as possible:

- enhanced similarity experiments: off/on or an explicitly named experimental
  method;
- variety policy: off/on, with at most one advanced influence control;
- transition-aware reranking: off/on;
- transition influence: one advanced slider, if needed for evaluation;
- personalization: optional, with the existing learned-matrix influence kept as
  an advanced control rather than a prerequisite;
- feedback progress: judgments collected, current model tier, held-out evidence,
  and whether more answers are expected to help;
- analysis status/coverage: informational;
- rebuild enhanced analysis: maintenance action.

Feature families, segment policy, anchor duration, normalization method,
candidate-pool multiplier, and individual DSP weights should remain experimental
settings or command-line options until there is evidence that users benefit from
controlling them.

All enhanced methods should initially default to **off** until analysis
migration, fallback behavior, evaluation, and performance are proven.
Personalization is different: the unpersonalized baseline remains the default,
while an existing compatible personal matrix may continue to be opt-in. The UI
should invite short, resumable feedback sessions rather than imply that users
must complete 100 or more rounds before BlissMixer becomes useful.

## Observability

Debug output should make a decision explainable without logging raw audio:

- active feature schema and representation type;
- selected global algorithm and seed tracks;
- baseline and enhanced global ranks/scores when an experiment is active;
- enhanced-analysis coverage and missing-feature fallbacks;
- actual boundary source track;
- candidate pool size and anchor-data coverage;
- relevance-versus-diversity contributions and duplicate suppression;
- normalization method and active weights;
- personal-metric schema, model tier, validation confidence, normalization,
  effective blend contribution, and fallback reason;
- for top candidates: global rank/score, transition rank/distance, loudness
  penalty, final score, and missing-data fallback;
- analysis/schema version mismatches;
- time spent in global search, metadata lookup, and reranking.

## Performance expectations

- Audio decoding and feature extraction happen offline.
- Runtime metadata should be loaded or indexed so scoring does not perform an
  SQLite query per descriptor or candidate.
- Normal mixing should load only hot summaries, anchors, and selected segments;
  dense frame sequences remain cold unless an explicit algorithm needs them.
- `bliss-rs` analysis products should be opt-in so Version 2-only consumers do
  not pay segmentation or frame-retention cost.
- Shared transforms and intermediate measurements should be reused instead of
  decoding or computing parallel independent definitions of the same evidence.
- Enhanced similarity and task-specific reranking should add only a small
  fraction of the existing mix-request latency.
- Memory use should be measured with a realistic library, especially if window,
  segment, or anchor vectors are retained in memory.

No numeric latency or memory budget is committed until a prototype establishes
a baseline on the project's target hardware.
