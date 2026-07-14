# Bliss similarity and analysis design

**Status:** Living research and design proposal  
**Last reviewed:** 2026-07-14

This site develops a research-backed path for improving how Bliss represents,
compares, and selects music. Its primary goal is better mixing quality through
better similarity criteria. Transition-aware selection is one important use
case, but the scope also includes psychoacoustics, temporal structure,
segmentation, structural variance, contextual similarity, diversity, and
personalization.

The proposal is deliberately split into reusable analysis and downstream
mixing responsibilities. It does not present experimental ideas as accepted
`bliss-rs` direction or require one player ecosystem.

```mermaid
flowchart LR
    R[Research evidence] --> A[Player-neutral analysis products]
    A --> G[Global similarity]
    A --> C[Context and diversity]
    A --> T[Transition compatibility]
    G --> S[Candidate selection]
    C --> S
    T --> S
    P[Optional personalization] --> S
    S --> E[Evaluation and rollout]
```

## How to read this site

| Area | Question answered | Start here |
|---|---|---|
| Foundations | What exists today, and where are the system boundaries? | [Current system and ecosystem](foundations/current-system.md) |
| Research | What evidence supports or challenges the proposal? | [Analysis research](research/analysis-research.md) and [mixing research](research/mixing-research.md) |
| Analysis | What reusable evidence could `bliss-rs` expose? | [Analysis evolution](analysis/overview.md) |
| Mixing | How could consumers turn that evidence into better sequences? | [Mixing architecture](mixing/overview.md) |
| Integration | Who stores and consumes each product? | [Downstream consumers](integration/downstream-consumers.md) |
| Evaluation | How will the hypotheses be tested and delivered safely? | [Analysis evaluation](evaluation/analysis-evaluation.md) and [mixing evaluation](evaluation/mixing-evaluation.md) |

## Responsibility boundary

The analysis section is the source of truth for proposed descriptor contracts,
temporal representations, API products, feature versioning, serialization, and
resource costs. The mixing section is the source of truth for cross-repository
feature goals, candidate selection, context, diversity, personalization,
transition scoring, UX, and downstream rollout.

Reusable measurement belongs in `bliss-rs`; persistence, library lifecycle,
candidate retrieval, sequencing, and user feedback remain consumer concerns.

## Evidence and proposal status

The pages distinguish among:

- the **stable baseline**, describing behavior that exists today;
- **experimental evidence**, describing prototypes or comparison systems;
- a **working proposal**, which still requires design review and validation;
- an **open question**, for which the evidence or ownership is unresolved.

No candidate descriptor or metric is assumed to improve perceived similarity.
Promotion into a stable representation requires reproducible extraction,
measurable downstream benefit, acceptable resource cost, and listener-facing
evaluation.

## Project context

- [`Polochon-street/bliss-rs`](https://github.com/Polochon-street/bliss-rs) is the upstream, player-neutral analysis library.
- [`Polochon-street/blissify-rs`](https://github.com/Polochon-street/blissify-rs) represents the MPD ecosystem.
- [`CDrummond/bliss-mixer`](https://github.com/CDrummond/bliss-mixer) provides the upstream HTTP mixing service.
- [`chrober/bliss-mixer`](https://github.com/chrober/bliss-mixer) adds variance-based weighting and learned-matrix support.
- [`chrober/lms-blissmixer`](https://github.com/chrober/lms-blissmixer) integrates the mixer with Lyrion Music Server and hosts current user-facing experiments.
