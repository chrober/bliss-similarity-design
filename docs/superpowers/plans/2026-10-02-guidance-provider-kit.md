# Lyrion Guidance Provider Kit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a reusable provider-authoring kit and one canonical host settings renderer so guidance providers are visually and behaviorally consistent in every Lyrion host.

**Architecture:** `lms-bliss-guidance-provider-kit` supplies authoring documentation, a scaffold, descriptor fixtures, and compatibility tests. `lms-bliss-guidance-host` owns a normalized settings render model plus canonical Template Toolkit and browser assets. Better Call Bliss and Bliss Mixer Lab vendor those assets unchanged and assert parity in CI.

**Tech Stack:** Lyrion Perl, Template Toolkit, browser JavaScript, Lyrion provider descriptor v1, JSONL SPI v2.

**Spec:** [`2026-09-26-lyrion-guidance-provider-discovery-design.md`](../specs/2026-09-26-lyrion-guidance-provider-discovery-design.md)

## Current delivery status

The Library Signals provider-discovery vertical slice and the shared-host
consolidation are delivered. Better Call Bliss and Bliss Mixer Lab discover the
provider descriptor, resolve defaults and host overrides, obtain trusted native
SPI configuration, and vendor the shared settings model plus canonical assets
with parity tests. Tasks 1 through 4 are therefore complete. The first native
`bliss-mixer` Library Signals host endpoint and `selection_trace_v1` are also
delivered; Lab already uses that endpoint for enabled native-provider DSTM
candidate pools. This plan is retained as an implementation record rather than
an active task list.

## Global Constraints

- Bliss remains authoritative; providers add only bounded secondary guidance to Bliss-qualified candidates.
- A provider plugin may be Perl-only for discovery, settings, defaults, and light host-side work. Rust is preferred, but not required, for JSONL provider execution.
- No raw provider HTML, JavaScript, CSS, callbacks, or trusted paths may be injected into a host.
- Provider settings own source configuration and defaults. Hosts own disabled-by-default enablement and sparse overrides. Explicit `0` and `false` remain overrides.
- Preserve precedence: per-job override, host override, provider saved default, provider factory default.
- The descriptor decides `render_as`, range, step, order, label, help, and overridability. Hosts must not infer widget style from value type.
- Saving remains explicit. `Use inherited default` changes the form and source annotation immediately, but does not save.
- Canonical UI assets must be vendor-copied byte-for-byte and verified in host CI; prose is not sufficient to prevent visual drift.
- Native guidance hosts must return structured facts, never preformatted user-facing log text. Perl hosts retain ownership of localization and the exact existing Lyrion log format.
- Define two independent, versioned explainability payloads: `evidence_acquisition_trace_v1` for collection of external evidence such as LastMix requests, and `selection_trace_v1` for how a Bliss-qualified candidate was affected and selected.

## Review Focus

- A horizon declared as `number` remains a number input in provider, Better Call Bliss, Lab, and Extras forms.
- Toggling provider enablement immediately hides/shows controls without saving and does not submit stale values.
- Explicit host override `0` survives save/reload; inherited provider values update only in subsequent jobs.
- `Use inherited default` updates the visible origin without submitting the page and is absent for already inherited values.
- Unavailable providers expose no active controls or trusted file paths.
- A frozen Lab fixture produces byte-for-byte identical `Candidate selection`, candidate detail, `Diagnostics`, and `Selection` log lines before and after native guidance-host migration.

---

### Task 1: Define the canonical host-settings contract

**Files:**
- Create: `D:\LMS\lms-bliss-guidance-host\Plugins\BlissGuidance\SettingsModel.pm`
- Create: `D:\LMS\lms-bliss-guidance-host\HTML\settings\guidance-provider-controls.html`
- Create: `D:\LMS\lms-bliss-guidance-host\HTML\settings\guidance-provider-controls.js`
- Create: `D:\LMS\lms-bliss-guidance-host\GUIDANCE_PROVIDER_HOST_UI.md`
- Create: `D:\LMS\lms-bliss-guidance-host\tests\settings_model.t`
- Create: `D:\LMS\lms-bliss-guidance-host\tests\settings_assets.t`

**Interfaces:**
- `SettingsModel::provider_sections($discovery, $host_state, $host_identity)` produces descriptor-ordered provider/control view models.
- Every control carries exact rendering metadata, effective value, origin, inherited value, and stable form/marker IDs.
- A canonical partial renders provider link, availability, checkbox, controls, origin annotation, and reset action. Shared JavaScript performs unsaved state changes.

