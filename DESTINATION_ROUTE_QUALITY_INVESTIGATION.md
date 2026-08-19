# Destination-route quality investigation

**Date:** 2026-08-11  
**System:** Lyrion at `192.168.1.111`, Better Call Bliss `0.15.4`, bliss-playlist-optimizer `0.1.4`  
**Status:** Gate 1 diagnostics/constraints and the bounded Gate 2 adjacent path search are implemented; live Pi quality and latency validation remains.  

## Implementation checkpoint: 2026-08-19

The first corrective slice is now implemented in the optimizer workspace:  

- destination results publish a `route_quality` object containing every actual adjacent edge, its fixed-matrix distance, a source-relative percentile calibrated against the same matrix and LMS-local library, the matrix role and hash, route sum, bottleneck, and worst percentile;  
- Automatic `quality_target_met`, `achieved_max_leg_percentile`, and `best_effort` now reflect that adjacent metric instead of the legacy rolling-context insertion values;  
- Static `score` legs report `static-weights` rather than `learned-matrix`; and  
- repeat validation checks each generated track against all tracks in its configured artist and album windows, including the explicit destination, while tolerating conflicts that already exist solely among immutable queue-context tracks.  

Gate 2 now replaces generic destination gap insertion with a fixed-matrix layered beam. It evaluates complete routes by adjacent bottleneck and sum, searches every permitted count when necessary, applies Variation only inside a complete-route quality band, checks generated tracks against the destination, and measures only the requested tail-to-destination suffix. A transformed-feature index reuses matrix work, while `search_effort=fast|balanced|thorough` exposes bounded speed/quality profiles; Fast is the deliberately bounded plugin default and older requests remain Balanced. Automatic routing now also accepts a validated minimum and maximum intermediate count.  

Candidate discovery still freezes one shortlist from the original endpoint gap. Split direct-trigger/route-target controls, depth-aware candidate expansion, semantic evidence between intermediates, richer acoustic evidence, and live listening/latency validation remain open.  

### Live false positive: Aretha Franklin to Rotor

Job `preview-1787147358-0004`, produced by optimizer 0.1.5, transitioned from Aretha Franklin - *I Get High* to Rotor - *Volllast*. Automatic inserted no bridge because the contextual direct percentile was 53.47% and the fixed learned-matrix adjacent percentile was 48.27%, both below the configured 70% target. The listener nevertheless experienced a tough break. The artifact also contained 126 acoustically accepted, repeat-safe bridge candidates; several one-track candidate diagnostics had legs around the 28th-35th percentiles, although the dedicated fixed-route search was skipped once the direct edge qualified.  

This is a genuine perceptual false positive for the present evidence, not proof that the listener is wrong. A library-relative percentile says only how the current 23-feature matrix ranks the pair; it is not a guarantee of compatible genre, instrumentation, intensity, arrangement, or actual outro-to-intro continuity. A positive Automatic minimum gives users a practical override, but it does not fix the evidence model. This case belongs in the future listening corpus for composite learned/Static evidence, segment-aware features, richer descriptors, and explicit user feedback.  
## Executive finding

The four inspected **Bliss me there...** previews are valid according to the current optimizer contract, but that contract is not yet a reliable model of a fluent audible journey from Nina Simone to Immortal. The weakness is not explained by one bad default. Several effects reinforce each other:  

1. Adaptive bridge diagnostics describe a candidate or destination relative to a rolling mean of preceding tracks, not necessarily the adjacent transition a listener hears.  
2. Automatic mode stops at the shortest route meeting the configured percentile target. A false feature-space midpoint can therefore make one bridge appear sufficient even for an extreme transition.  
3. Exact multi-hop search freezes one 256-track shortlist for the original endpoint gap. It does not discover a new local neighborhood at each step.  
4. A left-reachable expansion is still ranked primarily by its two-sided midpoint score, so the first bridge tends to be a compromise between both endpoints instead of a gentle first step away from the source.  
5. Last.fm evidence is collected only for the fixed source and destination. It can recognize Nina-like and Immortal-like candidates, but it supplies no semantic evidence for the links between intermediate tracks.  
6. Variation is applied while expanding candidates. At 25%, it shuffles the best 14 accepted candidates and retains only eight for a state, so it can remove better branches before complete routes are compared.  
7. The current 23 whole-track features, whether scored through the learned matrix or Static weights, can contain mathematical midpoints that are not convincing perceptual transitions.  
8. The destination's artist and album repeat keys are cleared to honor explicit user intent. This also prevents generated candidates from being checked against the destination and can violate the configured repeat windows.  
9. A two-track destination job builds one percentile reference from start-track-to-library distances, then reuses it for later distances produced by different contexts and sometimes different Adaptive matrices. Those later percentiles are not calibrated to what they claim to measure.  

