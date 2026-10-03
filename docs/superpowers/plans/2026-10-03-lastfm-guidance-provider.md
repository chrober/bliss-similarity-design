# Last.fm Guidance Provider Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a separately installable, discoverable Last.fm guidance provider
with provider-owned LastMix/API Key acquisition settings, disabled by default in
each host, while preserving Bliss-first candidate selection.

**Architecture:** Create `lms-guidance-lastfm` as the Lyrion provider layer and
extend the existing `bliss-guidance-lastfm` native provider with artifact and
direct acquisition adapters. Hosts discover the provider through the shared
guidance-host library, resolve sparse overrides, and pass only trusted,
non-secret configuration to native hosts. Better Call Bliss supplies the
per-job optimizer environment; Bliss Mixer Lab supplies the environment when it
starts its local mixer sidecar.

**Tech Stack:** Lyrion Perl plugin APIs, shared `lms-bliss-guidance-host`,
Rust 2021, `bliss-guidance-jsonl-v2`, LastMix, Last.fm public API, `cargo`,
GitHub Actions release packaging.

**Spec:** [Last.fm guidance acquisition plan](../../../LASTFM_GUIDANCE_ACQUISITION_PLAN.md)

## Global Constraints

- Bliss remains the acoustic authority; provider signals only rerank a bounded,
  already eligible candidate pool.
- `LastMix` is selectable only while the LastMix Lyrion plugin is installed;
  `API Key` is always selectable but neutral without a valid key.
- Providers are separately installable and disabled by default in every host.
- The Last.fm API key is provider-owned LMS preference data. It must never
  occur in JSONL, HTTP request bodies, provider options, artifacts, command
  arguments, output JSON, LMS logs, crash reports, or test snapshots.
- Use `guidance_provider_process_environment_v1` only as a trusted in-process
  hook. Its values must not enter descriptor or native-SPI configuration
  structures.
- In direct mode all network work happens during `prepare`; `score` is
  network-free, bounded, deterministic for one prepared session, and does not
  query whole libraries.
- Preserve the existing Better Call Bliss and Bliss Mixer Lab settings UI,
  selection policy, and logging wording. Provider rendering uses the shared
  canonical settings assets.
- Package `lms-guidance-lastfm` and every supported native binary platform as
  its own Lyrion extension. Do not bundle it inside either host.

## Review Focus

- A previously selected LastMix mode becomes unavailable after LastMix is
  uninstalled: show unavailable status and produce neutral guidance, never a
  hidden fallback to direct API mode.
- A direct API key changes while Lab's mixer sidecar is alive: restart the
  sidecar before the next direct-provider request and do not expose the key in
  its command line or startup log.
- A cache miss, timeout, invalid response, rate limit, or cancellation during
  direct `prepare`: preserve a valid Bliss-only host result with concise,
  redacted diagnostics.
- Last.fm artist identity prefers artist MBID and falls back to normalized name
  only when the MBID relation is absent; track and artist evidence remain
  independent channels.
- Provider-specific controls inherit provider defaults until a host or job
  explicitly overrides them; explicit `0` remains an override that disables a
  channel.

---

## File structure

| Repository | Files | Responsibility |
| --- | --- | --- |
| `lms-guidance-lastfm` (new) | `LastFmGuidance/{Plugin,Provider,Settings}.pm`, settings template, strings, `install.xml`, tests, packaging workflow | Lyrion provider descriptor, own settings, source availability, safe host hooks, release package. |
| `lms-bliss-guidance-host` | `Plugins/BlissGuidance/Discovery.pm`, fixture/tests, README | Validate and expose the non-serialized process-environment hook without changing canonical UI behavior. |
| `lms-bliss-guidance-provider-kit` | descriptor fixture, README | Document the optional secret-environment and acquisition-hook boundary for future providers. |
| `bliss-guidance-lastfm` | `src/main.rs`, new adapter/cache modules, fixtures/tests, README | Artifact regression adapter plus direct API-key preparation, cache, identity matching, diagnostics. |
| `bliss-playlist-guidance-spi` | `SPI.md`, schemas/tests only if needed | Specify trusted provider modes and ensure raw secrets are excluded from the wire contract. |
| `lms-better-call-bliss` | provider acquisition adapter, jobs/request builder, settings/extras tests, docs | Discover/enable provider, use provider acquisition, inject environment into optimizer process, preserve per-job policy and reporting. |
| `lms-blissmixer-lab` | mixer startup, provider integration, tests/docs | Discover/enable provider, pass environment when launching `bliss-mixer`, use its existing `/api/guidance/score` path, preserve logs. |

### Task 1: Define safe provider lifecycle hooks

**Files:**
- Modify: `lms-bliss-guidance-host/Plugins/BlissGuidance/Discovery.pm`
- Modify: `lms-bliss-guidance-host/tests/*`
- Modify: `lms-bliss-guidance-provider-kit/fixtures/provider-descriptor-v1-all-controls.json`
- Modify: `lms-bliss-guidance-provider-kit/README.md`