- [x] Write failing tests for descriptor order, explicit zero, inherited provider values, `slider`/`number` fidelity, and hidden reset actions for inherited values.
- [x] Run `& 'C:\Program Files\Git\usr\bin\perl.exe' tests\settings_model.t` and verify the missing-model failure.
- [x] Implement the normalized model exclusively from existing discovery/policy results and descriptor metadata; accept host-localized source labels as input.
- [x] Write failing asset tests requiring standard link placement, checkbox behavior, origin annotation, and non-submitting inherited-default buttons.
- [x] Implement canonical Material-Skin-compatible partial/JavaScript and `GUIDANCE_PROVIDER_HOST_UI.md` documenting exact UX behavior.
- [x] Run all `lms-bliss-guidance-host` Perl tests and commit `feat: standardize guidance provider settings UI`.

### Task 2: Create `lms-bliss-guidance-provider-kit`

**Files:**
- Create: `D:\LMS\lms-bliss-guidance-provider-kit\README.md`
- Create: `D:\LMS\lms-bliss-guidance-provider-kit\PROVIDER_AUTHORING_GUIDE.md`
- Create: `D:\LMS\lms-bliss-guidance-provider-kit\templates\LyrionProvider\Plugin.pm`
- Create: `D:\LMS\lms-bliss-guidance-provider-kit\templates\LyrionProvider\Provider.pm`
- Create: `D:\LMS\lms-bliss-guidance-provider-kit\templates\LyrionProvider\Settings.pm`
- Create: `D:\LMS\lms-bliss-guidance-provider-kit\templates\LyrionProvider\HTML\EN\plugins\LyrionProvider\settings\provider.html`
- Create: `D:\LMS\lms-bliss-guidance-provider-kit\fixtures\provider-descriptor-v1-all-controls.json`
- Create: `D:\LMS\lms-bliss-guidance-provider-kit\tests\scaffold_contract.t`

**Interfaces:**
- Documents three provider shapes: configuration-only Perl, language-neutral JSONL executable, and Rust-recommended high-volume provider.
- Provides a fixture with boolean, enum, slider integer, and number controls.
- Points to `bliss-playlist-guidance-spi` for protocol authority and `lms-bliss-guidance-host` for host UX authority.

- [x] Write a failing scaffold-contract test for stable metadata, provider settings URI, `render_as`, no raw markup field, and the standard Save footer.
- [x] Run the test to verify the expected missing-kit failure.
- [x] Implement the kit guide and scaffold: ownership boundaries, security, defaults/overrides, native execution choices, testing, logging, packaging, and host compatibility.
- [x] Run the scaffold test, initialize the repository, and commit `feat: add Lyrion guidance provider kit`.

### Task 3: Migrate Better Call Bliss to the canonical renderer

**Files:**
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\Settings.pm`
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\HTML\EN\plugins\BetterCallBliss\settings\bettercallbliss.html`
- Create: `D:\LMS\lms-better-call-bliss\BetterCallBliss\HTML\EN\plugins\BlissGuidance\settings\guidance-provider-controls.html`
- Create: `D:\LMS\lms-better-call-bliss\BetterCallBliss\HTML\EN\plugins\BlissGuidance\settings\guidance-provider-controls.js`
- Create: `D:\LMS\lms-better-call-bliss\tests\guidance_ui_parity.t`

**Interfaces:**
- Uses the shared render model and unmodified canonical assets.
- Renders provider-specific settings links, source annotations, and inherited-default behavior consistently in settings and relevant Extras controls.

- [ ] Write a failing parity test comparing vendored assets to `lms-bliss-guidance-host`, preserving number controls, explicit zero, and display-name-specific settings link labels.
- [ ] Run the test and verify it fails before migration.
- [ ] Replace duplicated generic provider rendering/interaction only; retain Better Call Bliss-specific job UI and semantics.
- [ ] Run focused settings/policy/metadata tests plus parity test and commit `refactor: use shared guidance provider settings UI`.

### Task 4: Migrate Bliss Mixer Lab to the same renderer

**Files:**
- Modify: `D:\LMS\lms-blissmixer-lab\BlissMixerLab\Settings.pm`
- Modify: `D:\LMS\lms-blissmixer-lab\BlissMixerLab\HTML\EN\plugins\BlissMixerLab\settings\blissmixerlab.html`
- Create: `D:\LMS\lms-blissmixer-lab\BlissMixerLab\HTML\EN\plugins\BlissGuidance\settings\guidance-provider-controls.html`
- Create: `D:\LMS\lms-blissmixer-lab\BlissMixerLab\HTML\EN\plugins\BlissGuidance\settings\guidance-provider-controls.js`
- Create: `D:\LMS\lms-blissmixer-lab\tests\guidance_ui_parity.t`