The repair should therefore be a dedicated fixed-destination path search with explicit adjacent-edge evidence, not another threshold adjustment around the current generic gap-insertion search.  

## Live previews inspected

All four requests used Adaptive scoring, a three-track context, learned blend 20%, Variation 25%, Last.fm track and artist guidance 25%, artist/album/track windows 5/10/100, a 256-track shortlist, and 50 route-search restarts. The direct Nina Simone to Immortal transitions were all around the 99.9th percentile.  

| Job | Policy | Destination | Generated route |
| --- | --- | --- | --- |
| `preview-1786461653-0001` | Automatic, maximum 4, target 70% | Immortal - *Grim and Frostbitten Kingdoms* | Nina Simone - *My Baby Just Cares for Me* -> Stevie Ray Vaughan and Double Trouble - *Hug You, Squeeze You* -> Immortal |
| `preview-1786461772-0002` | Exactly 4 | Immortal - *Battles in the North* | Nina Simone -> Aretha Franklin - *Dr. Feelgood* -> Tarot - *Guardian Angel* -> Janis Joplin - *Half Moon* -> Jim Morrison / The Doors - *Roadhouse Blues* -> Immortal |
| `preview-1786461862-0003` | Exactly 4 | Immortal - *Grim and Frostbitten Kingdoms* | Nina Simone -> Aretha Franklin - *Dr. Feelgood* -> Janis Joplin - *Half Moon* -> Tarot - *Guardian Angel* -> Jim Morrison / The Doors - *Roadhouse Blues* -> Immortal |
| `preview-1786461884-0004` | Exactly 4 | Immortal - *Through the Halls of Eternity* | Nina Simone -> Aretha Franklin - *You're a Sweet Sweet Man* -> Dizzy Gillespie - *The Bluest Blues* -> `[dialogue] / Chuck Berry` - *Jack Rabbit Slims Twist Contest / You Never Can Tell* -> Hawkwind - *Sonic Attack* -> Immortal |

The automatic job reported a successful 37.8% worst leg and selected a Bliss-only bridge with no Last.fm evidence. That figure is misleading as an adjacent-transition claim: the Immortal destination was evaluated against the mean context `[Nina Simone, Stevie Ray Vaughan]`, not against Stevie Ray Vaughan alone.  

The exact-four artifacts do not publish `quality_target_met`, `achieved_max_leg_percentile`, or a final adjacent-route objective. Their per-candidate values are contextual removal/reinsertion evaluations. Later values collapse as low as 0.006%, which is not credible evidence that the neighboring songs are virtually identical.  

### Fixed-route pairwise rescoring

The four original routes were rescored unchanged with `seed_limit = 1`; the optimizer was not allowed to replace or reorder any track. This reveals the adjacent distances hidden by the original rolling-context artifacts:  

| Job | Learned-matrix adjacent distances, in route order | Worst learned edge | Static adjacent distances, in route order | Worst Static edge |
| --- | --- | ---: | --- | ---: |
| `preview-1786461653-0001` | `2.728, 4.708` | `4.708` | `1.433, 1.099` | `1.433` |
| `preview-1786461772-0002` | `2.641, 0.117, 0.171, 0.040, 4.736` | `4.736` | `0.609, 0.924, 1.422, 0.255, 1.100` | `1.422` |
| `preview-1786461862-0003` | `2.641, 0.129, 0.171, 0.133, 4.720` | `4.720` | `0.609, 0.575, 1.422, 1.308, 1.148` | `1.422` |
| `preview-1786461884-0004` | `2.717, 0.095, 0.335, 0.225, 4.722` | `4.722` | `0.924, 3.242, 0.750, 1.573, 1.225` | `3.242` |

