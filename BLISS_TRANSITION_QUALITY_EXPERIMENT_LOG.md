# Bliss transition-quality experiment journal

**Status:** Active exploratory study; second listening round complete

**Scope:** Evidence about temporal localization and directional transition quality  
**Started:** 2026-09-09  
**Last updated:** 2026-09-11

## Purpose and authority

This journal records the execution of the
[transition-quality experiment plan](BLISS_TRANSITION_QUALITY_EXPERIMENT_PLAN.md).
It distinguishes what was proposed from what was run, and records negative
results as carefully as promising observations.

The MkDocs site remains canonical for the research rationale and terminology.
In particular:

- the [Bohemian Rhapsody Problem](docs/analysis/overview.md#the-bohemian-rhapsody-problem)
  defines the whole-track aggregation failure under investigation;
- [enhanced analysis inputs](docs/mixing/analysis-inputs.md) describes temporal
  windows, structural evidence, and anchors;
- [temporal evidence and confidence](docs/analysis/temporal-and-confidence.md)
  defines uncertainty, segmentation, and anchor-policy requirements;
- [transition-aware selection](docs/mixing/transitions.md) separates global
  relevance from physical boundary compatibility;
- the [analysis evaluation protocol](docs/evaluation/analysis-evaluation.md)
  requires Version 2 controls, ablations, failure cases, and directional
  listening judgments; and
- the [analysis research roadmap](docs/evaluation/analysis-roadmap.md) orders
  baseline design, temporal evidence, descriptor prototypes, and structural
  refinement.

If this journal and the site disagree about a general design claim, the site is
authoritative. This journal is authoritative only about what the experiment
actually did.

## Scope and privacy

The immediate target is one task-specific part of acoustic similarity:
perceived coherence when one track leads into another. This does not establish
a better universal song-similarity representation. The work first asks whether
placing existing Bliss evidence at the audible boundary adds value. This
Version 2 temporal work is a control and reusable measurement scaffold, not
the assumed final descriptor set. New descriptor families should be tested only
through explicit ablations against that control.

The pilot uses a private music library and one listener. Published records omit
audio, private paths, server details, credentials, complete track inventories,
catalog identifiers, and blinded mappings. Private artifacts retain those
details locally. Named reference to *Bohemian Rhapsody* is retained because it
defines the public design example, not because the private library is being
published.

## Entry template for subsequent work

Each new entry uses the following fields:

| Field | Required content |
|---|---|
| Status and date | Planned, running, complete, superseded, or rejected |
| Canonical basis | Links to the relevant MkDocs sections |
| Question | One outcome the step is intended to clarify |
| Hypothesis | A claim that the observations can weaken or reject |
| Frozen settings | Inputs, windows, metric, playback, seeds, and treatment |
| Implementation identity | Repository, base revision, branch, tool/schema identity |
| Verification | Tests and integrity checks completed before interpretation |
| Results | Observations without retrospective parameter changes |
| Limitations | Known threats to validity and unsupported generalizations |
| Decision | Continue, revise, reject, or collect more evidence |
| Next evidence | The smallest follow-up capable of changing the decision |

## Experimental baseline

**Status and date:** Active baseline, established 2026-09-09

**Canonical basis:** [current analysis](docs/analysis/current-analysis.md),
[analysis principles](docs/analysis/overview.md#design-principles), and
[experimental protocol](docs/evaluation/analysis-evaluation.md#experimental-protocol).

The prototype is based on upstream `bliss-rs` revision
`0de922dd6121e11f958509f05a30444dcf2d12d2` on the local branch
`experiment/transition-anchors-v1`. The experiment files and `Cargo.toml`
registration remain uncommitted while the signal is being tested.

Unless an entry says otherwise:

- audio is decoded by the current `bliss-rs` Symphonia path;
- analysis runs at the internal 22,050 Hz sample rate;
- every global, window, and anchor vector uses the unchanged 23 Version 2
  feature semantics;
- comparisons use the default `Analysis::distance` implementation;
- lower distance is treated as closer;
- missing/failed candidates are reported rather than assigned a favorable
  score; and
- boundary-only ranks are diagnostic and do not replace the global relevance
  gate.

The branch currently contains five experimental executables:

| Example | Experimental role | Report schema |
|---|---|---|
| `transition_distance` | Whole-track versus fixed endpoint anchors | `bliss-transition-distance-experiment-v2` |
| `boundary_profile` | Sliding trajectory and change proposals | `bliss-boundary-profile-experiment-v1` |
| `boundary_review` | Blinded boundary-listening package | `bliss-boundary-review-package-v1` |
| `boundary_refine` | Multi-scale local proposal refinement | `bliss-boundary-refinement-experiment-v1` |
| `transition_policy_compare` | Frozen-pool endpoint-policy comparison | `bliss-transition-policy-comparison-v1` |

All five examples have passed their focused unit tests, formatting, strict
Clippy, and whitespace checks. At the latest verification point, the combined
example suite contained 28 passing tests and one intentionally ignored test.

## E0: choose transition quality as the first task

**Status and date:** Complete, 2026-09-09

**Canonical basis:** [task-conditioned similarity](docs/mixing/overview.md#design-principles),
[transition-aware selection](docs/mixing/transitions.md#transition-aware-selection),
and [research hypotheses H3-H6](docs/research/analysis-research.md#research-synthesis-and-working-hypotheses).

**Question:** Can a bounded experiment improve knowledge about acoustic
similarity without first proposing a new production representation?

**Hypothesis:** Directional transition judgments can expose information lost by
whole-track aggregation and provide a tractable first evaluation target.

**Setting:** Preserve Version 2 as the control. Separate three questions:
whether a candidate belongs in the mix, whether the literal overlap sounds
plausible, and whether the candidate remains a good continuation after its
opening.

**Result:** The task admits concrete source/candidate comparisons, exact audio
rendering, and low-effort listener judgments. It also directly exercises the
Bohemian Rhapsody Problem without claiming that transition compatibility is the
definition of general song similarity.

**Decision:** Continue with boundary-localized Version 2 evidence before adding
new descriptors. This is a scope decision, not evidence that local evidence is
better.

## E1: fixed endpoint anchors over Version 2

**Status and date:** Complete as a feasibility step, 2026-09-09

**Canonical basis:** [anchor windows](docs/mixing/analysis-inputs.md#anchor-windows),
[anchor feature vectors](docs/mixing/analysis-inputs.md#anchor-feature-vectors),
and [transition distance](docs/mixing/transitions.md#transition-distance).

**Question:** Can the existing analyzer be applied reproducibly to bounded
intros and outros, and can those ranks differ from whole-track ranks?

**Hypothesis:** `distance(source.outro, candidate.intro)` contains directional
ranking information that is absent from whole-track distance.

**Frozen settings:** The first executable used one whole-track analysis plus a
fixed 30-second source outro and candidate intro. Candidates were supplied as a
fixed scenario. The same Version 2 semantics and default distance were used in
both arms. Feature-group contribution shares were retained for diagnosis, not
treated as causal importance.

**Verification:** Tests cover exact range selection, short inputs, deterministic
tie ordering, schema rejection, zero self-distance, reconstruction of default
distance from feature contributions, and a synthetic case in which global and
boundary ranks differ.

**Result:** Bounded analysis is technically feasible and produces rankings that
can differ from whole-track rankings. This proves only that localization changes
the evidence; it does not show that the changed rank is perceptually better.

**Decision:** Add actual listening and temporal profiling. Do not adopt
boundary-only selection.

## E2: align listening clips with LMS playback

**Status and date:** Complete protocol correction, 2026-09-09

**Canonical basis:** [boundary source](docs/mixing/transitions.md#boundary-source),
[loudness and boundary shape](docs/mixing/analysis-inputs.md#loudness-and-boundary-shape),
and [operational reproducibility](docs/mixing/operations.md).

**Question:** Does the audible experiment reproduce the transition the listener
actually hears in LMS closely enough to support judgments?

**Hypothesis:** Crossfade duration and ReplayGain can materially affect a
transition rating and must be frozen rather than treated as incidental playback
details.

**Frozen settings:** Read-only inspection established a 10-second LMS crossfade,
Smart Gain mode, and Smart Transition. Source and candidate track gain are used
for different-album transitions, with peak-based clipping prevention. The final
pilot clips used a 10-second linear complementary crossfade. No server restart
or playback reconfiguration was performed.

**Result:** Successive render revisions changed the interpretation of the small
three-transition pilot. With the final ReplayGain-aware rendering, the ratings
were `5+`, `3`, and `5`; the middle transition remained impaired mainly by a
spoken passage. Earlier ratings produced before the playback contract was fully
specified are retained only as protocol-development observations and are not
pooled with the final scores.

**Decision:** Every later listening package must record crossfade geometry,
gain mode, clipping prevention, sample format, and the amount of candidate
continuation heard after the overlap.

## E3: window trajectory and boundary proposals

**Status and date:** Complete as proposal generation, 2026-09-09

**Canonical basis:** [temporal windows and segmentation](docs/mixing/analysis-inputs.md#temporal-windows-and-segmentation),
[segmentation](docs/analysis/temporal-and-confidence.md#segmentation), and
[structural variance](docs/mixing/analysis-inputs.md#structural-variance).

**Question:** Can short-window Version 2 contrast identify audible change
regions across stable and heterogeneous tracks?

**Hypothesis:** Large distance between adjacent non-overlapping window analyses
is a useful boundary-proposal signal, while a sliding trajectory also exposes
whole-track-to-local divergence.

**Frozen settings:** Six deliberately varied tracks represented stable vocal,
stable instrumental, strongly sectional, distinctive-vocal, spoken-intro, and
stable piano-instrumental cases. Analysis used 10-second windows, a 5-second
sliding hop, two non-overlapping 10-second windows around each boundary
candidate, and 60-second intro/outro search contexts.

**Verification:** Tests cover full endpoint coverage, invalid/short inputs,
non-overlapping change windows, and the requirement for two complete windows.
The report records all Version 2 features and explicitly marks their short-input
validity as unestablished.

**Result:** Every track produced a ranked local trajectory and endpoint/change
proposals. Numerical contrast alone could not say whether a proposal was a
formal section boundary, a transition-relevant regime change, or merely a
measurable harmonic event.

**Decision:** Use the detector only to propose blinded excerpts. Human review is
required before interpreting contrast as boundary evidence.

## E4: blinded boundary-proposal review

**Status and date:** Complete pilot, 2026-09-09

**Canonical basis:** [representation tests](docs/evaluation/analysis-evaluation.md#representation-tests),
[retrieval and listener evaluation](docs/evaluation/analysis-evaluation.md#retrieval-and-listener-evaluation),
and [human agreement](docs/research/analysis-research.md#human-agreement-and-evaluation-validity).

**Question:** Do algorithm-selected contrast locations contain perceptible,
transition-relevant musical or acoustic changes?

**Hypothesis:** The strongest within-track and endpoint-context proposals will
be accepted more often than a middle-ranked distribution control.

**Frozen settings:** A deterministic seed (`20260909`) produced 20 unique,
anonymous 20-second clips, with 10 seconds on either side of the proposal.
Selection included the strongest proposal per track, strongest intro-context
proposal, strongest outro-context proposal, and one median-contrast control per
track, with overlaps deduplicated. One listener recorded yes/no/unsure,
boundary type, perceptual salience from 1 to 5, confidence from 1 to 5, and
optional notes in Markdown.

**Results:**

| Selection role | Yes | No | Unsure | Total |
|---|---:|---:|---:|---:|
| Strongest contrast in each track | 6 | 0 | 0 | 6 |
| Strongest intro-context candidate | 5 | 1 | 0 | 6 |
| Strongest outro-context candidate | 3 | 1 | 2 | 6 |
| Median-contrast control | 3 | 2 | 1 | 6 |
| All unique excerpts | 13 | 4 | 3 | 20 |

Selection roles overlap, so role totals are not additive. The strongest
proposal always corresponded to a perceived change, but salience ranged from 1
to 5. Absolute distance did not separate accepted, rejected, and uncertain
examples. In the stable piano case, much of the disagreement was driven by
chroma: meaningful harmonic movement was measurable without constituting a
transition-relevant structural boundary.

**Limitations:** One listener, six tracks, candidate-selected excerpts, no
manually verified non-boundary set, and only a median-distance control. A real
change is not necessarily relevant to mixing.

**Decision:** Retain contrast as a proposal signal, reject it as perceptual
boundary confidence, distinguish formal segmentation from transition-relevant
regime change, and add explicit timing on a smaller subset.

## E5: timing notes and multi-scale local refinement

**Status and date:** Complete pilot, 2026-09-09

**Canonical basis:** [temporal representation design](docs/analysis/temporal-and-confidence.md#temporal-representation-design),
[segmentation](docs/analysis/temporal-and-confidence.md#segmentation), and the
[Phase 3 structure comparison](docs/evaluation/analysis-roadmap.md#phase-3-structure-and-local-context).

**Question:** Does maximizing local Version 2 contrast at finer resolution move
the proposal toward the listener's perceived event?

**Hypothesis:** A one-second local search at several window scales will refine a
coarse five-second-grid proposal and reveal localization uncertainty.

**Frozen settings:** Eight reviews included approximate event times. One clip
contained two perceived events. Each original proposal was searched from six
seconds before to six seconds after at one-second steps. Independent
non-overlapping comparisons used 5-, 10-, 15-, and 20-second windows.

**Results:** Some events showed narrow cross-scale agreement close to the
listener estimate. Other scales selected different nearby events, and several
maxima landed at the search edge. One clear counterexample moved away from the
listener's event at every scale. Blank timing notes were not counted as exact
agreement.

**Decision:** Reject “nearby maximum raw contrast” as a general boundary
refiner. Represent candidate boundaries as intervals or alternative hypotheses
with scale agreement and event identity. Keep the literal 10-second playback
overlap separate from any inferred musical section boundary.

## E6: first endpoint-policy falsification

**Status and date:** Complete negative result, 2026-09-11

**Canonical basis:** [four evidence roles](docs/mixing/transitions.md#four-evidence-roles-in-a-musical-route),
[transition distance](docs/mixing/transitions.md#transition-distance), and
[score normalization and fusion](docs/mixing/transitions.md#score-normalization-and-fusion).

**Question:** Does multi-window endpoint context correct a transition failure
that a literal overlap comparison misses?

**Hypothesis:** A weighted comparison of the final source context with the
initial candidate context will rank the listener-preferred continuation above a
candidate whose promising opening leads into a poor spoken continuation.

**Frozen settings:** The same three candidates and final human ratings from E2
were rescored. Each endpoint contained three non-overlapping 10-second windows.
Weights decayed boundary-outward by `0.5`. The executable reported whole-track
distance, literal last-to-first-window distance, two one-to-context variants,
weighted-RMS all-pairs endpoint context, and balanced/minimax rank fusions.

**Results:** The whole-track ranking selected the `5+` candidate. Literal
overlap, all-pairs context, and both fusions selected the candidate rated `3`.
The tested all-pairs formulation therefore failed this scenario. Consecutive
candidate-prefix distances for the poorer continuation were `0.672` and
`0.755`, compared with `0.214/0.097` and `0.259/0.355` for the preferred
continuations.

**Interpretation:** Existing features detected a large change after the spoken
opening, but the all-pairs average hid it. This suggests that overlap
compatibility and post-overlap continuation stability are separate signals. It
also suggests, without proving, that explicit speech or vocal-state evidence
could explain a failure the current descriptors only detect indirectly.

**Decision:** Reject this endpoint-context average as a proposed policy. Do not
tune a volatility penalty from one case. Evaluate physical overlap,
continuation stability, and overall transition quality separately on mixed-
provenance candidate pools.

## E7: fixed mixed-provenance candidate pools

**Status and date:** Complete construction, listening pending, 2026-09-11

**Canonical basis:** [candidate generation](docs/mixing/transitions.md#candidate-generation),
[score normalization](docs/mixing/transitions.md#score-normalization-and-fusion),
and [experimental controls](docs/evaluation/analysis-evaluation.md#experimental-protocol).

**Question:** Do the candidate policies disagree often enough on a less narrowly
selected set to support a blinded comparison?

**Hypothesis:** A mixture of near, middle, and distant whole-track candidates
will expose trade-offs that a pool of nearest neighbours alone conceals.

**Frozen settings:** A read-only snapshot of one local Bliss database supplied
six source cases and ten candidates per source. Each pool contained four nearest
candidates with unique artists, candidates at or after global ranks 50, 250,
and 1,000, and three deterministic broad candidates sampled from ranks
1,001-30,000. The source artist was excluded and candidate artists were unique
within each pool. Seed `20260911` controlled broad selection. Files that the
prototype decoder could not analyze were replaced deterministically and logged
as experiment-runner exclusions, not musical rejections.

**Verification:** All six final pools contain ten analyzable candidates, for 60
candidate transitions. Every policy ranks the identical supplied pool for a
given source.

**Results before listening:** All five policies selected the same candidate for
only one of six sources. Literal physical-overlap and all-pairs context winners
agreed for four sources. Balanced and minimax fusions agreed for all six, while
the whole-track and fused winners agreed for two. Agreement is descriptive; it
does not identify a better policy.

**Limitations:** One private library, deterministic but judgmental strata,
whole-track distance still influences every pool, and the broad rank interval
is not uniform in perceptual difficulty.

**Decision:** The pool has enough policy disagreement for a small blinded
screening round. Do not use the selected-route legs as a percentile reference
distribution and do not infer population accuracy.

## E8: blinded transition-policy screening round

**Status and date:** Complete screening round, 2026-09-11

**Canonical basis:** [directional listener evaluation](docs/evaluation/analysis-evaluation.md#retrieval-and-listener-evaluation),
[transition versus fixed-set sequencing](docs/mixing/transitions.md#relationship-to-fixed-set-sequencing),
and [reproducibility and observability](docs/mixing/operations.md).

**Questions and hypotheses:**

- **H6a:** the literal physical-overlap winner improves the overlap rating over
  the whole-track winner.
- **H6b:** the three-window context winner improves continuation or overall
  rating over the whole-track winner.
- **H6c:** the lowest prefix-volatility challenger avoids misleading openings
  and improves continuation ratings.
- **H6d:** balanced or minimax global/context fusion preserves overall quality
  better than context-only ranking.

These are screening hypotheses, not a powered confirmatory study.

**Frozen selection:** For each of the six source cases, include the winner of
whole-track, physical-overlap, endpoint-context, balanced rank fusion, and
minimax rank fusion, plus the candidate with the lowest prefix-volatility RMS.
Deduplicate candidates selected by multiple policies within the same source.
This produced 18 clips, shuffled with seed `20260911`.

**Frozen rendering:** Every anonymous 40-second stereo 44.1-kHz FLAC contains:

- 0-10 seconds: source outro only;
- 10-20 seconds: linear complementary 10-second crossfade; and
- 20-40 seconds: candidate continuation only.

Track ReplayGain and peak-based clipping prevention reproduce the relevant LMS
Smart Gain behavior for different-album transitions. Track-identifying metadata
is removed.

**Frozen judgments:** One listener independently rates overlap, continuation,
and overall transition quality on a 1-5 scale; plus/minus and notes are allowed.
The answer key remains hidden until all 18 rows are complete.

**Verification:** All 18 declared clips exist, decode successfully, last 40.00
seconds, and contain stereo 44.1-kHz FLAC audio. The Markdown sheet contains 18
anonymous rows and no source/candidate title or artist strings. Every clip has a
selection reason. All six policy/challenger roles cover all six sources before
deduplication. ReplayGain tags were available for all inputs; clipping
prevention limited one candidate.

**Analysis:** The mapping was revealed only after all rows were complete. Each
role contributes one result per source. When several roles selected the same
candidate, its one heard rating was reused for those roles rather than counted
as several independent observations. Differences below are paired against the
whole-track winner for the same source; unchanged candidates contribute a tie.

**Results:**

| Role | Overlap mean | Continuation mean | Overall mean | Explicit relevance/style mismatches |
|---|---:|---:|---:|---:|
| Whole-track winner | 3.67 | 3.67 | 3.83 | 1 |
| Physical-overlap winner | 3.50 | 3.33 | 3.50 | 1 |
| Endpoint-context winner | 4.00 | 3.83 | 3.83 | 1 |
| Balanced fusion winner | 3.83 | 3.33 | 3.50 | 2 |
| Minimax fusion winner | 3.83 | 3.33 | 3.50 | 2 |
| Lowest-prefix-volatility challenger | 3.67 | 3.50 | 3.67 | 2 |

The balanced and minimax fusions selected the same candidate for every source,
so their results are identical rather than independent confirmation.

| Role versus whole-track | Sources with a changed candidate | Overlap mean delta | Overlap W/T/L | Continuation mean delta | Continuation W/T/L | Overall mean delta | Overall W/T/L |
|---|---:|---:|---:|---:|---:|---:|---:|
| Physical overlap | 4 | -0.17 | 1/4/1 | -0.33 | 0/4/2 | -0.33 | 0/4/2 |
| Endpoint context | 5 | +0.33 | 2/3/1 | +0.17 | 1/3/2 | 0.00 | 1/3/2 |
| Balanced fusion | 4 | +0.17 | 1/5/0 | -0.33 | 1/2/3 | -0.33 | 0/4/2 |
| Minimax fusion | 4 | +0.17 | 1/5/0 | -0.33 | 1/2/3 | -0.33 | 0/4/2 |
| Lowest prefix volatility | 6 | 0.00 | 1/4/1 | -0.17 | 2/1/3 | -0.17 | 2/1/3 |

Win/tie/loss columns cover all six sources, including unchanged-candidate ties.
Across the 18 unique heard clips, mean ratings were 3.83 for overlap, 3.50 for
continuation, and 3.61 overall. Six notes explicitly identified a genre, style,
or mood mismatch. Overall ratings comprised two `2`s, six `3`s, seven `4`s, and
three `5`s.

The endpoint-context winner produced the only large rescue: for the
distinctive-vocal source case it improved the overall rating from 2 to 4 and
removed the explicit relevance mismatch. It also lost one overall point for two
other source cases. The lowest-volatility candidate improved the strongly
sectional case from 4 to 5, but lost overall quality in three other cases.
These are useful counterexamples to both “local context never helps” and “the
most stable opening is generally best.”

**Limitations:** This is one listener, six sources, and candidates selected
because at least one tested policy favored them. Means have no population or
uncertainty interpretation. More importantly, the mixed-provenance stress pool
included globally distant rank anchors and broad candidates. Allowing a local
policy to choose freely from that pool does not implement the documented
global-relevance gate. The six explicit mismatch notes expose that design
difference rather than measuring the final proposed reranker.

**Decision:**

- H6a is not supported: physical-overlap selection did not improve overlap on
  average and produced no overall wins against the whole-track winner.
- H6b remains unresolved: endpoint context improved mean overlap, was neutral
  overall, and produced both a major rescue and two losses. The tested
  unrestricted policy is not suitable for adoption.
- H6c is not supported as a general selector: low prefix volatility produced
  two overall wins and three losses.
- H6d is not supported: both fusions produced no overall win and two losses
  when their candidate differed from the whole-track choice.
- Do not tune weights or add a volatility penalty from this round. The next
  comparison must enforce global relevance before asking whether local evidence
  improves the remaining choice.

## E9: AcousticBrainz and Essentia precedent review

**Status and date:** Complete research review, 2026-09-11

**Canonical basis:** [current comparison systems](docs/research/comparison-systems.md#current-alternatives-and-comparison-baselines),
[analysis research alternatives](docs/research/analysis-research.md#current-alternatives-and-comparison-systems),
and [Phase 2 descriptor prototypes](docs/evaluation/analysis-roadmap.md#phase-2-high-value-descriptor-prototypes).

**Question:** Can AcousticBrainz provide reusable acoustic evidence or methods
for the Bliss experiment?

**Hypothesis:** AcousticBrainz is useful as a descriptor and evaluation
precedent, even though it is not a current replacement or reliable similarity
ground truth.

**Method:** Review the official AcousticBrainz feature schema, extractor,
similarity metrics, data downloads, and MetaBrainz discontinuation report;
compare them with the existing Essentia treatment in the MkDocs research
foundation.

**Results:** AcousticBrainz used Essentia to separate low-level spectral,
rhythmic, and tonal evidence from high-level predictions. Its similarity system
offered aspect-specific MFCC, GFCC, BPM, onset-rate, key, mood, instrument, and
genre metrics with separate indices rather than one universal distance. The
extractor could retain frame values and calculate multiple distribution and
temporal-difference statistics, although AcousticBrainz normally stored
aggregates.

MetaBrainz discontinued new collection in 2022 after finding unreliable BPM/key
values without adequate confidence, poor cross-domain classifier behavior,
insufficient retained resolution for newer methods, and disappointing
content-similarity results. The frozen CC0 dumps remain potentially useful for
population statistics, duplicate/alternate-submission robustness, and external
descriptor comparisons, but not as listener ground truth or temporal audio
fixtures.

**Decision:** Add AcousticBrainz to the canonical research material as both a
historical precedent and a negative result. Reuse selected Essentia algorithms
as independently evaluated research baselines; do not import the full feature
dump, depend on the discontinued service, or copy/link implementation code
without a license review.

## E10: relevance-gated local reranking

**Status and date:** Complete screening round, 2026-09-11

**Canonical basis:** [candidate generation](docs/mixing/transitions.md#candidate-generation),
[four evidence roles](docs/mixing/transitions.md#four-evidence-roles-in-a-musical-route),
and [task-conditioned similarity](docs/research/analysis-research.md#research-synthesis-and-working-hypotheses).

**Question:** Once globally distant candidates are excluded, does endpoint or
continuation evidence improve transition quality within a fixed Version 2
relevance frontier?

**Hypotheses:**

- **H7a:** literal physical-overlap selection improves overlap without reducing
  relevance or overall quality relative to the whole-track winner.
- **H7b:** three-window endpoint-context selection improves continuation or
  overall quality without reducing relevance.
- **H7c:** the lowest-prefix-volatility challenger improves continuation
  without reducing relevance or overall quality.

These remain screening hypotheses for one listener and six sources.

**Frozen candidate frontier:** For each source, rank the eligible library by
ascending whole-track Version 2 distance, with database row order as a
deterministic tie-break. Retain the first ten candidates with distinct artists.
Exclude the source artist, ignored database rows, tracks shorter than 60
seconds, rows without all Version 2 features, missing local audio, and files
known to be incompatible with the experimental decoder. The latter is a
runner-compatibility exclusion, not a musical filter. No genre, style, or other
metadata gate is used, so this tests a pure Version 2 acoustic frontier rather
than claiming that all ten candidates are perceptually relevant.

**Frozen local policies:** Analyze the same ten candidates for every arm using
exact 10-second windows, three non-overlapping endpoint windows ordered outward
from the boundary, and context decay `0.5`. Compare the whole-track winner,
literal physical-overlap winner, endpoint-context winner, and lowest
candidate-prefix-volatility challenger. E8's balanced and minimax fusions are
not repeated because they did not improve overall quality and selected the same
candidate throughout that round. The implementation identity and unchanged
23-feature semantics are inherited from the experimental baseline above; the
comparison report schema is `bliss-transition-policy-comparison-v1`.

**Frozen listening treatment:** Deduplicate candidates selected by multiple
policies within each source and shuffle the resulting clips with seed
`2026091102`. As in E8, each anonymous 40-second stereo 44.1-kHz FLAC contains
10 seconds of source outro, a 10-second linear complementary crossfade, and 20
seconds of candidate continuation. Apply LMS-style Smart Gain track ReplayGain
for different-album transitions and peak-based clipping prevention. Rate
relevance, overlap, continuation, and overall quality independently on the same
1-5 scale.

**Results before listening:** All six candidate reports completed with ten of
ten successful analyses. No source had the same winner/challenger under all
four roles. Whole-track differed from physical overlap, endpoint context, and
lowest prefix volatility for every source; physical overlap and endpoint
context agreed for two sources. Deduplication reduced 24 role selections to 21
anonymous clips. These disagreements make the listening round informative but
do not imply that any local policy is better.

**Verification:** The package declares 21 clips and contains 21 FLAC files, 21
Markdown rating rows, and 21 playlist entries. Every clip decoded completely,
lasts 40.00 seconds, and contains stereo 44.1-kHz FLAC audio. All four roles
cover all six sources before deduplication. The sheet exposes no track identity
and includes a separate relevance column. Tagged track ReplayGain was available
for all 42 rendered legs; clipping prevention limited one leg. The answer key
remained closed until every rating was complete.

**Analysis:** Each role contributes one result per source. When two roles chose
the same candidate, its one heard rating was reused rather than treated as an
independent observation. All three challengers chose a different candidate
from the whole-track winner for every source, so paired ties below mean equal
ratings, not identical candidates. Differences are paired within each source.

**Results:**

| Role | Relevance mean | Overlap mean | Continuation mean | Overall mean | Wrong-genre notes | Opening-issue notes |
|---|---:|---:|---:|---:|---:|---:|
| Whole-track winner | 3.17 | 4.00 | 3.83 | 3.33 | 1 | 1 |
| Physical-overlap winner | 3.50 | 3.67 | 4.17 | 3.67 | 0 | 1 |
| Endpoint-context winner | 3.17 | 4.00 | 4.17 | 3.50 | 2 | 0 |
| Lowest-prefix-volatility challenger | 3.83 | 4.33 | 4.17 | 3.83 | 2 | 0 |

| Role versus whole-track | Relevance delta (W/T/L) | Overlap delta (W/T/L) | Continuation delta (W/T/L) | Overall delta (W/T/L) |
|---|---:|---:|---:|---:|
| Physical overlap | +0.33 (1/5/0) | -0.33 (2/1/3) | +0.33 (2/4/0) | +0.33 (3/1/2) |
| Endpoint context | 0.00 (1/3/2) | 0.00 (2/2/2) | +0.33 (2/4/0) | +0.17 (1/4/1) |
| Lowest prefix volatility | +0.67 (3/3/0) | +0.33 (3/1/2) | +0.33 (2/4/0) | +0.50 (3/3/0) |

Across the 21 unique clips, mean ratings were 3.48 for relevance, 4.00 for
overlap, 4.10 for continuation, and 3.62 overall. Four clips received explicit
wrong-genre notes. Those clips nevertheless received overlap ratings from 3 to
5 and a continuation rating of 4 in every case, while relevance was 1 to 3 and
overall quality was 2 to 3. Smooth boundary mechanics therefore did not imply
that the next track belonged in the musical context. Two other notes identified
an unusual candidate opening; neither occurred under the endpoint-context or
lowest-volatility roles in this sample.

**Limitations:** The frontier is acoustic rather than human-validated, and ten
distinct-artist candidates can still contain weak musical matches. That is why
relevance is a measured outcome rather than an assumed property. The study is
still limited to one private library, one listener, six sources, and policies
that rearrange existing Version 2 evidence. Candidate membership was selected
from stored database vectors, whereas the comparator reanalyzed the audio. A
documented lossless decoder workaround slightly reordered whole-track
candidates for one source within the frozen frontier. This does not change the
candidate set or paired treatment, but a replication should derive frontier
and policy scores from one representation identity.

**Decision:**

- H7a is not supported. Physical-overlap selection reduced mean overlap, with
  three losses and two wins, and also produced two overall losses.
- H7b remains mixed. Endpoint context improved continuation twice without a
  continuation loss, but produced two relevance losses and no mean relevance
  gain. It is not ready to serve as an unrestricted reranker.
- H7c passes this round's screening gate. Lowest prefix volatility improved
  relevance and overall quality for three sources with no losses, and improved
  continuation twice with no losses. This is evidence for replication, not for
  adoption: E8 was negative, the sample is very small, and the selector does
  not itself model source-to-candidate compatibility.
- Keep relevance, overlap, continuation, and overall quality separate. The
  wrong-genre counterexamples show why a single transition judgment would hide
  important failure modes.
- Do not tune fusion weights from these results.

**Next evidence:** Replicate the lowest-prefix-volatility comparison on a new,
larger set of source cases with the same predeclared frontier, playback, and
rating dimensions. Use one analysis identity for both frontier construction
and reranking. Retain whole-track as the control and endpoint context as a
secondary diagnostic, but do not expand the policy set or tune parameters from
this round. A persistent global-relevance failure should become a separate
descriptor/retrieval experiment rather than being attributed to boundary
selection.

## E11: Version 2 temporal-control replication package

**Status and date:** Package verified; listener ratings pending, 2026-09-13

**Canonical basis:** [research sequencing after early evidence](BLISS_TRANSITION_QUALITY_EXPERIMENT_PLAN.md#research-sequencing-after-early-evidence),
[temporal evidence experiments](docs/evaluation/analysis-roadmap.md#phase-1-temporal-evidence-experiments),
and [vocal presence and character](docs/analysis/representations.md#vocal-presence-and-character).

**Question:** Does the lowest-prefix-volatility result from E10 survive a
larger, predeclared replication when the candidate frontier and local policies
use one analysis identity?

**Hypothesis:** A stable candidate opening improves continuation and overall
transition quality often enough to remain a useful Version 2 temporal control.
The hypothesis is about the scaffold and control condition only; it does not
claim that Version 2-derived stability is the best or final acoustic evidence.

**Frozen setting:** Use twelve new source cases, excluding the original six
source cases. The source set is deterministically sampled from six broad
library strata: rock or hard rock, metal or extreme music, long or progressive
tracks, classical/soundtrack/instrumental material, folk/blues/jazz/soul, and
pop/alternative/punk. Two sources are selected per stratum, with unique source
artists. This stratification is intended to broaden the replication sample; it
is not a claim that the strata are ground-truth musical categories.

Each source first receives a thirty-candidate database prefrontier using stored
Version 2 distance as a cheap prefilter. The experimental `bliss-rs`
transition-policy comparator then reanalyzes the source and prefrontier
candidates. The final ten-candidate frontier is selected by ascending
reanalyzed whole-track distance, so the final frontier and local policies use
one analyzer identity. Candidates that the experimental runner could not
decode are excluded as runner failures before final-frontier selection, not as
musical judgments.

Final policy comparison preserves the E10 settings: exact 10-second windows,
three candidate-prefix windows, context decay `0.5`, LMS-style 10-second
ReplayGain-aware crossfade rendering, and separate relevance, overlap,
continuation, and overall ratings. Compare the unchanged whole-track winner,
lowest-prefix-volatility challenger, and endpoint-context diagnostic without
adding new local policies or tuning weights.

**Implementation identity:** The private package uses the local experimental
`bliss-rs` branch `experiment/transition-anchors-v1` and the release-built
`transition_policy_compare` example over the unchanged Version 2 feature
semantics. Private helper scripts create the source prefrontier, derive the
reanalyzed final frontier, and render anonymous review clips. Generated paths,
track inventories, and answer keys remain private.

**Verification before listening:** Twelve final source pools were created, each
with ten successful candidates. The three selected roles cover every source:
whole-track winner, endpoint-context winner, and lowest candidate-prefix
volatility. Deduplication across roles produced thirty-three anonymous clips.
All thirty-three FLAC files decode successfully. Each clip uses the same
40-second structure as E10: 10 seconds source outro, 10 seconds linear
crossfade, and 20 seconds candidate continuation. ReplayGain probing and
clipping-prevention data are stored in the private answer key. No listener
ratings have been interpreted yet.

**Planned analysis:** Reveal the answer key only after all thirty-three rows
are rated. Reuse the E10 analysis shape: role means, paired deltas against the
whole-track winner for relevance, overlap, continuation, and overall quality,
win/tie/loss counts, explicit wrong-genre notes, opening-issue notes, and
results by sanitized source stratum. Do not tune thresholds, add roles, or
reinterpret skipped decoder failures after seeing ratings.

**Decision rule:** If the prefix-stability signal does not replicate, stop
tuning Version 2 temporal distances and move to the first missing descriptor
family. The preferred next family is vocal activity, speech-like evidence, and
instrumental coverage because earlier failures exposed spoken or unusual vocal
state that the current 23 features can only describe indirectly. If the signal
does replicate, keep it as a control baseline and still test the vocal/speech
family against it before considering integration work.

## Current state and next action

The experiment has established that:

1. current Bliss evidence can be computed over bounded windows;
2. raw contrast proposes many audible changes but is not boundary confidence;
3. musical event identity and timing scale matter;
4. one intuitive endpoint-context average has already failed a known case;
5. the current descriptors can expose continuation instability without
   explicitly identifying speech or vocal state;
6. unrestricted local selection does not outperform whole-track selection in
   the first blinded screening, although one distinctive-vocal failure was
   substantially improved by endpoint context; and
7. under the ten-candidate Version 2 frontier, low candidate-prefix volatility
   passed a six-source screening gate while physical overlap did not; and
8. smooth overlap and continuation can coexist with an explicitly irrelevant
   next track, so global relevance and boundary quality require separate
   judgments.

It has **not** established that prefix stability generalizes, that
boundary-localized Version 2 evidence is sufficient for transition choice, or
that any new descriptor should become part of Bliss. The next action is E11: a
predeclared replication of the prefix-stability result on new source cases,
with frontier and local scores computed from one analysis identity. The
temporal machinery should be treated as reusable scaffold. The next substantive
feature-family experiment should begin with vocal activity, speech-like
evidence, and instrumental coverage, then proceed to rhythm/onset,
dynamics/boundary shape, and harmonic trajectory only through separate
ablations.
