# Implementation checkpoint 36: released global fixed-gap planning

**Date:** 2026-10-20  
**Scope:** Native global planning and released Better Call Bliss UX for **Fill every gap with N bridge tracks**.  

## Delivered behavior

- Better Call Bliss exposes the capability-gated **Fill every gap with N bridge tracks** addition purpose with a validated `1..8` per-gap count and a derived final-size preview.  
- Optimize first freezes its selected source-only route; Preserve uses the submitted source order. Neither policy allows the global gap planner to move those anchors.  
- `bliss-playlist-optimizer` uses the shared anchored A-to-B kernel to retain several exact-count alternatives per source gap, then combines them with one deterministic global beam.  
- Global state carries used membership, repeat constraints, contextual acoustic scores, guidance adjustments, Variation, transition sum, and worst transition across all gaps.  
- The workflow adds no opening or closing tracks and either returns the complete exact route or fails without a partial playlist.  
- Preflight rejects fixed-spacing artist/album conflicts that the chosen per-gap count cannot repair, insufficient unique candidate inventory, and final sizes above 500 before the expensive global search.  
- The progress sidecar reports the active gap plus evaluated and retained state counts, including heartbeat updates while one native search step runs.  
- The native artifact proves exact per-gap placement, unchanged original subsequence, unique membership, absent endpoint additions, and final repeat-window compliance. The Perl host independently validates those proofs before exposing output actions.  

## Revisions and releases

| Component | Revision | Release |
| --- | --- | --- |
| `bliss-playlist-optimizer` | `28faa258078b8d77813fe7e604b7bd45e023146a` | [v0.2.5](https://github.com/chrober/bliss-playlist-optimizer/releases/tag/v0.2.5) |
| `lms-better-call-bliss` | `285c736b493f9a8302004bb7e8ce38ba9dd4228c` | [0.22.8](https://github.com/chrober/lms-better-call-bliss/releases/tag/0.22.8) |

Better Call Bliss 0.22.8 pins and packages optimizer v0.2.5. Its release workflow published separate Linux, macOS, and Windows plugin archives and updated the private Lyrion extension feed.  

## Verification evidence

- The optimizer [v0.2.5 release workflow](https://github.com/chrober/bliss-playlist-optimizer/actions/runs/39376540487) completed successfully and published five platform binaries plus their checksum files.  
- The plugin [CI workflow](https://github.com/chrober/lms-better-call-bliss/actions/runs/39380750356) completed successfully on the release commit.  
- The plugin [0.22.8 release workflow](https://github.com/chrober/lms-better-call-bliss/actions/runs/39380804175) completed successfully, downloaded optimizer v0.2.5, verified its SHA-256 files, tested the packaged native contract, verified platform layouts, and updated `chrober/lms-plugins`.  
- All three plugin ZIPs were downloaded independently after publication. Their SHA-1 and SHA-256 files matched, every `install.xml` reported 0.22.8, and every packaged `Bin/SOURCE.md` pinned optimizer v0.2.5 at `28faa258078b8d77813fe7e604b7bd45e023146a`.  
- The Linux package's ARM64 optimizer SHA-256 matched the independently verified official v0.2.5 ARM64 release asset.  

## Remaining boundaries

- **Improve difficult transitions** still decides locally which gaps deserve an optional bridge and does not yet allocate one global addition budget across several difficult gaps.  
- Preserved-order **Extend playlist** still selects membership against the complete original source set and uses its separate placement path; it does not yet jointly solve structural multi-track repeat deficits.  
- Duration-based targets, explicit endpoint additions, durable job history, persistence-phase cancellation, and richer acoustic path evidence remain roadmap work.  

## Next useful step

Reuse the proven global outer-planner structure for one distinct allocation problem at a time: either budgeted difficult-transition improvement or structural preserved-order extension placement. Preserve their current listener-facing meanings and candidate-relevance rules rather than treating fixed-count gap filling as a generic replacement.  
