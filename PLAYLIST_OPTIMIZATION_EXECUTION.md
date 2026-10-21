# Example Playlist 2026 optimization execution

## Adaptive correction, current deployment

The active server setting is `use_adaptive_weights=1`. The earlier static/fused
route revisions recorded below are retained as history but are superseded. The
current optimizer mirrors bliss-mixer at every position: the strict final three
tracks form the seed window, the ideal point is their raw-feature mean, inverse
population-variance weights are normalized to sum to 23, and the server's learned
matrix is blended at 20 percent. The first transition uses the single-seed
learned-matrix behavior. Static sliders 20/28/3/49 are captured for provenance
but do not influence this adaptive run.

The shipped Windows `bliss-mixer.exe` was copied from the Pi and run locally
against the frozen database and learned matrix. For a real three-track seed
context, its 23 effective diagonal weights match the Python implementation with
maximum absolute difference `6.271448818040426e-07`. The binary SHA-256 is
`7f0fc393ae6ae3f3eb099524f9d5ab63ec80b1a3a93a89bf7fb2c6fa08a1bbe3`;
the complete comparison is frozen as `adaptive-binary-parity.json`.

### Base playlist

- Live path: `/mnt/usbHD/LMS/playlists/Example Playlist 2026.m3u`
- SHA-256: `fe6f17853e8097baeb4b9bec214cd608002f04bd8ab624deab8140eae81f8cfa`
- Lyrion catalog ID: 723633
- Tracks / unique tracks: 20 / 20
- Exact permutation of the original curated set: yes
- Artist / album look-back violations: 0 / 0
- Adaptive objective: 5.9382140821902
- Mean / worst dynamic transition: 0.26304858427650535 / 0.4701454904682993
- Worst contextual bridge percentile: 0.5169230769230769
- Automatic bridges: 0 (`not-needed`, below the 0.70 threshold)
- Clean final-code 250-restart rerun: byte-identical order and objective
- Recoverable backup: `/mnt/usbHD/LMS/playlists/Example Playlist 2026.pre-adaptive-20260717T195000Z.m3u.bak`
- Backup SHA-256: `b5cd99f306bfb4ab90e25709218453b13b0fb00a432d795551573933524884af`

Adaptive order:

1. Cream — Tales of Brave Ulysses
2. Wishbone Ash — Rock 'n Roll Widow
3. Grateful Dead — The Music Never Stopped
4. Ten Years After — It's Getting Harder
5. The Answer — Gone Too Long (acoustic version)
6. The Susan Tedeschi Band — Gonna Write Him a Letter
7. Night Beats — Her Cold Cold Heart
8. Early James — Blue Pill Blues
9. Rival Sons — Feral Roots
10. Ten Years After — I'd Love to Change the World
11. Wolfmother — Vagabond
12. Warren Haynes — Take a Bullet
13. The Black Keys — So He Won't Break
14. Fleetwood Mac — The Green Manalishi (With the Two-Pronged Crown)
15. Thomas Naïm — Slidance
16. The Answer — Strange Kinda' Nothing
17. Jared James Nichols — What Love
18. Blues Pills — Burned Out
19. Warren Haynes feat. Railroad Earth — Coal Tattoo
20. Rival Sons — Shooting Stars

### Extended playlist

- Live path: `/mnt/usbHD/LMS/playlists/Example Playlist 2026 Extended.m3u`
- SHA-256: `108b85260eb60da5306177fb5e9aa4a1c6868772a0000b3da6aa1a239d2f5358`
- Lyrion catalog ID: 723634
- Total / unique / additional tracks: 40 / 40 / 20
- All original curated tracks retained: yes
- Artist / album look-back violations: 0 / 0
- Last.fm evidence: 20 edge-one, 0 collection fallbacks
- Maximum contextual bridge leg / two-leg total: 0.5784615384615385 / 1.0246153846153847
- Recoverable backup: `/mnt/usbHD/LMS/playlists/Example Playlist 2026 Extended.pre-adaptive-20260717T195000Z.m3u.bak`
- Backup SHA-256: `debfe68d76d5ec4c2bc72f061369e4952c7120d841f2ab33d036ad5d420267d5`