Raw distances are comparable only inside one scoring strategy; each strategy has its own matrix and reference distribution. The direct Nina Simone -> *Grim and Frostbitten Kingdoms* baselines are `7.424` with the learned matrix and `1.800` with Static weights. The learned-matrix pattern is unambiguous: the original one-bridge route still has a `4.708` bottleneck, while all three exact-four routes retain a `4.720-4.736` bottleneck. Forcing four bridges therefore did not improve the learned bottleneck beyond the one-bridge result; it added an extremely tight middle cluster before essentially the same final cliff into Immortal instead of distributing the change progressively across five transitions.  

The automatic route is equally revealing. Its original artifact reported left and right contextual distances near `2.73`, but unchanged pairwise rescoring gives Nina Simone -> Stevie Ray Vaughan `2.728` and Stevie Ray Vaughan -> Immortal `4.708`. The apparent balanced midpoint was created by scoring Immortal against the mean of Nina Simone and Stevie Ray Vaughan.  
Each final edge was then calibrated correctly against distances from that same last bridge to the complete local candidate library:  

| Job | Final adjacent edge | Learned percentile | Static percentile |
| --- | --- | ---: | ---: |
| `preview-1786461653-0001` | Stevie Ray Vaughan -> *Grim and Frostbitten Kingdoms* | `98.71%` | `52.96%` |
| `preview-1786461772-0002` | Jim Morrison / The Doors -> *Battles in the North* | `98.86%` | `69.29%` |
| `preview-1786461862-0003` | Jim Morrison / The Doors -> *Grim and Frostbitten Kingdoms* | `98.84%` | `71.75%` |
| `preview-1786461884-0004` | Hawkwind -> *Through the Halls of Eternity* | `98.75%` | `72.30%` |

Each reference contained about `64,127` distances produced from the exact same left track and matrix as its observed edge. The direct Nina Simone -> Immortal transitions were about the `99.9th` learned percentile. The learned scorer therefore agrees with the listening impression: every generated route left a final transition almost as extreme as the original problem, although the original contextual artifacts presented much lower values and Automatic declared its target met.  

The Static control for the fourth route exposes a different hidden discontinuity: Aretha Franklin -> Dizzy Gillespie has distance `3.242`, much larger than its other Static edges. Different matrices disagree about which transition is bad, reinforcing the need to publish component evidence and evaluate route quality explicitly rather than treating one contextual score as truth.  

The `score` artifact also mislabels every Static leg as `learned-matrix`. `algorithm_requested` is correctly `static`, and the distances come from the captured Static-weight matrix, but the per-leg algorithm label is inherited from the generic adaptive scorer. This is a diagnostics defect and should be covered alongside the destination artifact changes.  

## Controlled replays

The original requests and results remain below `/usr/local/slimserver/Cache/bettercallbliss/jobs/<job-id>/` on the Pi. Diagnostic requests and results were written only to `/tmp/bcb-*` and may disappear on reboot. No playlist, queue, or LMS service was changed by these replays.  

### One-track context, original Variation

Setting `seed_limit = 1` makes every reported leg pairwise under the learned matrix. It removes rolling-mean leakage but does not by itself make the routes good:  

- Automatic selected Mithotyn - *Stories Carved in Stone* as the sole bridge. Both legs were reported near 58%, yet Nina Simone -> Mithotyn is not a gentle transition.  
- Exact four to *Battles in the North* produced Nina Simone -> Lenny Kravitz -> Aretha Franklin -> Emperor -> Darkthrone -> Immortal.  
- Exact four to *Grim and Frostbitten Kingdoms* produced Nina Simone -> Mithotyn -> Dio -> Tom Petty -> Darkthrone -> Immortal, moving into metal, back toward rock, then into black metal again.  
- Exact four to *Through the Halls of Eternity* included a 36-second Ten Years After radio advert and a track whose Bliss metadata is completely blank.  

