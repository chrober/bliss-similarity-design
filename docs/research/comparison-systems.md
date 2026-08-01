# MusicIP and current comparison systems

**Status:** Living research and design proposal  
**Primary scope:** Historical design evidence and contemporary baselines  
**Last reviewed:** 2026-08-01

## What MusicIP actually did

MusicIP is useful historical evidence, but its closed production analyzer is
not a specification that can be reconstructed from marketing descriptions.
This section separates documented behavior from attractive but unverified
claims.

### Analysis and identity

The [MusicIP patent](https://patents.google.com/patent/WO2005038666A1/en)
describes an acoustic attribute vector used for similarity separately from an
audio fingerprint used for identity. It lists possible attributes such as
tempo, energy, repeating-section proportion, rhythm, bass patterns, harmony,
instrument presence, and distances to musical classes. It also describes
possible normalization, mono conversion, and silence removal. A patent lists
possible embodiments; it does not prove that every described attribute shipped
in every MusicIP product.

The public `libofa` code is the Open Fingerprint Architecture component, not the
proprietary MusicIP similarity extractor. A PUID or fingerprint should therefore
not be treated as the secret similarity vector. The exact production feature
set, dimensionality, analysis interval, and distance function remain unknown.

### Context profiles and mix policy

The strongest documented MusicIP idea is hierarchical context. The patent
describes profiles for groups such as artists, albums, playlists, and moods,
using each attribute's deviation from the overall music population. It then
combines track-level acoustic distance with group-profile distance. In modern
terms, this is a library-relative, regularized context representation rather
than merely another audio descriptor.

One described coefficient is:

```text
profile_i = (group_mean_i - library_mean_i) / library_variance_i
```

That signed coefficient identifies how a group differs from the population.
The exact denominator should not be copied unquestioningly: standard deviation,
robust scale, shrinkage, and clipping are safer candidates for a modern
experiment.

The deployed [MusicIP HTTP
API](https://github.com/LMS-Community/slimserver/blob/public/9.2/Slim/Plugin/MusicMagic/HTML/EN/plugins/MusicMagic/html/docs/httpprotocol.html)
corroborates several user-visible behaviors: multiple seeds, moods, recipes,
filters, genre restrictions, repeat/reject controls, a `style` range, and a
separate `variety` setting. The distinction is important: relevance to a seed or
context and diversity within the returned set are different policies.

### Ordering and feedback

MusicIP also treated selection and ordering separately. Its documented smooth
shuffle minimized adjacent-track distance using a traveling-salesperson-style
ordering; jagged and sawtooth modes deliberately produced other trajectories.
The LMS integration also exposed more-like/less-like feedback, saved moods, and
playlist morphing. These ideas inform both this design and
[PATH_INTERPOLATION.md](https://github.com/chrober/lms-blissmixer/blob/master/PATH_INTERPOLATION.md), but they are not evidence that
MusicIP analyzed intro/outro anchors or optimized crossfades.

## Current alternatives and comparison baselines

There are current alternatives at the application, analysis-toolkit, and
learned-representation levels, but no clear drop-in replacement for the complete
Bliss design point: a lightweight Rust analysis library, a compact canonical
versioned vector, reusable distance and playlist utilities, and established MPD
and LMS consumers. The detailed analysis-layer comparison and its implications
for future research live in the companion [Bliss Analysis
Evolution](analysis-research.md#current-alternatives-and-comparison-systems)
document.

### AudioMuse-AI

[`AudioMuse-AI`](https://github.com/NeptuneHub/AudioMuse-AI) is the closest
current open-source comparator at the self-hosted product level. It provides
local sonic analysis, similar-song playlists, clustering, song paths, maps,
listening-derived profiles, add/subtract interaction, and integrations including
LMS/Lyrion. Its [published documentation](https://neptunehub.github.io/AudioMuse-AI/)
lists Lyrion as supported and links an unofficial Lyrion plugin, so it is
already a deployable alternative for Lyrion users rather than a possible future
competitor. It is therefore relevant to the complete
`analyzer + similarity service + player integration` architecture described
here.

It is not a drop-in library replacement. It is an AGPL, Dockerized application
stack built around Python, ONNX/librosa-oriented analysis, service storage, and
web APIs. Configurable modes may combine acoustic evidence with CLAP, learned
tags, lyrics, or text. A fair sonic-similarity comparison must therefore report
an audio-only configuration separately from hybrid or multimodal modes. It
should be treated as an end-to-end system baseline, not as an ablation of one
Bliss descriptor.

AudioMuse-AI can run on ARM and has been tested on a Raspberry Pi 5 with 8 GB
RAM and NVMe storage; its [FAQ](https://neptunehub.github.io/AudioMuse-AI/FAQ/)
suggests four cores, 8 GB RAM, and SSD-class storage. That demonstrates
feasibility on a well-equipped Pi 5, but does not establish optimal operation on
the wider range of Raspberry Pi systems used for Lyrion. Older CPUs, less RAM,
microSD storage, and concurrent player duties may materially change analysis,
clustering, and idle behavior. Hardware suitability must therefore be measured,
not inferred from feature availability.

### Analysis and representation baselines

[`Essentia`](https://github.com/MTG/essentia) is the strongest current
alternative analysis framework. Its
[`MusicExtractor`](https://essentia.upf.edu/tutorial_extractors_musicextractor.html)
offers a much larger spectral, psychoacoustic, loudness, rhythm, tonal, and chord
inventory, while its [model catalogue](https://essentia.upf.edu/models.html)
includes Discogs-derived, musicnn, and MAEST inference options. That breadth is
valuable for prototyping and cross-checking hypotheses, but does not provide one
canonical vector, distance, persistence contract, or mixer.

[`librosa`](https://librosa.org/doc/latest/feature.html) plus learned
representations such as
[`musicnn`](https://github.com/jordipons/musicnn), MAEST, or
[MERT](https://openreview.net/pdf?id=w3YZ9MSlBu) provides a flexible research
stack. Such a stack still needs declared frame selection, pooling, model
identity, normalization, storage, indexing, and playlist policy. These are
component baselines, not finished Bliss alternatives.

### Proprietary behavioral reference

[Plex Sonic
Analysis](https://support.plex.tv/articles/sonic-analysis-music/) demonstrates
a current polished experience with sonically similar tracks, artists and
albums, track and album radio, and generated mixes. Its closed representation
cannot validate this proposal or serve as a reproducible algorithmic baseline;
it is useful as a product and UX reference.

The practical comparison policy is therefore:

- compare AudioMuse-AI audio-only results at the complete-system level where
  deployment is feasible;
- include representative Raspberry Pi/Lyrion hardware in that comparison and
  measure initial and incremental analysis, clustering, idle footprint, storage
  traffic, and playback interference;
- compare named Essentia/librosa descriptors and learned embeddings under a
  common local scoring and evaluation harness;
- keep multimodal and metadata-assisted systems in a separate hybrid baseline;
- report quality together with compute, storage, licensing, reproducibility,
  explainability, and schema stability;
- retain the existing Bliss path as the control unless another approach
  demonstrates enough benefit to justify its additional analysis and deployment
  cost.