Every entry in both files is an exact Lyrion-style `#EXTURL`, title-only
`#EXTINF`, and raw-path block. A supported playlists-only scan handled both
files as changed, completed normally, and left `_rescan=0`. LMS's indexed URLs
match both deployed M3Us position-for-position.

## Initial outcome, superseded by constrained revision

The optimized playlist was deployed on 2026-07-17 to:

    /mnt/usbHD/LMS/playlists/Example Playlist 2026.m3u

The final file is an exact permutation of the 20 unique paths in the original curated
playlist. No bridge track was inserted because the largest optimized transition was below
the predeclared bridge threshold.

- Original SHA-256: c11d3c137620d5b3a28fd0437a44295289a69cbb9070d0e69e367d7eee4a83cc
- Final SHA-256: bcfb592a09e5162487c2fc96c035ea707a4841eb5e688ec7504a834dd162f40c
- Recoverable backup:
  /mnt/usbHD/LMS/playlists/Example Playlist 2026.pre-optimization-20260717T122819Z.m3u.bak
- Backup SHA-256: c11d3c137620d5b3a28fd0437a44295289a69cbb9070d0e69e367d7eee4a83cc
- Lyrion playlist ID after indexing: 723622

The candidate was validated locally and on the server: 20 entries, 20 unique paths, and all
20 referenced audio files exist. The bridge-stage file includes the deterministic comment
marker #PLAYLIST-OPTIMIZER:fixed-set-v1. Lyrion continued to serve its previously indexed
order after same-path replacement and rescans; no further cache manipulation was attempted,
and the server was rebooted by the user.

## Constrained revision, deployed after reboot

The initial route used only immediate adjacency penalties and therefore did not implement
the active lms-blissmixer windows. The revised optimizer treats artist=5 and album=10 as hard
constraints across the complete sequence. The track=100 setting is satisfied because the
20 curated file paths are unique.

- Final candidate SHA-256:
  285cc0b4301b38b2cb1ac0f855b97ff98ef4973f4f843e714454c56aae633225
- Policy marker: #PLAYLIST-OPTIMIZER:fixed-set-v2;artist=5;album=10
- Live server path: /mnt/usbHD/LMS/playlists/Example Playlist 2026.m3u
- Superseded-route backup:
  /mnt/usbHD/LMS/playlists/Example Playlist 2026.pre-repeat-window-revision-20260717T131721Z.m3u.bak
- Superseded-route backup SHA-256:
  bcfb592a09e5162487c2fc96c035ea707a4841eb5e688ec7504a834dd162f40c
- Curated tracks: 20
- Repeat-window violations: 0
- Fused objective: 5.198942
- Mean transition: 0.223837
- Worst transition: 0.473016
- Automatic bridges: 0; the worst gap remains below 0.70

The repeat-safe bytes are deployed and server-validated. The one standard playlist rescan
reported zero changed files for the pre-existing path, and Lyrion continued to expose its
older indexed order. Per user instruction no cache workaround was attempted; the on-disk
playlist will be picked up by a subsequent normal server reload.

Revised order:

1. Rival Sons — Shooting Stars
2. Blues Pills — Burned Out
3. The Answer — Strange Kinda' Nothing
4. Night Beats — Her Cold Cold Heart
5. Cream — Tales of Brave Ulysses
6. Ten Years After — It's Getting Harder
7. Warren Haynes feat. Railroad Earth — Coal Tattoo
8. The Black Keys — So He Won't Break
9. Fleetwood Mac — The Green Manalishi (With the Two-Pronged Crown)
10. Warren Haynes — Take a Bullet
11. Wolfmother — Vagabond
12. Early James — Blue Pill Blues
13. The Susan Tedeschi Band — Gonna Write Him a Letter
14. Grateful Dead — The Music Never Stopped
15. Wishbone Ash — Rock 'n Roll Widow
16. Thomas Naïm — Slidance
17. Jared James Nichols — What Love
18. Rival Sons — Feral Roots
19. Ten Years After — I'd Love to Change the World
20. The Answer — Gone Too Long (acoustic version)

