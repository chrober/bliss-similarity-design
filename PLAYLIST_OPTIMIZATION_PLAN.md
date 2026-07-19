# Example Playlist 2026 one-shot playlist optimization plan

**Status:** Adaptive 20-track base and 40-track Extended playlists deployed,
scanned, and positionally verified on 2026-07-17. The base is catalog ID
723633; Extended is 723634. See PLAYLIST_OPTIMIZATION_EXECUTION.md for hashes,
adaptive metrics, binary parity evidence, alternatives, and rollback paths.  
**Target playlist:** `/mnt/usbHD/LMS/playlists/Example Playlist 2026.m3u`  
**Primary objective:** Turn the existing curated set into a fluent, intentional
open-ended listening sequence while preserving every curated track.  
**Secondary objective:** Permit a small number of clearly justified bridge
tracks when they materially reduce an otherwise severe transition.

## Decision summary

This should be treated primarily as a **sequencing** problem, not as a normal
BlissMixer candidate-generation problem.

The current playlist already defines membership: it contains 20 curated tracks
and no intentional order. The first result must therefore contain all 20 tracks
exactly once. Relevance retrieval and diversity selection have largely already
been performed by the curator. The remaining problem is to find a smooth open
Hamiltonian path through those tracks, then validate its most difficult
transitions by listening.

The current `bliss-mixer` cannot perform this task directly:

- `/api/list` finds tracks similar to one seed;
- `/api/mix` finds new candidates from one or more seeds;
- neither endpoint reorders a supplied fixed set or returns a pairwise distance
  matrix;
- Adaptive Weighting scores candidates against the mean of a seed set, which
  is useful for continuation but the endpoint does not optimize a complete
  fixed-set sequence.

The recommended one-shot solution is a small local Python tool, using only the
standard library, that reads a consistent copy of `bliss.db`, reproduces the
current mixer's sliding adaptive context at every proposed position, and
optimizes a directional open path. `bliss-mixer` and LastMix remain useful as
supplemental candidate sources and semantic checks if bridge tracks are needed.

This approach deliberately does not add a feature to `lms-blissmixer`. It does,
however, preserve enough diagnostics and configuration to inform a later
`/api/order` or playlist-ordering feature.

## Known environment and preconditions

The initial access check established the following:

- Lyrion Music Server is available at `192.168.1.111:9000` and reported version
  9.1.1;
- SSH login as `tc` worked;
- `bliss.db` is a readable SQLite database at
  `/mnt/mmcblk0p2/tce/slimserver/prefs/bliss.db`;
- `bliss-mixer` 0.8.0 is executable from the installed BlissMixer plugin;
- `/mnt/usbHD/music/` is readable and traversable;
- the playlist is readable and writable and its directory is writable;
- the current extended M3U has 61 lines: one header plus 20 three-line track
  blocks (`#EXTURL`, `#EXTINF`, and the local file path).

The server later became temporarily unreachable during an optional follow-up
inspection. Execution must therefore begin by repeating the lightweight
connectivity and path checks. That transient outage does not change the design.

The server does not expose a standalone `sqlite3` executable. The database
inspection and optimizer should run on the Windows workstation against a
read-only snapshot. No server password, database snapshot, learned matrix, or
music metadata should be committed to this repository.

## Design principles applied to this playlist

The repository documentation leads to these constraints:

1. **Separate membership, diversity, and sequencing.** Membership is the 20
   curated songs. Their global variety is fixed. Ordering may improve local
   coherence without removing that variety.
2. **Use Version 2 as the measurable baseline.** The available `TracksV2`
   representation contains 23 whole-track features: tempo, seven timbral
   values, two loudness values, and thirteen chroma-derived values.
3. **Do not mistake whole-track distance for transition truth.** Version 2 has
   no temporal order and no intro/outro anchors. It can propose a good order,
   but actual outro-to-intro transitions require an audition gate.
