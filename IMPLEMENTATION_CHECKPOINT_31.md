# Implementation checkpoint 31 - Context entry points and 0.14.4 release

Date: 2026-08-09

This checkpoint records the first connected context-entry implementation slice and the `0.14.4` plugin release.

## What changed

- The saved-playlist context action is now a real workflow shortcut. It opens the Better Call Bliss Extras editor with the selected saved playlist preselected.
- **Bliss me there…** is now connected as a first route-to-track slice. It opens the Extras editor with the selected player and destination track prefilled.
- The connected **Bliss me there…** route preserves two anchors: the selected player's current queue tail and the selected local destination track.
- The preview uses the existing exact-count bridge engine to evaluate `queue tail -> one bridge -> destination`.
- Queue output skips the queue-tail anchor, so accepting the preview appends only the generated suffix to the selected player queue.
- Route-to-track previews remain read-only until the user explicitly accepts **Send to player queue**.
- The accept panel hides playlist-copy and source-overwrite actions for route-to-track previews because those previews are queue-oriented.
- The plugin status contract advanced to `extras-job-editor-v20`.
- The plugin version was bumped to `0.14.4`, committed as `8a43a0d`, pushed to `main`, released on GitHub, and published into `chrober/lms-plugins` by the release workflow.
- The release workflow now accepts either `LMS_PLUGINS_TOKEN` or `MS_PLUGINS_TOKEN` for the cross-repository plugin-feed update.

## Boundaries

- Native fixed-destination route generation is still not implemented. The current route-to-track behavior is a plugin-composed two-anchor bridge request, not the future multi-hop destination-lock optimizer mode.
- The first **Bliss me there…** slice supports one inserted bridge. Auto/no-bridge cases, user-selected multi-intermediate counts, and native longer fluent routes remain future work.
- Material exposes these actions through the item menu / More affordance. They are not permanent inline row buttons.
- Perl syntax checks were still not available in the Windows workspace because no local Perl or installed WSL distribution was present.

## Validation

- `git diff --check` passed before commit.
- The GitHub release workflow completed successfully for `0.14.4`.
- The workflow downloaded and verified the pinned optimizer release binaries, packaged the LMS plugin ZIP, published the GitHub release, and updated `chrober/lms-plugins`.
- Published release: <https://github.com/chrober/lms-better-call-bliss/releases/tag/0.14.4>
- Release workflow run: <https://github.com/chrober/lms-better-call-bliss/actions/runs/31266982441>