The exact-count option was exercised separately with --bridge-count 1. It produced a
21-track, zero-violation candidate by inserting Free — Wishing Well between Jared James
Nichols and Rival Sons. That example is retained for reproducibility but is not the automatic
deployment candidate. Its SHA-256 is
88ec95771ff05e4c44d5fe20f1cce9e408682d39f7a0e87866aaf65b447f837a.

## Playlist scanner diagnosis and catalog repair

A later diagnostic deployment added the harmless marker
`#PLAYLIST-REVISION:scanner-debug-20260717T142718Z` while preserving all 20
optimized paths. The resulting live M3U is 4,962 bytes with SHA-256
`b5cd99f306bfb4ab90e25709218453b13b0fb00a432d795551573933524884af`.
Its pre-change backup is:

    /mnt/usbHD/LMS/playlists/Example Playlist 2026.pre-debug-scan-change-20260717T142718Z.m3u.bak

With `scan.scanner` debug logging enabled, the playlist scan discovered both
Example Playlist files but classified only Extended as changed. A read-only inspection
of `/mnt/mmcblk0p2/tce/slimserver/Cache/library.db` showed the reason:

- base playlist ID 723622: `content_type=ssp`, `timestamp=NULL`,
  `filesize=NULL`;
- Extended playlist ID 723627: `content_type=ssp`, timestamp populated,
  filesize 7,886.

The installed server code matches `D:\LMS\slimserver`. Its changed-file query
in `Slim/Utils/Scanner/Local.pm` compares `scanned_files.timestamp !=
tracks.timestamp OR scanned_files.filesize != tracks.filesize`. SQLite null
comparisons are not true, so a row with both values null is permanently omitted
from the changed set. `playlistSaveCommand` in `Slim/Control/Commands.pm`
explains the state: it creates the `ssp` row before scheduling the initial M3U
write and does not populate file metadata at that point.

The repair deliberately avoids direct database mutation. The verified M3U is
temporarily staged outside scanner visibility, a playlist scan removes the
invalid catalog row, the exact bytes are restored, and a second playlist scan
imports it as a new file. `tools/inspect_lms_playlist_db.py` provides the
read-only metadata check used before and after this procedure.

The fresh import completed its playlist phase and created base playlist ID
723631 before the server rebooted during later scan post-processing. The reboot
left `_rescan=1` even though no `scanner.pl` process existed. Lyrion's supported
`abortscan` CLI command cleared that stale state and the scan queue; no database
row was edited directly. Final verification then showed:

- `_rescan=0`;
- base playlist ID 723631, `timestamp=1784298504`, `filesize=4962`,
  `content_type=ssp`;
- 20 indexed tracks and 20 expected M3U paths;
- exact positional match between every indexed URL and the revised M3U;
- live M3U SHA-256
  `b5cd99f306bfb4ab90e25709218453b13b0fb00a432d795551573933524884af`;
- no staging file left behind.

## Extended 40-track playlist, corrected edge-local/LMS-block revision

The separate Example Playlist 2026 Extended request uses --bridge-count 20. It retains all 20
curated tracks and inserts exactly 20 additional tracks. The corrected revision uses 18
internal gaps plus the start and end slots because one internal edge had Last.fm endpoint
evidence but no acceptable local library track; collection-wide evidence was therefore not
allowed to replace it.