This proves that rolling context is one defect, but not the only defect.  

### One-track context, Variation zero

Removing Variation made the routes more deterministic and usually more semantically coherent:  

- to *Battles in the North*: Nina Simone -> Siena Root -> Emperor -> Gorgoroth -> Enslaved -> Immortal;  
- to *Grim and Frostbitten Kingdoms*: Nina Simone -> Santana -> Aretha Franklin -> Emperor -> Enslaved -> Immortal; and  
- to *Through the Halls of Eternity*: Nina Simone -> Aretha Franklin -> Satyricon -> Darkthrone -> Immortal - *At the Stormy Gates of Mist* -> Immortal.  

The last route violates the artist look-back window: the generated Immortal track is only two positions before the explicit Immortal destination while the artist window is five. Both database artist strings are exactly `Immortal`.  

The reason is visible in `main.rs`: destination routes clear the destination's artist and album keys. This is intended to allow the user's explicit destination even if the same artist occurs in recent queue history, but it also exempts generated candidates from comparison with the destination. The exemption must become role-aware: an explicit destination may conflict with pre-existing queue history, while a generated bridge must still be checked against the destination and other generated tracks.  

### Static weights, one-track context, Variation zero

Static controls used the captured BlissMixer weights rather than the learned matrix. Percentiles cannot be numerically compared across the two matrices because each run rebuilds its reference distribution, but track choices can be inspected:  

- Automatic still stopped after one bridge, Bélmez - *Und süß setzt ein das Leiden...*, which is an immediate move from Nina Simone into metal rather than a gradual path.  
- Exact four to *Battles in the North* produced Nina Simone -> Aretha Franklin -> Soundgarden -> Blackberry Smoke -> Dropkick Murphys -> Immortal.  
- Exact four to *Grim and Frostbitten Kingdoms* produced Nina Simone -> Janis Joplin -> Dropkick Murphys -> The Sweet -> Satyricon -> Immortal.  
- Exact four to *Through the Halls of Eternity* produced Nina Simone -> The White Stripes -> Satyricon -> Immortal -> Enslaved -> Immortal and repeated the same destination-identity constraint violation.  

Static weights sometimes gave a more intuitive broad genre progression, but they did not solve shortest-route stopping, non-monotonic detours, feature-space false midpoints, or repeat enforcement. Switching the default strategy is therefore not a sufficient repair.  

## Root causes in the current implementation

### Contextual scores are presented as route legs

`bridge::contextual_distance` scores the next track against the mean of up to `seed_limit` preceding tracks. `evaluate_candidate` therefore computes the right side after adding the candidate to the context. This matches next-song Adaptive mixing behavior, but it is not equivalent to the audible adjacent edge required by a progressive destination route.  

Destination artifacts need to expose at least two explicitly named views:  

- **adjacent transition evidence**, computed from the actual neighboring pair under a declared pairwise metric; and  
- **rolling-context evidence**, retained as secondary information when Adaptive is selected.  

Neither value should be labelled generically as a leg without identifying its context.  

### The frozen percentile reference does not follow the scoring context

For a two-track destination request, the initial reference contains one source observation and triggers the library fallback. `build_frozen_reference` then scores every local candidate from the original start-track context. In the investigated jobs, all `64,127` reference distances are therefore Nina-Simone-to-library distances under the one-seed learned matrix.  

The same sorted distribution is subsequently used to percentile-rank:  

- the first bridge from Nina Simone, for which it is appropriately calibrated;  
- the destination from `[Nina Simone, first bridge]`;  
- later bridges and destinations from other rolling means; and  
- with multi-track Adaptive context, distances produced by variance/learned blended matrices that can differ at every depth.  

Those quantities do not share one distribution. The original automatic result's similar `37.8%` left and `37.5%` right values therefore do not demonstrate two equally smooth adjacent legs. The correctly calibrated Stevie Ray Vaughan -> Immortal edge is at the `98.71st` learned percentile. The reported right value merely ranked an unrelated rolling-context distance inside the Nina-to-library distribution. This also explains why later exact-route contextual percentiles can collapse toward zero.  

