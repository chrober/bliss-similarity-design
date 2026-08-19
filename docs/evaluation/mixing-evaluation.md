# Mixing evaluation

**Status:** Living research and design proposal  
**Primary scope:** Task-specific quality, coherence, diversity, personalization, and transitions  
**Last reviewed:** 2026-08-19

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

## Fixed-set sequencing evaluation

Evaluate the [experimental fixed-set sequencing and bridge
insertion](../mixing/fixed-set-sequencing.md) workflow as a separate task from
retrieval. The curated input defines the membership baseline; ordering quality
cannot compensate for losing, replacing, or silently adding a track.

### Structural correctness

Every run must verify:

- **Reorder-only membership:** the output path multiset exactly equals the
  original path multiset, every path occurs once, and each extended-M3U metadata
  block remains attached to its track.
- **Bridged membership:** all original members remain exactly once, every added
  path is unique and outside the original set, and the number of additions
  equals the requested explicit bridge count or the separately reported
  automatic decision.
- **Order-preserving gap filling:** the complete original sequence is an
  identical ordered subsequence of the output. Each addition is assigned to a
  declared internal, opening, or closing gap, and endpoint additions occur only
  when the policy explicitly permits them.
- **Destination-constrained routing:** the existing source sequence remains an
  identical prefix, the selected destination occurs exactly once at the end of
  the appended route, and a failed request leaves the source unchanged.
- **Repeat policy:** zero track, artist, and album look-back violations under
  the captured LMS BlissMixer settings, checked again after every insertion and
  on the final route.
- **Determinism:** identical frozen inputs, algorithm parameters, random seed,
  and restart count reproduce the selected order and reported scores.

An explicit bridge-count run that cannot find the requested number of
acceptable repeat-safe tracks should fail. Returning fewer additions without
changing the declared mode would make the output contract ambiguous.

### Route metrics and controls

For every evaluated order, report the leg count and at least:

- total and mean transition cost;
- worst transition cost and position;
- an upper-tail statistic such as the 90th or 95th percentile;
- the complete route objective, with the worst-leg penalty reported
  separately; and
- artist and album repeat counts even when both are zero.

Compare against the same membership in:

- its original order;
- several seeded random orders, reporting their distribution rather than one
  convenient sample;
- reversed original and reversed optimized orders; and
- the best reorder-only route before any bridge is added.

The reversed controls are particularly important for Adaptive scoring because
its sliding context makes route costs directional. Search restarts are not
independent baselines: they are attempts by the same optimizer.

### Destination-route disagreement and path quality

Destination-constrained routes need a dedicated false-acceptance fixture set.
Include endpoints for which the active learned metric, Static metric, contextual
continuation score, and listening judgment disagree. For each case, compare:

- direct-edge acceptance under the learned metric alone;
- direct-edge acceptance under Static alone;
- conservative acceptance using the higher separately calibrated risk;
- routes found at every permitted intermediate depth; and
- the direct and routed boundaries in a blind listening review.

Report each model's raw distance and source-relative percentile separately.
Never add the raw learned and Static distances: they do not share a calibrated
scale. A disagreement is itself diagnostic evidence and should remain visible
in the result trace.

An automatic destination-route bridge count is a **maximum search budget**, not
a target count and not a promise that consuming more of it improves quality. A
shorter route that satisfies the declared acceptance rule may be preferable to
a longer one. Evaluation should nevertheless retain the best admissible route
at each explored depth so that stopping policy, route-length penalty, worst-leg
risk, total path quality, and listener preference can be compared rather than
conflated.

Runtime reports must separate inventory preparation, reference-distribution
construction, candidate discovery, exact route scoring, and local search. Run
the same fixtures at multiple library sizes, including at least a roughly
64,000-track real or synthetic inventory and a 200,000-track condition. Report
both warm- and cold-cache behavior and verify that the configured search effort
changes bounded work rather than the result contract.

### Bridge ablation and evidence

Compare the reorder-only backbone with the bridged result and, where practical,
with the same bridge candidates inserted under simpler pairwise scoring. For
each accepted bridge, report:

- the direct leg that triggered consideration;
- incoming, outgoing, maximum-leg, and two-leg costs after contextual
  rescoring;
- the Last.fm evidence tier: both endpoints, one endpoint, collection fallback,
  original-artist fallback, or Bliss-only fallback;
- the endpoint sources that supplied evidence;
- whether the endpoint-local pool was empty; and
- any rejected insertion caused by acoustic or repeat constraints.

Aggregate results should state how often collection-wide fallback was used.
The frozen original-playlist artist profile must be verified so bridge tracks
cannot generate recursively favorable evidence.

For provider-neutral experiments, extend this trace with recording-level
support, artist-level support, provider identity, identity-match confidence,
cache state, and the precise fallback that admitted the candidate. Do not merge
raw provider scores as though they shared a scale. Evaluate both-endpoint and
one-endpoint recording support before artist support, and allow
collection-profile evidence only when the endpoint-local semantic pool is
empty. The complete evidence snapshot must remain frozen from the original
request so inserted tracks cannot recursively expand it.

Provider behavior needs explicit controls: all providers disabled, each
provider alone, all enabled, partial coverage, unavailable service, and a
declared stale-cache policy. These runs determine whether semantic evidence
adds value beyond Bliss-only scoring and whether failure correctly degrades
capability instead of invalidating an otherwise feasible acoustic route.

For a multi-track gap route, report every created leg and rescore through the
right immutable anchor. Compare it with the direct anchor-to-anchor leg and
with the best admissible single insertion. For a destination-constrained route,
compare the direct source-to-destination transition with routes of controlled
intermediate length; route length and discovery value must be reported beside
flow rather than treated as free improvements.

### Human assessment

Assess at least three concepts separately:

1. **Relevance:** does each track still belong in the playlist or local context?
2. **Variety:** does the sequence avoid unwanted homogeneity and repetition?
3. **Local flow:** does each directional transition sound appropriate?

Listening review is essential. The prototype's whole-track Adaptive cost is a
proxy that cannot observe the actual outro, intro, silence, fade, or section at
the playback boundary. A lower objective or improved upper tail is useful
diagnostic evidence, not validation of audible transition quality. Blind or
counterbalanced reviews should include the original, optimized, and bridged
variants without revealing their objective scores.

The current aggregate observations are recorded as a deliberately limited
[two-playlist exploratory case study](fixed-set-case-study.md).

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
