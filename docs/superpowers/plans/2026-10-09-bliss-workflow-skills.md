# Bliss Workflow Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create focused skills for investigating real runs, maintaining cross-repository documentation, and safely working with Lyrion playlists and library state.

**Architecture:** These skills are evidence-oriented consumers of the foundational and development knowledge, but remain independently useful. They route to concise references for artifacts, documentation ownership, playlist formats, and scanner/database behavior.

**Tech Stack:** Codex skills, Markdown, YAML, PowerShell, Lyrion logs/databases/playlists, Mermaid.

**Spec:** `docs/superpowers/specs/2026-10-07-lyrion-bliss-agent-skills-design.md`

## Global Constraints

- Investigations are read-only unless the user explicitly requests a change or live test.
- Preserve chronology, settings, identifiers, artifacts, and uncertainty; do not infer success from aggregate summaries alone.
- Documentation belongs with the component that owns the behavior or limitation.
- Existing log formats and UI text are compatibility surfaces.
- Playlist writes must preserve LMS-compatible URL/path formatting and source files unless explicitly accepted.

## Review Focus

- A completed job has misleading summary counters but correct per-track evidence: report the reporting defect separately.
- A run uses stale or unavailable artifacts: do not attribute the result to the algorithm without verifying inputs.
- A README duplicates limitations owned by another component: replace it with a neutral link/contract statement.
- A playlist contains paths with spaces, apostrophes, case differences, or non-library entries: avoid shell-quoting false positives.
- A scan or live playback is active during a proposed test: preserve service availability and user state.

---

### Task 1: Run Investigation Skill

**Files:**
- Create: `C:\Users\chris\.codex\skills\bliss-run-investigation\SKILL.md`
- Create: `C:\Users\chris\.codex\skills\bliss-run-investigation\agents\openai.yaml`
- Create: `C:\Users\chris\.codex\skills\bliss-run-investigation\references\better-call-bliss-runs.md`
- Create: `C:\Users\chris\.codex\skills\bliss-run-investigation\references\lab-dstm-runs.md`
- Create: `C:\Users\chris\.codex\skills\bliss-run-investigation\references\evidence-and-reporting.md`

**Interfaces:**
- Consumes: job IDs, server logs, progress/timing sidecars, requests/results, provider artifacts/traces, settings, and listening feedback.
- Produces: chronological diagnoses separating acquisition, eligibility, scoring, selection, persistence, reporting, and formatting.

- [ ] **Step 1: Document artifact and log discovery**

Identify current job storage, log locations, request/result/progress/timing files, provider artifacts, native diagnostics, and retention caveats; require live verification of paths.

- [ ] **Step 2: Write the correlation workflow**

Start from the job ID and effective settings, reconstruct the timeline, inspect per-track reasons and provider traces, compare runtime phases, and identify the first unsupported assumption.

- [ ] **Step 3: Add logging-regression handling**

Require before/after message-body comparison and distinguish changed computation, changed structured trace, and changed rendering.

- [ ] **Step 4: Validate representative investigations**

Validate the skill against no-guidance results, duplicate-source errors, slow first runs, bridge-quality complaints, progress stalls, and false summary counters.

### Task 2: Documentation Maintenance Skill

**Files:**
- Create: `C:\Users\chris\.codex\skills\bliss-documentation-maintenance\SKILL.md`
- Create: `C:\Users\chris\.codex\skills\bliss-documentation-maintenance\agents\openai.yaml`
- Create: `C:\Users\chris\.codex\skills\bliss-documentation-maintenance\references\ownership-and-audience.md`
- Create: `C:\Users\chris\.codex\skills\bliss-documentation-maintenance\references\markdown-and-mermaid.md`
- Create: `C:\Users\chris\.codex\skills\bliss-documentation-maintenance\references\roadmaps-and-status.md`

**Interfaces:**
- Consumes: current implementation, repository ownership, Git history, existing plans/checkpoints/backlogs, and target audience.
- Produces: concise non-duplicative documentation with valid links/diagrams and truthful implementation status.

- [ ] **Step 1: Document ownership and placement rules**

Define README scope, component-owned limitations, generic host/provider boundaries, shipped-plugin relative-link constraints, and when to use product names versus inline-code repository names.

- [ ] **Step 2: Document Markdown and Mermaid verification**

Cover UTF-8, line endings, required hard breaks where intended, link styles, concise tables, architecture/sequence diagrams, GitHub Mermaid syntax, and duplicate-content checks.

- [ ] **Step 3: Document roadmap/status reconciliation**

Require comparison with current Git history and implementation tests before marking roadmap rows complete or writing a checkpoint.

- [ ] **Step 4: Validate documentation scenarios**

Validate the skill against provider README alignment, host-neutral guidance descriptions, implementation-plan updates, checkpoint creation, malformed Mermaid, and misplaced roadmap details.

### Task 3: Playlist and Library Operations Skill

**Files:**
- Create: `C:\Users\chris\.codex\skills\lyrion-playlist-library-operations\SKILL.md`
- Create: `C:\Users\chris\.codex\skills\lyrion-playlist-library-operations\agents\openai.yaml`
- Create: `C:\Users\chris\.codex\skills\lyrion-playlist-library-operations\references\m3u-and-playlists.md`
- Create: `C:\Users\chris\.codex\skills\lyrion-playlist-library-operations\references\library-scanner-and-paths.md`
- Create: `C:\Users\chris\.codex\skills\lyrion-playlist-library-operations\references\virtual-libraries-and-candidates.md`

**Interfaces:**
- Consumes: playlist paths, Lyrion library state, scanner logs, virtual-library selection, filesystem paths, and explicit mutation authority.
- Produces: safe playlist/library diagnoses or LMS-compatible playlist changes with reproducible reports.

- [ ] **Step 1: Document LMS playlist representation**

Capture `#EXTURL`, `#EXTINF`, filesystem path ordering, URL escaping, comments/metadata, source preservation, and safe copy/overwrite rules.

- [ ] **Step 2: Document scanner and filesystem checks**

Cover scan state, scanner logs, network filesystems, case-sensitive identity mismatches, shell-safe path verification, rescan behavior, and non-library/stream entries.

- [ ] **Step 3: Document library and candidate boundaries**

Cover Bliss rows versus LMS membership, virtual libraries, active candidate library, genre restrictions, immutable source/history tracks, and generated-track eligibility.

- [ ] **Step 4: Validate the complete skill suite**

Run `quick_validate.py` for these three skills and then for all twelve suite skills. Scan descriptions for overlap, scan content for secrets/stale hard-coded versions, and exercise one routing scenario per skill. Expected: all validators pass and each scenario selects a narrow skill set.
