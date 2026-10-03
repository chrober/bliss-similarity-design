# Lyrion Host-Pull Guidance Providers Implementation Plan

> **Delivery status (2026-10-03): Delivered.** The Library Signals provider,
> Better Call Bliss host-pull discovery and trusted native configuration,
> canonical shared host support, release packaging, and Raspberry Pi acceptance
> were completed. This document retains its original unchecked task list as an
> implementation record; new work belongs to separate provider plans, starting
> with Last.fm, rather than to another provider-discovery mechanism.

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the first independently installable Lyrion guidance provider, `lms-guidance-library-signals`, and let Better Call Bliss discover, configure, and invoke it through the existing native guidance SPI without a central registry plugin.

**Architecture:** A provider publishes a stable Perl descriptor through `guidance_provider_descriptor_v1`; Better Call Bliss discovers that descriptor from Lyrion's enabled-plugin list, validates its serializable contract, resolves provider defaults plus host/job overrides, and calls the provider's trusted `native_spi_config_v1` factory. Better Call Bliss passes the resulting frozen configuration to `bliss-playlist-optimizer`, which launches the Rust provider over JSONL. The provider reads only the hash-bound eligible-candidate identity artifact and a read-only `persist.db` snapshot; it returns bounded signals for Bliss-qualified candidates.

**Tech Stack:** Lyrion Perl plugin APIs (`Slim::Plugin::Base`, `Slim::Utils::PluginManager`, `Slim::Utils::Prefs`, `Slim::Web::Settings`), Template Toolkit, Rust, `rusqlite`, existing JSONL SPI v2, GitHub Actions release packaging.

**Spec:** [`2026-09-26-lyrion-guidance-provider-discovery-design.md`](../specs/2026-09-26-lyrion-guidance-provider-discovery-design.md)

## Global Constraints

- Do not create `lms-bliss-guidance`, a central registry plugin, a plugin-directory scan, or automatic plugin installation.
- Providers publish descriptors; hosts discover enabled provider modules through `Slim::Utils::PluginManager` and stay provider-neutral.
- Every discovered provider is disabled by default in every host. Installation must not change candidate selection, make network calls, open databases, or start Rust processes.
- Preserve the precedence order: per-job override, explicit host override, provider saved default, provider factory default. Explicit `0` and `false` are overrides, not absence.
- Bliss remains authoritative for eligibility, acoustic ranking, route validity, repeat windows, genres, virtual-library scope, and final selection. Guidance can only apply bounded boosts or penalties to Bliss-qualified candidates.
- Provider settings pages own source configuration and shared defaults. Hosts own provider enablement and sparse host/job overrides. Hosts never read another plugin's preferences directly.
- `prepare.options` is a JSON object in the native request and then a JSONL field, not a file. Native binaries never read Lyrion preferences.
- Provider executable paths, resource paths, and artifact paths are resolved only by trusted host/provider code, never by web form values.
- The library-signals provider reads `persist.db` read-only inside one job-scoped SQLite snapshot. It must never write Lyrion databases or retain the complete raw signal population in RAM.
- Keep the existing direct Last.fm path unchanged. Last.fm provider migration and APC are later, independent provider slices.
- Do not modify upstream `lms-blissmixer-origin`. The maintained `D:\LMS\bliss-mixer` fork is a future second native host and must consume the same fixture/contract rather than a second discovery mechanism.

## Review Focus

- An enabled provider whose effective influences are all `0` must produce no native addon launch and exactly the same Bliss-only result as a disabled provider.
- A provider default changed after job start must affect the next job only; the active native request, `prepare.options`, and policy weights must remain frozen.
- A malformed descriptor, duplicate provider ID, unavailable native binary, unavailable `persist.db`, or failed provider `prepare` must yield a successful Bliss-only preview with a diagnostic, never a failed route.
- `persist.db` must be opened read-only and queried only through candidate `urlmd5` identities; no provider or host may accept a database path from user input.
- The provider settings page must not perform candidate scans, SQLite reads, native startup, or Last.fm acquisition; all collection begins only after native `prepare`.

---

### Task 1: Publish the versioned Lyrion provider-descriptor contract

**Files:**
- Create: `D:\LMS\bliss-playlist-guidance-spi\LYRION_PROVIDER_DISCOVERY.md`
- Create: `D:\LMS\bliss-playlist-guidance-spi\schemas\lyrion-guidance-provider-descriptor-v1.schema.json`
- Create: `D:\LMS\bliss-playlist-guidance-spi\fixtures\lyrion-provider-descriptor-v1-library-signals.json`
- Modify: `D:\LMS\bliss-playlist-guidance-spi\README.md`
- Modify: `D:\LMS\bliss-playlist-guidance-spi\SPI.md`
- Modify: `D:\LMS\bliss-playlist-guidance-spi\src\lib.rs`

