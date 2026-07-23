# Analysis research foundation and state of the art

**Status:** Living research and design proposal  
**Primary scope:** Audio representation, structure, similarity, and evaluation validity  
**Last reviewed:** 2026-07-23

## Scope and research questions

This section is a working literature review for an early research phase, not a
claim that the proposed descriptor set has already been validated. It traces the
scientific basis of the current Bliss representation, follows direct successor
work, and relates newer music-information-retrieval research to the proposed
`bliss-rs` analysis contract.

The review is organized around five research questions:

1. **RQ1 - representation:** Which acoustic and mid-level musical properties
   are lost when a track is reduced to one flat whole-track vector?
2. **RQ2 - time scale:** Which information should remain local, multi-scale, or
   sequential rather than being immediately aggregated?
3. **RQ3 - similarity:** Is there a defensible general-purpose music distance,
   or should similarity be conditioned on musical aspects and downstream tasks?
4. **RQ4 - uncertainty:** Which outputs should retain alternatives,
   probabilities, confidence, or multiple interpretations?
5. **RQ5 - evaluation:** What evidence would demonstrate that a new analysis
   product improves retrieval, playlist construction, or transitions?

The resulting hypotheses are intentionally broader than a future Version 3
vector. The purpose is to identify reusable evidence that `bliss-rs` could
extract and to define experiments that determine which compact views are worth
stabilizing.

## Evidence interpretation and limitations

The reviewed papers do not all evaluate the same task:

- the direct harmonic lineage primarily evaluates Western classical style or
  composer classification;
- structure-analysis work evaluates boundary detection and segment grouping;
- representation-learning work commonly evaluates tagging, nearest-neighbor
  retrieval, or proxy objectives;
- playlist-supervision work learns from aggregate consumption behavior;
- listener studies demonstrate subjectivity but do not prescribe one feature
  set;
- only some work evaluates an interactive similarity-search experience.

These results establish that particular representations retain meaningful
musical information. They do **not** by themselves establish that a descriptor
improves heterogeneous-library mixing or directional transition quality. This
document therefore treats paper results as candidate-generating evidence.
Promotion still requires task-specific ablation and listener evaluation on the
target library.

Dataset and repertoire scope also matter. In particular, results obtained on
Western tonal classical music must not be generalized without measurement to
electronic, jazz, hip-hop, ambient, non-Western, highly percussive, or weakly
tonal material. Descriptor confidence and explicit unsupported-domain behavior
are part of the proposed contract for this reason.

## Scientific origin of the current Bliss chroma features