**Interfaces:**
- Produces the same provider-control DOM and browser behavior as Better Call Bliss.
- Leaves Lab-specific candidate-selection behavior and logging unchanged.

- [ ] Write a failing parity test for canonical assets, control widget fidelity, immediate toggling, and unchanged logging contract.
- [ ] Run it to verify it fails before migration.
- [ ] Replace only Lab’s duplicated generic provider renderer with the shared model and assets.
- [ ] Run Lab settings/provider/discovery/parity tests and commit `refactor: share guidance provider settings UI`.

### Task 5: Define native guidance explainability traces

**Files:**
- Modify: `D:\LMS\bliss-playlist-guidance-spi\SPI.md`
- Modify: `D:\LMS\bliss-playlist-guidance-spi\schemas\guidance-addon-spi-v2.schema.json`
- Modify: `D:\LMS\bliss-playlist-guidance-spi\src\lib.rs`
- Create: `D:\LMS\bliss-playlist-guidance-spi\fixtures\selection-trace-v1-library-signals.json`
- Create: `D:\LMS\bliss-playlist-guidance-spi\fixtures\evidence-acquisition-trace-v1-lastfm.json`
- Modify: `D:\LMS\bliss-mixer\src\api.rs`
- Modify: `D:\LMS\bliss-mixer\src\main.rs`
- Modify: `D:\LMS\lms-blissmixer-lab\BlissMixerLab\Plugin.pm`
- Modify: `D:\LMS\lms-blissmixer-lab\tests\guidance_provider_adapter.t`
- Modify: `D:\LMS\lms-blissmixer-lab\tests\plugin_contract.t`

**Interfaces:**
- `evidence_acquisition_trace_v1` describes provider-side collection facts: source, request/response/failure/cache counts, retained relations, and neutral-degradation category. It does not contain preformatted messages.
- `selection_trace_v1` describes native selection facts for selected candidates: Bliss similarity facts, policy, structured guidance contributions, raw observations, per-channel weights, final score, dominant boost, stochastic key, and cutoff.
- The Perl host renders both traces through its existing logging functions; neither trace changes eligibility, ranking, or selection.

- [ ] Write failing shared-SPI fixture/schema tests for both trace versions, including Last.fm similar-track and similar-artist provenance, Library Signals observations, signed contributions, target-share policy data, and absence of raw rendered messages.
- [ ] Run the focused SPI tests and verify they fail before trace types exist.
- [ ] Add the trace types and versioning rules to the shared contract. Keep acquisition separate from selection: LastMix collection is performed by a provider-side Perl lifecycle hook, while a native host reports the later candidate-selection outcome.
- [ ] Extend the native `bliss-mixer` per-mix guidance result to return a bounded selected-candidate `selection_trace_v1`; full-pool traces are opt-in diagnostics only.
- [ ] Update Lab to format the returned data through its existing logging functions. Do not change user-visible wording, field order, categories, or logger source.
- [ ] Add golden tests proving the current Library Signals log output is byte-for-byte preserved, then commit native-host and Lab changes separately after their respective tests pass.

### Task 6: Document ownership and validate the vertical slice

**Files:**
- Modify: `D:\LMS\bliss-playlist-guidance-spi\LYRION_PROVIDER_DISCOVERY.md`
- Modify: `D:\LMS\bliss-playlist-guidance-spi\README.md`
- Modify: `D:\LMS\lms-guidance-library-signals\README.md`
- Modify: `D:\LMS\lms-better-call-bliss\README.md`
- Modify: `D:\LMS\lms-blissmixer-lab\README.md`
- Modify: `D:\LMS\lms-better-call-bliss\IMPROVEMENT_BACKLOG.md`

- [ ] Add link/contract tests and document the authoritative ownership map: native protocol, provider kit, shared host UI, provider plugin, and host plugin.
- [ ] State that executable JSONL providers are language-neutral, Rust is recommended rather than mandatory, and provider UI is schema-driven rather than raw injection.
- [ ] Run all available Perl contract suites in the kit, shared host, Library Signals, Better Call Bliss, and Lab; then run each GitHub CI workflow.
- [ ] Commit repository-local documentation changes only after verification. Do not release or deploy without a separate user request.

## Self-Review

- The plan adds no registry plugin or automatic installation mechanism.
- The canonical partial, JavaScript, and parity tests directly address the prior slider-versus-number and interaction inconsistencies.
- It preserves distinct ownership of provider defaults and host overrides while making the presentation identical.
- Trace payloads preserve current user-facing logging while separating evidence collection from native selection explanation.
