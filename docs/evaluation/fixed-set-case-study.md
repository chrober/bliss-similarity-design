# Exploratory fixed-set sequencing case study

**Status:** Limited exploratory evidence from two private playlists; not a
general evaluation and not shipped functionality

**Primary scope:** Aggregate lessons from the 2025 and 2026 one-shot executions

**Last reviewed:** 2026-07-19

This page summarizes only non-sensitive aggregate observations from two
manually curated playlists. It intentionally omits machine addresses,
credentials, filesystem locations, playlist and catalog identifiers, hashes,
scanner transcripts, and track lists. The private execution reports and ignored
run artifacts are not publication dependencies.

The work exercised the [fixed-set sequencing and bridge
insertion](../mixing/fixed-set-sequencing.md) prototype. Two playlists are far
too little evidence for defaults, thresholds, or product claims; they are useful
as integration cases and as a source of sharper evaluation requirements.

## Aggregate observations

| Observation | 2025 playlist | 2026 playlist |
|---|---:|---:|
| Original curated members | 9 | 20 |
| Reorder-only result preserved every original exactly once | Yes | Yes |
| Artist and album look-back violations in retained result | 0 | 0 |
| Automatic bridge decision used for the base result | Not the evaluated extended case | 0 bridges because the declared gate was not crossed |
| Explicit extended variant | 8 additions | 20 additions |
| Last.fm collection-wide fallbacks in the retained extended result | 0 | 0 |
| Native effective-matrix parity checked | Yes | Yes |

For the nine-track case, the Adaptive reorder reduced the declared objective by
32.8%, mean whole-track continuation cost by 31.8%, and worst-leg cost by 35.3%
relative to the original order. Both orders already satisfied the repeat
constraints. This demonstrates that membership-preserving reordering can change
the proxy substantially; it does not establish an equally large perceptual
improvement.

For the twenty-track case, the final Adaptive run was an exact, repeat-safe
permutation and a clean rerun with the same seed and restart budget reproduced
the same order and objective. Its automatic bridge gate added no track. A
separate explicit-count variant deliberately doubled the playlist length to
exercise bridge selection, endpoint slots, serialization, and scanner handling;
that stress test is not evidence that a 1:1 bridge ratio is desirable.

Across both cases, the effective Adaptive diagonal computed by the Python
prototype matched the native mixer diagnostic within an absolute difference
below `1e-6` for a real multi-seed context. This supports the reproduced
inverse-variance and learned-matrix blend calculation. It does not validate the
entire route search, filters, candidate ranking, or every single-seed request
against the native executable.

The retained bridge additions used Last.fm evidence from both transition
endpoints or one endpoint; neither case needed collection-wide fallback. That
is evidence that the endpoint-local policy was operational on these libraries,
not that fallback will be rare elsewhere or that artist similarity guarantees
a good audible bridge.

## Lessons for the design

### Membership, ordering, and bridging must remain separate

The reorder-only outputs could be checked as exact permutations. Extended
outputs could then be checked as the original set plus an explicit number of
unique additions. Keeping those contracts separate made it possible to compare
an ordering change with a membership change and prevented “better flow” from
silently authorizing replacement tracks.

### Repeat windows are route constraints, not adjacency hints

An early twenty-track route used only immediate same-artist and same-album
penalties. It was superseded when the active look-back settings were applied as
hard constraints over the complete sequence. This is the clearest implementation
lesson from the executions: a visually plausible order is invalid if it does
not reproduce the configured repeat semantics.

### Automatic and explicit bridge modes answer different questions

The automatic gate could decide that no repair was justified, while an
explicit-count run could still construct a requested extended artifact under
the acoustic and repeat constraints. Automatic mode tests conservative repair;
explicit mode tests controlled expansion. Their results should never be pooled
as if they represented one policy.

### Context must be recomputed after insertion

The Adaptive implementation rescored the bridge from its preceding seed window
and then rescored the original right endpoint with the bridge included in the
new outgoing context. The executions showed that a bridge is not a static
two-edge lookup when continuation scoring depends on several preceding tracks.

### Deployment success is more than a valid M3U

Exact LMS-style entry serialization was necessary but not sufficient. Scanner
and catalog verification exposed a case in which the playlist row had to be
recreated through supported scanning behavior; its database ID consequently
changed. Stable identity must rest on the intended playlist and verified
ordered URLs, not a catalog row number.

## Evidence still missing

These executions do not satisfy the complete [fixed-set evaluation
contract](mixing-evaluation.md#fixed-set-sequencing-evaluation):

- only two playlists and one private library were used;
- the archived comparisons do not provide distributions over random controls;
- reversed-order controls and upper-tail metrics were not reported uniformly;
- the search heuristic was not compared with an exact solver or stronger
  optimizer;
- bridge thresholds and budgets were not estimated on held-out playlists;
- there was no blind, counterbalanced listener study; and
- whole-track descriptors cannot measure the actual outro-to-intro boundary.

The appropriate conclusion is therefore modest: the prototype is reproducible
enough to motivate a formal experiment and has already revealed useful
correctness and deployment requirements. Listening validation and broader
controls remain prerequisites for productization.
