# Analysis evolution: research scope and principles

**Status:** Living research and design proposal  
**Primary scope:** Potential extensions to the current Bliss representation
**Last reviewed:** 2026-08-01

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

## The Bohemian Rhapsody Problem

This design uses the term **Bohemian Rhapsody Problem** as informal shorthand for the
failure of one whole-track representation to describe a composition containing
several strongly contrasting sections. The name uses Queen's *Bohemian
Rhapsody* as a familiar example, but the problem applies to any track whose
internal states, order, or boundary character matter more than their aggregate.
It is a term introduced by this design, not established MIR terminology.

A mean may fall between the song's actual sections and resemble none of them.
Dispersion can indicate that the song varies, but it still cannot say which
musical states occurred, in what order, for how long, or which state is present
at an intro or outro. Consequently, whole-track nearest neighbours may match a
synthetic centre, and a transition score may compare evidence from sections
that never touch during playback.

The term names the representation failure, not one prescribed solution.
Temporal frames, multi-scale summaries, segmentation, structural descriptors,
and boundary anchors preserve different parts of the missing evidence and must
be evaluated separately. Adding more whole-track scalars may help detect the
problem, but cannot in general reconstruct the discarded sequence.

## Goals

- Use the current Version 2 representation as a documented comparison baseline.
- Analyze musical properties that the compact whole-track vector may miss.
- Compare compact global descriptors with temporal, structural, local, and
  learned representations.
- Treat validity, confidence, provenance, normalization, and invariance as part
  of every experimental result.
- Quantify analysis, storage, and runtime costs alongside quality.
- Define evidence that would support retaining, revising, or rejecting a
  candidate representation.
- Keep player-neutral findings distinct from application-specific retrieval,
  diversity, personalization, and sequencing policy.
- Leave implementation ownership and upstream integration decisions open.

## Non-goals

- Proposing changes to `bliss-rs` public APIs, internal modules, crate layout,
  feature versions, or release plan.
- Selecting a final production descriptor set before evaluation.
- Replacing Version 2 or changing its documented semantics.
- Prescribing an upstream extraction pipeline, serialization format, database
  schema, or ownership boundary.
- Assigning any future implementation to `bliss-rs`, a companion library, or a
  particular application.
- Reproducing undocumented MusicIP internals.
- Requiring a neural model or network service for the research direction.
- Treating instrument, genre, mood, or key predictions as certain labels.

## Design principles

1. **Preserve a known comparison.** Every experiment should remain measurable
   against Version 2.
2. **Compare several views.** Global summaries, frames, structure, anchors, and
   embeddings answer different questions.
3. **Do not flatten too early.** Retain temporal evidence in experiments until the target
   representation is known.
4. **Keep intrinsic evidence separate from model-relative outputs.** Audio
   measurements belong in analysis; distances to a learned population or user
   model do not.
5. **Make uncertainty explicit.** An ambiguous key or unstable tempo is not a
   precise scalar merely because its storage type is
   [`f32`](https://doc.rust-lang.org/std/primitive.f32.html).
6. **Define invariance per descriptor and task.** Gain, trim, absolute key, and
   boundary silence can be nuisances in one use case and signals in another.
7. **Identify every experiment.** Results are comparable only when feature
   definitions, preprocessing, model artifacts, and pooling are recorded.
8. **Report the cost of evidence.** Segmentation, dense frames, and learned
   models must justify their compute and storage burden.
9. **Retain only demonstrated value.** A plausible MIR descriptor remains a
   hypothesis until it improves defined outcomes.

## Conceptual separation, not ownership

The research separates concerns because they require different evidence, not to
assign them to repositories or code modules:

| Concern | Question considered here |
|---|---|
| Audio evidence | Which measurements are reliable, perceptually meaningful, and reproducible? |
| Representation | Which global, temporal, structural, or local view suits the task? |
| Experimental identity | Which definitions, parameters, confidence semantics, and model provenance make results comparable? |
| Persistence and lifecycle | What resource and reproducibility costs would a real experiment incur? |
| Similarity and retrieval | Which distance or scoring view improves a named outcome? |
| Diversity and sequencing | How should relevant tracks be selected and ordered for a specific task? |
| Personalization | Which consented evidence improves an individual listener's results? |

The current ecosystem demonstrates several possible separations of these
concerns. The documentation does not prescribe where a future implementation
should place them.