The destination search needs a declared calibration model. A practical primary adjacent-edge measure is a source-relative neighbor percentile: rank `distance(A, B)` among `distance(A, C)` for eligible local `C`, using the same fixed pairwise matrix for both the observed edge and its reference distribution. Cache this distribution for each retained frontier track. If rolling Adaptive context remains as secondary evidence, its percentile must be calibrated against candidates scored from that exact same context and effective matrix; otherwise publish only a clearly labelled raw contextual score.  
### The multi-hop search begins with a midpoint

The current exact search inserts every new candidate immediately before the original right endpoint. `ReachableFromLeft` checks only the left percentile for acceptance, but `rank_for_evolving_route` still sorts accepted candidates by adjusted `max_percentile` and detour, both of which include the right endpoint. The first retained candidates are therefore endpoint compromises. Subsequent tracks refine only the remaining right side; the search cannot reconsider the initial large step.  

### One frozen shortlist represents every depth

The optimizer reserves at most 32 endpoint-semantic candidates and fills the remainder of a 256-track shortlist with candidates ranked against the original two-sided gap. The exact beam width is 64 and each expansion retains at most eight candidates, but all depths draw from the same frozen 256 tracks. A useful song close to the current frontier but not close to the original endpoint midpoint is invisible.  

### Last.fm has no intermediate graph

Each job made four LastMix calls: similar tracks for both endpoints and similar artists for both endpoint artists. The evidence artifact contained 25 recording edges for each endpoint and 50 artist edges for each endpoint artist. No calls or edges were created for selected or prospective intermediate tracks.  

Consequently, endpoint-local evidence can favor Aretha Franklin near Nina Simone and Emperor, Enslaved, Darkthrone, or Satyricon near Immortal. It cannot say whether Aretha -> Santana, Santana -> Emperor, Emperor -> Enslaved, or another middle edge is semantically plausible. Increasing the current Last.fm percentages cannot create evidence that was never collected.  

At the configured 25% similar-track and 25% similar-artist guidance, `adjusted_percentile` can improve a candidate by at most five percentile points when both evidence kinds have maximum support; a candidate supported by only one kind normally gains at most 2.5 points. Thirty-two semantic candidates are reserved in the 256-track shortlist, but final ranking remains predominantly acoustic. The poor automatic Stevie Ray Vaughan bridge was `bliss_only`, so Last.fm did not select it. The defect is missing path evidence, not excessive Last.fm weight.  

### Variation removes branches too early

For exact selection, the minimum variation pool is `candidate_limit + 1`, currently nine. With 25% Variation and up to 32 accepted candidates, the best 14 are shuffled before only eight are expanded. Variation therefore changes reachability and can discard higher-quality paths. It should operate over complete routes inside a bounded quality band, not alter the candidate graph before route quality is known.  

### One percentile performs two different jobs

`extension.trigger_percentile` becomes `BridgeConfig.max_leg_percentile` for a destination route. A value of 70% therefore means both "intervene when the direct transition is worse than the 70th percentile" and "accept a generated leg as long as it is no worse than the 70th percentile." The first is a sensitivity control; the second is a route-quality target. They should not be the same setting.  

For these jobs the direct edge was around 99.9%, so intervention was appropriate. But a one-track mathematical midpoint at 38% or 58% easily passed the permissive 70% leg gate, causing Automatic to stop immediately. Split the contract into a direct-transition trigger, a desired adjacent-leg target, and a minimum material-improvement or knee-point rule. Exact mode also needs quality wording rather than calling its leg gate a trigger.  
### Whole-track features permit false midpoints

The current 23 normalized whole-track features capture tempo, zero-crossing rate, spectral summaries, loudness, and chroma. They do not directly encode genre, instrumentation, vocal style, distortion, rhythmic density, arrangement, or the ending and opening segments that form the audible transition. A linear Mahalanobis midpoint can therefore be close to both endpoints without sounding like a bridge. This is expected evidence for the broader richer-acoustic-evidence roadmap, but Better Call Bliss still needs robust routing behavior with the present representation.  

