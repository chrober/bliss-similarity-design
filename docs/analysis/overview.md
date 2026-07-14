# Analysis evolution: scope and principles

**Status:** Living research and design proposal  
**Primary scope:** Reusable, player-neutral bliss-rs analysis  
**Last reviewed:** 2026-07-14

## Problem statement

The current vector describes aggregate acoustic character more effectively than
musical organization. In particular, it only partially or indirectly represents:

- perceived energy and dynamic trajectory;
- rhythm beyond one tempo value;
- tempo confidence and stability;
- repeated sections and structural development;
- bass-specific energy, pitch, and rhythm;
- tonal movement and harmonic rhythm;
- absolute key where a task requires it;
- instrumentation or source character;
- intro and outro behavior.

Two tracks can have similar means, dispersions, tempo, and aggregate harmonic
character while differing strongly in groove, arrangement, progression, and
boundary shape. No alternative Euclidean or Mahalanobis matrix can reconstruct
those missing dimensions after aggregation.

## Goals

- Preserve the existing Version 2 [`Analysis`](https://github.com/Polochon-street/bliss-rs/blob/master/src/song/mod.rs#L240) as a stable
  baseline.
- Expose reusable temporal measurements without forcing consumers to duplicate
  the analysis pipeline.
- Distinguish compact global descriptors from variable-length representations.
- Make feature validity and confidence first-class data.
- Define explicit schema identity, units, normalization, and invariance.
- Permit consumers to request only the analysis products they need.
- Keep decoding and shared DSP implementation independent of LMS or a specific
  database.
- Enable deterministic serialization by downstream analyzers.
- Establish an evidence-based route for promoting proven scalars into a future
  canonical feature version.
- Keep runtime playlist scoring possible without audio-analysis dependencies.

## Non-goals

- Selecting the final production descriptor set before evaluation.
- Replacing Version 2 or silently changing its semantics.
- Making every intermediate DSP value public API.
- Making `bliss-rs` own an LMS-specific SQLite schema.
- Defining relevance, diversity, transition fusion, or playlist sequencing
  policy inside the audio analyzer.
- Reproducing undocumented MusicIP internals.
- Requiring a neural model or network service for the initial design.
- Treating instrument, genre, mood, or key predictions as certain labels.

## Design principles

1. **Preserve the compatible baseline.** New analysis must be comparable with
   and optional beside Version 2.
2. **Measure once, derive several views.** Shared intermediate computation
   should support global summaries, frames, structure, and anchors.
3. **Do not flatten too early.** Preserve temporal evidence until the target
   representation is known.
4. **Keep intrinsic evidence separate from model-relative outputs.** Audio
   measurements belong in analysis; distances to a learned population or user
   model do not.
5. **Make uncertainty explicit.** An ambiguous key or unstable tempo is not a
   precise scalar merely because its storage type is
   [`f32`](https://doc.rust-lang.org/std/primitive.f32.html).
6. **Define invariance per descriptor and task.** Gain, trim, absolute key, and
   boundary silence can be nuisances in one use case and signals in another.
7. **Version representations, not just binaries.** A consumer must detect
   incompatible features even if analyzer versions happen to match.
8. **Pay for requested products.** Consumers that need only Version 2 should
   not automatically incur segmentation or dense-frame cost.
9. **Promote only demonstrated value.** A plausible MIR descriptor is not a
   canonical Bliss feature until it improves defined outcomes.

## Responsibility boundary

| Concern | Preferred owner |
|---|---|
| Decode and resample audio | Decoder implementation used by `bliss-rs` |
| Spectral, loudness, onset, beat, chroma, and bass measurements | `bliss-rs` |
| Reusable frame and confidence representation | `bliss-rs` |
| General-purpose novelty, repetition, and segmentation primitives | `bliss-rs` or an optional companion module |
| Track identity, incremental scheduling, and persistence | Library application/analyzer, such as `blissify-rs` or `bliss-analyser` |
| SQLite layout and migration policy | Database-owning analyzer/application |
| Population and group profiles | Mixer/application analysis layer |
| Learned personal metric | Downstream learner and metric consumer |
| Candidate retrieval and relevance | Playlist consumer/mixer |
| Diversity and exploration | Playlist consumer/application |
| Transition and playlist sequencing policy | Playlist consumer/application |
| User feedback and privacy policy | Player/application integration |

`bliss-rs` may provide generic distance and playlist utilities, as it does now,
without making player-specific policy part of the analysis contract.
