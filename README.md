# Bliss Similarity and Analysis Design

Research and design documentation for evolving Bliss audio analysis, similarity,
and mixing quality.

The published site is intended to live at
<https://chrober.github.io/bliss-similarity-design/>.

## Local preview

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m mkdocs serve
```

## One-shot playlist optimization

- [Example Playlist 2026 plan](PLAYLIST_OPTIMIZATION_PLAN.md)
- [Executed run, results, reproduction, and rollback](PLAYLIST_OPTIMIZATION_EXECUTION.md)
- [Example Playlist 2025 evaluation and Extended execution](PLAYLIST_OPTIMIZATION_2025_EXECUTION.md)

The reproducible workflow captures live `plugin.blissmixer` preferences with
`tools/capture_lms_blissmixer_settings.py` and validates generated playlist
entries with `tools/validate_m3u.py --require-lms-blocks`. Adaptive runs mirror
the server's sliding seed window and can be checked against a running shipped
Windows mixer using `tools/validate_adaptive_binary_parity.py`.

## Validation

```powershell
.venv\Scripts\python -m mkdocs build --strict
```

The documentation is a working proposal, not an official `bliss-rs` roadmap.
