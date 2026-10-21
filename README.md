# Bliss Similarity and Analysis Design

Research and design documentation for evolving Bliss audio analysis, similarity,
and mixing quality.

The published site is intended to live at
<https://chrober.github.io/bliss-similarity-design/>.

## Current implementation snapshot

The deployed Bliss guidance slice is Bliss-first and provider-neutral:

- Better Call Bliss and Bliss Mixer Lab use discoverable, disabled-by-default
  guidance providers where enabled. The native playlist optimizer and mixer
  endpoint host the same provider-neutral SPI lifecycle.
- Last.fm guidance supports a LastMix-backed resolved-artifact path and direct
  provider-owned API-key acquisition with persistent caching. Acquisition is
  confined to `prepare`; bounded candidate scoring stays network-free.
- Library Signals can optionally use an enabled Alternative Play Count plugin
  as the source for play count and last played. APC-only skip/DPSV guidance,
  and the remaining playlist/path-quality research are still future work.

See [Last.fm guidance acquisition plan](LASTFM_GUIDANCE_ACQUISITION_PLAN.md)
and [local library guidance plan](LOCAL_LIBRARY_GUIDANCE_PLAN.md) for the
authoritative status and acceptance work.

## Playlist optimization implementation record

- [Better Call Bliss productization and implementation plan](BLISS_PLAYLIST_OPTIMIZER_IMPLEMENTATION_PLAN.md)
- [Latest implementation checkpoint: released repeat-window spacer repair](IMPLEMENTATION_CHECKPOINT_38.md)
- [Acoustic path-finding design](ACOUSTIC_PATH_FINDING_DESIGN.md)
- [Example Playlist 2026 plan](PLAYLIST_OPTIMIZATION_PLAN.md)
- [Executed run, results, reproduction, and rollback](PLAYLIST_OPTIMIZATION_EXECUTION.md)
- [Example Playlist 2025 evaluation and Extended execution](PLAYLIST_OPTIMIZATION_2025_EXECUTION.md)

The implementation history records the one-shot workflow and its later native
productization. Current shipped behavior remains documented by the owning
Better Call Bliss and `bliss-playlist-optimizer` repositories.

## Local preview

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m mkdocs serve
```

## Validation

```powershell
.venv\Scripts\python -m mkdocs build --strict
```

The documentation is a working proposal, not an official `bliss-rs` roadmap.
