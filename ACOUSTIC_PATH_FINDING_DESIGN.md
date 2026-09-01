# Acoustic path finding for Better Call Bliss

**Status:** Outer-planner-neutral anchored A-to-B kernel extracted for destination routes; playlist-planner convergence and the shared trajectory model remain partial  
**Scope:** Destination routes, gap repair, preserved-anchor insertion, fixed-set sequencing, and extension placement  
**Last reviewed:** 2026-09-01  

## Decision

Pairwise distance should remain a fast, cacheable building block, but one pairwise matrix must not define musical flow by itself. Better Call Bliss needs separate evidence for four questions:

1. **Collection relevance:** Does a candidate belong to the requested playlist, mood, or seed set?
2. **Contextual continuation:** Does it follow the recent route history coherently?
3. **Adjacent compatibility:** Do the two songs that actually touch in playback form an acceptable edge?
4. **Trajectory:** Does the complete route progress toward its destination or intended arc without wandering or saving one large cliff for the end?

A shared constrained sequence engine should retain these channels separately. Current Static, learned, and Adaptive whole-track evidence can support the first implementation. Depth-aware candidate discovery and a position-aware endpoint corridor can improve routes without a new Bliss database. Future intro/outro evidence should become an additional directional channel rather than require another route-contract rewrite.

## Evidence from Aretha Franklin to Rotor

Live job `preview-1787147358-0004` accepted Aretha Franklin - *I Get High* directly before Rotor - *Volllast*. With the learned matrix, the direct edge ranked around the 53rd percentile in contextual trigger evidence and around the 48th percentile in the fixed adjacent report, below the configured 70% target.

Removing only the learned-matrix artifact from the same request exercised the supported Static fallback. The direct edge ranked at 77.23%, triggered routing, and selected Anathema - *Lost Control*. That route's worst Static adjacent percentile was 61.60%. This proves that learned and Static evidence can disagree materially; it does not prove that this particular Static bridge is perceptually correct.

The shared core explains an important effective-setting detail. With two or more Adaptive context tracks, the configured percentage blends learned and variance matrices. With one seed, variance cannot be calculated, so a present learned matrix is used directly. Destination pairwise edges therefore are not a 20/80 learned/variance blend even when the captured preference says 20%. This inherited single-seed behavior must be reported truthfully.

The learned matrix is optional personal similarity evidence. It was not trained as a directional transition model and must not be the sole authority for audible boundaries.

### Implemented safeguard and live replay

Optimizer revision `baf626f` implements the first conservative slice. Adaptive destination requests with a learned matrix now measure the direct endpoint edge under both that matrix and the current Static BlissMixer weights. The view assigning the higher source-relative risk percentile governs candidate discovery, adjacent path scoring, and target acceptance. The result artifact preserves both direct verdicts and the selected role; Better Call Bliss exposes the comparison in Preview and its completed-job log. Static-only jobs and Adaptive jobs without a learned matrix continue to use Static weights alone.  

The exact Aretha/Rotor request was replayed on `192.168.1.111` with the ARM64 build from optimizer main. Static rated the direct jump at 73.75%, while the learned matrix rated it at 48.27%. Static therefore governed, the direct jump was no longer accepted, and the search inserted Jethro Tull - *Rare and Precious Chain*. Its measured worst Static adjacent percentile was 64.71%, below the configured 70% target. Native runtime was 1.432 seconds and external wall time 1.45 seconds on the current library. This verifies the regression mechanism and runtime budget; it does not by itself prove that the selected bridge is perceptually ideal.  

## Shared evidence contract

Every complete route should retain, where available:

- hard repeat and unique-membership constraint state;
- relevance of selected additions to the immutable source;
- per-edge Static and learned percentiles as separate values;
- per-position Adaptive continuation with the exact preceding context;
- route bottleneck and aggregate values per adjacent channel;
- endpoint-corridor or playlist-arc error;
- optional semantic evidence and provider state;
- future intro/outro boundary evidence; and
- deterministic tie-break and Variation provenance.

