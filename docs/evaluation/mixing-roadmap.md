# Mixing delivery, risks, and open questions

**Status:** Living research and design proposal  
**Primary scope:** Phased downstream experimentation and rollout  
**Last reviewed:** 2026-07-14

## Delivery phases

These are downstream experimentation and integration phases, not lockstep
milestones for the companion `bliss-rs` roadmap. An application-level analyzer
may derive experimental summaries or anchors from a frame API before equivalent
stable library products exist; reusable extraction and final representation
contracts still follow the ownership boundary above.

### Phase 0: discovery

- inspect the exact `bliss.db` schema and lifecycle;
- document the current 23-feature extraction, ranges, normalization, and known
  behavior as the measurable baseline;
- align with the companion `bliss-rs` baseline/API discovery and representation
  schema work;
- verify short-excerpt validity for candidate features rather than assuming
  whole-track semantics transfer to bounded slices;
- identify orchestration and persistence extension points in `bliss-analyser`
  and loading/scoring extension points in `bliss-mixer`;
- define path normalization and cross-platform binary packaging constraints;
- confirm sidecar lifecycle, attachment, locking, and cleanup behavior.

### Phase 1: scoring and selection experiments with existing data

- add reproducible library-population statistics;
- test regularized population-aware Adaptive Weighting;
- compare centre, robust member-distance, and small clustered multi-seed
  profiles on compact and multimodal contexts;
- version and scale-normalize the existing learned-matrix artifact;
- establish learning curves for the current random survey and full matrix;
- prototype active triplet selection and progressive family/diagonal models;
- prototype MMR, cluster coverage, and relevance-aware submodular selection;
- establish separate relevance, diversity, and local-versus-global coherence
  measures;
- retain an exact baseline path and avoid schema changes where possible.

### Phase 2: analysis prototype

- consume an experimental structured `bliss-rs` frame API for a controlled
  library subset;
- store representation manifests, shaped frame series, hot summaries, and
  confidence in versioned sidecar metadata;
- derive initial structural summaries and intro/outro anchors;
- implement a small number of psychoacoustic or additional-feature hypotheses
  with precise definitions;
- create repeatable baseline, ablation, and listener-evaluation reports.

### Phase 3: enhanced global similarity experiments

- load enhanced metadata in `bliss-mixer`;
- compare late-fusion or reranking approaches with the existing Static, EIF, and
  Adaptive results;
- evaluate structural summaries and perceptual descriptors independently;
- preserve exact baseline and missing-data fallback paths;
- retain only feature families that demonstrate a measurable benefit.

### Phase 4: opt-in transition-aware scoring

- load anchor and boundary metadata in `bliss-mixer`;
- rerank a global candidate pool using normalized rank fusion;
- compare fixed and structure-aligned anchors plus whole-track and
  boundary-specific distances;
- add key-sensitive tonal evidence only if harmonic-transition evaluation
  justifies it, with confidence-aware fallback;
- preserve existing fallbacks and filters;
- add plugin configuration and diagnostics;
- run listener evaluation before selecting defaults.

### Phase 5: segmentation and structural modeling

- compare fixed-window summaries with content-aware segments;
- determine whether structural data improves global similarity, adaptive
  context, reranking, candidate-pool sizing, or confidence;
- avoid hard gating until listener results justify it.

### Phase 6: advanced psychoacoustic research and hardening

- evaluate masking, alternative scales, and learned perceptual representations
  against the retained Phase 3 baseline;
- adopt only improvements that survive blinded comparison and deployment-cost
  review;
- decide which proven scalar descriptors meet the companion document's
  promotion criteria for a possible `FeaturesVersion::Version3`; frames,
  structure, anchors, embeddings, and their cross-cutting metadata remain
  parallel products.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| More features make similarity worse or overfit one library | Require feature-family ablations and held-out listener judgments. |