4. **Respect the active algorithm switch.** With adaptive weighting enabled,
   static sliders are frozen as provenance but excluded from route and bridge
   scoring. The learned matrix is blended with each context's variance matrix
   exactly as bliss-mixer does.
5. **Optimize both total flow and the worst jump.** A route with a low total
   cost may hide one very bad transition. The objective must penalize the
   maximum or upper-tail edge as well.
6. **Treat extra songs as bridges, not recommendations.** A bridge is admitted
   only if it measurably splits a difficult jump, remains musically plausible,
   and passes listening review.
7. **Keep the original recoverable.** Candidate playlists are written beside
   the source first. The source is replaced only after approval and only after
   a timestamped backup is made.

## Phase 0: read-only preflight and snapshot

### 0.1 Recheck the live system

Confirm:

- ports 22 and 9000 are reachable;
- SSH authentication still works;
- the database, music root, playlist, and playlist directory remain
  accessible;
- no `bliss-analyser` process is currently writing the database;
- whether `bliss.db-wal`, `bliss.db-shm`, or another SQLite sidecar exists;
- the running `bliss-mixer` command line, including `--weights` and `--matrix`;
- whether `learned_matrix.json` exists and is the artifact actually loaded;
- whether LastMix is installed and enabled;
- the relevant Lyrion ReplayGain and crossfade settings, because playback
  configuration affects perceived transitions.

### 0.2 Create consistent local inputs

Copy, without changing the server:

- the playlist;
- `bliss.db` and any active SQLite sidecars needed for consistency;
- the learned matrix only if one is present and active.

Prefer a quiescent copy when the analyzer is not running. Validate the local
snapshot with `PRAGMA quick_check` and open it using SQLite read-only mode. If a
safe consistent snapshot cannot be obtained while the database is active,
pause only the analyzer workflow for the duration of the copy; there is no
reason to stop Lyrion playback or modify `bliss.db`.

Record source paths, sizes, modification times, and SHA-256 hashes in the run
report. Keep the snapshots outside Git or delete them after the accepted
playlist and report have been produced.

### 0.3 Validate playlist identity and database coverage

The inspector must:

- parse the UTF-8 BOM and `#EXTM3U` header correctly;
- treat each `#EXTURL`/`#EXTINF`/path group as one indivisible track block;
- resolve exactly 20 unique absolute paths;
- verify that every file exists and is readable;
- match every path to exactly one `TracksV2.File` row with `Ignore IS NOT 1`;
- reject missing, duplicate, ignored, or multiply matched rows before scoring;
- report title, artist, album, genre, duration, tempo, and the 23 feature
  values for audit purposes.

This phase is a hard gate. An optimization over incomplete or ambiguously
matched data must not be deployed.

## Phase 1: build the one-shot optimizer

Use the standalone `tools/playlist_optimizer.py` created for this execution.
It is a task tool,
not plugin code and not a production API.

### Inputs

- read-only SQLite snapshot;
- source M3U;
- optional learned matrix;
- optional locked start and/or end track;
- deterministic random seed;
- bridge policy, defaulting to disabled for the first run;
- output directory.

### Outputs

- curated-only candidate M3Us;
- an optional bridged candidate M3U;
- `REPORT.md` for human review;
- `run.json` containing hashes, schema, metric configuration,
  complete ordering, edge scores, constraints, and reproducibility data;
- `dynamic-transitions.csv` containing each selected seed window and next-track score.

The tool must never write to SQLite. It should fail closed on schema mismatch,
non-finite values, missing paths, or an incompatible matrix.

### M3U handling

For existing tracks, move the complete original three-line block rather than
regenerating it. This preserves the exact title, duration, URL encoding, and
path spelling.

For an added bridge track, generate:

1. `#EXTURL:` plus the exact `URI::file` serialization used by
   `Slim::Utils::Misc::fileURLFromPath` (including unescaped commas and escaped
   spaces/apostrophes/UTF-8);
