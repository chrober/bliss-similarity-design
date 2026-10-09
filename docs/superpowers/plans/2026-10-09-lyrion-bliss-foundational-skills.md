# Lyrion and Bliss Foundational Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the foundational user-profile skills that locate the Bliss workspace, operate the Pi safely, diagnose Lyrion, coordinate releases, and guide generic Lyrion plugin work.

**Architecture:** Each skill is independently discoverable under `C:\Users\chris\.codex\skills` and keeps its `SKILL.md` concise. Conditional operational detail lives in focused references so a reachability check does not load deployment, database, and release instructions unnecessarily.

**Tech Stack:** Codex skills, Markdown, YAML, PowerShell, bundled `skill-creator` initializer and validator.

**Spec:** `docs/superpowers/specs/2026-10-07-lyrion-bliss-agent-skills-design.md`

## Global Constraints

- Do not store passwords, tokens, API keys, or private keys in a skill.
- Live host addresses, versions, architecture, branch state, and playback state must be verified before use.
- Read-only Pi and Lyrion checks are the default; deployment, restart, publishing, playlist mutation, and deletion require explicit user authorization.
- Deploy Lyrion plugins only to the official installed-plugin location; do not use the development `Cache/Plugins` directory.
- Do not restart Lyrion while a player is active unless the user explicitly authorizes it after being told.
- Preserve existing log category, level, message body, field order, spacing, punctuation, and conditional fields unless the user explicitly requests a log-format change.
- The user-profile skills directory is not assumed to be a Git repository; do not initialize one or commit there.

## Review Focus

- A Pi host or address has changed: the skill must verify it rather than silently use stale information.
- A deployment request arrives while music is playing: preflight must stop before restart and report the active state.
- A repository has dirty or unpushed work: release/workspace guidance must preserve it and surface the conflict.
- A plugin refactor changes log wording accidentally: the engineering/release guidance must require a baseline and complete message-body comparison.
- A skill contains a credential-like literal: validation must flag it before completion.

---

### Task 1: Workspace Navigation Skill

**Files:**
- Create: `C:\Users\chris\.codex\skills\bliss-workspace-navigation\SKILL.md`
- Create: `C:\Users\chris\.codex\skills\bliss-workspace-navigation\agents\openai.yaml`
- Create: `C:\Users\chris\.codex\skills\bliss-workspace-navigation\references\repositories.md`
- Create: `C:\Users\chris\.codex\skills\bliss-workspace-navigation\references\git-safety.md`

**Interfaces:**
- Consumes: verified local clones under `D:\LMS`, their remotes, current branches, and ownership documentation.
- Produces: routing guidance that identifies the authoritative repository and safe Git preflight for later skills.

- [ ] **Step 1: Inventory repository names, remotes, branches, worktrees, and dirty state**

Run read-only Git commands across direct child repositories of `D:\LMS`; record only stable ownership and relationship facts in `references/repositories.md`, and describe volatile state as something to re-check.

- [ ] **Step 2: Initialize the skill with references**

Run `init_skill.py bliss-workspace-navigation --path C:\Users\chris\.codex\skills --resources references` and generate concise UI metadata.

- [ ] **Step 3: Write routing and Git-safety instructions**

Define how to select the owning repository, distinguish upstream/fork/sidecar components, inspect worktrees, and avoid overwriting user changes. Add tests-as-procedures for dirty worktrees, ahead/behind branches, and feature branches already merged to main.

- [ ] **Step 4: Validate the skill**

Run `quick_validate.py C:\Users\chris\.codex\skills\bliss-workspace-navigation` and scan for scaffold placeholders and credential-like values. Expected: validator exit code 0 and no secrets.

### Task 2: Pi Operations Skill

**Files:**
- Create: `C:\Users\chris\.codex\skills\lyrion-pi-operations\SKILL.md`
- Create: `C:\Users\chris\.codex\skills\lyrion-pi-operations\agents\openai.yaml`
- Create: `C:\Users\chris\.codex\skills\lyrion-pi-operations\references\access-and-inventory.md`
- Create: `C:\Users\chris\.codex\skills\lyrion-pi-operations\references\deployment.md`
- Create: `C:\Users\chris\.codex\skills\lyrion-pi-operations\references\service-and-playback.md`

**Interfaces:**
- Consumes: explicit user authorization, current Pi address, SSH username/port, discovered architecture, current player state, and target plugin/binary.
- Produces: verified access, safe deployment instructions, and post-deployment evidence without embedding credentials.

- [ ] **Step 1: Verify the current operational layout read-only**

Confirm reachable ports, SSH identity method, Lyrion URL, installed-plugin path, service control, logs, filesystem persistence model, and binary architecture. Do not persist the password.

- [ ] **Step 2: Initialize and write the skill**

Route simple access, diagnostic, deployment, and restart requests to their relevant references. State the official `InstalledPlugins/Plugins` path rule and the active-playback restart guard in `SKILL.md`.

- [ ] **Step 3: Add deployment and rollback preflight**

Document source/target resolution, architecture verification, permissions, backup of replaced files when warranted, no deployment to `Cache/Plugins`, and verification without restart when requested.

- [ ] **Step 4: Validate with non-mutating scenarios**