**Interfaces:**
- Produces serializable descriptor data with `protocol_version: 1`, `provider_id`, display metadata, capabilities, scopes, host-exposable control schema, and native SPI metadata.
- Defines Perl runtime methods `guidance_provider_descriptor_v1()`, `guidance_provider_defaults_v1()`, `guidance_provider_status_v1()`, and `guidance_provider_native_spi_config_v1($resolved_policy, $trusted_job_context)`.
- Produces the canonical library-signals fixture. Code references are intentionally absent from JSON and are checked separately by host/provider contract tests.

- [ ] **Step 1: Write failing fixture and schema tests**

Add Rust tests that load the canonical descriptor fixture, validate its schema, require stable provider ID `library-signals`, native provider ID `library-signals-guidance`, and channel mappings `play_count -> playcount`, `last_played -> last_played`, `library_age -> library_age`.

- [ ] **Step 2: Run the focused tests to verify they fail**

Run: `cargo test --locked lyrion_provider_descriptor` from `D:\LMS\bliss-playlist-guidance-spi`  
Expected: FAIL because the descriptor schema and fixture do not exist.

- [ ] **Step 3: Define the descriptor and runtime boundary**

Document that the descriptor is pure metadata and that a host must discover only enabled modules via `Slim::Utils::PluginManager`. Define strict control types (`integer`, `boolean`, `enum`), stable IDs, `global_candidate`/`edge_candidate` scopes, supported native policy modes, default revision, and native SPI metadata. Document that `native_spi_config_v1` receives only typed trusted context: identity-artifact descriptor, trusted resource resolver, frozen `as_of` time, and effective policy.

- [ ] **Step 4: Define the complete data flow in the normative SPI documentation**

Add the same file/payload distinction as the approved design: host writes native request plus hash-bound identity artifact; native host reads request then sends JSONL `describe`, `prepare`, and `score`; provider reads the artifact and read-only `persist.db`; provider returns JSONL `scores`. State that `options` is a JSON message field, never a path.

- [ ] **Step 5: Run SPI checks**

Run: `cargo test --locked`  
Expected: all tests pass.

- [ ] **Step 6: Commit the public contract**

```powershell
git add README.md SPI.md LYRI* schemas fixtures src
git commit -m "feat: define Lyrion guidance provider descriptors"
```

### Task 2: Create the standalone `lms-guidance-library-signals` Lyrion provider

**Files:**
- Create: `D:\LMS\lms-guidance-library-signals\LibrarySignals\Plugin.pm`
- Create: `D:\LMS\lms-guidance-library-signals\LibrarySignals\Provider.pm`
- Create: `D:\LMS\lms-guidance-library-signals\LibrarySignals\Settings.pm`
- Create: `D:\LMS\lms-guidance-library-signals\LibrarySignals\install.xml`
- Create: `D:\LMS\lms-guidance-library-signals\LibrarySignals\strings.txt`
- Create: `D:\LMS\lms-guidance-library-signals\LibrarySignals\HTML\EN\plugins\LibrarySignals\settings\librarysignals.html`
- Create: `D:\LMS\lms-guidance-library-signals\tests\provider_descriptor.t`
- Create: `D:\LMS\lms-guidance-library-signals\tests\settings_contract.t`
- Create: `D:\LMS\lms-guidance-library-signals\README.md`
- Create: `D:\LMS\lms-guidance-library-signals\.github\workflows\ci.yml`

**Interfaces:**
- Produces `Plugins::LibrarySignals::Provider::guidance_provider_descriptor_v1()` matching Task 1's fixture.
- Produces `guidance_provider_defaults_v1`, `guidance_provider_status_v1`, and `guidance_provider_native_spi_config_v1`.
- Owns default controls: `playcount_influence`, `last_played_influence`, `last_played_horizon_days`, `library_age_influence`, and `library_age_horizon_days`.

- [ ] **Step 1: Write failing provider contract tests**

Test descriptor/fixture parity; plugin-owned preference namespace; neutral factory defaults for the three influences; 180/365-day horizon defaults; no provider activation on installation; an unavailable binary/database status; and a settings-page construction path that performs no SQLite or native-process work.

