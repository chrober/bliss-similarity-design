# Enhanced analysis inputs for mixing

**Status:** Living research and design proposal  
**Primary scope:** How optional analysis products can inform downstream selection  
**Last reviewed:** 2026-07-14

## Baseline and extension strategy

The existing 23 Bliss features remain the reference representation. Enhanced
analysis should initially store additional data separately rather than silently
changing the meaning or order of those features. This allows the same tracks to
be scored by both baseline and experimental criteria.

Separate metadata is an experimentation and compatibility strategy, not a
separate definition of shared audio extraction. Reusable descriptors, temporal
measurements, and representation contracts belong in `bliss-rs`; application
experiments can remain external until their algorithms and dependencies are
ready for a library API. LMS-specific orchestration and mixing policy remain in
the surrounding analyzer/mixer ecosystem.

## Flat and structured analysis boundary

The current proposed representation model is:

```text
Version 2 Analysis
  stable 23-feature flat baseline

Parallel bliss-rs analysis products
  optional schema-defined global descriptors
  optional aligned or typed frame series
  optional structure analysis and segments
  optional configured intro/outro anchors
  optional model-identified learned embeddings
  cross-cutting schema, provenance, confidence, and invariance metadata

Possible Version 3 Analysis
  only validated scalar summaries
  coexists with Version 2
  does not absorb variable-length structured products
```

Optional products are requested explicitly so a consumer that needs only the
baseline does not pay for dense temporal analysis. Detailed Rust API and schema
identity design belongs to the companion document.

Candidate feature families include:

- perceptually motivated timbre or spectral descriptors;
- perceived-energy, loudness-range, dynamics, crest-factor, and spectral-flux
  descriptors;
- tempo confidence and stability, pulse clarity, rhythmic density, onset
  regularity, and syncopation-related descriptors;
- bass-specific energy, onset, pitch-class, and rhythmic evidence;
- key/mode confidence, tonal stability, harmonic-change rate, and tonal
  trajectory;
- temporal statistics that retain more than a whole-track mean;
- repetition, segment, novelty, and structural-change descriptors;
- optional confidence-bearing instrument or source-character evidence;
- intro/outro anchors for directional transition scoring.

This list is a research backlog, not a proposed production vector. Each family
needs a precise hypothesis and an ablation against the baseline.

The priority is the missing mid-level musical layer between low-level aggregate
DSP and high-level metadata: rhythm, structure, energy development, temporal
harmony, and bass behavior. Instrument classifiers and embeddings are lower
priority because they add model, bias, licensing, and deployment concerns.

Each feature family must also declare an invariance contract. For global
similarity, a descriptor may ideally remain stable across codec changes, gain,
small trims, and alternate masters. For boundary scoring, gain trajectory,
fades, silence, and absolute tonal position may be exactly the information to
preserve. Intermediate measurements should be stored where practical so that
task-specific representations can apply different policies without decoding
the audio again.

## Temporal windows and segmentation

Windowed temporal evidence is a common foundation for structural variance,
segmentation, and transition anchors. Depending on the descriptor families, the
analyzer may retain one aligned sequence or several typed series at their native
cadences, then derive several representations:

- robust whole-track statistics beyond a single mean;
- a novelty curve or change-point candidates;
- a small set of coherent segment vectors;
- structural-variance descriptors;
- fixed intro and outro anchors.

Fixed windows are simpler and reproducible; content-aware segmentation may
better represent musical sections but adds algorithmic and schema complexity.
The first prototype should preserve the source series long enough to compare
both approaches instead of committing immediately to K-means or a particular
segmentation algorithm. Every series must declare its cadence and whether it is
native or resampled; alignment and resampling policy are part of representation
identity.

Useful intermediate forms include a self-similarity matrix, novelty curve, and
change-point confidence. They permit later comparison of robust statistics,
explicit segments, and distributional or sequence-aware distances without
assuming that musical sections form spherical clusters.

## Anchor windows

A fixed first and last 20-30 seconds is an intuitive starting point, not a
validated requirement.

The analyzer should define windows in terms of audible content, with explicit
handling for very short tracks and leading/trailing digital silence. Candidate
policies include:

- fixed-duration windows after conservative silence trimming;
- duration-relative windows with minimum and maximum lengths;
- windows ending immediately before the detected fade or track boundary;
- multiple short subwindows summarized into one anchor.

**Initial experiment:** compare fixed 15-, 20-, and 30-second anchors. Avoid
aggressive silence trimming until it is clear how intentional silence and fades
should behave.

## Anchor feature vectors

**Working proposal:** begin with the same feature semantics used by Bliss where
they can be meaningfully computed on a short window. This keeps transition
distance interpretable relative to the existing system.

Not every baseline feature is necessarily valid on a 15-30 second excerpt.
Tempo, chroma, and dispersion estimates need short-window stability tests and
per-vector confidence or validity flags. An anchor distance should ignore or
downweight a component that could not be estimated reliably.

The current 13 chroma-derived Bliss features are intentionally transposition
invariant: their templates are evaluated over pitch rotations. They describe
harmonic or interval character, not absolute key. If overlapping transitions
should prefer harmonically compatible keys, the anchor representation needs an
additional key-sensitive pitch-class, key/mode, or tonal-centroid descriptor.
This is optional transition evidence, not a reason to make global similarity
key-locked. See the Bliss [chroma
implementation](https://docs.rs/bliss-audio/latest/src/bliss_audio/chroma.rs.html).

The physical storage format is not yet chosen. A single scalar `intro_timbre`
or `outro_timbre` is insufficient because Bliss timbre and chroma are
multi-dimensional. The working storage direction is one
compact numeric vector/BLOB per track, anchor kind, and representation schema,
with start/end times and confidence stored alongside it. JSON is suitable for a
small human-readable schema manifest, not for bulk floating-point values. Exact
encoding remains authoritative in the companion `bliss-rs` design.

The selected format must encode schema identity, dimension, ordering,
normalization, and confidence layout, and must reject incompatible vectors.

## Loudness and boundary shape

Useful boundary descriptors may include:

- short-term or momentary loudness near the boundary;
- peak or true-peak level;
- loudness slope over the anchor;
- fade-in, fade-out, cold-start, and cold-end confidence;
- amount of effective silence at the boundary.

Terminology must follow the implemented measurement. In particular, a value
over the final few seconds should not be called EBU R128 _integrated loudness_,
which describes a programme-level gated measurement.

## Structural variance

Structural variance may help detect tracks for which whole-track averages are
least representative. It should not be assumed to mean "progressive music" or
used as a genre classifier.

One scalar called structural variance is probably too broad. It can also be
confounded by track duration, arrangement, and mastering. Candidate independent
descriptors include:

- repetition ratio or dominant-section share;
- feature-space path length normalized by duration or window count;
- novelty magnitude and confident change-point rate;
- section-distribution entropy;
- tempo and harmonic stability;
- loudness dynamics and range.

The analysis prototype should compute a small number of simple candidate
definitions once window vectors and evaluation data exist. A hard gate based on
an uncalibrated scalar risks reducing variety and rejecting otherwise good
matches or transitions.

## Incremental identity and invalidation

Path alone is compatible with current integration but is not enough to detect a
replaced file. Each analysis record should include, where available:

- canonical track path matching `TracksV2.File` semantics;
- file size and modification time, or another inexpensive content identity;
- analyzer version;
- feature-schema version;
- window-policy version;
- analysis timestamp and failure status.

Renames and library rescans need an explicit cleanup strategy.
