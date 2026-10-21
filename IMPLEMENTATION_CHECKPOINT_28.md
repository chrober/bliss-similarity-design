# Implementation checkpoint 28: per-job variation and optional Last.fm evidence

**Date:** 2026-08-01  
**Native optimizer commit:** 9fd794ce0b0105e7f59ac0fb4a5b35c6e9d6b1f8  
**Plugin version:** 0.13.0  
**UX contract:** extras-job-editor-v14

## Outcome

Better Call Bliss now exposes per-job **Variation** and an optional repeatable
generation seed. A blank field derives a new seed from the unique job ID;
reusing a reported seed reproduces the native selection. Fixed-membership jobs
use the seed for movable-route search, while **Grow from these seeds** also uses
it for reproducible weighted membership sampling inside a bounded, high-quality
acoustic pool. Repeat windows remain hard constraints.

Optional Last.fm artist evidence is connected through the installed LastMix
plugin. Its enable switch and 1-100 target artist probability mirror
lms-blissmixer. Better Call Bliss queries every distinct artist in the complete
original playlist when the provider is healthy, prefers evidence local to the
transition endpoints, and uses the complete collection only as fallback.
Missing LastMix, offline access, malformed responses, and API failures never
fail playlist optimization. Last.fm errors 11, 16, and 29 open a per-job circuit
breaker so an outage or rate limit does not trigger calls for every remaining
artist. ListenBrainz remains later.

## Native contract and validation

The optional top-level selection request block contains:

    {
      "variation_percent": 25,
      "generation_seed": 123456789,
      "lastfm_artist_probability": 25
    }

Omitting the block retains the previous deterministic defaults. The native
gate passed 39 tests, cargo fmt --check, Clippy with warnings denied, and the
ARM64 workflow. Same-seed membership reproduction and different-seed variation
are covered by native tests.

## JSON payload correction

The first deployed plugin payload exposed a Perl/JSON scalar-type boundary:
schema-defined integers could be serialized as strings. A proposed recursive
normalizer was rejected during review because it would also convert legitimate
digit-only strings such as track IDs, titles, album names, or provider data.

The final implementation converts only fields declared numeric by the native
request schema and preserves JSON::XS boolean objects for boolean fields.
Jobs::_write_json remains a neutral serializer and does not mutate arbitrary
artifacts. Permanent Perl regressions verify that shortlist_limit is a JSON
integer, bridge/output flags are JSON booleans, and titles such as 1999 plus
albums such as 1984 remain strings.

## Live evidence

The corrected payload completed a live 3-to-25 seed-growth job on ARM64:

- native result validation passed;
- all 22 additions resolved to current LMS-local tracks;
- exact target, immutable seed membership, uniqueness, and all repeat-window
  proofs passed;
- Last.fm returned a partial state after one error 29 and the job continued
  with Bliss; and
- the reviewed 25-track copy was created and verified.

Eight recent seed-growth artifacts used eight different automatic seeds and
produced eight different selected-membership hashes. Reproducibility with an
explicit repeated seed remains covered by the deterministic native regression.

## Deployment boundary

The reviewed circuit-breaker and narrowly scoped serializer fix are retained in
the workspace for the next deployment. They were not loaded into the running
Lyrion process during this checkpoint because playback was active and the user
explicitly prohibited a service restart.
