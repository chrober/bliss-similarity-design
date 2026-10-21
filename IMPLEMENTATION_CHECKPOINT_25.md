# Better Call Bliss - LMS-local bridge inventory and persistent audit

**Date:** 2026-07-26  
**State:** Pre-search LMS membership gate, persistent unmatched-row audit, and cross-restart inventory cache deployed and verified on ARM64 Lyrion Music Server  
**Plugin version:** `0.10.0`  

## Outcome

Addition jobs no longer search every usable `TracksV2` row and discover stale/non-LMS membership only after selection. The plugin now freezes current non-remote LMS audio membership as a checksum-protected `lms-local-candidate-inventory-v1` allowlist bound to both the exact `bliss.db` file identity and LMS last-scan timestamp. The native optimizer validates the artifact and removes non-allowlisted rows before semantic candidate construction, acoustic shortlisting, or contextual bridge scoring.

The existing post-result proof remains independent: every selected bridge must still have an unchanged Bliss row, an existing file, and an exact current local/audio LMS catalog row before the job can complete. This second check protects against time-of-check/time-of-use changes while a native job is running.

## Persistent review ledger

Each cold inventory pass atomically updates:

```text
<LMS cache>/bettercallbliss/non-lms-bliss-rows.json
```

The private `non-lms-bliss-row-audit-v1` ledger retains the database identity, LMS scan time, current and historical counts, and one entry per unmatched Bliss identity. Entries include row ID, `database_file`, title/artist/album metadata, a stable identity hash, reason, active/resolved state, first/last-seen timestamps, and observation count. A later successful comparison marks a historical row resolved instead of deleting it. Normal server logs contain only counts and the audit location; the Extras page and `bettercallbliss status` expose the same review pointer.

The live library currently has 63,822 usable Bliss rows: 63,819 match current local LMS tracks and three are excluded. Their private paths and metadata were verified in the ledger but are deliberately omitted from this published checkpoint.

## Cache and performance boundary

The allowlist is content-addressed and a checksum-verified current-state record reuses it across LMS restarts only while the LMS last-scan timestamp, `bliss.db` identity, schema, builder revision, file path, and SHA-256 all match. Any mismatch logs one stable reason and causes a cold rebuild. A same-process reuse is labelled `memory`; a cross-restart reuse is labelled `hit`; a rebuild is labelled `miss`.

On the live 63k-track ARM64 server, the cold LMS/Bliss intersection took about 14 seconds. Same-process Preview startup then measured 515-668 ms, and a post-restart disk-cache Preview reached the running page in 3.1 seconds including the page's cold LMS work. Native loading and validation of the 800 KiB allowlist measured 190 ms in the captured exact-count result. The native bridge search remains the dominant addition-job cost.

## Repository commits

| Repository | Commit | Change |
| --- | --- | --- |
| `bliss-playlist-optimizer` | `60cc270` | Versioned LMS-local inventory schema, hash/database binding, source proof, pre-search row filter, diagnostics, and regression tests |
| `bliss-playlist-optimizer` | `d6e39cd` | Strict-Clippy correction; green CI and ARM64 artifact build |
| `lms-better-call-bliss` | `007fde1` | Plugin `0.10.0`, inventory/audit module, request integration, Extras/status UX, bundled ARM64 binary, and public contracts |
| `lms-better-call-bliss` | `3f0eb2c` | Numeric artifact correction and faster URL-prefix membership pass |
| `lms-better-call-bliss` | `acb4694` | Checksum-verified cross-restart inventory cache and cache-state logging |
| `lms-better-call-bliss` | `d9a233b` | Stable cache-miss reason logging and accurate memory-hit label |
| `lms-better-call-bliss` | `ed24692` | Scalar JSON reads preserving both cached state and historical audit entries |
| `lms-better-call-bliss` | `92b50d4` | Post-result bridge resolution through the exact LMS catalog row |
| `lms-better-call-bliss` | `924f10c` | Locale-byte URL construction for non-ASCII bridge paths |

The active ARM64 helper was built from optimizer commit `d6e39cd` by GitHub Actions run `30209142405`. Its SHA-256 is `889826b9b40e1ce3ac7a49b7c8b950d794f57608a119edea429b798562e88e52`.

## Verification

- Local optimizer: `cargo fmt --check`, strict Clippy, focused inventory/hash/database-binding tests, end-to-end excluded-row search test, and the full 8-unit/12-contract suite passed.  
- GitHub: corrected optimizer CI and ARM64 build both passed.  
- Live status: `ready=1`, `problem_count=0`, `candidate_inventory_ready=1`, `non_lms_bliss_row_count=3`, and `ux_contract=extras-job-editor-v9`.  
- Extras: the membership-audit panel shows 63,819 allowed rows, three excluded rows, and the persistent review path.  
- Preserve plus exact one: 13 source tracks produced 14 tracks and one locally resolved bridge.  
- Preserve plus exact eight: 13 source tracks produced 21 tracks and eight locally resolved bridges after the non-ASCII path proof was corrected.  
- Audit durability: its SHA-256 and modification time remained unchanged across multiple LMS restarts and cache-hit jobs.  
- Safety: every exercise was Preview-only; no playlist persistence action was invoked.  

## Rollback and cleanup

The pre-deployment plugin is preserved at:

```text
/mnt/mmcblk0p2/tce/slimserver/Cache/BetterCallBliss-backups/BetterCallBliss-0.9.0-pre-007fde1
```

Temporary upload and diagnostic files were removed after verification. The persistent audit, content-addressed inventory, job artifacts, decoded Bliss-library cache, and rollback copy remain intentionally available for review and recovery.

## Next user-facing slice

The membership reliability gate no longer blocks larger strict presets. The next user-facing step remains **One bridge per source-track transition** as a preserved-order exact-count preset with `N = S - 1`, followed by target-length/double-length wrappers and explicit endpoint controls. Cancellation/resource UX should be considered before enabling expensive presets for very large playlists.
