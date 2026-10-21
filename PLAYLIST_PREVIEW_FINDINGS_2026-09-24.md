# Playlist preview findings - 24 September 2026

**Status:** Follow-up work identified from 14 read-only Better Call Bliss previews after the LMS restart at 13:33:21.  
**Scope:** Constraint correctness, duplicate prevention, gap-routing behavior, optional guidance, runtime, and preview diagnostics.  
**Related design:** [Better Call Bliss productization and implementation plan](BLISS_PLAYLIST_OPTIMIZER_IMPLEMENTATION_PLAN.md) and [Acoustic path finding for Better Call Bliss](ACOUSTIC_PATH_FINDING_DESIGN.md).  

## Evidence base

The reviewed runs used the `Alles ohne Hörbücher` candidate library, Adaptive scoring with three seeds and a 20% learned-matrix blend, artist/album/track windows of `5 / 10 / 100`, 50 restarts, Last.fm track/artist guidance of 75%, and play-count influence of -80 unless a row says otherwise.  

The review covered these source playlists:

- `Christoph's neue Liste` - 12 tracks;  
- `Fragile Strings Extended` - 15 tracks;  
- `GloomPsychRock` - 7 tracks; and  
- `California` - 23 tracks, deliberately assembled from songs whose titles contain a California variant rather than from a curated musical sequence.  

No reviewed job changed a saved playlist or player queue; all were previews.  

## Prioritized follow-up work

| Priority | Work item | Why it is needed | Completion evidence |
| --- | --- | --- | --- |
| P0 | Canonical music identity for all repeat and duplicate checks | The current unique-membership proof only compares LMS-file / Bliss-row identities. It can admit multiple local copies of the same recording. | A route cannot contain two entries with the same canonical recording key, even when LMS has separate files. |
| P0 | Shared ordered-repeat diagnosis and non-circular recommendations | Preserve-order repair and spacing feasibility currently disagree about the same anchor conflict. | Each mode reports the same fixed-anchor violation; a recommendation only names a mode that can solve it. |
| P1 | Multi-track, globally budgeted playlist-gap planner on the shared A-to-B engine | One conservative addition per selected gap cannot turn an arbitrary source sequence into a fluent journey. | The planner evaluates several valid path alternatives per gap, allocates one global budget, and preserves all required anchors. |
| P1 | Truthful per-gap preview diagnostics | A listener needs to know whether a gap was untouched, not selected, or searched but retained because no bridge improved it. | Preview and logs report considered, bridged, rejected, and untouched gaps with stable reasons. |
| P1 | Runtime budgets for large exact extensions | The `California` exact `+40` extension took 9m17, including 8m43 native routing. | Search effort has bounded cost, progress estimates, and regression measurements at realistic library sizes. |
| P2 | Explain and validate optional-guidance influence | Last.fm was fresh and working, but its soft target is not a guarantee for small bridge selections. | Artifacts distinguish supported candidate pools from guidance actually applied to chosen additions. |
| P2 | Regression corpus and listening evaluation | Synthetic constraints alone cannot establish that bridge choices sound good. | Reproducible fixtures cover canonical duplicates, repeat conflicts, arbitrary collections, no-beneficial bridges, guidance, and runtime. |

## P0 - canonical music identity

### Observed failure

`preview-1790252274-webh2ahqh` optimized and extended `California` by exactly 40 tracks. It selected **Aerosmith - Sweet Emotion** three times. Two selected LMS entries had distinct file identities but the same recording MBID, `ac8c46cb-d9b9-4e70-bda9-1ffc36e05eb6`.  

The route therefore satisfied the current technical proof, `unique_membership`, because every `bliss-row-*` value was different. It did not satisfy the listener's normal meaning of “do not repeat this track.”  

### Canonical-identity contract

Capture the following immutable keys when Better Call Bliss freezes the local candidate inventory. The optimizer must consume these keys for every route-membership and repeat-window decision.  

