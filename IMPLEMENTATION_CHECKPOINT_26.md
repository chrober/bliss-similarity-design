# Better Call Bliss - draft retention, audit clarity, and second-server deployment

**Date:** 2026-07-29  
**State:** UX hardening implemented, published, and deployed to the second ARM64 Lyrion server  
**Plugin version:** `0.10.1`  

## Outcome

The Extras job editor now preserves the submitted values after a running job is polled, a Preview succeeds or fails, or a reviewed result is saved. Users can adjust one parameter and try again without reconstructing ordering, extension, scoring, repeat, search, and copy-name choices from global defaults.

Warning, error, success, and information banners now force readable foreground colors on their nested headings, lists, and other inherited content. The unavailable-Preview message also distinguishes a temporary LMS scan from a plugin compatibility problem and schedules a page retry while the scan is active.

The membership audit now distinguishes an exact filesystem/catalog miss from a Bliss row whose filename differs from the current LMS catalog only by case. The latter remains excluded from bridge searches because candidate membership is intentionally exact, while the audit points to the related current LMS database file for diagnosis.

## Membership-audit lifecycle

The JSON review ledger remains persistent across LMS restarts, but the current Extras panel is driven by candidate-inventory state held in the LMS process:

1. opening Extras does not prepare the candidate inventory;  
2. reorder-only jobs do not need or prepare it;  
3. the first automatic or exact-count addition Preview prepares or cache-loads it; and  
4. Extras then renders the audit panel for the remainder of that LMS process.  

Consequently, the panel is absent immediately after a restart even when the previous review JSON is present. A future UX refinement should load and label that persisted summary as “last checked” during plugin initialization, without triggering a potentially expensive library intersection merely to render the page.

## Filename-case diagnosis

The observed excluded row is a case-only duplicate of a currently indexed LMS track, not a missing music file. The analyser stores `TracksV2.File` as an exact, case-sensitive primary key and uses an exact lookup before inserting. Its stale-row cleanup asks the host filesystem whether each path exists. On a case-insensitive filesystem or share, both filename spellings can therefore exist from the cleanup's perspective, allowing an older spelling to remain when a later scan inserts the current spelling. The analyser's `--keep-old` option also intentionally suppresses cleanup.

This is analyser database bookkeeping rather than an acoustic-similarity error. A robust analyser correction should reconcile a unique case-only filesystem identity by updating the stored spelling, while preserving genuinely distinct files on case-sensitive filesystems. Blanket SQLite `NOCASE` matching is not sufficient because filesystem and Unicode case rules vary by platform.

## Scanner resource note

The observed greedy post-boot work was the normal LMS scanner pipeline, not Better Call Bliss or the BlissMixer importer. LMS exposes **Settings → Advanced → Performance → Scanner process priority**. Positive values lower the scanner's operating-system priority: `10` is a moderate responsiveness bias and `15` is stronger, at the cost of a longer scan. This deployment did not change that server preference.

## Deployment and verification

Plugin commit `1aa1587` was deployed to the server at `192.168.1.111`. The active installation reports:

- plugin version `0.10.1`;  
- UX contract `extras-job-editor-v10`;  
- `ready=1` and no compatibility problems;  
- HTTP and Lyrion CLI service availability; and  
- the expected bundled optimizer SHA-256.  

The live Extras response contains the contrast and form-restoration contracts. Immediately after restart, `candidate_inventory_ready=0` and the audit box is intentionally absent under the lifecycle above. No addition Preview was launched, and no playlist was created, overwritten, or otherwise changed.

The pre-deployment plugin remains recoverable at:

```text
/mnt/mmcblk0p2/tce/slimserver/Cache/BetterCallBliss-backups/BetterCallBliss-0.10.0-pre-1aa1587-20260729
```

Temporary upload and restart-log files were removed after verification.

## Next UX correction

Initialize the status view from the persisted audit ledger and show its observation time and stale/current state. Rebuild the candidate inventory only when an addition job actually needs it or when the user explicitly requests a refresh. This keeps page rendering cheap while making the persistent audit discoverable immediately after restart.
