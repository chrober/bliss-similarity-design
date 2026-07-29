# Better Call Bliss - clarified job controls and extension icon checkpoint

**Date:** 2026-07-23
**State:** The richer terminology, control relevance, directional-context
explanation, no-op validation, and packaged extension icon are deployed and
verified on ARM64 LMS

## Published implementation revision

| Repository | Revision | Result |
| --- | --- | --- |
| [chrober/lms-better-call-bliss](https://github.com/chrober/lms-better-call-bliss/tree/feature/first-ux-preview) | `5deb00752af8da2f38eed63f9e291309f27cf893` | Version `0.5.2` clarified job editor, relevance-aware controls, preserved-order no-op guard, and packaged 512x512 icon |

No native optimizer or shared-core change was required.

## UX changes

- **Ordering** is now **Source-track order**, with **Optimize source order** and
  the visibly unconnected **Preserve source order**.
- **Extension** is now **Additional tracks**. The working choices are
  **None - reorder existing tracks only** and **Add automatically**; future
  exact-count, per-transition, target-length, and double-length choices remain
  explicitly disabled and labelled not connected.
- **Adaptive context tracks** is now **Musical context window (previous
  tracks)**. Its help states that scoring is directional and uses a rolling
  preceding history. For a bridge C between A and B, the first leg uses history
  ending in A to score C; the second uses the updated history including C to
  score B. A value of one reduces those legs to A-to-C and C-to-B.
- **Route-search restarts** is now **Additional route-search attempts**, grouped
  under **Advanced search effort**. The help explains that each deterministic
  attempt starts from a different candidate route, may improve the result, and
  costs additional processing time; zero still retains built-in fixed starts.
- Automatic-addition fields are disabled and visually de-emphasized outside
  automatic mode. Route-search attempts are disabled when source order is
  preserved.
- A preserved-order request with no possible additions is a guaranteed no-op.
  The browser disables submission and explains why, while `JobOptions.pm`
  independently rejects a bypassed request before native execution.

## Extension icon

The plugin package now contains
`BetterCallBliss/HTML/EN/plugins/BetterCallBliss/html/images/bettercallbliss.png`, and
`install.xml` declares its public plugin URL. The 512x512 transparent ARGB image
uses four charcoal source-track nodes on a forward route and an amber fifth
node inserted into the path. It contains no text, note glyph, or external
trademark and remains recognizable at 32x32.

The asset was generated with the built-in image-generation tool from a
purpose-specific flat-icon prompt, generated against a flat chroma background,
converted to transparency with the image skill's background-removal helper,
resized with high-quality resampling, and validated for dimensions, alpha, and
transparent corners. Only the final packaged asset is tracked; intermediate
generation files were removed.

## Live verification

The deployed plugin reported:

```text
ready=1
problem_count=0
ux_contract=extras-job-editor-v5
working_mode=per-job-adaptive/reorder-or-auto-extend/create-copy
```

The rendered Extras page returned HTTP 200 and contained every revised label,
the bridge-context explanation, Advanced search help, and the relevance script.
The icon URL returned HTTP 200 as `image/png` at 512x512.

A handcrafted Preserve source order plus no-additions POST was rejected with:

```text
Preserve source order requires an addition mode with a non-zero target
```

A normal two-track, no-additions Preview then completed successfully while the
browser-irrelevant automatic-addition fields were omitted, confirming that
server defaults and the working path remained intact.

The deployment backup remains outside the scanned plugin root under
`Cache/BetterCallBliss-backups`.

## Next gate

Resume **Add exactly N tracks** using the established result feedback, safe
copy publication, clarified terminology, and relevance behavior.