## Why the existing tests passed

The current tests establish useful structural behavior but do not exercise this quality contract:  

- `automatic_destination_route_accepts_a_qualified_direct_transition` uses a 100% threshold and checks only that a direct route can be returned.  
- `two_track_destination_uses_library_reference_for_automatic_trigger` verifies that the frozen reference has more than one observation and that the internally reported contextual percentile is below the same configured threshold. It does not independently evaluate adjacent edges.  
- the exact multi-hop unit test uses a tiny linear synthetic set where `[0, 1, 2, 3]` is the obvious route. It cannot reveal a frozen midpoint shortlist or false midpoints in a 64k-track real library.  
- no destination test places a generated candidate with the same artist or album as the explicit destination; and  
- no test compares complete-route quality before and after Variation, missing metadata, or endpoint-only semantic evidence.  

The release gates operated correctly against their current assertions. The missing work is stronger behavioral specification and fixtures, not merely running the same test suite more often.  
## Recommended repair sequence

### Gate 1: Regression and truthful artifacts

1. **Pending:** add a sanitized fixture derived from these feature vectors and identities without publishing private paths or the full library database.  
2. **Partial:** adjacent distances, source-relative percentiles, reference identity, and strategy/matrix identity are published and use a matching metric/reference. Per-edge semantic evidence remains to be added.  
3. **Pending:** add separate, explicitly labelled rolling-context metrics when Adaptive is active.  
4. **Partial:** final adjacent bottleneck, sum, target outcome, and best-effort state are published for feasible Automatic and Exact routes. An explicit route-length field and split trigger/target controls remain.  
5. **Implemented:** `destination_candidate_cannot_use_explicit_destination_repeat_exemption` covers generated artist and album conflicts with the destination while allowing conflicts solely among immutable endpoints.  
6. **Pending:** add tests proving that Variation cannot move a result outside the accepted complete-route quality band.  

Suggested regression names:  

- `destination_route_reports_adjacent_and_contextual_metrics_separately`;  
- `destination_leg_percentiles_use_matching_context_reference`;  
- `destination_candidate_cannot_use_explicit_destination_repeat_exemption`;  
- `multi_hop_search_can_improve_the_first_leg_after_depth_one`;  
- `destination_variation_is_applied_only_after_complete_route_ranking`;  
- `exact_destination_result_reports_final_quality`; and  
- `static_score_legs_report_static_strategy`.  

### First implementation slice and compatibility contract

Do not ship `seed_limit = 1` alone as the fix; the controlled pairwise replays still produced implausible paths. Implement the first corrective slice in this order:  

1. Preserve the existing route result for comparison, but add truthful final adjacent-edge diagnostics and fix the Static leg label.  
2. Make the explicit-destination repeat exemption role-aware. Existing immutable endpoint/context conflicts may be tolerated, while every pair involving a generated track must respect artist and album windows, including generated track versus destination.  
3. Add a fixed pairwise primary matrix for destination edges: learned matrix when Adaptive has one available, captured Static weights for Static or matrix-free fallback. Keep rolling Adaptive context only as a labelled secondary score.  
4. Rank complete deterministic routes by worst primary adjacent distance, then primary adjacent sum, then optional contextual/semantic evidence. Calibrate percentiles only from observations produced by the same metric/reference model.  
5. Split the request controls before reconnecting Automatic selection. Evaluate every depth through the configured budget, choose the shortest route that genuinely meets the adjacent target, and use the best bottleneck route only as an explicitly reported best effort.  
6. Move Variation to the final complete-route quality band. A variation seed may choose among routes close to the deterministic optimum, but it must not change graph reachability or evade repeat constraints.  

Keep request schema version 1 replayable during migration by accepting the current `trigger_percentile` as a deprecated fallback. New destination requests should distinguish fields equivalent to:  

- `direct_trigger_percentile`: whether the unmodified endpoint edge warrants intervention;  
- `target_max_adjacent_percentile`: desired maximum adjacent edge in the generated route; and  
- `max_added_tracks` or exact `additional_track_count`: structural budget, not a quality percentage.  