**Interfaces:**
- Produces: optional Perl hook
  `guidance_provider_process_environment_v1($resolved_policy, $trusted_context) -> \%environment`.
- Produces: optional acquisition hook contract returning only trusted artifact
  descriptors or a neutral diagnostic; it may never return raw credentials.
- Consumes: provider descriptor/default/status/native-config interfaces already
  used by Library Signals.

- [ ] Add failing host-library tests proving environment values remain separate
  from `native_spi_config` and are not included in a serialized native payload.
- [ ] Implement discovery validation and a host-facing accessor for the optional
  environment hook; accept only a non-empty environment-variable name and an
  opaque scalar value, and redact it from diagnostics.
- [ ] Add failing fixture/contract tests for a provider declaring Last.fm
  source/default controls and an acquisition capability.
- [ ] Document the hook boundary in the provider kit: provider owns secrets,
  host owns process launch, and neither exposes values in descriptor/UI JSON.
- [ ] Run the focused Perl/provider-kit tests and commit the shared contract.

### Task 2: Create `lms-guidance-lastfm`

**Files:**
- Create: `lms-guidance-lastfm/LastFmGuidance/Plugin.pm`
- Create: `lms-guidance-lastfm/LastFmGuidance/Provider.pm`
- Create: `lms-guidance-lastfm/LastFmGuidance/Settings.pm`
- Create: `lms-guidance-lastfm/LastFmGuidance/HTML/EN/plugins/LastFmGuidance/settings/lastfmguidance.html`
- Create: `lms-guidance-lastfm/LastFmGuidance/strings.txt`
- Create: `lms-guidance-lastfm/LastFmGuidance/install.xml`
- Create: `lms-guidance-lastfm/tests/{provider_descriptor,settings_contract,plugin_contract,installed_layout}.t`
- Create: `lms-guidance-lastfm/.github/workflows/release.yml`

**Interfaces:**
- Produces: descriptor `provider_id => 'lastfm'`, display name `Bliss Guidance:
  Last.fm`, Last.fm signal channel declarations, native provider path/status,
  shared defaults, and the two lifecycle hooks from Task 1.
- Consumes: LastMix public plugin API only in `LastMix` acquisition mode and
  `bliss-guidance-lastfm version --json` for binary compatibility.

- [ ] Add failing descriptor tests: plugin has a provider-owned settings URI,
  `LastMix`/`API Key` source enum, and controls for track influence, artist
  mode, and artist level.
- [ ] Implement provider preferences with safe factory defaults and a revision
  counter. Render source selection, API-key help, conditional API-key field,
  status, and the standard `settings/footer.html` Save control.
- [ ] Implement LastMix presence detection. An unavailable LastMix selection
  remains visible as an invalid configuration with an actionable reason; it
  must not silently switch sources.
- [ ] Implement `guidance_provider_process_environment_v1`: return an empty
  map outside direct mode; in direct mode return only the job/sidecar
  environment variable carrying the API key. Do not log the key.
- [ ] Implement provider status/native-SPI configuration and a source-neutral
  effective policy resolver. Verify missing binary, missing key, and missing
  LastMix states.
- [ ] Package a source-only plugin archive with platform binary placeholders and
  run the provider contract/layout tests before committing.

### Task 3: Preserve artifact mode and add direct acquisition in Rust

**Files:**
- Modify: `bliss-guidance-lastfm/src/main.rs`
- Create: `bliss-guidance-lastfm/src/{artifact,direct,cache,lastfm_api,diagnostics}.rs`
- Create: `bliss-guidance-lastfm/tests/{artifact_mode,direct_mode,cache,redaction}.rs`
- Modify: `bliss-guidance-lastfm/Cargo.toml`
- Modify: `bliss-guidance-lastfm/README.md`

**Interfaces:**
- Consumes: `prepare.options.acquisition_mode` of `artifact` or `direct`,
  trusted anchors, and the process environment variable named by trusted
  integration configuration.
- Produces: existing `lastfm_track`/`lastfm_artist` signals plus aggregate,
  redacted prepared diagnostics and the existing provider policy capabilities.

- [ ] Add artifact-mode regression fixtures from current resolved LastMix
  evidence and tests proving output signals remain byte-for-byte equivalent.
- [ ] Add failing direct-mode tests using a local mock Last.fm HTTP server:
  deduplicated anchor queries, positive/negative cache behavior, MBID-first
  identity joins, and no request during `score`.
- [ ] Implement a persistent versioned cache with TTL, bounded concurrent
  `prepare` requests, cancellation, deadlines, rate-limit/backoff handling,
  and sanitized aggregate diagnostics.
- [ ] Implement direct API parsing for similar artists and tracks. Freeze the
  decoded relations after `prepare`; score only supplied candidates and never
  perform outbound I/O.