The Bliss technical description states that similarity begins with global
tempo, timbre, loudness, and chroma-derived values followed by Euclidean
distance. Its chroma descriptors are based on Weiß, Mauch, and Dixon (2014)
[[1]](#r1). The compact implementation should not be mistaken for the full
method studied by that source.

Arzelier's 2018 MSc thesis behind Bliss [[18]](#r18) provides important design
context. It targets local libraries and smooth seed-based playlists, combines
timbral, temporal, tonal, and intensity features, and studies a distance metric
tuned from listening-survey triplets. The thesis deliberately limits feature
count relative to the expected number of survey observations and aggregates
frame-level measurements for practical storage and learning. It explicitly
acknowledges that richer summaries still do not recover song evolution or
semantic sections such as verses and choruses.

The learned metric did not substantially improve prediction of held-out survey
answers in the reported split, but the final listening comparison found the
trained metric produced more enjoyable playlists than the untrained metric.
This is useful preliminary evidence that end-to-end playlist judgment can
differ from proxy triplet accuracy. As an MSc study with limited survey data,
it should be treated as the implementation's rationale and an exploratory
result, not a conclusive evaluation.

**Implications for `bliss-rs`:** the current compact representation is a
pragmatic starting point rather than a claim of analytical completeness. The
structured-analysis proposal directly addresses limitations already identified
in the thesis, while the evaluation plan should retain both held-out comparison
tasks and complete playlist outcomes. Learner dimensionality must remain
proportional to available feedback, motivating passive supervision,
regularization, and family-level rather than unconstrained per-dimension
personalization.

The source paper:

- starts from time-dependent chroma at 10 Hz;
- compares four chroma extraction methods;
- smooths chroma at seven temporal resolutions, including local and global
  views;
- computes interval- and triad-related mid-level features at those resolutions;
- initially evaluates 280 feature variants per track;
- finds that neither the global representation nor a fine local representation
  is sufficient alone, and retains several scales for the final experiments.

The musical argument is important. Chords and chord changes appear at fine
scales, while local keys and modulations appear at coarser scales. A globally
complex Romantic work can still contain locally simple harmony, whereas other
music may be complex at both scales. Whole-track aggregation cannot distinguish
these cases.

The same paper also states important limits of chroma: octave information,
voice separation, pitch order, bass-relative interval function, and much
voice-leading information are lost. The current aggregate interval/triad values
are therefore useful transposition-invariant evidence, but they are not a
complete mathematical description of harmony.

**Implications for `bliss-rs`:**

- the scientific rationale supports a multi-scale temporal representation more
  strongly than it supports only a larger global vector;
- retained chroma or a derived tonal sequence should be available to
  experimental consumers without changing Version 2;
- multi-scale pooling should be schema-declared rather than hidden inside one
  value;
- absolute key, bass-relative evidence, and voice-leading proxies should be
  separate task-selectable products rather than silently changing the current
  transposition invariance;
- chroma extractor identity and configuration belong in representation schema
  identity.

## Direct harmonic-feature lineage

### Tonal complexity

Weiß and Müller (2015) [[2]](#r2) derive chroma-based statistical measures of
tonal complexity and compare them with standard audio features across piano and
orchestral recordings. Their experiments indicate that the complexity features
capture musically meaningful information that is comparatively robust to
orchestration and timbre. The method again operates at multiple temporal
resolutions.

**Potential implications:** tonal concentration, dispersion, entropy, and
local-versus-global complexity are plausible experimental descriptors. Their
main value may be a typed multi-scale harmonic product from which consumers
derive summaries, rather than hundreds of permanently stored scalar columns.

Weiß, Mauch, Dixon, and Müller (2019) [[3]](#r3) subsequently apply tonal
features
to 2,000 recordings spanning more than 300 years and examine the evolution of
intervals, chord transitions, and tonal complexity. The work provides evidence
that interpretable audio-derived tonal measures can support unsupervised
relationships as well as classification. It does not establish a universal
song-similarity metric, but it motivates retaining descriptors whose musical
meaning remains inspectable.

### Soft chord transitions

Weiß, Brand, and Müller (2019) [[4]](#r4) compare chord-transition features derived
from a hard decoded chord sequence with soft probabilistic transition features.
The soft method avoids selecting one supposedly optimal chord sequence before
feature derivation and performs consistently better in their style
classification experiments.

**Potential implications:**

- hard chord symbols should not be the canonical temporal representation;
- posterior-like tonal evidence or soft transition counts should be retained
  where feasible;
- any decoded chord label should carry ambiguity and model identity;
- consumers should be able to compare harmonic movement without treating an
  uncertain intermediate transcription as truth.

### Perceptually motivated tonal interval vectors

Almeida, Bernardes, and Weiß (2022) [[5]](#r5) explicitly connect the 2014, 2015,
and 2019 lineage to the perceptually inspired Tonal Interval Vector (TIV)
space. They propose interpretable mid-level features for dissonance,
chromaticity, dyadicity, triadicity, diminished quality, diatonicity, and
whole-toneness. They also measure:

- perceptual distance between consecutive harmonic segments;
- tonal dispersion relative to a whole-piece tonal center;
- harmonic-change rate and magnitude;
- harmonic complexity through TIV entropy;
- relationships between short- and long-term harmonic organization;
- context-sensitive segmentation driven by harmonic change.

TIV cosine and Euclidean distances capture different relationships between
sonorities. The proposed measurements can be computed at multiple segment sizes:
short segments describe chord-scale change, while longer segments describe
larger tonal movement such as modulation.

The paper reports that context-sensitive segmentation produced only slight
classification improvements that may not justify its additional computation in
that experiment. This is evidence for testing simple fixed-window multi-scale
features before making adaptive harmonic segmentation a default product.

**Potential implications:**

- evaluate TIV or an equivalent perceptually motivated tonal representation as
  an optional typed series;
- distinguish harmonic-change frequency from harmonic-change magnitude;
- evaluate tonal dispersion and short/long-term relationships as experimental
  summaries;
- do not use one unexplained scalar called `harmonic_complexity`;
- compare fixed multi-scale pooling with context-sensitive segmentation under
  an explicit cost/benefit benchmark;
- record the tonal representation, distance, segment scale, and aggregation in
  schema identity.

## Music structure and segmentation

McFee and Ellis (2014) [[6]](#r6) combine local continuity and long-range
repetition through a graph representation derived from time-series features and
self-similarity. Although demonstrated on flat structural annotation, their
representation supports analysis at multiple resolutions. This supports
retaining frame evidence and compact recurrence/novelty products rather than
only a final list of section labels.

Nieto et al. (2020) [[7]](#r7) review audio-based music structure analysis and
identify subjectivity, ambiguity, and hierarchy as persistent challenges. A
single track may have several defensible structural descriptions depending on
the musical attribute, requested time scale, annotator, and application. The
review argues for application-dependent systems and, where useful, multiple or
user-selectable structural outputs.

Peeters (2023) [[8]](#r8) demonstrates a newer supervised approach that learns both
features for a self-similarity matrix and kernels for novelty estimation. The
method is optimized using losses directly related to self-similarity and
novelty, and reports that relative feature learning through self-attention is
beneficial. The paper organizes structure cues around novelty, homogeneity,
repetition, and regularity while again noting multiple viewpoints, hierarchy,
and subjectivity.

**Potential implications:**

- expose the feature source, self-similarity configuration, novelty curve,
  boundary candidates, and confidence separately from inferred labels;
- support a scale or level identifier for boundaries and segments;
- permit multiple structural hypotheses when an algorithm exposes them;
- avoid `verse` or `chorus` as required truth in the initial API;
- do not persist a quadratic self-similarity matrix by default;
- use learned structure features only as an optional, versioned backend; a
  reproducible handcrafted baseline remains necessary for ablation.

## Singing voice, vocal character, and extreme techniques

Monir, Kostrzewa, and Mrozek (2022) survey singing-voice detection as a
frame- or segment-level classification problem [[28]](#r28). The literature
supports treating vocal activity as temporal evidence rather than assigning one
whole-track vocal label. It also shows reliance on relatively small annotated
corpora and substantial variation in features, model families, and evaluation
protocols. High reported accuracy on one corpus therefore does not establish
calibration across the heterogeneous libraries targeted by Bliss.

Kalbag and Lerch (2022) study scream detection and classification in heavy-metal
music using more than 280 minutes of manually annotated material and compare
cepstral, spectral, and temporal representations [[29]](#r29). Their results
establish that extreme techniques such as screams and growls can be analyzed from
polyphonic music, but the narrow domain is equally important: a genre-specific
classifier is feasibility evidence, not a universal vocal taxonomy.

Audio-language models provide another research probe. CLAP learns a joint audio
and natural-language space and reports zero-shot classification across several
audio domains [[30]](#r30). Flexible prompts could help explore terms such as
clean, spoken, shouted, screamed, or growled without first fixing a production
label set. Zero-shot similarity is nevertheless model-relative, prompt-sensitive
evidence; it is not automatically calibrated enough for a stable descriptor or
lightweight enough for the target deployment.

**Potential implications:**

- separate vocal presence and coverage from register, delivery, technique, and
  optional embeddings;
- retain frame or segment probabilities and aggregate them with explicit support
  rather than forcing one track-level class;
- prefer continuous pitch and tessitura evidence to unsupported voice-type labels;
- treat delivery and technique as probabilistic and multi-label because clean,
  spoken, rough, screamed, and growled evidence may overlap or change by section;
- reinterpret binary voice-presentation classifiers as model-relative perceived
  timbre, not biological sex, gender identity, or singer identity;
- benchmark mixture-based analysis before optional source separation, and measure
  both separation artifacts and deployment cost; and
- require aspect-specific retrieval and listener evidence before vocal features
  influence a general-purpose distance.

## Multidimensional and controllable similarity

Lee et al. (2020a) [[9]](#r9) formulate music similarity as several simultaneous
notions, including genre, mood, instrumentation, and tempo. A conditional
similarity network supports both general and aspect-specific retrieval in one
disentangled representation. Their model outperforms specialized alternatives
in the reported experiments and is preferred by annotators in a user study.

Lee et al. (2020b) [[10]](#r10) compare metric-learning and classification
objectives for disentangled music representations. The preferred training
objective depends on the evaluation: classification-based models are generally
stronger for training time, similarity retrieval, and auto-tagging, while deep
metric learning is stronger for triplet prediction. An embedding optimized for
one proxy task therefore cannot be assumed to be the best representation for
another.

McCallum et al. (2024a) [[15]](#r15) show that contrastive-training augmentations
change the local organization of a music embedding. Time stretching and pitch
shifting can suppress sensitivity to tempo or key and allow other attributes to
dominate, but can also damage downstream tasks that require the suppressed
property. The optimal invariance depends on the downstream task.

McCallum et al. (2024b) [[16]](#r16) learn a tempo-translation function within an
existing embedding. This supports queries that remain similar in other respects
while moving toward a requested tempo, illustrating that a useful
representation may be predictably transformable rather than simply invariant.

**Potential implications:**

- do not define the new analysis around one universal distance;
- retain separable evidence for rhythm, tonality, dynamics, timbre, vocals,
  structure, and boundaries;
- let downstream profiles select or weight the relevant aspects;
- distinguish invariant, sensitive, and predictably equivariant behavior;
- treat training augmentations as part of a learned representation's semantic
  contract;
- evaluate global neighbor quality separately from aspect-conditioned and
  directional transition tasks.

## Self-supervised and weakly supervised representations

Spijkervet and Burgoyne (2021) [[11]](#r11) introduce CLMR, a self-supervised
contrastive method for raw music audio. It learns transferable representations
without ground-truth labels and performs competitively on downstream
classification, including with limited labelled data. This makes a learned
embedding a useful experimental baseline, but the reported tasks do not prove
that it captures the aspects needed for mixing.

Thomé, Piwell, and Utterbäck (2021) [[12]](#r12) report a production-oriented
segment-level similarity engine trained with triplet losses and explicit
musical transformations. Five professional video producers rated retrieved
similarities at an average 7.8/10 in their qualitative study. The work is a
late-breaking extended abstract with a small user study, but it demonstrates
the practical value of local excerpt embeddings and makes the intended
invariances explicit in the augmentation chain.

Alonso-Jiménez et al. (2023) [[13]](#r13) use playlist co-occurrence as weak
supervision for contrastive representation learning. In their experiments,
playlist-derived positive pairs improve similarity and provide competitive
classification results compared with same-artist pairing and other baselines.
Consumption context can therefore supply useful supervision, but it represents
human behavior and curation rather than an intrinsic acoustic property.

Li et al. (2024) [[14]](#r14) introduce MERT, a large music-specific
self-supervised model using acoustic and musically informed teachers and report
evaluation across 14 music-understanding tasks. It is relevant as an offline
benchmark or potential teacher representation. Its 95M- and 330M-parameter
variants, opaque dimensions, model lifecycle, and deployment cost make it a
poor mandatory dependency for the initial `bliss-rs` structured API.

**Potential implications:**

- include optional segment and whole-track embeddings in the representation
  taxonomy, but not in Version 2 or an automatic Version 3 proposal;
- define model provenance, input policy, pooling, augmentation-derived
  invariances, and licensing/deployment assumptions;
- benchmark learned embeddings against interpretable descriptors rather than
  treating them as a replacement by default;
- keep playlist, setlist, skip, and listener-history supervision in learner or
  application layers;
- use passive behavioral supervision to bootstrap personalization and reserve
  explicit comparisons for uncertain or high-information cases.

## Human agreement and evaluation validity

Flexer, Lallai, and Rašl (2021) [[17]](#r17) study repeated human ratings of general
music similarity. They find that intra-rater agreement is higher than
inter-rater agreement, that agreement becomes lower in the harder within-genre
setting, and that listener state can affect repeated judgments. They question
evaluation based on unspecified general similarity and recommend more specific
aspects and use cases.

**Potential implications:**

- a generic question such as "Are these songs similar?" is insufficient as the
  only ground truth;
- evaluation should distinguish rhythmic feel, harmonic movement, energy
  development, timbral character, structure, and transition compatibility;
- repeated judgments and uncertainty should be retained for a calibration
  subset;
- personal models should be evaluated against held-out judgments by the same
  listener as well as aggregate preference;
- complete playlist and transition outcomes matter in addition to isolated
  pairwise distances.

These concerns apply directly to the `bliss-metric-learning` survey built
around a `blissify-rs` library, and therefore to the derived `bliss-learner`
experiment described under [Existing application and personalization
experiments](../analysis/current-analysis.md#existing-application-and-personalization-experiments): generic
odd-one-out judgments are useful personal evidence, not objective similarity
ground truth. The `blissify-rs` interactive-playlist mode asks a narrower
contextual question by letting the listener choose the next track among close
candidates. It currently uses that choice immediately rather than retaining it
for learning or evaluation; with explicit consent and appropriate context, such
choices could become lower-effort, task-specific evidence for future
experiments.

## Current alternatives and comparison systems

The current ecosystem contains credible alternatives for individual layers and
one close self-hosted product-level comparator, but no direct replacement that
combines the same design properties as Bliss: a lightweight Rust analysis
library, a compact canonical versioned vector, reusable distance and playlist
utilities, and established MPD and LMS consumers. This is an inference from the
systems below, not a claim that Bliss is uniquely capable or already superior.

| System | Closest Bliss layer | Relevant capabilities | Why it is not a drop-in replacement |
|---|---|---|---|
| **AudioMuse-AI** | Analyzer, similarity service, and playlist application | Local sonic analysis, similar-song search, clustering, song paths, music maps, and integrations including LMS/Lyrion | Dockerized AGPL application stack rather than an embeddable crate or stable canonical representation |
| **Essentia** | Audio analysis and representation extraction | Broad spectral, Bark/ERB, loudness, rhythm, tonal, chord, and learned-model support | Analysis toolkit without one prescribed song vector, distance, persistence contract, or mixer |
| **librosa plus learned models** | Experimental descriptor and embedding backends | Temporal features, recurrence/segmentation tools, and representations such as musicnn, MAEST, or MERT | Research construction kit requiring custom pooling, schema, metric, indexing, and playlist policy |
| **Plex Sonic Analysis** | End-user sonic similarity and radio | Similar tracks, artists, albums, track/album radio, and generated mixes | Proprietary implementation whose representation and algorithms cannot be reused or audited |

### AudioMuse-AI

AudioMuse-AI is the closest current open-source alternative at the complete
self-hosted-system level. Its project describes local analysis, clustering,
query-by-song playlists, paths between songs, listening-derived sonic
fingerprints, add/subtract interaction, and integrations with LMS/Lyrion,
Navidrome, Jellyfin, Emby, and other servers [[19]](#r19). It therefore provides
a relevant operational baseline for the wider
`bliss-rs + analyzer + mixer + player` ecosystem.

Lyrion is already listed as a supported server and an unofficial Lyrion plugin
is available, so AudioMuse-AI is a present alternative for Lyrion users rather
than only a research comparator. Its official documentation reports successful
operation on a Raspberry Pi 5 with
8 GB RAM and NVMe storage and suggests four CPU cores, 8 GB RAM, and SSD-class
storage [[27]](#r27). This establishes feasibility on a well-equipped Pi 5, not
optimal behavior across the broader Raspberry Pi installations used for music
servers. Analysis time, clustering time, sustained memory, storage I/O, idle
footprint, and interference with playback remain empirical deployment
questions, particularly for older, lower-memory, or microSD-based systems.

It is not a substitute for the `bliss-rs` API contract. It is an AGPL-licensed,
Dockerized application using a Python/ONNX/librosa-oriented analysis stack plus
database and service infrastructure. Its configurable modes may also include
CLAP, lyrics, learned tags, or other evidence beyond audio similarity
[[20]](#r20). A favorable result cannot be attributed to its sonic
representation unless audio-only and multimodal configurations are reported
separately.

### Essentia

Essentia is the strongest current alternative analysis framework. It is an
AGPL-licensed C++ library with Python bindings, reusable DSP and music-analysis
algorithms, and executable extractors [[21]](#r21). Its music extractor exposes
a much broader descriptor inventory than Version 2 Bliss, including Bark- and
ERB-band statistics, EBU R128 loudness measures, spectral flux and complexity,
onset and beat evidence, BPM histograms, danceability, HPCP, key strength,
chords, and chord-change measures [[22]](#r22). Its model catalogue also makes
Discogs-derived classifiers and embeddings, musicnn variants, and MAEST models
available through defined inference wrappers [[23]](#r23).
The catalogue includes voice-versus-instrumental and binary vocal-presentation
classifiers, demonstrating readily available prototype backends. Their category
semantics, training-domain bias, and noncommercial model licensing still require
review before they can define a Bliss feature.

That breadth makes Essentia valuable as an external prototype and reference
implementation, not an automatic dependency or representation definition.
Selecting hundreds of outputs does not define a perceptually valid distance;
feature redundancy, scale, confidence, versioning, licensing, and deployment
cost still need explicit treatment. Any adopted algorithm should be specified
and validated independently rather than importing an opaque extractor dump as a
new canonical vector.

### librosa and learned representations

librosa provides a flexible Python construction kit for chroma, mel spectra,
MFCCs, spectral descriptors, tempo and tempograms, recurrence matrices,
segmentation, and beat-synchronous aggregation [[24]](#r24). It is appropriate
for research prototypes but deliberately does not prescribe a canonical song
representation, similarity metric, storage model, or playlist algorithm.

Pretrained representations such as musicnn [[25]](#r25), Essentia's MAEST and
Discogs models [[23]](#r23), and MERT [[14]](#r14) are useful learned baselines.
They remain model-relative products: frame selection, whole-track pooling,
artifact identity, objective, augmentations, intended invariances, licensing,
and compute cost are part of their semantic contract. A high-dimensional
embedding is not evidence of better mixing until it wins held-out task and
listener comparisons against Version 2 and simpler interpretable additions.

### Proprietary behavioral reference

Plex Sonic Analysis demonstrates a polished current product experience based
on local library analysis: sonically similar tracks, artists and albums, track
and album radio, and generated mixes [[26]](#r26). Its closed representation
cannot validate a `bliss-rs` descriptor or be used as a reproducible algorithmic
baseline. It is useful only as a behavioral and UX reference unless an
evaluation can compare returned playlists without claiming to explain the
underlying method.

**Potential implications:**

- benchmark AudioMuse-AI in a declared audio-only mode as an end-to-end system
  baseline where deployment is practical;
- run that comparison on representative Lyrion hardware, including the target
  Raspberry Pi class, and report initial analysis, incremental analysis,
  clustering, idle, and mix-request resource costs;
- treat multimodal AudioMuse-AI modes as a separate hybrid-recommendation
  comparison, not evidence about acoustic analysis alone;
- use Essentia and librosa to prototype or cross-check descriptor hypotheses
  without silently adopting their complete output inventories;
- include at least one lightweight and one larger learned representation in
  offline benchmarks, with exact model and pooling identity;
- distinguish component ablations from full-system comparisons, since a system
  can improve through retrieval, clustering, diversity, metadata, or UX even
  when its audio representation is not better;
- include deployment cost, licensing, reproducibility, explainability, and
  schema stability alongside similarity quality;
- retain Bliss's lightweight, versioned baseline unless another representation
  demonstrates sufficient benefit to justify migration and reanalysis.

## Research synthesis and working hypotheses

The literature motivates the following hypotheses for the prototype program:

- **H1 - multi-scale harmony:** a multi-scale tonal representation improves
  aspect-specific retrieval over the current whole-track chroma aggregates.
- **H2 - soft temporal evidence:** retaining ambiguous harmonic evidence and
  soft transitions is more robust than committing early to hard chord labels.
- **H3 - interpretable mid-level features:** perceptually motivated harmonic,
  rhythmic, dynamic, and structural descriptors add information that cannot be
  reconstructed by reweighting Version 2.
- **H4 - structure as evidence:** self-similarity, novelty, repetition, and
  boundary confidence are more reusable than one supposedly definitive section
  labelling.
- **H5 - task-conditioned similarity:** different tasks require different
  sensitivities; no single unqualified music distance should define the
  analysis API.
- **H6 - local transition context:** intro/outro or segment representations add
  directional information that a whole-track vector cannot provide.
- **H7 - hybrid representation:** interpretable descriptors and optional
  learned embeddings may be complementary, but each must demonstrate held-out
  value independently and in combination.
- **H8 - efficient personalization:** passive behavioral evidence plus
  uncertainty-driven questions can reduce the explicit survey burden relative
  to training solely from a large fixed questionnaire.
- **H9 - comparative efficiency:** a compact, versioned representation can
  remain competitive with heavier learned or full-system audio-only baselines
  on target mixing tasks while requiring less analysis, storage, and deployment
  machinery.
- **H10 - conditional vocal evidence:** vocal activity and coverage provide a
  useful first distinction, while confidence-gated temporal register, delivery,
  and technique evidence can improve aspect-specific similarity beyond a single
  hard whole-track label.

These are falsifiable design hypotheses. Negative results are useful: they can
prevent unstable, redundant, or task-irrelevant descriptors from entering the
public API or a future canonical vector.

## Working bibliography

<a id="r1"></a>**[1]** C. Weiß, M. Mauch, and S. Dixon,
"[Timbre-invariant Audio Features for Style Analysis of Classical
Music](https://speech.di.uoa.gr/ICMC-SMC-2014/images/VOL_2/1461.pdf),"
ICMC/SMC, 2014.

<a id="r2"></a>**[2]** C. Weiß and M. Müller,
"[Tonal Complexity Features for Style Classification of Classical
Music](https://dihana.cps.unizar.es/proceedings/ICASSP/2015/pdfs/0000688.pdf),"
ICASSP, 2015.

<a id="r3"></a>**[3]** C. Weiß, M. Mauch, S. Dixon, and M. Müller,
"[Investigating Style Evolution of Western Classical Music: A Computational
Approach](https://qmro.qmul.ac.uk/xmlui/handle/123456789/53963),"
*Musicae Scientiae*, vol. 23, no. 4, 2019 (first published online 2018),
DOI 10.1177/1029864918757595.

<a id="r4"></a>**[4]** C. Weiß, F. Brand, and M. Müller,
"[Mid-level Chord Transition Features for Musical Style
Analysis](https://openreview.net/forum?id=OhkhINjORj)," ICASSP, 2019.

<a id="r5"></a>**[5]** F. Almeida, G. Bernardes, and C. Weiß,
"[Mid-level Harmonic Audio Features for Musical Style
Classification](https://archives.ismir.net/ismir2022/paper/000024.pdf),"
ISMIR, 2022.

<a id="r6"></a>**[6]** B. McFee and D. P. W. Ellis,
"[Analyzing Song Structure with Spectral
Clustering](https://archives.ismir.net/ismir2014/paper/000319.pdf)," ISMIR,
2014.

<a id="r7"></a>**[7]** O. Nieto, G. J. Mysore, C.-i. Wang,
J. B. L. Smith, J. Schlüter, T. Grill, and B. McFee,
"[Audio-Based Music Structure Analysis: Current Trends, Open Challenges, and
Applications](https://transactions.ismir.net/articles/10.5334/tismir.54),"
*Transactions of the International Society for Music Information Retrieval*,
2020.

<a id="r8"></a>**[8]** G. Peeters,
"[Self-Similarity-Based and Novelty-Based Loss for Music Structure
Analysis](https://archives.ismir.net/ismir2023/paper/000089.pdf)," ISMIR,
2023.

<a id="r9"></a>**[9]** J. Lee, N. J. Bryan, J. Salamon, Z. Jin, and
J. Nam,
"[Disentangled Multidimensional Metric Learning for Music
Similarity](https://www.justinsalamon.com/uploads/4/3/9/4/4394963/lee_disentangledmusicsim_icassp2020.pdf),"
ICASSP, 2020.

<a id="r10"></a>**[10]** J. Lee, N. J. Bryan, J. Salamon, Z. Jin, and
J. Nam,
"[Metric Learning vs Classification for Disentangled Music Representation
Learning](https://archives.ismir.net/ismir2020/paper/000304.pdf)," ISMIR,
2020.

<a id="r11"></a>**[11]** J. Spijkervet and J. A. Burgoyne,
"[Contrastive Learning of Musical
Representations](https://archives.ismir.net/ismir2021/paper/000084.pdf),"
ISMIR, 2021.

<a id="r12"></a>**[12]** C. Thomé, S. Piwell, and O. Utterbäck,
"[Musical Audio Similarity with Self-supervised Convolutional Neural
Networks](https://archives.ismir.net/ismir2021/latebreaking/000012.pdf),"
ISMIR Late-Breaking/Demo, 2021.

<a id="r13"></a>**[13]** P. Alonso-Jiménez, X. Favory,
H. Foroughmand, G. Bourdalas, X. Serra, T. Lidy, and D. Bogdanov,
"[Pre-Training Strategies Using Contrastive Learning and Playlist Information
for Music Classification and
Similarity](https://repositori-api.upf.edu/api/core/bitstreams/e5890f58-ce4d-467b-96b8-e96efb16d17d/content),"
ICASSP, 2023.

<a id="r14"></a>**[14]** Y. Li et al.,
"[MERT: Acoustic Music Understanding Model with Large-Scale Self-supervised
Training](https://openreview.net/pdf?id=w3YZ9MSlBu)," ICLR, 2024.

<a id="r15"></a>**[15]** M. C. McCallum, M. E. P. Davies, F. Henkel,
J. Kim, and S. E. Sandberg,
"[On the Effect of Data-Augmentation on Local Embedding Properties in the
Contrastive Learning of Music Audio
Representations](https://arxiv.org/abs/2401.08889)," ICASSP, 2024.

<a id="r16"></a>**[16]** M. C. McCallum, F. Henkel, J. Kim,
S. E. Sandberg, and M. E. P. Davies,
"[Similar but Faster: Manipulation of Tempo in Music Audio Embeddings for
Tempo Prediction and Search](https://arxiv.org/abs/2401.08902)," ICASSP,
2024.

<a id="r17"></a>**[17]** A. Flexer, T. Lallai, and K. Rašl,
"[On Evaluation of Inter- and Intra-Rater Agreement in Music
Recommendation](https://transactions.ismir.net/articles/10.5334/tismir.107),"
*Transactions of the International Society for Music Information Retrieval*,
2021.

<a id="r18"></a>**[18]** P. Arzelier,
"[Music Similarity Tool for Contemporary Music](https://lelele.io/thesis.pdf),"
MSc thesis, Technical University of Denmark, 2018.

<a id="r19"></a>**[19]** NeptuneHub,
"[AudioMuse-AI](https://github.com/NeptuneHub/AudioMuse-AI)," open-source
self-hosted sonic-analysis and playlist application, accessed July 13, 2026.

<a id="r20"></a>**[20]** NeptuneHub,
"[AudioMuse-AI Configuration
Parameters](https://neptunehub.github.io/AudioMuse-AI/PARAMETERS/)," project
documentation, accessed July 13, 2026.

<a id="r21"></a>**[21]** Music Technology Group, Universitat Pompeu Fabra,
"[Essentia](https://github.com/MTG/essentia)," open-source audio-analysis and
music-information-retrieval library, accessed July 13, 2026.

<a id="r22"></a>**[22]** Music Technology Group, Universitat Pompeu Fabra,
"[Computing Features with
MusicExtractor](https://essentia.upf.edu/tutorial_extractors_musicextractor.html),"
Essentia documentation, accessed July 13, 2026.

<a id="r23"></a>**[23]** Music Technology Group, Universitat Pompeu Fabra,
"[Essentia Models](https://essentia.upf.edu/models.html)," model catalogue and
inference documentation, accessed July 13, 2026.

<a id="r24"></a>**[24]** librosa development team,
"[Feature Extraction](https://librosa.org/doc/latest/feature.html)," librosa
documentation, accessed July 13, 2026.

<a id="r25"></a>**[25]** J. Pons et al.,
"[musicnn](https://github.com/jordipons/musicnn)," pretrained convolutional
models for music audio tagging and feature extraction, accessed July 13, 2026.

<a id="r26"></a>**[26]** Plex,
"[Sonic Analysis for
Music](https://support.plex.tv/articles/sonic-analysis-music/)," product
documentation, accessed July 13, 2026.

<a id="r27"></a>**[27]** NeptuneHub,
"[AudioMuse-AI Documentation](https://neptunehub.github.io/AudioMuse-AI/)" and
"[FAQ](https://neptunehub.github.io/AudioMuse-AI/FAQ/)," Lyrion integration,
ARM support, and hardware guidance, accessed July 13, 2026.

<a id='r28'></a>**[28]** R. Monir, D. Kostrzewa, and D. Mrozek,
[Singing Voice Detection: A Survey](https://www.mdpi.com/1099-4300/24/1/114),
*Entropy*, vol. 24, no. 1, art. 114, 2022, DOI 10.3390/e24010114.

<a id='r29'></a>**[29]** V. Kalbag and A. Lerch,
[Scream Detection in Heavy Metal Music](https://arxiv.org/abs/2205.05580),
arXiv:2205.05580, 2022.

<a id='r30'></a>**[30]** B. Elizalde, S. Deshmukh, M. Al Ismail, and
H. Wang, [CLAP: Learning Audio Concepts From Natural Language
Supervision](https://arxiv.org/abs/2206.04769), arXiv:2206.04769, 2022.
