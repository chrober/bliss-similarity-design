# Implementation checkpoint 30 - Target and double track-count presets

Date: 2026-08-08

This checkpoint records the first connected **target/double** implementation slice: target by track count, not target by duration.

## What changed

- The Extras **Additional tracks** selector now exposes **Reach target track count** and **Double track count** as working modes.
- **Reach target track count** asks for a final track count `T`; Better Call Bliss derives `additional_track_count = T - S` from the selected source playlist size `S`.
- **Double track count** derives `additional_track_count = S`, yielding exactly `2S` final tracks.
- Both modes reuse the native exact-count bridge workflow. The plugin keeps the user-facing mode in job options while sending a schema-compatible native `exact_count` request to `bliss-playlist-optimizer`.
- Plain **Add exactly N tracks** remains internal-gap-only with no endpoint slots. Target/double presets may enable opening/closing slots only when the requested count cannot be reached with the `S - 1` internal slots alone.
- Result summaries now distinguish manually requested exact additions, target-count completion, and double-count completion.

## Boundaries

- These are track-count features only. Duration targets and double-duration presets remain future work because they need duration tolerance and a quality-vs-duration objective.
- Explicit user controls for opening and closing additions remain unconnected. Endpoint slots are an implementation detail of target/double count when required for feasibility.
- The native optimizer still owns exact feasibility and returns no partial playlist on failure.

## Validation

- Inline Extras JavaScript parses with `node --check`.
- `git diff --check` passes for the plugin repository.
- The local Windows workspace still has no Perl executable, so the updated Perl regression test could not be executed locally.
