# Example Playlist 2025 optimization execution

## Outcome

The original nine-track playlist is valid and already satisfies the active
artist=5, album=10, and unique-track constraints. Adaptive evaluation nevertheless
finds a materially smoother order, so reordering is worthwhile:

- Existing order: objective 3.380266, mean 0.306867, worst 0.462667.
- Adaptive order: objective 2.272644, mean 0.209236, worst 0.299378.
- Both orders have zero repeat-window violations.

This is a 32.8% objective reduction, 31.8% mean-transition reduction, and
35.3% worst-transition reduction. The original server file was deliberately
left unchanged. The reordered route is used as the backbone of the new Extended
variant.

## Extended deployment

- Server path: `/mnt/usbHD/LMS/playlists/Example Playlist 2025 Extended.m3u`
- Lyrion catalog ID: 723637
- SHA-256: `1b15d93f29c1d8f38390f3fcdd0e40465632925024ae443990fbfc584fd965ed`
- Tracks / unique tracks: 17 / 17
- Original tracks / additions: 9 / 8
- Placement: exactly one bridge in each of the eight internal backbone gaps
- Artist / album look-back violations: 0 / 0
- Last.fm evidence: 3 both-endpoint, 5 one-endpoint, 0 collection fallbacks
- Maximum bridge leg / two-leg total: 0.42 / 0.72
- Exact Lyrion `#EXTURL`, title-only `#EXTINF`, raw-path blocks: yes

The original remains at `/mnt/usbHD/LMS/playlists/Example Playlist 2025.m3u`,
catalog ID 723635, with unchanged SHA-256
`e480d52d3e769d8fa8919c7349b5f6105991b7bd9e633cb0aedc2e46ff53acf5`.

A supported playlists-only scan imported the Extended file as new, completed
normally, and left `_rescan=0`. LMS's indexed URL order matches both M3Us
position-for-position.

## Adaptive backbone

1. Siena Root — Dusty Roads
2. Graveyard — Far Too Close
3. Wucan — Wizard of Concrete Jungle
4. Tito & Tarantula — Back to Mexico
5. Renato Unterberg — The Two Sisters
6. Bob Dylan — I'll Be Your Baby Tonight
7. Freshlyground — Would You Mind
8. Neil Young & Crazy Horse — Sail Away
9. The Doors — Yes, the River Knows

## Final Extended order

1. Siena Root — Dusty Roads
2. Blues Pills — Dust
3. Graveyard — Far Too Close
4. Kadavar — The Lost Child
5. Wucan — Wizard of Concrete Jungle
6. Shivaree — Goodnight Moon
7. Tito & Tarantula — Back to Mexico
8. Joe Bonamassa — Chains and Things
9. Renato Unterberg — The Two Sisters
10. The Merry Poppins — My Way
11. Bob Dylan — I'll Be Your Baby Tonight
12. Joan Baez — No Mermaid
13. Freshlyground — Would You Mind
14. Neil Young — Angry World
15. Neil Young & Crazy Horse — Sail Away
16. The Rolling Stones — Coming Down Again
17. The Doors — Yes, the River Knows

## Inputs and scoring

The live settings were captured immediately before the run:

- algorithm: adaptive;
- strict sliding seed window: 3;
- learned-matrix blend: 20%;
- no-repeat artist / album / track: 5 / 10 / 100;
- static sliders 20/28/3/49 were captured but not used by adaptive scoring.

The shipped Windows bliss-mixer binary was run locally against the frozen inputs.
Its effective adaptive diagonal matched the Python implementation with maximum
absolute difference `5.245987875213132e-07`.

Input hashes:

- source playlist: `e480d52d3e769d8fa8919c7349b5f6105991b7bd9e633cb0aedc2e46ff53acf5`;
- bliss.db: `e5837e6c036b6a071ccdc836410ead4b79c2828e2674fae7ff6f10741b4d71e2`;
- learned matrix: `71e26b00faa9bb2709f0f6e8b66ae6fc27b33edc239d2ff11fdb74393cf7eb6e`;
- settings snapshot: `e23be085edc9a7763d03114bc192096aee69a2e1d03e24998ef02dacab8c90c8`;
- Last.fm profile: `a2e0e814402947efabdef987e66acacd95fbd45e12df29e0386ca3a33b64fd0d`;
- Windows binary: `7f0fc393ae6ae3f3eb099524f9d5ab63ec80b1a3a93a89bf7fb2c6fa08a1bbe3`.

The Last.fm source set is all nine distinct artists from the original playlist.
All nine lookups succeeded and produced 188 distinct similar artists. Added
tracks never became new Last.fm seeds.

## Reproduction and detailed logs

Primary run directory:

`runs/example-playlist-2025-20260719-adaptive-extended/`

Important files:

- `REPORT.md`: original/adaptive/arc candidate comparison;
- `run.json`: complete route metrics, inputs, and orders;
- `dynamic-transitions.csv`: each adaptive seed window and next-track score;
- `BRIDGE_ANALYSIS.md`: human-readable bridge decision;
- `bridge-analysis.json`: all eight placements, Last.fm evidence, and leg costs;
- `lastfm-artist-profile.json`: frozen full-original-set artist evidence;
- `adaptive-binary-parity.json`: shipped-binary parity result;
- `selected-with-bridges.m3u`: deployed bytes.

The optimizer accepts Lyrion's optional leading `#CURTRACK` marker before
`#EXTM3U`; generated candidates omit that playback-state marker and retain exact
three-line Lyrion track blocks.

These scores use whole-track Bliss features. Technical validation is complete;
the remaining judgment is a subjective audition of the eight bridge transitions.