| Seed agreement overweights an ordinary feature | Blend seed reliability with population distinctiveness, shrinkage, and a baseline prior. |
| One centroid erases a multimodal seed or context | Compare member-distance, robust-centre, and clustered representations; use dispersion to choose or fall back. |
| Group profiles leak artist/album identity instead of musical evidence | Report audio-only and profile-only ablations; regularize small groups. |
| Relevance optimization returns near duplicates | Apply and evaluate a separate diversity policy. |
| Objective diversity does not match perceived variety | Report listener ratings beside feature-space diversity and repetition metrics. |
| Personalization requires an exhausting survey | Use active queries, short resumable sessions, progressive model capacity, and a useful default prior. |
| A full learned matrix overfits sparse personal judgments | Compare family, diagonal, and low-rank models; increase capacity only with held-out evidence. |
| Random triplets are obvious but uninformative | Query plausible neighbors, model disagreements, and uncertain cases. |
| Weak playback feedback is mistaken for preference | Store provenance and context; evaluate signal types separately; use lower confidence, decay, and repeated evidence. |
| A skip caused by a section boundary is learned as dislike | Retain within-track time and queue context; do not convert isolated skips directly into preference triplets. |
| Learned and seed-derived matrices have incompatible scale | Normalize both against a declared convention before blending. |
| A learned matrix is applied to incompatible Bliss features | Embed feature and model schema versions and reject mismatches. |
| An external system appears better because it also uses lyrics, tags, metadata, clustering, or different playlist policy | Separate audio-only, hybrid, representation, retrieval, and full-system comparisons. |
| A broad toolkit or learned model becomes an accidental production dependency | Keep comparison backends separable; review licensing, model provenance, packaging, compute, and reproducibility before adoption. |
| Availability for Lyrion is mistaken for acceptable performance on every Raspberry Pi server | Benchmark representative Pi generations, RAM sizes, and storage classes during both analysis and playback. |
| Experimental features silently change baseline semantics | Store them separately and version every representation. |
| The enhanced analyzer duplicates or diverges from `bliss-rs` DSP | Consume structured `bliss-rs` products and isolate only explicitly experimental external algorithms. |
| Dense temporal data slows normal mixing | Separate hot runtime products from cold rebuildable frame sequences. |
| A future Version 3 silently invalidates matrices and consumers | Promote only proven scalars through coordinated feature-version migration; keep Version 2 available. |
| Segmentation adds complexity without useful signal | Compare with fixed-window and robust-statistics baselines first. |
| Locally smooth but globally inappropriate tracks | Global candidate generation remains the first-stage gate. |
| Raw scores from different algorithms are incomparable | Normalize within the candidate pool before fusion. |
| Enhanced metadata covers only part of the library | Candidate-level fallback and coverage diagnostics. |
| File paths become stale after library changes | Store source identity, version analysis, and implement cleanup. |
| Window, segment, and anchor vectors increase database and memory size | Prototype serialization choices and benchmark realistic libraries. |
| Unknown tables are lost during a Bliss database rebuild | Prefer a sidecar DB until lifecycle behavior is verified. |
| DSP complexity makes deployment fragile | Keep analysis offline and phase advanced psychoacoustics separately. |
| A smoothness objective reduces variety | Evaluate variety independently and cap transition influence. |
| Structural variance becomes a genre proxy | Treat it as confidence/context, not a genre label; avoid early hard gates. |
| Short anchors produce unstable tempo or tonal estimates | Store confidence/validity and downweight unreliable components. |
| Rank fusion makes a weak candidate pool look confident | Log pool quality and later compare calibrated score fusion. |
| A useful invariance for one task erases another task's signal | Define invariance contracts per descriptor and task. |
| Crossfade behavior differs by player | Optimize selection only; test with representative LMS playback setups. |

## Open questions

The following questions should drive the next design discussions. Detailed
`bliss-rs` API questions remain in the companion document rather than being
duplicated here.

1. What sidecar lifecycle, attachment, locking, cleanup, and retention policy
   works across supported LMS deployments?
2. Which specific shortcomings of the current 23 features can be demonstrated
   with reproducible examples or listener judgments?
3. Which mid-level feature family should be tested first: rhythm/onset behavior,
   repetition/structure, dynamics/energy, temporal harmony, or bass behavior?
4. Can existing Bliss feature extraction operate correctly on bounded slices,
   and which features remain stable on short windows?
5. Which dense frame products should be retained as cold rebuildable data, and
   which summaries, segments, or anchors must remain hot for runtime scoring?
6. How should structural variance be defined, normalized, and evaluated?
7. Does population-aware Adaptive Weighting improve the existing algorithm
   before any new DSP features are added?
8. Which diversity policy - MMR, cluster coverage, relevance-aware submodular
   selection, or a DPP-like method - gives useful exploration without
   sacrificing seed relevance?
9. Which group profiles and aggregation methods - robust centre, member-distance
   statistic, or clustered mixture - add value beyond leaking metadata identity?
10. How many actively selected judgments are needed for family, diagonal,
    low-rank, and full personal models to beat the default reliably?
11. Which LMS behaviors are sufficiently interpretable to use as weak feedback,
    and what privacy/retention policy should govern them?
12. How should personal-metric confidence control its effective blend without
    exposing unnecessary configuration?
13. Should experimental global similarity use vector expansion, a separate
   distance, late fusion, or learned weights?
14. What is the exact boundary track for every LMS request flow?
15. At what point in each current algorithm should the pre-rerank pool be
   captured, relative to hard and fallback filters?
16. Is percentile rank fusion sufficient, or does calibrated score normalization
   produce better results?
17. How should candidates without enhanced analysis be treated during partial
   rollout?
18. Do fixed or structure-aligned anchors work better, and which duration and
    silence policy produces the best listener ratings?
19. Does key-sensitive tonal compatibility improve real LMS transitions, and
    how should ambiguous key estimates be handled?
20. Which loudness and boundary-shape descriptors add value beyond anchor vectors?
21. Which repository should own and release the enhanced analyzer binary?
22. How should analysis be triggered after new tracks are added?
23. What minimum listener-study result would justify enabling any enhancement by
    default?
24. Which local-versus-global coherence measure predicts listener-rated flow
    without rewarding homogeneous or boring playlists?
25. Which reproducible audio-only AudioMuse-AI configuration should serve as an
    end-to-end baseline, and how should its retrieval and playlist policy be
    separated from representation quality?
26. Which Raspberry Pi configurations can run AudioMuse-AI analysis and
    clustering alongside Lyrion without unacceptable memory, storage, thermal,
    or playback impact, and how does that compare with the Bliss pipeline?
