# Psychoacoustics and operational concerns

**Status:** Living research and design proposal  
**Primary scope:** Research scope, UX, observability, and performance  
**Last reviewed:** 2026-08-01

## Psychoacoustic scope

Psychoacoustics should be treated as a source of hypotheses for the general
audio representation, not only for transition anchors, and not as a separate
runtime layer or a promise to reproduce MusicIP.

### Reasonable early work

- document the perceptual assumptions already present in spectral and chroma
  processing before adding another feature family;
- use a standards-based loudness implementation with correctly named outputs;
- test level normalization choices before comparing timbre;
- evaluate whether very low and very high frequency energy should influence
  perceived similarity as strongly as mid-band content;
- compare candidate perceptual descriptors with the current timbre, loudness,
  chroma, and tempo groups through feature-family ablations.

### Research work, not MVP assumptions

- simultaneous masking and spreading functions;
- temporal masking around transients;
- Bark-scale replacement of existing timbre features;
- learned perceptual embeddings;
- claims that a particular preprocessing chain models "what a human hears."

Bliss does not currently extract MFCCs. Applying A-weighting before hypothetical
MFCC extraction would therefore be a new pipeline rather than a correction to
the existing one. A-weighting is designed for particular sound-level
measurement contexts and is not automatically the correct preprocessing for a
new musical timbre descriptor. Any such experiment must be evaluated against
unweighted and loudness-normalized baselines.

## User experience and configuration

The development version should expose as little configuration as possible:

- enhanced similarity experiments: off/on or an explicitly named experimental
  method;
- variety policy: off/on, with at most one advanced influence control;
- transition-aware reranking: off/on;
- transition influence: one advanced slider, if needed for evaluation;
- personalization: optional, with the existing learned-matrix influence kept as
  an advanced control rather than a prerequisite;
- feedback progress: judgments collected, current model tier, held-out evidence,
  and whether more answers are expected to help;
- analysis status/coverage: informational;
- rebuild enhanced analysis: maintenance action.

Feature families, segment policy, anchor duration, normalization method,
candidate-pool multiplier, and individual DSP weights should remain experimental
settings or command-line options until there is evidence that users benefit from
controlling them.

All enhanced methods should initially default to **off** until analysis
migration, fallback behavior, evaluation, and performance are proven.
Personalization is different: the unpersonalized baseline remains the default,
while an existing compatible personal matrix may continue to be opt-in. The UI
should invite short, resumable feedback sessions rather than imply that users
must complete 100 or more rounds before BlissMixer becomes useful.

## Observability

Debug output should make a decision explainable without logging raw audio:

- active feature schema and representation type;
- selected global algorithm and seed tracks;
- baseline and enhanced global ranks/scores when an experiment is active;
- enhanced-analysis coverage and missing-feature fallbacks;
- actual boundary source track;
- candidate pool size and anchor-data coverage;
- relevance-versus-diversity contributions and duplicate suppression;
- normalization method and active weights;
- personal-metric schema, model tier, validation confidence, normalization,
  effective blend contribution, and fallback reason;
- for top candidates: global rank/score, transition rank/distance, loudness
  penalty, final score, and missing-data fallback;
- analysis/schema version mismatches;
- time spent in global search, metadata lookup, and reranking.

## One-shot reproducibility and deployment observability

The [fixed-set sequencing prototype](fixed-set-sequencing.md) operates outside
the shipped LMS BlissMixer flow and can affect a saved playlist if its result is
deployed manually. Its evidence is useful only when the complete decision can
be reconstructed from frozen inputs and the deployed catalog state is checked
afterward.

### Frozen input and executable identity

Each run should record:

- the input playlist's SHA-256 and track count;
- the Bliss database SHA-256, integrity result, schema or table identity,
  eligible-track count, and exact analysis coverage for the curated and bridge
  candidate sets;
- the learned-matrix SHA-256, dimensions, and feature-schema identity;
- a snapshot of the relevant `plugin.blissmixer` preferences, including the
  selected algorithm, learned blend, seed behavior, and track, artist, and
  album repeat windows;
- the frozen original-playlist artist-profile SHA-256, source-artist count,
  successful and failed lookup counts, and query policy;
- the exact optimizer identity: repository commit, dirty-state indicator,
  hashes of the executable scripts, interpreter and dependency versions, and
  platform; and
- where parity is checked, the native `bliss-mixer` version and binary hash.

Hashes belong in private run artifacts. A public report may state that identity
was frozen and parity passed without publishing run-specific hashes, private
paths, server addresses, credentials, or playlist contents.

### Algorithm and decision trace

Record every input that can change the route:

- algorithm mode and whether Static weights are active or provenance-only;
- strict sliding seed-window size and single-seed behavior;
- learned-matrix blend;
- random seed and restart count;
- track, artist, and album look-back windows;
- route objective and worst-leg weight;
- energy-arc policy and selection thresholds; and
- bridge mode, automatic threshold, maximum budget or explicit count,
  two-leg acceptance limits, and Last.fm fallback policy.

For each selected leg, retain the ordered seed context, next track, raw
continuation cost, and any normalized value. For each bridge proposal, retain
the direct gap, both rescored legs, evidence tier and sources, local-pool state,
repeat-policy result, acceptance or rejection reason, and the final insertion
position. This is the minimum trace needed to distinguish a metric decision
from a semantic fallback or a constraint failure.