- [ ] **Step 2: Run the provider tests to verify they fail**

Run: `& 'C:\Program Files\Git\usr\bin\perl.exe' tests\provider_descriptor.t` from `D:\LMS\lms-guidance-library-signals`  
Expected: FAIL because the plugin does not exist.

- [ ] **Step 3: Implement provider lifecycle and descriptor publication**

Use `Slim::Plugin::Base`, a provider-specific preference namespace, and `Slim::Web::Settings`. `guidance_provider_descriptor_v1` returns descriptor metadata only. It must not enumerate hosts, call host APIs, read `persist.db`, or invoke Rust.

- [ ] **Step 4: Implement provider defaults, status, and native backend factory**

Validate all controls against the schema. The factory resolves the platform-specific `bliss-guidance-library-signals` executable from this plugin's own `Bin` tree; verifies its `version --json` reports SPI v2 and provider ID `library-signals-guidance`; resolves the trusted read-only `persist.db` location; and returns `options` containing frozen `as_of_unix_seconds` plus the two horizons. It must never receive a raw executable/database path from the host or form.

- [ ] **Step 5: Implement the provider settings page**

Render provider defaults, native/version/database status, and the meaning of inherited host values. Saving valid values increments the provider settings revision. State that saved defaults do not activate the provider in any host.

- [ ] **Step 6: Package native binaries without committing them**

Create release automation which downloads checksum-verified `bliss-guidance-library-signals` artifacts for x86_64 Linux, AArch64 Linux, armhf Linux, macOS, and Windows, places them under the release package's provider `Bin` paths, and tests that source control contains no executable assets.

- [ ] **Step 7: Run provider tests and commit**

Run: `& 'C:\Program Files\Git\usr\bin\perl.exe' tests\provider_descriptor.t; & 'C:\Program Files\Git\usr\bin\perl.exe' tests\settings_contract.t`  
Expected: all tests pass.

```powershell
git add LibrarySignals tests README.md .github
git commit -m "feat: add library signals guidance provider"
```

### Task 3: Add generic host-pull discovery and policy resolution to Better Call Bliss

**Files:**
- Create: `D:\LMS\lms-better-call-bliss\BetterCallBliss\GuidanceProviderDiscovery.pm`
- Create: `D:\LMS\lms-better-call-bliss\BetterCallBliss\GuidanceProviderPolicy.pm`
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\Plugin.pm`
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\BlissCompatibility.pm`
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\Defaults.pm`
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\Settings.pm`
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\strings.txt`
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\HTML\EN\plugins\BetterCallBliss\settings\bettercallbliss.html`
- Create: `D:\LMS\lms-better-call-bliss\tests\guidance_provider_discovery.t`
- Create: `D:\LMS\lms-better-call-bliss\tests\guidance_provider_policy.t`

**Interfaces:**
- `GuidanceProviderDiscovery::discover()` returns stable-ID-ordered, validated provider descriptors plus availability/error information.
- `GuidanceProviderPolicy::resolve($descriptor, $host_state, $job_overrides)` returns `{ enabled, effective, origins, provider_revision, descriptor_version, diagnostic }`.
- `GuidanceProviderDiscovery::native_spi_config($provider, $resolved_policy, $trusted_job_context)` calls only the provider's `guidance_provider_native_spi_config_v1` factory.

- [ ] **Step 1: Write failing discovery tests**

Use fake enabled Lyrion modules to cover discovery; descriptor absence; malformed metadata; incompatible protocol; deterministic duplicate-ID rejection; and a late enabled provider becoming visible on the next discovery refresh. Assert no directory scanning and no direct provider preference reads.

- [ ] **Step 2: Run the focused discovery test to verify it fails**

Run: `& 'C:\Program Files\Git\usr\bin\perl.exe' tests\guidance_provider_discovery.t`  
Expected: FAIL because generic discovery does not exist.

- [ ] **Step 3: Implement descriptor discovery and validation**

Discover enabled plugin modules using `Slim::Utils::PluginManager`, check `can('guidance_provider_descriptor_v1')`, invoke the method defensively, and validate its serializable portion against Task 1's contract. Sort provider IDs deterministically; surface duplicate/incompatible providers as unavailable; cache only metadata/status until settings/job refresh.

- [ ] **Step 4: Write failing policy-resolution tests**

Cover disabled-by-default provider state; provider-default inheritance; explicit host zero; explicit per-job zero; reset-to-inherit; invalid inherited/overridden cross-field combinations; current provider revision; and immutable job snapshots.