2. `#EXTINF:<integer duration>,<title>` with the title only, matching an LMS
   user-added playlist entry;
3. the exact `TracksV2.File` path.

Write UTF-8 with the same BOM and newline convention as the source. A valid
curated-only result must contain 61 lines; each accepted bridge adds three.
Validate final candidates with `validate_m3u.py --require-lms-blocks` so a
missing or differently escaped `#EXTURL` fails before deployment.

## Phase 2: construct trustworthy distance views

### 2.1 Static-mixer path, only when configured

Use the feature order implemented by `bliss-mixer/src/db.rs`:

```text
Tempo,
Zcr,
Mean/StdDev SpectralCentroid,
Mean/StdDev SpectralRolloff,
Mean/StdDev SpectralFlatness,
Mean/StdDev Loudness,
Chroma1..Chroma13
```

Reproduce the running plugin's actual 23 startup multipliers only when the
captured algorithm is `static`. The plugin derives them from the four
Tempo/Timbre/Loudness/Chroma settings and the mixer multiplies each coordinate
before squared-Euclidean search:

```text
d_static²(a, b) = sum_i (w_i * (a_i - b_i))²
```

The documented default settings `4/30/9/57` produce a multiplier of 1.0 for
every feature. Do not assume the defaults if the running process shows a
different `--weights` value.

Capture the live values through LMS's `pref plugin.blissmixer:* ?` API and
freeze them with the run. The algorithm switch is authoritative: static
sliders are provenance only and must not influence an adaptive run.

### 2.2 Learned-matrix view, when available

If the running mixer loads a learned 23x23 matrix, validate:

- dimensions are exactly 23x23;
- all entries are finite;
- symmetry is within a stated tolerance;
- the matrix is positive semidefinite within numerical tolerance;
- it corresponds to the same Version 2 schema.

Then calculate:

```text
d_learned(a, b) = sqrt((a - b)^T M (a - b))
```

The learned matrix is not a separate rank-fusion channel in adaptive mode. It
is blended directly with the context-specific variance matrix using the
server's configured coefficient.

### 2.3 Adaptive weighting as the primary contextual metric

When `use_adaptive_weights=1`, mirror bliss-mixer for every next-track decision.
With strict seed order and `num_seed_tracks=3`, position `k` uses the final
three already-ordered tracks (or the available one/two tracks at the start):

```text
S_k = p[max(0, k-3) .. k]
mu_k = mean(raw_features(S_k))
V_k[i,i] = normalize_to_sum_23(1 / (population_variance_i(S_k) + 1e-6))
M_k = 0.20 * M_learned + 0.80 * V_k       when |S_k| >= 2
M_k = M_learned                            when |S_k| = 1
d_k = sqrt((features(p[k]) - mu_k)^T M_k (features(p[k]) - mu_k))
```

The 0.20 value is read from `learned_blend=20`, not hard-coded as a universal
default. Do not build one variance matrix from the full curated set: the
sliding context is the feature being reproduced. The first transition uses the
single-seed learned-matrix behavior implemented by bliss-mixer.

### 2.4 Supplemental control

Optionally calculate a library-robust standardized distance using medians and
MAD or another declared robust scale over all non-ignored tracks. This detects
whether one raw feature scale dominates unexpectedly. It is a diagnostic and
must not silently replace the exact mixer baseline.

## Phase 3: optimize the curated-only open path

### 3.1 Objective

For an order `p`, minimize a transparent directional objective:

```text
base(p) = sum dynamic_context_cost(p[0..k], p[k+1])
smooth(p) = base(p)
          + lambda_max * max dynamic_context_cost(p[0..k], p[k+1])
```

Use raw adaptive Mahalanobis distances, because the variance matrix and ideal
centroid change at every position. Start with `lambda_max = 2.0`, then report
sensitivity at 1.0 and 3.0. This gives the
largest transition enough influence to avoid one dramatic cliff without
overriding all 19 local decisions.

