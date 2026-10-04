# Bliss Similarity and Analysis Design

Research and design documentation for evolving Bliss audio analysis, similarity,
and mixing quality.

The published site is intended to live at
<https://chrober.github.io/bliss-similarity-design/>.

## Current implementation snapshot

The deployed Bliss guidance slice is Bliss-first and provider-neutral:

- Better Call Bliss 0.22.0 and Bliss Mixer Lab 0.10.0 use discoverable Library
  Signals where enabled; the Lab keeps its established direct LastMix DSTM
  path for now.
- LastMix-backed Last.fm guidance is working through the resolved-artifact
  path. The separate Last.fm provider is released, but its API Key mode does
  not yet perform direct native HTTP/cache acquisition and remains neutral.
- APC, direct Last.fm acquisition, and the remaining playlist/path-quality
  research are still future work.

See [Last.fm guidance acquisition plan](LASTFM_GUIDANCE_ACQUISITION_PLAN.md)
and [local library guidance plan](LOCAL_LIBRARY_GUIDANCE_PLAN.md) for the
authoritative status and acceptance work.

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