- Output SHA-256: debfe68d76d5ec4c2bc72f061369e4952c7120d841f2ab33d036ad5d420267d5
- Live server path: /mnt/usbHD/LMS/playlists/Example Playlist 2026 Extended.m3u
- Lyrion playlist ID after corrected indexing: 723632
- Total / unique tracks: 40 / 40
- Additional tracks: 20
- Repeat-window violations: 0
- Both-endpoint Last.fm artist evidence: 2 additions
- One-endpoint Last.fm artist evidence: 18 additions
- Collection-wide fallbacks: 0
- Maximum individual bridge leg: 0.627513
- Maximum two-leg total: 1.211640
- Every one of the 40 entries is an exact Lyrion-style `#EXTURL`, title-only
  `#EXTINF`, and raw path block
- Automatic 20-track playlist remains unchanged by this separate artifact
- Superseded Extended backup:
  /mnt/usbHD/LMS/playlists/Example Playlist 2026 Extended.pre-lms-block-edge-local-20260717T190247Z.m3u.bak
- Superseded Extended SHA-256: ebe0611fa2b37475452afd3a255ec876cfd7076fb3bc50eaa71059e84741c13f

The debug scanner log recorded both changed and new handling for this path. JSON-RPC returned
40 tracks, and their decoded URL sequence exactly matched the deployed M3U.

## Initial deployed order

1. Thomas Naïm — Slidance
2. Wishbone Ash — Rock 'n Roll Widow
3. Grateful Dead — The Music Never Stopped
4. The Susan Tedeschi Band — Gonna Write Him a Letter
5. Early James — Blue Pill Blues
6. Wolfmother — Vagabond
7. Warren Haynes — Take a Bullet
8. Fleetwood Mac — The Green Manalishi (With the Two-Pronged Crown)
9. The Black Keys — So He Won't Break
10. Warren Haynes feat. Railroad Earth — Coal Tattoo
11. Ten Years After — It's Getting Harder
12. Cream — Tales of Brave Ulysses
13. Jared James Nichols — What Love
14. Night Beats — Her Cold Cold Heart
15. The Answer — Strange Kinda' Nothing
16. Rival Sons — Feral Roots
17. Ten Years After — I'd Love to Change the World
18. The Answer — Gone Too Long (acoustic version)
19. Blues Pills — Burned Out
20. Rival Sons — Shooting Stars

## Superseded static/fused inputs and policy

- bliss.db SHA-256:
  96cdd6f8cd060567cacfeed614b0232e95e2aeafc22178545983bdf2be815d93
- learned_matrix.json SHA-256:
  71e26b00faa9bb2709f0f6e8b66ae6fc27b33edc239d2ff11fdb74393cf7eb6e
- Static weights: tempo 20, timbre 28, loudness 3, chroma 49
- Learned-distance blend: 20 percent
- Search seed: 20260717
- Restarts: 250
- Initial objective: transition sum plus twice the maximum transition, with adjacent artist
  and album repetition penalties
- Revised hard windows: artist 5, album 10, track uniqueness 100
- Candidate selection: use the energy-arc route only if it remains within 8 percent of the
  fused route objective and reduces arc error by at least 10 percent
- Bridge threshold: 0.70 fused empirical-percentile cost
- Maximum bridges: 2

These numeric values were re-read through LMS's supported `pref` API and frozen in
`lms-blissmixer-settings.json` (SHA-256
4a5a82f6f53eb87fdf82eadc9f644f6661f9cd070e2da413359fbe1c87399524).
The snapshot also records adaptive weighting enabled, strict three-seed order, Last.fm
weighting enabled at 60 percent, and repeat windows 5/10/100. The fixed-set route objective
uses the configured static sliders and 20-percent learned blend as its reproducible pairwise
distance model. That was the superseded methodology; the current deployment at the top of
this document instead reproduces adaptive weighting as the primary contextual route metric.

The database and learned matrix were copied while no analyzer or mixer process was using
bliss.db. The SQLite snapshot passed PRAGMA quick_check, all 20 playlist paths matched one
usable TracksV2 row, and the learned matrix was finite and symmetric.