Apply the active lms-blissmixer repeat policy as hard sequence constraints:

- no repeated artist among the next 5 tracks;
- no repeated album among the next 10 tracks;
- no repeated track among the next 100 tracks.

The original curated set already contains unique file paths, so the track
constraint is satisfied by every exact permutation. Artist and album checks are
performed against the complete proposed route, not only adjacent pairs. A
candidate with any violation is ineligible. If no feasible curated-only route
exists, bridge insertion may be used to add spacing, but every resulting route
must pass the same complete-window validation.

Do not optimize a cycle. The playlist has a beginning and an end, so the edge
from the last track back to the first must not contribute.

### 3.2 Search strategy

Twenty tracks are small enough for an extensive deterministic heuristic without
adding a solver dependency:

1. nearest-neighbour construction from every possible start;
2. cheapest-insertion construction;
3. randomized greedy construction with a fixed recorded seed;
4. repeated 2-opt improvement for open paths;
5. swap and single-track relocation moves;
6. optional simulated annealing or iterated local search if the same local
   optimum is not reached consistently.

Run enough restarts to establish convergence and keep the best distinct
solutions. An optional exact or branch-and-bound verifier may be written in
Rust later, but it is unnecessary for the one-shot result if repeated searches
converge and the listening gate passes.

### 3.3 Produce useful curated-only candidates

1. **Original:** unchanged curated order, evaluated by the dynamic metric.
2. **Adaptive smooth:** exact sliding-context adaptive metric.
3. **Adaptive arc:** selected from solutions within 8% of the best smoothness objective,
   using a declared intensity proxy only to choose orientation and broad shape.

The intensity proxy may use normalized tempo, mean loudness, ZCR, and spectral
brightness, but it must be labelled a proxy rather than a measured universal
"energy" value. A reasonable first arc is a gentle opening, a gradual rise, a
late crest, and a short comedown. It must not be allowed to create severe local
jumps merely to fit that shape.

Adaptive route costs are directional: reversing a route changes its seed
windows, centroids, variance matrices, and usually its score. Do not
canonicalize a route against its reversal.

## Phase 4: consider bridge tracks conservatively

Bridge insertion starts only after the best curated-only order is known. It has
two explicit modes:

- **automatic:** insert only for a transition above the severe-gap threshold;
- **exact count:** insert exactly the user-requested number of additional
  tracks, even when no gap triggers automatic mode, while retaining acoustic,
  semantic, uniqueness, and repeat-window gates.

### 4.1 Identify bridge-worthy gaps

Inspect the largest and upper-tail edges. A gap becomes bridge-worthy only when
it is both:

- an objective outlier relative to the optimized route; and
- judged awkward in an actual listening transition.

This avoids adding songs merely because one edge must mathematically be the
largest.

### 4.2 Candidate generation

For a difficult edge `A -> B`, gather candidates from:

- a direct full-database scan around both endpoints and their midpoint;
- `/api/list` neighbours of A and B as a sanity check;
- `/api/mix` with A and B as the two seeds, `adaptiveweights=1`, `shuffle=0`,
  and the curated tracks in `previous`;
- a LastMix/Last.fm artist-neighbourhood profile built from the complete
  original 20-track playlist.

Build the artist profile once, before considering individual gaps:

1. take every distinct artist from the original playlist as a seed artist;
2. call `Plugins::LastMix::LFM->getSimilarArtists` for each seed, using its
   MusicBrainz ID when available and the normalized artist name as fallback;
3. retain artist name, MBID, Last.fm match value/rank, and which original seed
   artists endorsed it;
4. retain the per-source results for edge-local decisions and separately merge
   them into a collection-level fallback score;
5. freeze this profile for the run: added bridge tracks must not become new
   Last.fm seeds or otherwise create a feedback loop.