Use a visible lexicographic policy before attempting one unexplained weighted sum:

1. Reject hard-constraint violations.
2. Prefer routes satisfying the target in every required adjacent channel.
3. Minimize worst calibrated adjacent risk.
4. Minimize total calibrated adjacent risk.
5. Reduce trajectory or arc error where applicable.
6. Improve contextual continuation and collection relevance.
7. Use optional semantic evidence as bounded support.
8. Apply Variation only among complete routes inside a declared quality band.

Raw distances from Static, learned, contextual, semantic, and future boundary models must not be added directly because their scales and meanings differ.

## Depth-aware path engine

Destination and multi-track gap searches should stop reusing one frozen endpoint shortlist at every depth. At each layer, candidate discovery should union:

- nearest local tracks to the current frontier under Static and optional learned views;
- nearest tracks to the right endpoint;
- tracks near the expected position between the endpoints;
- candidates retained by a reverse endpoint frontier;
- cached Last.fm-supported endpoint candidates; and
- a small deterministic exploration reserve.

For a path with `N` intermediates, expected position `i` has progress `t = i / (N + 1)`. In matrix-transformed feature space, measure each candidate by progress along the endpoint axis and lateral deviation from it. Prefer monotonic progress and low lateral deviation, but keep actual adjacent quality primary. The corridor guides discovery; it does not claim that a straight line through 23 whole-track features is inherently musical.

A layered beam or bounded A* search can score the bounded union exactly. Full bidirectional merging is difficult when Adaptive history and repeat state make paths directional, so an initial forward beam can use reverse-neighbor candidates and a destination heuristic.

Automatic evaluates every permitted depth and selects the shortest route meeting its target. Exact count searches one depth with the same model. A best effort is acceptable only when UI and artifact label it explicitly.

## Applying it across features

| Feature | Shared-model use |
| --- | --- |
| **Bliss me there...** | Locked one-way endpoints or a three-anchor start/waypoint/rejoin excursion, conservative dual-metric baseline test, depth-aware frontier, corridor, and adjacent objective. Recent queue tracks remain contextual and repeat evidence but do not redefine the selected live start or rejoin boundary. |
| **Preserve order and improve difficult transitions** | Detect gaps with the same adjacent evidence, construct path options per gap, then allocate the global addition budget by marginal improvement instead of committing left to right. |
| **Preserve order while extending** | Keep fixed-source relevance selection, then jointly place all additions around immutable anchors. Replace one-addition-at-a-time greedy placement with a beam or dynamic program across slots. |
| **Reorder only** | Keep fixed membership and multi-start permutation search, but report and eventually optimize calibrated adjacent evidence alongside contextual continuation. Keep the energy arc secondary and explicit. |
| **Extend and optimize order** | Keep two stages: select relevant membership against the immutable source, then sequence that membership with the shared report. Do not silently sacrifice relevance to repair ordering. |

Collection relevance, route continuation, adjacent boundaries, and trajectory remain different decisions even when they share feature vectors and search utilities.

### Current split and desired convergence

The optimizer now has one pure anchored-path kernel for the bounded inner search from `A` to `B`. Its input separates the anchors, route prefix, immutable listening history, unavailable outer-plan membership, candidate evidence, repeat windows, search breadth, Variation, and adjacent-distance function. It returns complete scored alternatives without knowing whether a playlist or queue will eventually be changed. Existing destination and waypoint-and-rejoin paths use this kernel through compatibility adapters, so their request/result contracts remain unchanged.

Playlist gap filling still uses the preserved-order bridge machinery. It may examine many gaps in one playlist, such as `A -> B`, `B -> C`, and `C -> D`, then decide where additions are justified or how already selected additions can be placed around ordered anchors. That outer problem is different because the budget, repeat windows, and earlier insertions can interact across several gaps. It must migrate to the shared kernel through a global planner rather than call the kernel independently and commit each local winner.

