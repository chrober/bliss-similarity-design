# Bliss 'Em All - complete UX shell checkpoint

**Date:** 2026-07-21
**State:** Complete planned hierarchical UX shell deployed and verified on LMS
9.1.1 ARM64; one read-only reorder path is connected and every incomplete
capability is explicitly labelled in the UI and documentation

## Published implementation revision

| Repository | Revision | Result |
| --- | --- | --- |
| [chrober/lms-bliss-em-all](https://github.com/chrober/lms-bliss-em-all/tree/feature/first-ux-preview) | `aa4f5819b0102dd0fbfb757242fde280aef81b08` | Version `0.2.0` full UX shell, context providers, expanded settings, result drill-downs, capability labels, and UX status contract |

## UX now visible

The Applications flow now exposes the intended product decisions:

```text
Bliss 'Em All
|- Optimize a saved playlist
|  `- playlist
|     |- Optimize order
|     |  |- Reorder only [working preview]
|     |  |- Extend automatically [not connected]
|     |  |- Add exactly N [not connected]
|     |  |- One bridge per transition [not connected]
|     |  |- Target length [not connected]
|     |  `- Double length [not connected]
|     `- Preserve order and fill gaps [not connected]
|        `- the five meaningful extension policies
|- Active previews [session only]
|- Recent results [session only]
|- System status
|- Settings
`- Feature availability and help
```

The playlist context menu contains an informational **Bliss 'Em All...**
shortcut, and local tracks contain an informational **Bliss me there...**
entry. Neither starts a job until the shared workflow-state adapter exists.

The connected review and result path shows inherited dynamic Adaptive scoring,
seed/learned blend, artist/album/track windows, restart effort, aggregate route
diagnostics, proposed order with Original provenance, additions, warnings, and
an in-memory report summary. Playlist creation, cancellation, per-transition
drill-down, report persistence/export, semantic providers, and complete menu
localization are visibly marked unavailable or partial.

## Live verification

The server status command returned:

```text
ready=1
problem_count=0
ux_contract=full-shell-v1
working_mode=optimize-order/reorder-only/read-only-preview
```

Live JSON-RPC navigation verified both ordering policies, all extension labels,
automatic size calculation, the absence of an irrelevant numeric editor in
Auto, the working review, and non-action future screens. Playlist- and
track-info queries returned both context entries with `action=none`.

An anonymized two-track playlist completed the real read-only path in about two
seconds with 50 restarts. The result exposed proposed order, additions/reasons,
aggregate transition summary, warnings, and report screens. No saved playlist
or M3U file was modified. The settings page rendered the working restart
setting separately from future-only output, bridge, provider/cache, and report
preferences.

## Deployment rule discovered

piCorePlayer adds `<LMS cache>/Plugins` as its manual plugin root. Development
builds belong at `Cache/Plugins/BlissEmAll`. `Cache/InstalledPlugins/Plugins`
is extension-manager-owned; a hand-copied unregistered plugin there can be
removed during restart. The repository documentation now records this rule.
Production still requires a plugin ZIP and the planned extension repository.

## Current boundary and next gates

The full shell is a UX contract, not a claim that all native capabilities are
wired. The only executable combination remains **Optimize order + Reorder only
+ Preview**. The next implementation gate should connect one additional mode
end to end--preferably **Extend automatically**--including candidate discovery,
native request/result adaptation, bridge provenance, and UI error handling,
while retaining read-only Preview. Playlist persistence should follow only
after exact LMS serialization and scanner verification are transactional.