- [ ] **Step 5: Implement sparse host policy semantics**

Store only host enablement and a presence-aware sparse override map under Better Call Bliss preferences. Do not copy inherited defaults. Migrate current local-signal values into disabled sparse host overrides, preserving values but making no behavior change until the user enables the newly discovered provider.

- [ ] **Step 6: Implement Better Call Bliss settings integration**

Render one schema-derived section per discovered provider: status, explicit enablement, link to its own settings page, origin/effective value, override/reset controls, and precise unavailable diagnostics. The initial page must work for library signals without hard-coded provider UI logic beyond the generic schema renderer.

- [ ] **Step 7: Run Better Call Bliss discovery/policy tests and commit**

Run: `& 'C:\Program Files\Git\usr\bin\perl.exe' tests\guidance_provider_discovery.t; & 'C:\Program Files\Git\usr\bin\perl.exe' tests\guidance_provider_policy.t`  
Expected: all tests pass.

```powershell
git add BetterCallBliss tests
git commit -m "feat: discover Lyrion guidance providers"
```

### Task 4: Migrate Better Call Bliss library signals to provider-owned native configuration

**Files:**
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\RequestBuilder.pm`
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\Jobs.pm`
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\JobOptions.pm`
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\Web.pm`
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\GuidanceReporting.pm`
- Modify: `D:\LMS\lms-better-call-bliss\BetterCallBliss\HTML\EN\plugins\BetterCallBliss\index.html`
- Modify: `D:\LMS\lms-better-call-bliss\tests\request_json_types.t`
- Modify: `D:\LMS\lms-better-call-bliss\tests\job_options.t`
- Create: `D:\LMS\lms-better-call-bliss\tests\guidance_provider_request.t`

**Interfaces:**
- Consumes a frozen resolved provider policy plus the trusted candidate-identity artifact from `CandidateInventory`.
- Produces native request `guidance_addons` from provider factories and separate `guidance_policy` entries from host policy.
- Retires Better Call Bliss ownership of `findbin('bliss-guidance-library-signals')` and direct `persist.db` lookup.

- [ ] **Step 1: Write failing request-boundary tests**

Assert that an enabled library-signals provider with at least one non-zero effective influence produces one addon with trusted `program`, identity artifact SHA-256, read-only `persist.db`, and the frozen `prepare.options` fields. Assert policy weights are separate; all-zero/disabled/unavailable provider produces no addon; malformed factory output degrades to neutral guidance.

- [ ] **Step 2: Run the focused request test to verify it fails**

Run: `& 'C:\Program Files\Git\usr\bin\perl.exe' tests\guidance_provider_request.t`  
Expected: FAIL because request construction still owns direct library-signals configuration.

- [ ] **Step 3: Refactor request construction around generic provider factories**

At job start, capture the resolved policy, provider revision, descriptor version, trusted candidate identity artifact, and one frozen clock value. Pass that typed context to `native_spi_config_v1`; validate its returned program/options/artifacts/resources against the descriptor before serializing the optimizer request. Generate channel policy weights separately. Retain existing Last.fm construction unchanged.

- [ ] **Step 4: Update Extras controls and preview provenance**

Show provider-derived controls only when the provider is enabled and compatible. Preserve effective values after a preview and explain contribution origin in results. Keep `as_of_unix_seconds` internal: display horizons and signal rationale, never the raw frozen epoch.

- [ ] **Step 5: Preserve neutral failure behavior**

On missing provider, incompatible binary, inaccessible `persist.db`, factory error, SPI timeout, or malformed provider response: continue the preview with Bliss-only selection, record provider ID plus failure category, and never expose trusted paths or raw provider errors in the normal UI.

- [ ] **Step 6: Run Better Call Bliss regression suite and commit**

Run:

```powershell
& 'C:\Program Files\Git\usr\bin\perl.exe' tests\guidance_provider_request.t
& 'C:\Program Files\Git\usr\bin\perl.exe' tests\request_json_types.t
& 'C:\Program Files\Git\usr\bin\perl.exe' tests\job_options.t
& 'C:\Program Files\Git\usr\bin\perl.exe' tests\metadata_hygiene.t
```

Expected: all focused tests pass. Run full CI in GitHub for the complete Lyrion/DBI environment.

```powershell
git add BetterCallBliss tests
git commit -m "feat: route library signals through provider discovery"
```

### Task 5: Document parity boundaries and prepare future `bliss-mixer` reuse

**Files:**
- Modify: `D:\LMS\lms-better-call-bliss\README.md`
- Modify: `D:\LMS\lms-better-call-bliss\docs\GUIDANCE_DATA_FLOW.md`
- Modify: `D:\LMS\bliss-playlist-optimizer\README.md`
- Modify: `D:\LMS\bliss-playlist-optimizer\docs\ARCHITECTURE.md`
- Modify: `D:\LMS\lms-better-call-bliss\IMPROVEMENT_BACKLOG.md`
- Modify: `D:\LMS\bliss-similarity-design\docs\superpowers\specs\2026-09-26-lyrion-guidance-provider-discovery-design.md`

**Interfaces:**
- Produces one cross-repository documented flow from provider settings through the host request and native JSONL SPI to preview provenance.
- Leaves `D:\LMS\bliss-mixer` unchanged but gives its future integration the canonical descriptor fixture and explicit no-duplication requirements.

- [ ] **Step 1: Add documentation/fixture parity checks**

Add Better Call Bliss tests which load Task 1's fixture and prove the request contains the expected native provider ID, channels, artifact kind, resource kind, and `prepare.options` keys. Add a documentation check that links use the stable SPI/provider/host repository URLs.

- [ ] **Step 2: Update public documentation**

Explain that Lyrion discovery happens outside the native optimizer; the optimizer only receives trusted `guidance_addons` plus `guidance_policy` and launches providers. Document the full file/message flow, normal failure degradation, and future `bliss-mixer` reuse. Change the backlog row from a shared-registry proposal to host-pull descriptor discovery; mark it implemented only after Task 6 acceptance succeeds.

- [ ] **Step 3: Run documentation and fixture checks**

Run the added fixture test, Better Call Bliss `metadata_hygiene.t`, and the repository documentation checker if available.  
Expected: all checks pass and Mermaid blocks render without parse errors.

- [ ] **Step 4: Commit documentation**

```powershell
git add README.md docs IMPROVEMENT_BACKLOG.md tests
git commit -m "docs: explain host-pull guidance flow"
```

### Task 6: Release packages and Pi acceptance

**Files:**
- Create/Modify: `D:\LMS\lms-guidance-library-signals\.github\workflows\release.yml`
- Modify: `D:\LMS\lms-better-call-bliss\.github\workflows\ci.yml`
- Modify: `D:\LMS\lms-better-call-bliss\.github\workflows\release.yml`
- Modify: `D:\LMS\lms-plugins\repo.xml`
- Modify: `D:\LMS\lms-plugins\README.md`

**Interfaces:**
- Produces an independently installable library-signals provider package containing platform-specific Rust binaries and an updated Better Call Bliss package that does not bundle that provider.

- [ ] **Step 1: Add packaging tests**

Require source repositories to contain no committed binaries, releases to carry all supported platform binaries with verified checksums, and `repo.xml` entries to offer the provider and Better Call Bliss independently.

- [ ] **Step 2: Build and publish release candidates**

Run native-provider tests and build the Rust binary in GitHub Actions. Package the provider plugin with exact release assets, then build Better Call Bliss against the stable descriptor fixture. Do not publish a plugin dependency declaration that Lyrion cannot enforce.

- [ ] **Step 3: Perform Pi acceptance on `192.168.1.111`**

Install the provider and Better Call Bliss, restart LMS once, then verify:

1. Library Signals has its own settings page and no database/native access occurs while opening it.
2. Better Call Bliss discovers the provider but keeps it disabled initially.
3. Enabling it inherits provider defaults; explicit `0` remains `0` after restart.
4. A real playlist preview records the provider's signals and horizons while retaining Bliss-only eligibility.
5. Changing provider defaults affects a new preview but not an already-running preview.
6. Disabling the provider, removing its executable, and making `persist.db` unavailable each produce a successful Bliss-only preview with an actionable diagnostic.

- [ ] **Step 4: Publish final versions and update extension metadata**

Publish only after CI and every Pi case pass. Record provider and Better Call Bliss versions, artifact SHA-256 values, test job IDs, and the accepted request/result artifacts in release notes or the next implementation checkpoint.

## Future `bliss-mixer` Guardrail

This plan intentionally does not modify `D:\LMS\bliss-mixer`. A later plan must make the fork a second native SPI host while ranking its own Bliss-derived DSTM candidate pool. It must reuse Task 1's fixture, the same descriptor method names, the same default/override precedence, and the same bounded channel semantics. It must not read provider preference namespaces, copy provider code, or create a competing discovery protocol.