A small read-only LMS-side helper may export this artist map for the local
optimizer. It must export only artist names, MBIDs, match/rank values, and seed
support—not LastMix credentials. Partial Last.fm failures are retained in the
coverage report instead of invalidating successful seed lookups.

Classify potential bridges separately for every edge `A -> B`:

1. **Both-endpoint artist:** returned by Last.fm for both A's and B's artists.
2. **One-endpoint artist:** returned for either A's or B's artist.
3. **Collection fallback artist:** present in the aggregate original-playlist
   profile, but eligible only when the endpoint Last.fm artist pool itself is
   empty. It is not enabled merely because local tracks fail acoustic or repeat
   checks.
4. **Original-playlist artist** and then **Bliss-only fallback:** later options
   only when the same endpoint artist pool is empty.

Normalize artist names as `lms-blissmixer` does and use MBIDs to avoid name
collisions where possible. Treat Last.fm match values as soft ranking evidence,
not calibrated probabilities. Candidate generation uses only the original
playlist as the frozen source set, but semantic selection is edge-local. Added
bridges never become Last.fm seeds.

The direct database scan remains authoritative because the HTTP endpoints do
not return scores and are designed for candidate selection rather than route
optimization. The endpoint Last.fm lookups narrow and rerank acoustically
plausible bridges. The collection profile is a true empty-local-pool fallback
and never rescues a candidate with poor endpoint transition distances.

### 4.3 Bridge scoring and acceptance

For candidate `X`, prioritize the worst of the two new contextual legs:

```text
left = dynamic_cost(preceding_seed_window, X)
right = dynamic_cost(updated_seed_window_including_X, B)
worst_leg(X) = max(percentile(left), percentile(right))
```

Initial acoustic requirements:

- worst_leg(X) <= 0.70 on a frozen cross-context adaptive-percentile scale;
- percentile(left) + percentile(right) <= 1.30 on that scale;
- X is not already curated or selected as another bridge;
- its file and non-ignored database row are valid;
- the full output still satisfies artist=5 and album=10 look-back windows;
- duration and genre metadata are plausible for this collection;
- it passes an audition of both `A -> X` and `X -> B`.

Build the frozen percentile reference by evaluating every original curated
track as a candidate under every actual selected-route seed context, excluding
tracks already in that context. Do not normalize only against the 19 selected
legs: that would force the route's worst leg to percentile 1.0 and make
automatic bridge insertion self-triggering.

Within the candidates that pass those requirements, choose both-endpoint and
then one-endpoint artist evidence before acoustic tie-breakers. If the raw
endpoint artist pool is non-empty but no local library track passes, skip that
gap rather than using collection-wide evidence. Any fallback report must record
the empty-pool reason explicitly.

Default cap: **two bridges total and one per gap**. Produce the bridged result
as a separate candidate. Do not silently alter the curated-only result.

### 4.4 Explicit bridge-count option

Expose --bridge-count N in the one-command runner and bridge analyzer. When
present, it overrides the automatic maximum and requires exactly N additions,
with at most one insertion per original gap plus optional start/end slots.
Internal gaps are considered from hardest downward; endpoint slots are used
only when the requested count exceeds the number of internal gaps. Each
addition must:

- come from the edge endpoints' frozen Last.fm results when those results are
  non-empty;
- pass the same acoustic limits as automatic bridges;
- remain unique by file and artist/title identity;
- leave zero artist/album look-back violations in the complete output.

If exactly N acceptable tracks cannot be found, fail visibly rather than
silently returning fewer. Omitting the option retains conservative automatic
threshold mode; specifying zero explicitly produces a curated-only result.

## Phase 5: transition audition and constraint loop

Whole-track Version 2 features cannot determine whether the exact ending of A
fits the exact beginning of B. Listening is therefore part of the algorithm,
not merely a ceremonial final check.

### 5.1 Audit set