| Policy concern | Preferred canonical key | Explicit fallback |
| --- | --- | --- |
| Local file instance | LMS track ID / URL hash | normalized local path |
| Same recording / track repeat | MusicBrainz recording MBID | normalized primary artist + title, with duration only as a cautious tie-breaker |
| Album repeat | MusicBrainz release-group MBID; retain release MBID separately | normalized album artist + album title |
| Artist repeat | one or more MusicBrainz artist MBIDs | normalized artist credits |

This is deliberately broader than a recording-only patch. Recording, release/release-group, and artist identity must be available to the respective repeat policies without conflating their meanings. The release group is the preferred default for an album window because it represents the listener-facing album concept across editions; release identity remains available for a later, more specific policy.  

### Collaborations and artist-repeat policy

Track metadata can legitimately contain several artist MBIDs. A collaboration should not be reduced to one arbitrary artist when the user wants its members to participate in repeat protection.  

Expose a per-job **Artist-repeat policy** control with these choices:  

| Policy | Meaning |
| --- | --- |
| **Treat collaborations as one credit** | Compare the complete displayed/normalized collaboration credit. A Lou Reed solo track and a Lou Reed & Metallica track are distinct artist identities for repeat-window purposes. |
| **Count any shared credited artist** | Compare every track-level artist MBID. A Lou Reed & Metallica track conflicts with a Lou Reed solo track, a Metallica track, or another collaboration containing either artist. |

### Observed tag and Lyrion behavior

Two real MP3 files were inspected with ExifTool and compared with Lyrion's `artists` query for the corresponding track IDs. Contrary to the initial assumption, neither currently supplies Lyrion with multiple artist MBIDs or multiple track-artist contributors.  

| MP3 / LMS track | `ARTIST` tag | `TXXX:ARTISTS` | `TXXX:MusicBrainz Artist Id` | Lyrion track artists |
| --- | --- | --- | --- | --- |
| *Brandenburg Gate* - `2624633` | `Lou Reed & Metallica` | `Lou Reed` | `9d1ebcfe-4c15-4d18-95d3-d919898638a1` | one contributor, `Lou Reed & Metallica`, ID `186462` |
| *Beachcombing* - `2627072` | `Mark Knopfler and Emmylou Harris` | `Mark Knopfler` | `e49f69da-17d5-4c5c-bac0-dadcb0e588f5` | one contributor, `Mark Knopfler and Emmylou Harris`, ID `186609` |

Both files also have an album-artist MBID equal to the single artist MBID shown above. The `ARTISTS` user-defined tag does not produce extra Lyrion contributor rows for these files. Therefore, the desired “Count any shared credited artist” behavior cannot infer a separate Metallica or Emmylou Harris identity from the current Lyrion database for these examples.  

Lyrion itself supports multiple artists structurally: `contributors` are linked to `tracks` through `contributor_track`, and `Track->artists` returns all `ARTIST` and `TRACKARTIST` rows. During import, `Slim::Schema::Contributor->add` splits both the artist tag and the corresponding `MUSICBRAINZ_*_ARTIST_ID` tag. It pairs them positionally only when the two lists have equal counts; otherwise it deliberately drops ambiguous MBIDs rather than assign one to the wrong name. The current files entered the database as a single composite credit, so there is only one row to return.  

The candidate-inventory builder must therefore obtain the complete Lyrion `Track->artists` contributor set, not merely `tracks.primary_artist` or one `artist_mbid`. For tracks whose current database representation is a composite-only credit, the user-facing policy needs an explicit lower-confidence fallback: parse the displayed credit into collaboration tokens where it is unambiguous, label that provenance in diagnostics, and never fabricate MBIDs. Correctly tagged multi-value artist metadata plus a rescan remains the high-confidence solution.  

The second mode must use the complete resolved track-level artist identity set, not album-artist metadata and not a lossy single `artist_mbid` field. When neither Lyrion contributor rows nor tags supply separable artists, it may apply the documented normalized-credit fallback. Generic compilation labels such as `Various Artists` must not create a false conflict with every compilation track.  