Do not choose final UI defaults until the sanitized regression corpus has calibrated the new adjacent reference. Better Call Bliss can migrate the old saved trigger into the new direct-trigger field, but should use an independently tested target default. Results should identify `quality_metric`, `reference_model`, pairwise matrix/hash, adjacent bottleneck/sum, contextual secondary score where applicable, target outcome, and whether the returned route is best effort. Existing ambiguous `left_percentile` and `right_percentile` fields should be retained only for artifact replay or renamed so their rolling context is unmistakable.  
### Gate 2: Dedicated layered destination search

**Bounded first implementation complete.** Destination requests no longer route through generic preserved-gap insertion. For exact `N`, the layered beam models `N + 1` fixed-matrix adjacent edges between immutable endpoints. Automatic returns a qualified direct edge, otherwise evaluates increasing depths and continues through the budget when it needs a best effort.  

Complete routes are ranked by worst raw adjacent distance, adjacent sum, semantic support, and deterministic identity. Automatic chooses the shortest route meeting the calibrated adjacent-percentile target; otherwise it returns the best bottleneck/sum result across the budget. Variation is delayed until complete routes and constrained to a 2% bottleneck/5% sum quality band. Fast, Balanced, and Thorough profiles control shortlist, per-state expansion, and beam width. The configured maximum remains a budget, not a promise to consume every slot.  

The remaining Gate 2 step is rebuilding candidate layers per depth or frontier instead of reusing the original endpoint shortlist. A future bounded expansion can union:  

- nearest candidates to the current left frontier;  
- nearest candidates to the right endpoint;  
- candidates near the expected feature-space position for that depth;  
- endpoint-semantic matches; and  
- candidates retained by the opposite-direction frontier.  

A bidirectional beam or layered beam/A* search can then meet in the middle. This avoids scoring all 64k tracks for every beam state while no longer forcing every step through one initial midpoint shortlist.  

### Gate 3: Strategy composition

Do not silently replace the user-selected BlissMixer strategy. Instead, define the destination contract explicitly:  

- Static requests use pairwise Static acoustic edges.  
- Adaptive requests use pairwise learned/static-fallback evidence for the adjacent bottleneck and may use rolling Adaptive context only as a secondary route score.  
- Compare whether a conservative composite such as the maximum of normalized Static and learned percentiles rejects false midpoints better than either metric alone.  
- Keep all component scores visible in diagnostics so a new bliss-rs representation can be added later without changing route semantics silently.  

### Gate 4: Semantic path evidence

First make endpoint evidence depth-aware: left evidence should matter most near the source, right evidence most near the destination. Then explore a bounded, optional LastMix expansion that resolves top local matches and fetches similarity for selected frontier artists/tracks. This should use durable caching, strict request budgets, cancellation, failure tolerance, and Bliss-only fallback. The native optimizer should remain network-free and consume a provider-neutral semantic graph supplied by the plugin.  

### Gate 5: Candidate quality controls

Add auditable optional penalties or exclusions for missing artist/title metadata, known dialogue/spoken-word markers, adverts, very short non-musical items, ignored tracks, and other library-quality signals. Do not hard-code a universal genre policy: interludes and soundtrack material can be legitimate when explicitly allowed.  

## Continuation checklist

- Preserve the four original Pi job directories until the fixture is captured.  
- Begin with the repeat-exemption regression because it is a hard correctness defect.  
- Add adjacent-edge artifacts before changing the search so old and new results can be compared honestly.  
- Implement the layered search with Variation zero first.  
- Reintroduce route-level Variation only after deterministic quality is established.  
- Compare learned, Static, and composite adjacent metrics on all four targets.  
- Listen to the resulting routes; percentiles are evaluation aids, not ground truth.  
- Update `BLISS_PLAYLIST_OPTIMIZER_IMPLEMENTATION_PLAN.md`, optimizer README/schema documentation, `ALGORITHMS.md`, and the Better Call Bliss result explanations when the contract changes.  