The extracted inner engine answers: "given a left anchor A, a right anchor B, context, repeat policy, candidate inventory, and bridge budget, which complete A-to-B paths are valid and worthwhile?" It can retain multiple alternatives per intermediate count so a future multi-gap planner is not trapped by one locally optimal route. The outer planner remains feature-specific:

- **Bliss me there... one-way actions:** one gap, fixed queue-end or current-song start, fixed destination, and append or replace-upcoming output.
- **Bliss me there... and back again!:** two coupled gaps, fixed current-song start, mandatory selected waypoint, locked first-upcoming rejoin, and non-destructive insertion with one shared bridge budget.
- **Preserve order and improve difficult transitions:** many existing playlist gaps, global addition budget, insert only where a bridge improves the transition.
- **Fill every gap with N bridge tracks:** many gaps with a strict per-gap count; fail visibly if any required gap route cannot be built.
- **Preserve order while extending:** choose membership against the complete original source set, then place selected additions around immutable anchors.

This convergence would reduce duplicated bridge logic without pretending the listener-facing workflows are the same feature.

## Last.fm and future boundary evidence

Last.fm track and artist similarity provide optional semantic support, not acoustic transition quality. Endpoint evidence should be depth-aware: source support matters more near the source and destination support more near the destination. Querying every frontier online would be slow and fragile, so an intermediate semantic graph needs durable caching, strict request budgets, and top-frontier-only expansion. The optimizer remains network-free and must preserve Bliss-only operation.

The fundamental current limit is whole-track analysis. A future transition channel should compare `A.outro` with `B.intro`, with independently normalized loudness, energy shape, rhythm, timbre, and tonal evidence where confidence permits. Missing enhanced analysis must fall back to whole-track evidence rather than exclude tracks.

## Performance

Search must not scale as `library size x beam width x path depth`. For 200k-track libraries:

- cache transformed feature arrays and neighbor indexes by database identity, schema, and matrix or weight hash;
- perform only a small bounded number of whole-library scans;
- use approximate retrieval for a generous frontier followed by exact deterministic scoring;
- reuse per-anchor percentile distributions;
- parallelize independent scoring with deterministic collection order; and
- bind frontier and beam breadth to Fast, Balanced, and Thorough profiles.

Fast should continue to target roughly five seconds on the current Raspberry Pi test host without naming one hardware model in the UI.

## Migration gates

1. **Truthful diagnostics - partial:** Static and learned direct-edge evidence, selected role, matrix identities, and effective single-seed behavior are published. Exact Adaptive context reporting and separate direct-trigger sensitivity versus generated-route quality remain open.
2. **Conservative direct-edge experiment - implemented:** disagreement selects the higher-risk view and triggers repair when that view misses the target. Generic unit and end-to-end destination tests cover the policy; a sanitized corpus case should still be added without hard-coding one bridge as the expected answer.
3. **Depth-aware destination frontier:** add frontier, endpoint, corridor, and reverse-frontier retrieval; measure recall and latency at 64k and synthetic 200k sizes.
4. **Shared anchored-path and preserved-gap engine - partial:** the pure A-to-B kernel and destination compatibility adapter are implemented. Next make playlist gap planning request multiple alternatives, coordinate membership/repeat state globally, allocate budgets across gaps, and jointly place preserved-order extension additions.
5. **Shared fixed-set report:** expose adjacent, contextual, and arc evidence before changing reorder selection behavior.
6. **Boundary-aware late fusion:** add versioned intro/outro evidence and require held-out directional improvement before changing defaults.

## Immediate recommendation

Do not begin with new audio analysis. The pure anchored-path boundary is now available without changing destination behavior. Next migrate preserved playlist gaps behind a global outer planner and use the kernel's multiple alternatives to keep later gaps feasible under shared membership and repeat constraints. This is the prerequisite for strict **Fill every gap with N bridge tracks**.

In parallel, replace the one-shot destination shortlist with a depth-aware, corridor-guided frontier and evaluate its route choices through listening tests. Reordering should adopt the shared report before its objective changes so old and new behavior can be compared honestly.
