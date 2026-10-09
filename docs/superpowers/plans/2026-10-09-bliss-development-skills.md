# Bliss Development Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create repository-specific skills for Better Call Bliss, Bliss Mixer Lab, guidance providers, and the native Rust components.

**Architecture:** Each skill captures only the stable invariants and routing knowledge for its component family. Detailed architecture, tests, UI contracts, and release/build information live in references, while volatile versions and live server state are always revalidated.

**Tech Stack:** Codex skills, Markdown, YAML, Perl/Lyrion conventions, Rust/Cargo conventions, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-07-lyrion-bliss-agent-skills-design.md`

## Global Constraints

- Existing UX and log formats are compatibility contracts; capture and compare baselines before changing affected code.
- Do not duplicate a provider's capabilities or limitations in host documentation.
- Bliss remains the primary candidate authority; guidance is bounded and advisory.
- Preserve repository ownership boundaries and use current local source before remote documentation.
- Do not commit generated native binaries to source repositories.
- Verify current branches, dependencies, schemas, and workflow status before changing or publishing anything.
- The private `codex-lyrion-bliss-skills` repository is the source of truth. Literal profile create paths below denote installed destinations; create versioned sources under `skills/<name>` and install them only after repository validation.

## Review Focus

- A host/provider refactor changes visible settings layout or log output despite identical behavior.
- A native schema changes while the Perl request/result adapter remains stale.
- A provider acquires data differently but host documentation incorrectly owns the limitation.
- A learned matrix is absent and the fallback path becomes inconsistent with Bliss Mixer.
- A Rust optimization increases memory or CPU use on large libraries or changes deterministic output.

---

### Task 1: Better Call Bliss Development Skill

**Files:**
- Create: `C:\Users\chris\.codex\skills\better-call-bliss-development\SKILL.md`
- Create: `C:\Users\chris\.codex\skills\better-call-bliss-development\agents\openai.yaml`
- Create: `C:\Users\chris\.codex\skills\better-call-bliss-development\references\architecture-and-jobs.md`
- Create: `C:\Users\chris\.codex\skills\better-call-bliss-development\references\ux-contract.md`
- Create: `C:\Users\chris\.codex\skills\better-call-bliss-development\references\logging-and-verification.md`

**Interfaces:**
- Consumes: Better Call Bliss source, optimizer contracts, provider descriptors, Lyrion queues/playlists, and current Pi evidence.
- Produces: repository-correct changes preserving preview, output, UI, provider, and logging behavior.

- [ ] **Step 1: Extract current architecture and job lifecycle**

Document source capture, preparing phase, optimizer invocation, progress polling, preview result, acceptance/output, cancellation, and recent-job behavior from current code and product docs.

- [ ] **Step 2: Capture UX and settings invariants**

Document established page layout, live status, settings persistence, provider controls, context actions, output handling, localization, and Material Skin behavior that must not regress.

- [ ] **Step 3: Capture request/result and logging invariants**

Document schema typing, optimizer/provider artifacts, progress/result diagnostics, effective settings, current information/debug formats, and the baseline/test procedure for logging changes.

- [ ] **Step 4: Validate with representative requests**

Validate the skill and test its routing against preview failure, provider issue, queue output, context action, performance regression, and log-format change requests.

### Task 2: Bliss Mixer Lab Development Skill

**Files:**
- Create: `C:\Users\chris\.codex\skills\bliss-mixer-lab-development\SKILL.md`
- Create: `C:\Users\chris\.codex\skills\bliss-mixer-lab-development\agents\openai.yaml`
- Create: `C:\Users\chris\.codex\skills\bliss-mixer-lab-development\references\upstream-and-sidecar.md`
- Create: `C:\Users\chris\.codex\skills\bliss-mixer-lab-development\references\dstm-and-guidance.md`
- Create: `C:\Users\chris\.codex\skills\bliss-mixer-lab-development\references\ui-and-log-contract.md`

**Interfaces:**
- Consumes: upstream Bliss Mixer behavior, Lab source, native mixer endpoint, provider outputs, and released Lab log examples.
- Produces: experimental features that remain isolated, compatible, and observationally consistent.

- [ ] **Step 1: Document the sidecar/upstream boundary**

Record what upstream owns, what Lab may extend, forbidden replacement registrations, DSTM drift checks, shared preferences, and learned-matrix behavior.

- [ ] **Step 2: Document DSTM and guidance behavior**

Cover candidate pool ownership, native guidance endpoint, provider discovery/settings, structured selection traces, reranking modes, and fallback behavior.

- [ ] **Step 3: Make released logging format an explicit hard invariant**

Record the authoritative released candidate-selection, per-track, Diagnostics, and Selection message layouts. Require complete formatter tests and Pi comparison whenever data moves between Perl and Rust.

- [ ] **Step 4: Validate Lab scenarios**

Validate the skill against upstream drift, provider disabled/enabled, learned matrix absent/present, DSTM startup failure, settings regression, and logging regression requests.

### Task 3: Guidance Provider Development Skill

**Files:**
- Create: `C:\Users\chris\.codex\skills\bliss-guidance-provider-development\SKILL.md`
- Create: `C:\Users\chris\.codex\skills\bliss-guidance-provider-development\agents\openai.yaml`
- Create: `C:\Users\chris\.codex\skills\bliss-guidance-provider-development\references\provider-and-host-contract.md`
- Create: `C:\Users\chris\.codex\skills\bliss-guidance-provider-development\references\spi-artifacts-and-resources.md`
- Create: `C:\Users\chris\.codex\skills\bliss-guidance-provider-development\references\settings-ui-and-traces.md`

**Interfaces:**
- Consumes: provider kit, guidance SPI, provider plugins/native binaries, and host integration code.
- Produces: discoverable passive providers with provider-owned settings, bounded signals, and host-compatible structured diagnostics.

- [ ] **Step 1: Document discovery and settings ownership**

Cover descriptor/default/status methods, provider-owned settings pages, disabled-by-default host opt-in, sparse host overrides, inherited-value UX, and localization.

- [ ] **Step 2: Document the native SPI lifecycle**

Cover `describe`, `prepare`, `score`, and `close`; trusted files/resources; SHA-256 artifacts; stdin/stdout JSONL; timeouts; neutral degradation; and `selection_trace_v1`.

- [ ] **Step 3: Document current provider implementations without making them generic requirements**

Use Last.fm and Library Signals as examples for artifact-backed and read-only-resource-backed providers, while keeping capability details in their owning repositories.

- [ ] **Step 4: Protect host logging and UI contracts**

Require providers to return structured data rather than rendered host log strings. Validate the skill against a new third-party provider, settings override, provider failure, and trace-format extension.

### Task 4: Native Rust Development Skill

**Files:**
- Create: `C:\Users\chris\.codex\skills\bliss-native-rust-development\SKILL.md`
- Create: `C:\Users\chris\.codex\skills\bliss-native-rust-development\agents\openai.yaml`
- Create: `C:\Users\chris\.codex\skills\bliss-native-rust-development\references\repositories-and-contracts.md`
- Create: `C:\Users\chris\.codex\skills\bliss-native-rust-development\references\testing-building-and-performance.md`
- Create: `C:\Users\chris\.codex\skills\bliss-native-rust-development\references\progress-and-selection-traces.md`

**Interfaces:**
- Consumes: Rust repositories, shared-core pins, JSON schemas, fixtures, performance targets, and host output requirements.
- Produces: compatible tested binaries and structured progress/results that hosts can render without UI or logging regressions.

- [ ] **Step 1: Map native repository responsibilities and contracts**

Cover optimizer, mixer fork, shared core, learner/analyser, guidance SPI/providers, schemas, CLI/version contracts, and host-neutral boundaries.

- [ ] **Step 2: Document verification and build workflows**

Include formatting, Clippy, tests, locked dependencies, fixtures, GitHub matrix builds, checksums, artifact download, platform placement, and no committed binaries.

- [ ] **Step 3: Document performance and observability requirements**

Require bounded memory, multi-core use where safe, deterministic seeded behavior, large-library tests, progress heartbeats, timing diagnostics, and structured traces rather than host-specific strings.

- [ ] **Step 4: Validate the development suite**

Run `quick_validate.py` for all four skills, inspect UI metadata, scan for stale version claims/secrets/placeholders, and exercise routing on representative Perl/Rust/provider boundary changes.
