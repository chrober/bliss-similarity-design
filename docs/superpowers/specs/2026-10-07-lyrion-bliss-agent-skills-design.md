# Lyrion and Bliss agent skills design

## Purpose

Create a composable set of user-profile Codex skills under `C:\Users\chris\.codex\skills` for the recurring Lyrion and Bliss work performed across the repositories under `D:\LMS` and on the Lyrion server running on the Raspberry Pi. The skills should reduce repeated discovery, preserve established project conventions, and make operational changes safer without turning one large catch-all skill into permanent context.

## Design principles

- Keep operational, architectural, repository-specific, diagnostic, and release knowledge in separate skills with precise descriptions.
- Keep each `SKILL.md` short. Route detailed procedures, repository maps, paths, and compatibility contracts to focused `references/` files.
- Prefer automatic discovery. A skill may be selected implicitly, but it never grants permission for deployment, service restart, playlist modification, deletion, publishing, or other external mutation.
- Start Pi and server investigations read-only. Deploy or restart only when the user explicitly asks, and check active playback before restarting Lyrion.
- Do not store SSH passwords, API keys, tokens, or other secrets in a skill. Document the credential source and retrieval convention instead.
- Treat live IP addresses, installed versions, paths, branches, and server state as facts to verify rather than permanent truths.
- Preserve user-owned dirty worktrees and unrelated files. Multi-repository tasks must inspect branch, upstream, worktree, and push state before mutation.

## Log compatibility contract

Existing Lyrion log output is a compatibility surface. Skills that may change plugin, native-host, guidance-provider, diagnostics, or release behavior must enforce these rules:

- Capture the current released implementation and representative before-change output before editing code that can affect logging.
- Preserve logger category, log level, message body, field names, field order, spacing, punctuation, conditional fields, and multi-line layout unless the user explicitly requests a format change.
- Ignore transport-owned prefixes such as timestamps and source line numbers when comparing messages, but compare the plugin-generated message body exactly.
- Prefer a new additional diagnostic line over altering an established information or debug line.
- When computation moves between Perl and Rust, return structured trace data and keep the established Perl-side formatter authoritative.
- Better Call Bliss and Bliss Mixer Lab have separate established formats. Do not replace either with a generic provider/native format.
- Add focused regression coverage for affected log messages. Where practical, compare complete rendered message bodies against fixtures rather than testing isolated tokens.
- For changes deployed to the Pi, run a representative real workflow and compare the resulting server log with the baseline before declaring success.
- Release coordination must treat an unexplained logging diff as a failed compatibility gate.

This concise contract is repeated in the relevant skill entrypoints so it is loaded even when a dedicated logging task is not explicitly requested. A detailed shared reference may be included in the skill suite, but repository-specific skills remain independently useful.

## Skill set

### `bliss-workspace-navigation`

Maps repositories under `D:\LMS`, component ownership, upstream/fork relationships, shared dependencies, local clone paths, and the rules for deciding which repository should receive a change. Includes safe branch, worktree, and synchronization checks.

### `lyrion-pi-operations`

Covers connection and reachability checks, architecture discovery, service and player-state inspection, official plugin and binary locations, permissions, deployment verification, logs, and safe restart behavior. Read-only by default; mutation requires an explicit request.

### `lyrion-server-diagnostics`

Covers plugin-load failures, server and scanner logs, JSON-RPC failures, jobs, database and virtual-library inspection, missing tracks, saved-playlist scanning, and Material Skin observations. Produces chronological, evidence-backed diagnoses before fixes.

### `lyrion-plugin-engineering`

Covers reusable Lyrion Perl-plugin patterns: plugin registration, settings, preferences, localization, classic-web templates, Extras pages, context menus, background jobs, Material Skin compatibility, test stubs, and the log compatibility contract.

### `better-call-bliss-development`

Covers Better Call Bliss previews, optimizer request/result contracts, playlist and queue inputs/outputs, live status, context actions, guidance discovery, provider settings inheritance, UX invariants, test patterns, and its established information/debug logging.

### `bliss-mixer-lab-development`

Covers the Lab sidecar relationship with upstream Bliss Mixer, DSTM behavior, learned matrices, experimental reranking, native guidance hosting, upstream drift checks, settings parity, and exact preservation of the released Lab logging format.

### `bliss-guidance-provider-development`

Covers the provider kit, Lyrion discovery contract, provider-owned settings, host overrides, SPI lifecycle, trusted artifacts/resources, JSONL transport, `selection_trace_v1`, native providers, and host-side rendering of provider diagnostics without log regressions.

### `bliss-native-rust-development`

Covers the optimizer, mixer fork, shared core, learner/analyser, and guidance binaries: schemas, CLI compatibility, performance, bounded parallelism, memory use, cross-platform builds, GitHub artifacts, structured progress, and structured selection traces required to preserve host logging.

### `bliss-release-coordination`

Covers coordinated version bumps, test gates, tags, GitHub workflows, platform packages, checksums, extension-repository updates, official artifact retrieval, optional Pi deployment, and post-release verification. Source repositories must not gain committed binaries.

### `bliss-run-investigation`

Covers Better Call Bliss preview and Bliss Mixer Lab DSTM investigations: correlate effective settings, requests, progress, server logs, temporary artifacts, native diagnostics, selected tracks, runtime, and quality. Distinguishes acquisition, scoring, reporting, and formatting defects.

### `bliss-documentation-maintenance`

Covers ownership-aware README content, implementation plans, checkpoints, backlogs, architecture documents, Mermaid diagrams, cross-repository links, terminology, line endings, and removal of component-specific details from repositories that do not own them.

### `lyrion-playlist-library-operations`

Covers LMS-compatible M3U formatting, `#EXTURL` and `#EXTINF`, playlist scanning, path case, virtual-library membership, scanner diagnostics, candidate-library restrictions, and safe one-shot playlist inspection or transformation.

## Skill structure

Each skill contains `SKILL.md` and `agents/openai.yaml`. Add only resources with a concrete repeated use:

- `references/` for repository maps, Pi paths, commands, database locations, protocol details, UI contracts, and log baselines.
- `scripts/` for deterministic read-only inventory, deployment preflight, artifact verification, or multi-repository status checks when repeated shell reconstruction would be error-prone.
- No separate README, changelog, or placeholder directories.

The Pi skill should route among access, diagnostics, and deployment references rather than loading every operational detail for a simple reachability check. Repository-specific skills should contain only the paths and dependencies they need; they should not depend on loading the complete workspace map.

## Creation order

1. `bliss-workspace-navigation`
2. `lyrion-pi-operations`
3. `lyrion-server-diagnostics`
4. `bliss-release-coordination`
5. `lyrion-plugin-engineering`
6. Repository-specific and provider/native skills
7. Investigation, documentation, and playlist/library skills

Each skill is initialized with the bundled skill initializer, filled with verified local information, and checked with `quick_validate.py`. Scripts, if introduced, are exercised against read-only or temporary targets before the skill is considered usable.

## Success criteria

- A future Codex instance can select the narrow relevant skill from its name and description.
- The instance can locate the correct repository and authoritative component without rediscovering the workspace.
- Pi access and diagnostics begin safely and use current verified state.
- Deployments use official locations and do not restart active playback unless explicitly authorized.
- Settings UI and established information/debug logging do not regress as implementation boundaries move.
- Releases are reproducible, platform-correct, and do not commit generated binaries.
- Skills remain concise enough that unrelated Lyrion or Bliss tasks do not load unnecessary context.