### Upstream Lyrion resolution path

[slimserver issue #1277](https://github.com/LMS-Community/slimserver/issues/1277) describes the underlying multiple-`MUSICBRAINZ_ARTISTID` / `MUSICBRAINZ_ALBUMARTISTID` problem. Its original symptom is consistent with the current composite-only rows: a collaboration display credit and the individual contributors are not represented independently enough for correct browsing and policy decisions.  

Draft [slimserver PR #1576](https://github.com/LMS-Community/slimserver/pull/1576), **Display artist**, is directly relevant. Its stated design preserves the human-readable display credit in a separate `contributor_display` structure while relating it to the individual contributors. It also introduces an opt-in `usePluralArtistTags` scan preference so plural `ARTISTS` / `ALBUMARTISTS` data can become the authoritative individual-contributor source.  

If that PR is merged and deployed, Better Call Bliss should:  

1. keep the display credit only for user-visible reports;  
2. obtain artist-repeat identities from the underlying individual contributor rows and their MBIDs;  
3. prefer that high-confidence set over any string parsing; and  
4. retain the composite-credit fallback only for older servers, disabled plural-tag support, or tracks whose plural data is genuinely absent.  

The two inspected files still need a post-upgrade validation. Their currently visible `ARTISTS` values contain only the first artist, so neither the new schema nor the preference can infer Metallica or Emmylou Harris unless the on-disk plural tags actually provide those individual values. After enabling the upstream option and rescanning, verify that Lyrion returns separate Lou Reed/Metallica and Mark Knopfler/Emmylou Harris contributor rows for the two track IDs before treating the data as high-confidence.  

The selected policy applies consistently to source anchors, immutable queue history, destinations, candidate additions, and every generated route member. Diagnostics must name the shared artist identity that caused a rejection.  

### Required behavior

- `track` windows use canonical recording identity, not merely the selected LMS file or Bliss row;  
- `album` windows use the selected release-group/release policy;  
- `artist` windows use canonical artist identities under the selected collaboration policy;  
- all source, history, destination, candidate, and selected-addition identities are resolved by the same implementation;  
- reports state which key was used and whether it was an MBID or a lower-confidence fallback; and  
- missing or ambiguous MBIDs never block a Bliss-only route; they lower identity confidence and invoke the documented fallback.  

## P0 - ordered-repeat diagnosis and recommendation loop

### Observed failure

For `Christoph's neue Liste`, `preview-1790249930-web730tj9` correctly found that preserving the source order violates the artist window: **Ten Years After** occurs at source positions 9 and 12 with an artist window of 5. It recommended **Add spacing tracks as needed** or optimized source order.  

The immediately following preserved-order spacing preview, `preview-1790249956-webcox7qr`, said the source was already feasible and recommended **Improve difficult transitions** again. This created a circular recommendation.  

### Root cause and required behavior

The difficult-transition path inspects the actual ordered anchors. The spacing preflight currently applies an aggregate/count-oriented feasibility shortcut, which cannot see that fixed positions 9 and 12 are too close.  

Replace these separate checks with one shared ordered-repeat diagnosis that returns:  

- existing fixed-anchor violations by artist, album, and canonical track identity;  
- whether source reordering alone can resolve them;  
- whether preserved-order spacing can resolve them;  
- the minimum required spacer placements or a clear infeasibility reason; and  
- mode-specific, non-circular recommendations.  

Expected user-facing outcomes:  

- **Preserve + Improve difficult transitions:** explain that this mode cannot repair an existing source-anchor repeat conflict; recommend preserved-order spacing only when it is feasible, otherwise recommend optimized source order.  
- **Preserve + Add spacing tracks as needed:** calculate and insert the required spacers; do not reject the job as already feasible when an ordered-anchor violation exists.  
- **Optimize + Add spacing tracks as needed:** if reordering alone resolves all windows, recommend optimized source order with no additions rather than returning the user to preserve-order repair.  

## P1 - California and preserved-order gap repair

### What the runs show

`California` is intentionally not a musical programme. It has varied genres and an arbitrary source order. With **Preserve source order and fill gaps**, Better Call Bliss must keep all 23 originals as immutable anchors; neither the shared word in their titles nor the user's expectation of a coherent journey becomes an optimizer input.  

The automatic runs behaved as follows:  

| Trigger percentile | Source gaps considered difficult | Accepted additions |
| ---: | ---: | ---: |
| 50% | 2 of 22 | 1 |
| 25% | 4 of 22 | 3 |
| 10% | 7 of 22 | 5 |

The direct Beth Hart & Joe Bonamassa to Led Zeppelin transition had a high source-relative percentile of about 85.5%, but was retained because no candidate bridge passed the cautious “meaningfully better than direct” acceptance rule. This is a valid conservative outcome, not evidence that the bridge search silently failed.  

### Product implication

**Improve difficult transitions** should remain a conservative repair mode. It is not the same as “make an arbitrary collection coherent.”  

The missing user capability is: preserve every original anchor while building multi-track A-to-B paths for selected or all difficult gaps. It must use the extracted shared anchored-path kernel, but a separate outer planner must:  

- request several valid alternatives per gap and permitted bridge depth;  
- allocate one global addition budget across all gaps;  
- coordinate canonical repeat state across paths and source anchors;  
- retain direct gaps when no candidate path improves them; and  
- report why each gap was bridged, retained, or skipped.  

This is the prerequisite for both **Fill every gap with N bridge tracks** and a future **bridge difficult gaps as needed** mode.  

## P1 - performance and progress

The exact `California +40` extension completed correctly but took 9m17 end to end, with 8m43 in native selection/routing. Smaller automatic jobs took roughly 23-61 seconds; source capture, candidate inventory preparation, and optional semantic-evidence collection accounted for a material part of that time.  

Follow-up requirements:  

- preserve the single, continuous live-progress view across Perl-side preparation and native optimization;  
- publish cost-aware phases and an estimated search scope for large exact extensions;  
- bound Fast, Balanced, and Thorough effort profiles with deterministic budgets;  
- benchmark 64k and synthetic 200k local libraries; and  
- keep CPU-bound independent work parallel while retaining deterministic tie-breaking.  

## P2 - optional guidance interpretation

All reviewed completed jobs had fresh Last.fm provider state with no request failures. Guidance is therefore not absent because the integration was offline.  

Small automatic jobs selected between zero and three additions with Last.fm artist support; the `California +40` extension selected eight additions with similar-track support and 35 with similar-artist support. Play-count guidance was attached to every selected addition in these runs.  

The 75% Last.fm controls are soft candidate-pool targets, not a promise that 75% of a short final result will carry Last.fm evidence. Adjacent acoustic quality, hard repeat constraints, and the chosen route remain primary.  

Follow-up work:  

- report separately: eligible candidates, candidates supported by each guidance channel, candidates admitted to the final shortlist, and selected additions with an actual positive or negative guidance contribution;  
- document the controls as soft influence targets; and  
- evaluate whether a stronger configurable quota is desirable without letting optional evidence overrule Bliss-first route quality.  

## Regression and listening-evaluation set

Add reproducible fixtures and review cases for:  

1. two distinct LMS files with the same recording MBID;  
2. duplicate title/artist tracks with no MBID, exercising the fallback;  
3. repeated artist and album anchors in a preserved order;  
4. an arbitrary cross-genre source collection similar to `California`;  
5. a high-risk direct transition where no bridge improves the route;  
6. a gap where a multi-track route is needed;  
7. Last.fm-supported and unsupported candidate pools; and  
8. exact extensions at realistic 64k and synthetic 200k-library scale.  

Every fixture should assert route membership, canonical repeat compliance, stable diagnostics, and bounded runtime. Listening reviews should remain separate evidence: they assess whether the model's accepted route sounds better than the direct transition rather than merely proving that a constraint was met.  