## Superseded static/fused candidate results

| Candidate | Fused objective | Mean leg | Worst leg | Energy-arc error |
|---|---:|---:|---:|---:|
| Original order | 9.186772 | 0.362796 | 0.596825 | 4.090081 |
| Static | 5.357672 | 0.220496 | 0.584127 | 2.561741 |
| Learned | 9.400000 | 0.416541 | 0.742857 | 3.793320 |
| Fused | 5.166138 | 0.222111 | 0.473016 | 4.177665 |
| Energy arc, selected | 5.173545 | 0.222501 | 0.473016 | 3.036370 |

Compared with the original order, the selected route reduces mean fused transition cost by
38.7 percent and the worst transition by 20.7 percent. Its fused objective is only 0.14
percent above the pure fused optimum while its energy-arc error is 27.3 percent lower.

These are model-based results, not a claim of human listening verification.

## Full-playlist similar-artist profile

The artist input was frozen before bridge evaluation and contains all 17 distinct artists
from the original playlist. LastMix does not require a Last.fm user login for this lookup.
It still supplies an application key: LastMix::LFM::aid() reads plugin id2 and removes its
UUID hyphens. The profile tool reproduces that behavior and never writes the key to output.

- Successful Last.fm artist.getSimilar lookups: 17 of 17
- Distinct similar artists in the frozen profile: 356
- Query limit: 25 per source artist
- Autocorrect: enabled

The worst selected gap is 0.473016, below the 0.70 threshold, so no bridge search was allowed
to add a song. This conservative gate avoids diluting a curated collection when reordering
alone has already removed the transition cliff. If a future run crosses the threshold,
artists supported by both endpoints are preferred, then artists supported by one endpoint.
The collection profile is eligible only when the raw endpoint Last.fm artist pool is empty.

## Reproduction

Run the regression suite:

    python -m unittest discover -s tests -v

Create fresh outputs and refresh Last.fm through the LastMix metadata:

    python tools/capture_lms_blissmixer_settings.py --server http://192.168.1.111:9000 --output INPUT/lms-blissmixer-settings.json
    python tools/run_playlist_optimization.py --db INPUT/bliss.db --playlist "INPUT/Example Playlist 2026.m3u" --matrix INPUT/learned_matrix.json --lastmix-install D:/LMS/LastMix/install.xml --settings INPUT/lms-blissmixer-settings.json --output runs/example-playlist-2026-rerun

For the same artist evidence used in this execution, reuse the frozen profile instead of
querying a changing external service:

    python tools/run_playlist_optimization.py --db INPUT/bliss.db --playlist "INPUT/Example Playlist 2026.m3u" --matrix INPUT/learned_matrix.json --artist-profile runs/example-playlist-2026-20260717-constrained/lastfm-artist-profile.json --settings INPUT/lms-blissmixer-settings.json --output runs/example-playlist-2026-rerun

The settings snapshot supplies the active artist=5 and album=10 windows. Override them
explicitly with --no-repeat-artist and --no-repeat-album only when reproducing another
declared policy.

To request an exact number of extra tracks rather than automatic threshold mode:

    python tools/run_playlist_optimization.py --db INPUT/bliss.db --playlist "INPUT/Example Playlist 2026.m3u" --matrix INPUT/learned_matrix.json --artist-profile runs/example-playlist-2026-20260717-constrained/lastfm-artist-profile.json --settings INPUT/lms-blissmixer-settings.json --output runs/example-playlist-2026-plus-1 --bridge-count 1

The current Extended result uses the same adaptive route and `--bridge-count 20`; its
artifacts are in `runs/example-playlist-2026-20260717-adaptive-extended`.

The exact inputs are intentionally not committed: bliss.db is a large live-library snapshot,
and the playlist and learned matrix remain server-owned state. Their hashes above make a
rerun fail visibly rather than silently using changed evidence.

Important run artifacts:

- runs/example-playlist-2026-20260717-adaptive/run.json — dynamic candidates and metrics
- runs/example-playlist-2026-20260717-adaptive/dynamic-transitions.csv — exact sliding contexts
- runs/example-playlist-2026-20260717-adaptive/adaptive-binary-parity.json — shipped-binary check
- runs/example-playlist-2026-20260717-adaptive/bridge-analysis.json — automatic no-bridge decision
- runs/example-playlist-2026-20260717-adaptive/selected-with-bridges.m3u — current base bytes
- runs/example-playlist-2026-20260717-adaptive-extended/bridge-analysis.json — 20 contextual additions
- runs/example-playlist-2026-20260717-adaptive-extended/selected-with-bridges.m3u — current Extended bytes

The remaining directories below preserve superseded static/fused experiments:

- runs/example-playlist-2026-20260717/run.json — parameters, every candidate order, and metrics
- runs/example-playlist-2026-20260717/pairwise.csv — raw pair distances and fused percentiles
- runs/example-playlist-2026-20260717/lastfm-artist-profile.json — frozen 17-source profile
- runs/example-playlist-2026-20260717/bridge-analysis.json — threshold decision and largest gaps
- runs/example-playlist-2026-20260717/selected-with-bridges.m3u — deployed bytes
- runs/example-playlist-2026-20260717-constrained/run.json — constrained candidate metrics
- runs/example-playlist-2026-20260717-constrained/selected-with-bridges.m3u — revised candidate
- runs/example-playlist-2026-20260717-constrained-plus-1/bridge-analysis.json — exact-count example
- runs/example-playlist-2026-20260717-extended/bridge-analysis.json — all 20 Extended additions
- runs/example-playlist-2026-20260717-extended/selected-with-bridges.m3u — superseded Extended bytes
- runs/example-playlist-2026-20260717-constrained-v2/lms-blissmixer-settings.json - frozen live preferences
- runs/example-playlist-2026-20260717-extended-v2/bridge-analysis.json - edge-local evidence per addition
- runs/example-playlist-2026-20260717-extended-v2/selected-with-bridges.m3u - corrected deployed Extended bytes

## Rollback

To restore the immediately preceding repeat-safe base and Extended revisions:

    cp -p -- "/mnt/usbHD/LMS/playlists/Example Playlist 2026.pre-adaptive-20260717T195000Z.m3u.bak" "/mnt/usbHD/LMS/playlists/Example Playlist 2026.m3u"
    cp -p -- "/mnt/usbHD/LMS/playlists/Example Playlist 2026 Extended.pre-adaptive-20260717T195000Z.m3u.bak" "/mnt/usbHD/LMS/playlists/Example Playlist 2026 Extended.m3u"

To restore the superseded first optimized route:

    cp -p -- "/mnt/usbHD/LMS/playlists/Example Playlist 2026.pre-repeat-window-revision-20260717T131721Z.m3u.bak" "/mnt/usbHD/LMS/playlists/Example Playlist 2026.m3u"

To restore the untouched original curated order instead:

    cp -p -- "/mnt/usbHD/LMS/playlists/Example Playlist 2026.pre-optimization-20260717T122819Z.m3u.bak" "/mnt/usbHD/LMS/playlists/Example Playlist 2026.m3u"

After either choice, validate the live bytes:

    python3 /tmp/validate_example_playlist_m3u.py "/mnt/usbHD/LMS/playlists/Example Playlist 2026.m3u" --expected-count 20 --check-files

Then issue the LMS CLI command rescan playlists through JSON-RPC.

## Feature direction

For this one-shot task, the standalone tools were easier and safer than changing
lms-blissmixer: they can use immutable snapshots, compare several global routes, freeze
external artist evidence, and produce a candidate before touching LMS. A future feature can
reuse the metric, route search, profile aggregation, and bridge gate, but should add a UI
preview, audition/accept controls, cancellation, and transactional playlist persistence.
