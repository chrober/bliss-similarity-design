# Bliss 'Em All - visible outcomes and safe copy naming checkpoint

**Date:** 2026-07-22
**State:** Browser-visible running/success/failure feedback, Unicode-safe
automatic names, numbered collision avoidance, and non-overwriting publication
are deployed and verified on ARM64 LMS

## Published implementation revision

| Repository | Revision | Result |
| --- | --- | --- |
| [chrober/lms-bliss-em-all](https://github.com/chrober/lms-bliss-em-all/tree/feature/first-ux-preview) | `3c9ad2cb46b0e63e7b3824831819dab8b9ad52e1` | Version `0.5.1` automatic polling, prominent structured outcomes, decoded Unicode naming, numbered blank-name collision handling, and exclusive final-path creation |

No native optimizer change was required.

## Root causes

The native job state and stable error codes already existed, but a running page
required manual refresh. Users therefore saw neither completion nor failure
unless they refreshed or inspected the server log. Copy errors were stored on
the job but were not presented as a sufficiently prominent operation outcome.

The live catalog exposed one local playlist title as mojibaked UTF-8 even though
its percent-encoded file URL still represented the correct filename. Automatic
names derived from the catalog title consequently lost an emoji flag.

The reported second-run overwrite was not an actual file replacement: the
server log recorded `OUTPUT_EXISTS`. The page failed to make that rejection
obvious. The writer nevertheless used an overwrite-capable final `rename`, so
the implementation was strengthened rather than relying only on the earlier
existence check.

## Connected behavior

- A running result displays an informational banner and polls its in-memory job
  every 1.5 seconds, while retaining manual refresh.
- Preview completion and failure, plus copy completion and failure, use
  prominent green/red banners. Failures include the stable code, actionable
  detail, and an explicit statement about whether anything changed.
- Local saved-playlist display and automatic copy names use the decoded basename
  of the file URL, with the catalog title only as a fallback.
- Leaving the copy-name field blank selects the first free name: base,
  `(2)`, `(3)`, and so on. The generated-name intent is frozen with the job
  and checked again at create time.
- An explicitly entered existing name fails with `OUTPUT_EXISTS`.
- The verified temporary M3U is published by opening the final path with
  `O_CREAT | O_EXCL` and copying the verified bytes. The final operation has
  no overwrite-capable rename; a concurrent collision fails closed.

## Live verification

The deployed plugin reported:

```text
ready=1
problem_count=0
ux_contract=extras-job-editor-v4
working_mode=per-job-adaptive/reorder-or-auto-extend/create-copy
```

An anonymized 13-track single-artist playlist with an emoji flag in its filename
was exercised through the Extras HTTP form:

1. The submitted running page contained the visible running state and automatic
   poll, and its proposed optimized name retained both Unicode regional
   indicators.
2. An impossible artist window produced a browser-visible
   `ROUTE_SEARCH_FAILED` result with capacity guidance and "No playlist was
   changed."
3. A valid per-job window produced the browser-visible Preview-success banner.
4. Reusing the source name produced browser-visible
   `Copy not created - OUTPUT_EXISTS`; the matching M3U had identical SHA-256
   `02c9abebedd751d8182615c09db554eea3a9c1cedcc961823f24c1ab1824f333`
   before and after.
5. A separate non-mutating validation request against an existing
   source/Extended pair proposed `Extended (2)`.

The deployment rollback remains outside the scanned plugin root under
`Cache/BlissEmAll-backups`.

## Next gate

Resume **Add exactly N tracks**. It should use the same visible lifecycle,
Unicode-safe destination naming, structured infeasibility banner, and
exclusive-create writer.