Audition, using the real Lyrion player and its normal ReplayGain/crossfade
configuration:

- the five highest-cost adjacent pairs;
- every bridge leg;
- the opening pair;
- the closing pair;
- any same-artist or same-album adjacency;
- a small random sample of low-cost pairs as a calibration control.

Rate each pair separately for:

- transition smoothness;
- next-track appropriateness;
- contribution to overall flow/variety.

These are distinct outcomes in the repository research and must not be reduced
to one score.

### 5.2 Optional boundary diagnostics

If `ffmpeg`/`ffprobe` is available, a one-shot helper may measure simple,
well-named boundary evidence from the final and initial 20-30 seconds:

- effective silence;
- fade/cold-end and fade/cold-start shape;
- short-window RMS or loudness jump;
- loudness slope.

Use this only as a tie-breaker or problem detector. Do not claim that a bounded
run of the whole-track Bliss analysis provides validated tempo, chroma, or
dispersion semantics; the design documents explicitly identify short-window
validity as an open issue.

### 5.3 Rerun with human constraints

When a pair fails audition, add a reproducible constraint rather than manually
shuffling the final file:

- forbid that exact adjacency;
- lock a preferred start or end;
- request a bridge for that gap;
- increase an artist/album separation penalty;
- choose the alternative orientation.

Rerun the optimizer and retain the constraint in `optimization-run.json`.
Normally one or two review rounds should be enough for 20 tracks.

## Phase 6: compare candidates and choose the final sequence

The report must compare the original order and every candidate using:

- total adjacent cost;
- mean, median, 90th-percentile, and maximum edge cost;
- local-to-global coherence: mean adjacent distance divided by mean distance
  across all curated pairs;
- same-artist and same-album adjacencies;
- the identity and score components of the five hardest transitions;
- route stability across optimization restarts;
- static-versus-learned rank disagreement, when applicable;
- listener ratings from the audit set;
- bridge count and the measured improvement for every bridge.

Because the curated membership is fixed, its order-independent diversity does
not change. This makes reduced local distance easier to interpret than it would
be for a generated playlist. For a bridged result, report metrics both with and
without the added tracks so extra length cannot create a misleading apparent
improvement.

Select the final sequence by listening evidence among solutions with strong
objective metrics, not by the smallest numeric cost alone.

## Phase 7: safe deployment and rollback

1. Write the chosen result first as a sibling candidate, for example
   `Example Playlist 2026 - optimized.m3u`.
2. Validate its BOM, header, three-line blocks, paths, counts, and readability.
3. Make Lyrion discover or reload the candidate and verify every entry resolves
   to the intended library track.
4. Play representative transitions from the candidate on the target player.
5. After explicit approval, create a timestamped backup of the original in the
   same playlist directory.
6. Upload the final content to a temporary file in that directory and rename it
   over the original, so replacement is atomic within the filesystem.
7. Re-read and hash the deployed file, confirm the expected track count, and
   retain the backup and run report for rollback.

For playlists originally created with LMS's `playlist save` command, also
verify the playlist row in `library.db` has non-null `timestamp` and `filesize`
values. LMS creates that row before its asynchronous M3U write, so those values
can remain null. The playlist scanner's changed-file SQL uses `!=` comparisons;
SQLite comparisons with null are not true, which makes later same-path changes
invisible to a playlist rescan.

Do not patch `library.db` directly. The supported recovery sequence is:

1. wait until LMS reports that no scan is active;
2. retain and hash a byte-identical staged copy outside scanner-visible file
   extensions;
3. run a playlist scan and verify the old playlist row is deleted;
4. wait for all scan post-processing to finish;
5. atomically restore the staged M3U to its original name;
6. run a second playlist scan so LMS imports it as a new file with populated
   `timestamp` and `filesize`;
7. verify the catalog order against the M3U and recheck the database metadata.

