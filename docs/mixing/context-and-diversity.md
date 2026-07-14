# Context, diversity, and exploration

**Status:** Living research and design proposal  
**Primary scope:** Session profiles, subset selection, and variety policy  
**Last reviewed:** 2026-07-14

## Group and context profiles

The same population-relative representation can describe an artist, album,
playlist, saved mood, multi-seed request, or recent session. Such profiles may
improve cold-start context and express what is unusual about the group rather
than merely its centroid.

A group must not, however, be assumed to have one meaningful centre. A playlist
or listening session can be deliberately multimodal, and even an album can
contain outliers. Early work on acoustic recommendation from song sets found
that minimum and median member distances outperformed a combined set model and
mean distance for its album-completion task [[4]](../research/mixing-research.md#m4). That result is not a
universal aggregation rule, but it makes a centroid-only design scientifically
unjustified.

The prototype should compare at least:

- a normalized centroid and a robust or trimmed centre;
- mean, median, and minimum distance from a candidate to individual seed
  tracks;
- a small cluster or mixture representation for demonstrably multimodal sets;
- population-relative variants of each representation, with shrinkage for
  small groups.

The profile artifact should identify the aggregation method, source population,
member count, dispersion, schema version, and any cluster assignment. A query
should be able to fall back to per-member distances when a centre has low
support or high dispersion.

Profiles derived from metadata must remain distinguishable from audio evidence.
Artist or album identity can improve coherence but can also create popularity,
catalog-size, and same-artist leakage. Experiments should report acoustic-only,
profile-only, and fused results, with regularization for small groups. User-made
moods or accepted/rejected tracks may eventually provide safer behavioral
context than assuming every artist or album is homogeneous. Research combining
acoustic evidence with cultural or situational context supports testing such
fusion [[16]](../research/mixing-research.md#m16) [[17]](../research/mixing-research.md#m17), but not collapsing context into an intrinsic
audio descriptor.

## Diversity and exploration policy

After relevance retrieval, a separate policy should decide how much redundancy
to allow. Existing artist shuffling and external recommendations partially
serve this purpose, but do not make the tradeoff explicit or measurable.

Candidate prototype policies include:

- maximal marginal relevance, balancing seed relevance against similarity to
  already selected tracks;
- cluster coverage or round-robin selection across relevant neighborhoods;
- relevance-aware submodular coverage, which has direct music-recommendation
  evidence [[7]](../research/mixing-research.md#m7);
- a determinantal-point-process-like objective if a simpler method proves
  insufficient; DPPs provide a principled relevance/diversity model, but the
  general method is not itself evidence of benefit for this library
  [[8]](../research/mixing-research.md#m8).

The policy should expose one conceptual variety control and preserve hard
filters. Its evaluation should measure relevance and diversity separately.
Ordering then operates on the selected set or on a sufficiently broad frontier;
it should not silently compensate for a relevance model that returned near
duplicates. Diversity is order-independent, whereas playlist coherence depends
on local adjacency relative to the variation of the full sequence
[[1]](../research/mixing-research.md#m1). Objective feature dispersion, local flow, and perceived variety
must therefore be reported separately; maximizing any one of them can make a
playlist worse on the others.
