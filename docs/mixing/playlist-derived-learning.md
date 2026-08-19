# Playlist-derived learning signals

**Status:** Living research and design proposal  
**Primary scope:** User-curated playlists, Better Call Bliss outputs, and lower-effort bliss-learner evidence  
**Last reviewed:** 2026-08-19

## Why playlists matter

The current `bliss-learner` workflow relies on explicit odd-one-out survey
rounds. Those rounds produce clean relative-similarity labels, but they cost
attention and many uniformly random questions are too obvious to teach the
model much.

Saved playlists contain another kind of evidence. They are not clean labels,
and they must not be treated as if every track in the playlist is simply
"similar" to every other track. A useful playlist may express mood, chronology,
contrast, narrative, party pacing, nostalgia, or practical listening habits.
Still, a user-curated playlist is valuable because it records tracks the
listener considered worth grouping, and sometimes worth ordering, in a real
context.

Better Call Bliss makes this evidence more concrete. It separates fixed-set
reordering, order-preserving extension, destination-constrained routing,
preview acceptance, copy creation, source overwrite, and player-queue output.
That separation gives the learner a chance to distinguish the source of a
signal instead of flattening all behavior into one implicit preference label.

## Signal classes

The learner should store playlist evidence as typed observations with
provenance, confidence, and context. The table below is a starting taxonomy.

| Signal | Example | What it may mean | Suggested confidence |
| --- | --- | --- | --- |
| Curated membership | A user-created playlist contains tracks A, B, and C | The tracks fit one user context | Low to medium |
| Curated adjacency | A user placed A followed by B | The transition or contrast may be acceptable | Medium |
| Curated order | The whole playlist has a deliberate sequence | The user may care about flow, energy arc, story, or chronology | Medium |
| Better Call Bliss preview acceptance | User accepts a generated reorder or extension | The proposed sequence was useful enough to keep | Medium |
| Better Call Bliss preview rejection | User reruns, discards, or changes parameters | The proposal or parameter choice was not satisfying | Medium |
| Generated bridge retention | Inserted bridge remains in a saved playlist over time | The addition may have been useful in that context | Medium, increasing with repeated evidence |
| Generated bridge removal | User removes an inserted bridge after saving | The local transition repair may have failed | Medium to high |
| Queue playback behavior | User sends a preview to a player and listens through it | The result may have fit the listening moment | Low to medium |
| Skip or abandonment | User skips or stops near a transition | Possible mismatch, interruption, familiarity, or section-boundary effect | Low unless repeated |
| Manual post-edit | User manually reorders, adds, or removes tracks | Strong contextual preference signal | Medium to high |

These observations should include the relevant playlist identity, track
identity, source application, timestamp, algorithm version, scoring strategy,
repeat-window settings, semantic-provider state, and whether the playlist was
human-curated, machine-generated, or mixed.

## Human-curated playlists versus generated playlists

Human-curated playlists are weak supervision. They can help the system choose
better survey questions, estimate low-confidence co-membership preferences, and
evaluate whether optimized routes improve over the original order.

Better Call Bliss-generated playlists are different. A generated playlist is
partly a product of the current metric, search strategy, and optional semantic
evidence. Feeding it directly back into `bliss-learner` as truth would create a
self-reinforcing loop:

```text
current metric -> generated playlist -> learner trains on generated playlist -> metric becomes more like itself
```

Therefore, generated playlists should not become training labels merely because
they exist. They become useful only when a human action supplies additional
evidence: accepting the preview, saving it, overwriting the source, listening
through it, editing it, removing bridge tracks, or repeatedly reusing it.

!!! warning "Avoid metric echo"
    Treat raw generated playlists as exposure records, not preference labels.
    Learn from the user's reaction to the generated result, not from the fact
    that the current system produced it.

## How this can reduce survey effort

Playlist-derived evidence should first make explicit survey rounds smarter, not
replace them outright. Useful applications include:

- choose familiar anchors from recently played or user-curated playlists;
- ask about plausible neighbors instead of arbitrary library extremes;
- prioritize transitions where the original playlist, Better Call Bliss route,
  and current learned matrix disagree;
- turn an accepted or edited bridge decision into a small contextual
  micro-question, such as "Which track fits better after A?";
- avoid asking about pairs already supported by repeated high-confidence
  behavior;
- keep an `unsure` or skipped question as question-quality evidence rather
  than a preference label.

This preserves the clean role of explicit triplets while using playlists to
find questions that are less tedious and more informative.

## Candidate learner use

`bliss-learner` currently consumes odd-one-out triplets over the fixed
23-feature Bliss representation. Playlist evidence should be a separate,
versioned input family before it is allowed to affect the matrix. A staged path
is safer than one large implicit-feedback model:

1. **Observation ledger:** store typed playlist and Better Call Bliss events
   without training on them.
2. **Active-query helper:** use the ledger only to choose better explicit
   survey questions.
3. **Weak pair weights:** derive low-confidence positive or negative pair
   hints only from repeated, well-contextualized behavior.
4. **Transition-specific experiment:** evaluate directional or context-bound
   models separately from the symmetric whole-track matrix.
5. **Validated blend:** allow playlist-derived evidence to influence runtime
   scoring only when held-out triplets and playlist-level evaluation improve.

The matrix artifact must continue to declare the exact feature schema,
normalization identity, model version, and evidence provenance. If playlist
evidence is used, the artifact should also record which signal families
contributed and with what confidence policy.

## Evaluation requirements

Playlist-derived learning is attractive precisely because it is easy to collect
too much ambiguous data. Evaluation therefore needs controls:

- hold out user-curated playlists from training and compare route quality;
- compare original, random, reversed, and Better Call Bliss optimized orders;
- evaluate accepted generated playlists separately from raw generated
  playlists;
- test whether survey effort decreases for the same held-out quality;
- report diversity and repetition separately from local transition smoothness;
- test whether generated-playlist feedback merely reproduces the old metric;
- retain Bliss-only and no-personalization baselines.

The goal is not to make the learner believe every saved playlist is perfect.
The goal is to spend fewer explicit questions on obvious cases and more effort
on the musical boundaries where the current representation, the user's taste,
and real playlist behavior disagree.