If the server is rebooted while external scan post-processing is active, first
verify that no `scanner.pl` process exists. If LMS still reports `_rescan=1`,
use its supported `abortscan` CLI command to clear the stale scan flag and any
queued scan task; do not update `metainformation` directly.

The scanner implementation governing this behavior is in
`Slim/Utils/Scanner/Local.pm`; the LMS playlist creation order is in
`Slim/Control/Commands.pm::playlistSaveCommand`.

No execution step should modify `bliss.db`, audio files, LMS preferences, the
learned matrix, or plugin binaries.

## Acceptance criteria

The task is complete only when all of the following hold:

- all 20 original curated tracks appear exactly once;
- every playlist path is readable and resolves uniquely in `TracksV2`;
- no unapproved track is added;
- no more than two bridge tracks are used by default, and each has a documented
  gap-reduction result and listening rationale;
- every bridge uses both-endpoint or one-endpoint LastMix evidence whenever the
  edge has an endpoint artist pool; any collection/Bliss fallback is allowed
  only for an empty endpoint pool and records that reason;
- the chosen order improves total, upper-tail, and maximum contextual cost over
  the original uncurated order under the declared primary metric;
- the five hardest transitions and every bridge leg pass actual-player review;
- no same-artist/album block remains unless deliberately accepted;
- the beginning, broad trajectory, and ending feel intentional;
- Lyrion loads and plays the deployed M3U correctly;
- the original playlist can be restored from a timestamped backup;
- the run is reproducible from its configuration and report.

No fixed percentage improvement is declared in advance. The original order is
uncurated, but metric scale and listener perception are still task-dependent.
The report should show the achieved percentages and let the audition gate decide
whether they are meaningful.

## Possible later productization

If this one-shot process proves useful, the smallest coherent product feature
would be a fixed-set ordering operation rather than another mix mode:

- a standalone `bliss-order` tool or `POST /api/order` in `bliss-mixer`;
- required input: an explicit list of tracks;
- optional input: locked endpoints, metric/matrix, bridge budget, forbidden
  adjacencies, and artist/album separation;
- output: ordered tracks plus edge scores and diagnostics;
- later integration with a versioned intro/outro sidecar for directional
  transition reranking.

The existing `PATH_INTERPOLATION.md` proposal is closely related: its midpoint
bridge search can supply candidates, while its TSP/nearest-neighbour/2-opt note
describes the basic fixed-set ordering problem. The one-shot run should retain
enough artifacts to evaluate that future design, but no plugin/API change is
needed now.

## Documentation and implementation evidence reviewed

All Markdown documentation in `bliss-similarity-design` was reviewed, with the
following pages most directly shaping this plan:

- `docs/mixing/overview.md`
- `docs/mixing/similarity-strategies.md`
- `docs/mixing/context-and-diversity.md`
- `docs/mixing/transitions.md`
- `docs/mixing/operations.md`
- `docs/evaluation/mixing-evaluation.md`
- `docs/research/mixing-research.md`
- `docs/research/comparison-systems.md`

The added local repositories were also reviewed:

- `D:\LMS\bliss-mixer`: `API.md`, database loading, static weighting,
  adaptive scoring, and learned-matrix loading;
- `D:\LMS\lms-blissmixer`: `ALGORITHMS.md`, `PATH_INTERPOLATION.md`,
  `METRIC_LEARNING.md`, plugin weight calculation, mixer requests, and Last.fm
  weighting integration;
- `D:\LMS\bliss-learner`: artifact format and learner behavior;
- `D:\LMS\LastMix`: CLI surface and Last.fm similar-track/artist lookup code.

The implementation review is important because it establishes that the active
Adaptive Weighting mode is a sliding centroid-based continuation strategy, not
a fixed-set ordering solver. The one-shot tool therefore applies that exact
directional scoring rule inside its own route search. The HTTP API does not
expose scores, and LastMix remains optional contextual evidence rather than the
acoustic sequence objective.
