# Mixing evaluation

**Status:** Living research and design proposal  
**Primary scope:** Task-specific quality, coherence, diversity, personalization, and transitions  
**Last reviewed:** 2026-07-14

## Dataset and fixtures

Create a small, redistributable or locally configured evaluation set containing:

- listener judgments about which tracks or pairs feel similar;
- tracks with similar current Bliss vectors but clearly different perceived
  character, and the inverse;
- alternate versions or sections that expose timbre, loudness, rhythm, and
  structure behavior;
- fade-out to fade-in and cold-start combinations;
- quiet-to-loud and loud-to-quiet boundaries;
- stable and structurally varied tracks;
- short tracks and tracks with leading/trailing silence;
- cases where global similarity and local compatibility disagree.

## Automated validation

- deterministic extraction for fixed audio fixtures;
- descriptor units, ranges, normalization, and invariance tests;
- confidence calibration and behavior when a feature is invalid or ambiguous;
- window, segmentation, anchor-boundary, and short-track tests;
- schema-version and stale-file invalidation tests;
- learned-matrix dimension, version, finiteness, symmetry,
  positive-semidefiniteness, and scale-normalization tests;
- baseline-versus-enhanced nearest-neighbor regression reports;
- score normalization tests for all three global algorithms;
- missing-metadata and mixed-version fallbacks;
- no regression in existing filters and repeat handling;
- runtime and memory benchmarks on a large synthetic metadata set.

## Task-specific evaluation

Evaluation labels must match the scoring task:

- general song similarity is usually a symmetric pair or triplet judgment;
- transition quality is directional (`A -> B`) and boundary-dependent;
- playlist/session fit is a set- or sequence-level judgment involving
  coherence, coverage, repetition, and trajectory.

One label type should not be silently reused as ground truth for another.

## General similarity evaluation

Evaluate new descriptors and representations through:

- nearest-neighbor inspection against the current 23-feature baseline;
- held-out similarity triplets from the existing or an extended survey;
- feature-family ablation: baseline plus exactly one new family at a time;
- retrieval consistency across quiet/loud masters, short/long tracks, and
  structurally simple/complex tracks;
- playlist-level ratings for coherence, relevance, and variety.

Structural and temporal features need their own ablations. A higher-dimensional
model that merely memorizes the evaluation library is not an improvement.

## External system and representation baselines

Where practical, run AudioMuse-AI over the same library in a declared
audio-only configuration. Compare neighbor and playlist outcomes, resource
cost, analysis coverage, and failure behavior, but treat it as an end-to-end
system comparison rather than evidence for or against one descriptor. Report
any CLAP-, lyrics-, text-, tag-, or metadata-assisted mode as a separate hybrid
baseline.

Run the comparison on representative deployment hardware rather than only a
development workstation. At minimum, distinguish the documented Raspberry Pi 5
8 GB/NVMe configuration from older, lower-memory, or microSD-based Lyrion
systems, and record concurrent playback behavior as well as offline throughput.

Essentia/librosa descriptors and MAEST, musicnn, or MERT embeddings should be
evaluated as identified representation components under the same retrieval,
pooling, diversity, and listener-evaluation harness used for Bliss experiments.
Exact versions, model artifacts, input windows, pooling, normalization, and
index configuration must be recorded. Plex Sonic Analysis can inform UX and,
where the same private library is available, an informal playlist comparison;
its closed implementation is not a reproducible algorithmic control.

## Context-profile, diversity, and coherence evaluation

Evaluate multi-seed and group representations on both compact and deliberately
multimodal contexts. Compare:

- normalized centroid, robust or trimmed centre, and a combined-set model;
- mean, median, and minimum candidate-to-member distance;
- one-centre and small clustered or mixture profiles;
- seed-only, population-relative, metadata-context-only, and late-fused scores.

Use album and artist completion only as diagnostic proxy tasks. The primary
tests should use held-out user-made playlists, saved contexts, or session
continuations, with artist- and album-disjoint splits where practical. Report
dispersion and performance by group size so a method is not rewarded merely for
identifying a repeated artist or album.

For selected result sets and sequences, compare relevance-only ranking with
MMR, cluster coverage, relevance-aware submodular selection, and, only if
needed, a DPP-like method. Report at least:

- seed or context relevance;
- intra-list diversity and artist/album repetition;
- global feature variation;
- adjacent-track distance and local-versus-global coherence;
- listener-rated relevance, variety, flow, and boredom.

Include random-order controls and retain the same candidate frontier across
policy comparisons. A method that increases objective diversity without
improving perceived variety, or that improves local smoothness by making the
whole sequence homogeneous, has not validated the design goal.

## Personalization evaluation

Evaluate personalization as a learning curve, not at one arbitrary survey
count. At several evidence thresholds, compare:

- the compatible unpersonalized baseline;
- population-aware or group-profile weighting;
- family-only, diagonal, low-rank, and full-matrix personal models;
- uniform-random versus active triplet selection;
- explicit judgments alone versus explicit plus lower-weight weak feedback;
- each weak signal type separately before any combined behavioral model.

Report held-out triplet accuracy with uncertainty, but also blind playlist
ratings and nearest-neighbor changes. Split evaluation by listener and, where
practical, by track or artist so repeated entities do not make generalization
look easier than it is. Record survey time, skips, abandoned rounds, and useful
improvement per judgment. The target is not merely a more accurate learner; it
is a useful improvement with a tolerable interaction cost.

## Transition evaluation

Run blind comparisons of:

- current global-only ordering;
- global plus anchor reranking;
- anchor reranking with and without loudness penalties;
- fixed-window versus structure-aligned anchors;
- whole-track, boundary-specific, and learned distance functions;
- alternative candidate-pool sizes, anchor lengths, normalization methods, and
  score weights.

Collect separate ratings for transition smoothness, next-track appropriateness,
and overall variety. A transition can be locally smooth while being globally
boring or semantically wrong; one rating must not stand in for all three.

The existing metric-learning survey can provide general similarity judgments.
Transition feedback therefore needs different training/evaluation data from
symmetric song-similarity triplets.

Where structural analysis is available, separately ablate section-boundary,
downbeat, timbre, chroma, loudness, and vocal-presence evidence. This tests
whether the inexpensive fixed-anchor baseline is sufficient and prevents a
complex transition model from receiving credit for one dominant feature.
