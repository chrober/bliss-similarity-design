# Bliss 'Em All - accessible outcomes and monochrome Extras icon checkpoint

**Date:** 2026-07-23
**State:** Theme-independent status contrast and a Material-recognized
monochrome Extras icon are deployed and verified on ARM64 LMS

## Published implementation revision

| Repository | Revision | Result |
| --- | --- | --- |
| [chrober/lms-bliss-em-all](https://github.com/chrober/lms-bliss-em-all/tree/feature/first-ux-preview) | `a4b84bf0cbda6f2365e08eac5e939c94466975d1` | Version `0.5.3` accessible status banners, theme-aware secondary text, explicit icon registration, and monochrome Material icon marker |

No native optimizer or shared-core change was required.

## Status-feedback contrast

The Extras page is hosted inside Material, whose dark theme supplies a light
`--text-color`. The prior light warning background inherited that foreground,
producing low contrast. Warning, error, success, and information banners now
declare both their foreground and background colors:

| State | Foreground | Background | Contrast |
| --- | --- | --- | --- |
| Warning | `#3d2a00` | `#fff2c2` | 12.25:1 |
| Error | `#5f0000` | `#ffe7e7` | 12.00:1 |
| Success | `#0b4a18` | `#e8f7eb` | 9.43:1 |
| Information/running | `#0b3c5d` | `#e8f5fd` | 10.40:1 |

Secondary notes and disabled hints use the host's `--text-color` with reduced
emphasis rather than a fixed gray that can disappear in a dark theme.

## Material Extras icon contract

The earlier plugin PNG was already present in the server's
`material-skin extras` response. Material nevertheless showed its generic
extension/puzzle glyph because its client deliberately replaces unrecognized
Extras images with that fallback.

The replacement follows Material's supported marker convention:

```text
plugins/BlissEmAll/html/images/blissemall_MTL_icon_timeline.png
```

`Web.pm` explicitly registers that value in the `icons` page-link category
under the same key as the Extras link, and `install.xml` declares it for
plugin metadata. Material parses `MTL_icon_timeline` and renders its own
theme-colored monochrome `timeline` glyph. Classic and metadata consumers can
load the actual packaged 512x512 transparent monochrome route PNG.

The route asset was generated with the built-in image tool on a flat chroma
background, then processed with the installed image-skill removal helper,
one-pixel edge contraction, high-quality resampling, and alpha/fringe
validation. The obsolete colored icon was removed.

## Live verification

The deployed plugin reported:

```text
ready=1
problem_count=0
ux_contract=extras-job-editor-v6
```

The live Extras payload returned:

```text
id=PLUGIN_BLISSEMALL_NAME
icon=plugins/BlissEmAll/html/images/blissemall_MTL_icon_timeline.png
material_glyph=timeline
```

The Extras page and new PNG both returned HTTP 200. The page contained the
explicit warning and error foreground rules, and the image was served as
`image/png` at 512x512. A rollback copy remains outside the scanned plugin
root under `Cache/BlissEmAll-backups`.

## Next gate

Connect **Add exactly N tracks** end to end. The native optimizer already has
an exact-count selection preview; the next slice should expose and validate N
per job, invoke that contract from LMS, render exact-count success or
infeasibility clearly, preserve the reviewed output through safe copy
publication, and add a live ARM64 exercise.