Validate the skill, then exercise instructions against reachability, installed-path inspection, architecture detection, and playback-state inspection only. Expected: no server mutation and no credential emitted.

### Task 3: Lyrion Server Diagnostics Skill

**Files:**
- Create: `C:\Users\chris\.codex\skills\lyrion-server-diagnostics\SKILL.md`
- Create: `C:\Users\chris\.codex\skills\lyrion-server-diagnostics\agents\openai.yaml`
- Create: `C:\Users\chris\.codex\skills\lyrion-server-diagnostics\references\logs-and-jobs.md`
- Create: `C:\Users\chris\.codex\skills\lyrion-server-diagnostics\references\library-and-databases.md`
- Create: `C:\Users\chris\.codex\skills\lyrion-server-diagnostics\references\web-and-material.md`

**Interfaces:**
- Consumes: current Lyrion logs, plugin state, job IDs, scan state, database paths, and browser evidence.
- Produces: chronological evidence, a scoped diagnosis, and clearly separated fix recommendations.

- [ ] **Step 1: Catalog authoritative diagnostic sources**

Document server and scanner logs, job artifacts, Lyrion database roles, virtual-library state, plugin loading, JSON-RPC errors, and relevant Material Skin HTML/JavaScript observations.

- [ ] **Step 2: Write the diagnostic workflow**

Require read-only evidence first, correlate timestamps and identifiers, distinguish reporting from execution failures, and avoid implementing a fix when the user asked only for diagnosis.

- [ ] **Step 3: Include logging-format evidence rules**

When a reported regression concerns logs, require a released baseline or before-change log and compare plugin-generated message bodies separately from timestamps and source line numbers.

- [ ] **Step 4: Validate realistic cases**

Validate the skill and mentally execute plugin-load failure, stalled preview, active scan, missing track, and Material status-update scenarios. Expected: each routes to a specific source without premature mutation.

### Task 4: Release Coordination Skill

**Files:**
- Create: `C:\Users\chris\.codex\skills\bliss-release-coordination\SKILL.md`
- Create: `C:\Users\chris\.codex\skills\bliss-release-coordination\agents\openai.yaml`
- Create: `C:\Users\chris\.codex\skills\bliss-release-coordination\references\release-workflows.md`
- Create: `C:\Users\chris\.codex\skills\bliss-release-coordination\references\package-and-feed-contract.md`
- Create: `C:\Users\chris\.codex\skills\bliss-release-coordination\references\release-gates.md`

**Interfaces:**
- Consumes: clean repository state, version ownership, passing tests, native release assets, checksums, and explicit publish/deploy authority.
- Produces: coordinated GitHub releases and extension-feed updates with verified platform packages.

- [ ] **Step 1: Map current release ownership and dependency order**

Record which repositories build native assets, which package Lyrion plugins, how `lms-plugins` is updated, and which workflows can be dry-run or manually dispatched.

- [ ] **Step 2: Write the release gates**

Require branch/upstream checks, tests, no committed binaries, package-platform inspection, checksum verification, log-format compatibility, feed update verification, and post-release status.

- [ ] **Step 3: Cover partial and failed releases**

Document how to stop after a failed native build, avoid publishing a plugin against missing assets, inspect workflow failures, and report which repositories were or were not published.

- [ ] **Step 4: Validate without publishing**

Validate the skill and apply its preflight to current repositories without tagging, dispatching, or modifying the feed. Expected: a reproducible ordered release graph and no external mutation.

### Task 5: Generic Lyrion Plugin Engineering Skill

**Files:**
- Create: `C:\Users\chris\.codex\skills\lyrion-plugin-engineering\SKILL.md`
- Create: `C:\Users\chris\.codex\skills\lyrion-plugin-engineering\agents\openai.yaml`
- Create: `C:\Users\chris\.codex\skills\lyrion-plugin-engineering\references\plugin-anatomy.md`
- Create: `C:\Users\chris\.codex\skills\lyrion-plugin-engineering\references\settings-and-ui.md`
- Create: `C:\Users\chris\.codex\skills\lyrion-plugin-engineering\references\logging-and-tests.md`

**Interfaces:**
- Consumes: an existing Lyrion plugin repository and the specific requested UI/runtime behavior.
- Produces: changes following established Perl, settings, localization, web-template, background-job, Material Skin, and testing patterns.

- [ ] **Step 1: Extract reusable plugin patterns from current repositories**

Use upstream Bliss Mixer, Better Call Bliss, Bliss Mixer Lab, and the provider plugins as examples while distinguishing generic Lyrion conventions from repository-specific behavior.

- [ ] **Step 2: Write settings and UI guidance**

Cover settings registration, explicit Save behavior, preference defaults, localization tokens, inherited-provider controls, dynamic enable/disable behavior, Extras-page limitations, context menus, and Material Skin compatibility.

- [ ] **Step 3: Write logging and testing guidance**

Embed the log compatibility contract, require baseline capture and message-body regression tests, and preserve existing UI structure and log format through refactors.

- [ ] **Step 4: Validate the foundational suite**

Run `quick_validate.py` for all five skills, inspect every `agents/openai.yaml`, scan for secrets/placeholders, and verify that descriptions do not overlap so broadly that all skills trigger for every Lyrion request.