- [ ] Add secret-redaction tests over errors, diagnostics, serialized requests,
  artifacts, and snapshots. Run `cargo test --locked` and commit.

### Task 4: Make Better Call Bliss consume the provider

**Files:**
- Modify: `lms-better-call-bliss/BetterCallBliss/{Jobs,RequestBuilder,LastFmEvidence}.pm`
- Modify: `lms-better-call-bliss/BetterCallBliss/Plugins/BlissGuidance/*` only
  through a refreshed source-vendored shared-host revision
- Modify: `lms-better-call-bliss/tests/{guidance_provider_*,lastfm_evidence,request_json_types,log_diagnostics}.t`
- Modify: `lms-better-call-bliss/docs/{GUIDANCE_DATA_FLOW.md,ARCHITECTURE.md}`

**Interfaces:**
- Consumes: `lms-guidance-lastfm` descriptor, resolved host/job policy,
  provider acquisition hook, and secret environment map.
- Produces: optimizer request with no raw key, provider-specific diagnostics,
  current preview provenance, and a process environment scoped to the optimizer
  child.

- [ ] Add failing tests that prove the provider is discovered disabled by
  default, its controls use canonical UI rendering, and an explicit per-job
  `0` disables only the selected Last.fm channel.
- [ ] Move existing LastMix evidence collection behind the provider acquisition
  hook. Preserve its frozen resolved artifact, identity mapping, cache behavior,
  progress updates, and neutral fallback.
- [ ] Apply the provider environment only with localized `%ENV` while spawning
  `bliss-playlist-optimizer`; verify the request file, arguments, result, and
  logs do not contain the API key.
- [ ] Map artifact/direct preparation diagnostics into the established Extras
  preview and LMS log vocabulary without changing unrelated guidance reporting.
- [ ] Run focused Perl tests plus a real LastMix-mode preview and direct-mode
  mocked/offline previews; commit Better Call Bliss changes.

### Task 5: Make Bliss Mixer Lab consume the provider

**Files:**
- Modify: `lms-blissmixer-lab/BlissMixerLab/{Plugin,GuidanceProviderAdapter}.pm`
- Modify: `lms-blissmixer-lab/BlissMixerLab/Plugins/BlissGuidance/*` only via
  the same vendored shared-host revision as Better Call Bliss
- Modify: `lms-blissmixer-lab/tests/{guidance_provider_adapter,plugin_contract,validate_repository.py}`
- Modify: `lms-blissmixer-lab/{GUIDANCE_PROVIDER_HOST_INTEGRATION.md,RUST_GUIDANCE_MIGRATION.md}`

**Interfaces:**
- Consumes: the provider descriptor, resolved host policy, LastMix artifact
  acquisition result or direct-mode sidecar environment, and existing
  `/api/guidance/score` response.
- Produces: unchanged Lab selection log lines and reranking behavior for the
  DSTM pool, plus source/availability diagnostics.

- [ ] Add failing tests that the discoverable provider is disabled by default,
  uses the canonical shared controls, and retains inherited/host-override
  behavior exactly as Better Call Bliss.
- [ ] For LastMix mode, acquire provider-owned evidence after the DSTM pool is
  known and before the existing guidance endpoint call; avoid a second
  candidate-ranking path.
- [ ] At sidecar launch, apply the resolved direct-mode provider environment
  with localized `%ENV`; changing direct-provider settings marks the sidecar for
  restart before it can service another mix.
- [ ] Preserve `_selectionLogLines` and diagnostics wording. Add golden tests
  comparing Library Signals logs before/after and Last.fm signal trace mapping.
- [ ] Run the Perl and Python contract suites plus Pi LastMix/direct/offline
  smoke tests; commit Lab changes.

### Task 6: Release, integration, and operational verification

**Files:**
- Modify: `lms-guidance-lastfm/README.md`
- Modify: `lms-guidance-lastfm/scripts/update_lms_plugins_repo.py`
- Modify: `lms-plugins/repo.xml` via the release automation
- Modify: host READMEs and release notes only where installation behavior
  changes.

**Interfaces:**
- Produces: a signed/reproducible provider release containing all supported
  platform binaries and an extension-repository entry.

- [ ] Build and test Linux ARM64, ARMHF, x86_64 Linux, Windows, and macOS
  provider binaries in GitHub Actions; attach them only to the provider release.
- [ ] Verify LastMix mode, direct cold-cache and warm-cache mode, unavailable
  LastMix, empty/invalid API key, offline fallback, cancellation, and
  no-guidance Bliss-only operation on `192.168.1.111`.
- [ ] Verify that hosts do not automatically enable the provider after an
  install, and that each host's UI/default/override behavior is unchanged until
  it is explicitly enabled.
- [ ] Scan release artifacts, job files, LMS logs, and diagnostics for the test
  key; require no matches before publishing.
- [ ] Publish the provider, update the extension repository, and document the
  final source/configuration behavior.