When a compatible native mixer binary is available, compare the prototype with
that binary on frozen real seed contexts. At minimum, validate seed count,
algorithm selection, and the effective blended diagonal within a declared
tolerance. Matrix parity alone does not prove full route parity: later work
should also compare candidate distances, rankings, filters, and single-seed
fallback behavior where the API exposes enough diagnostics.

### Extended-M3U contract

Reordering must preserve each existing track's complete entry block. A newly
inserted bridge must use the exact LMS-style three-line representation:

```text
#EXTURL:<LMS-compatible file URL>
#EXTINF:<duration>,<title>
<filesystem path>
```

The file URL must match LMS escaping rather than a generic approximation. The
parser may accept an LMS playlist containing a transient leading `#CURTRACK`
marker before `#EXTM3U`. Generated optimized playlists start with `#EXTM3U` and
must not copy `#CURTRACK` or other transient playback-state markers. Validate
header placement, block adjacency, encoding, path uniqueness, expected count,
and—where the target filesystem is available—file existence before deployment.

### Post-deployment verification

Writing valid bytes is not sufficient. After deployment:

1. hash and re-read the deployed playlist;
2. run the supported playlist scanner or rescan flow;
3. confirm that scanning has actually completed;
4. compare the catalog's decoded playlist URLs with the M3U position by
   position; and
5. verify track count, uniqueness, metadata, and absence of staging files.

Scanner metadata can cause an existing playlist row to be removed and recreated
during a supported rescan or repair. The LMS playlist database ID may therefore
change and must not be treated as stable playlist identity. Use the intended
playlist name/location, frozen input and output hashes, and exact ordered URLs
for verification; record a catalog ID only as transient deployment evidence.

## Future interactive execution contract

If constrained sequencing becomes an interactive application capability, its
operational boundary should be a versioned request/result contract rather than
an implicit sequence of UI or filesystem actions. The request should declare:

- the ordering policy: exact-permutation optimization, immutable-anchor gap
  filling, or a destination-constrained route;
- immutable anchors, queue prefix, start or end locks, and whether opening or
  closing additions are permitted;
- artifact and feature-schema identities, captured scoring settings, repeat
  windows, search effort, deterministic seed, and bridge or route-length policy;
  and
- a frozen, provider-neutral semantic-evidence snapshot with source endpoint,
  provider, raw rank or score, cache state, identity-match confidence, coverage,
  and failure metadata.

The result should identify the executable and schema versions, classify every
original and inserted track, expose per-leg contexts and costs, prove the hard
constraints, and explain every semantic fallback. A stable job identifier may
correlate progress, cancellation, diagnostics, and the retained report, but it
must not replace the immutable input and artifact identities needed for
reproduction. Cancellation or failure must not expose a partial result as a
completed playlist.

An integrated host should persist playlists through its supported playlist
objects or commands, create a new result by default, and verify the stored
order track for track. Direct extended-M3U serialization remains important for
file interoperability and parity testing, but manual file replacement should
not become the application transaction model. Likewise, a
destination-constrained queue operation should append a fully validated suffix
atomically and leave the existing queue unchanged on failure.

Remote semantic evidence is optional input. Disabled providers, network
failure, partial responses, or bounded stale-cache use must be reported as
capability states and should fall back to available evidence or Bliss-only
scoring. They must not turn a feasible local acoustic route into an operational
failure. Credentials, raw responses, complete playlists, and private paths
remain excluded from normal logs.

## Deterministic parallel evaluation

Parallel execution is safe only for independent work over immutable snapshots,
such as restart searches, candidate scoring under an already constructed context,
or provider lookups whose responses are captured before route evaluation. Each
work unit needs a stable identity and a deterministically derived random seed.
Results must be reduced with the complete declared objective and stable tie-breaks
so thread scheduling cannot change the selected route.

Context-dependent calculations remain attached to their exact ordered seed
window. In particular, an Adaptive matrix constructed from the preceding route
context must not be cached or published as one static pairwise track-distance
matrix. Different positions may legitimately assign different costs to the same
candidate pair because their preceding contexts differ.

Persistence, playlist mutation, final report assembly, and user-visible state
changes should cross one ordered side-effect boundary after validation. Parallel
workers return evidence; they do not independently commit partial results.
Concurrency should also reserve enough host capacity for playback and normal
server work. Reproducibility across thread counts belongs in the acceptance tests,
not merely in a performance benchmark.

## Performance expectations

- Audio decoding and feature extraction happen offline.
- Runtime metadata should be loaded or indexed so scoring does not perform an
  SQLite query per descriptor or candidate.
- Normal mixing should load only hot summaries, anchors, and selected segments;
  dense frame sequences remain cold unless an explicit algorithm needs them.
- Experimental analysis conditions should report incremental cost so the
  Version 2 baseline is not credited with segmentation or frame-retention work.
- Research prototypes should report whether shared or independently computed
  evidence changes quality, cost, or comparability; no upstream organization is
  prescribed.
- Enhanced similarity and task-specific reranking should add only a small
  fraction of the existing mix-request latency.
- Memory use should be measured with a realistic library, especially if window,
  segment, or anchor vectors are retained in memory.

No numeric latency or memory budget is committed until a prototype establishes
a baseline on the project's target hardware.
