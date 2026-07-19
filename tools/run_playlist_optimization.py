#!/usr/bin/env python3
"""Run the fixed-set optimizer, full-set artist profile, and bridge gate."""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys


def run(arguments: list[str]) -> None:
    subprocess.run(arguments, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=pathlib.Path, required=True)
    parser.add_argument("--playlist", type=pathlib.Path, required=True)
    parser.add_argument("--matrix", type=pathlib.Path, required=True)
    parser.add_argument("--lastmix-install", type=pathlib.Path)
    parser.add_argument("--artist-profile", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--music-root", default="/mnt/usbHD/music/")
    settings_group = parser.add_mutually_exclusive_group(required=True)
    settings_group.add_argument("--settings", type=pathlib.Path)
    settings_group.add_argument("--weights")
    parser.add_argument("--algorithm", choices=("static", "adaptive"))
    parser.add_argument("--learned-blend")
    parser.add_argument("--adaptive-seeds", type=int)
    parser.add_argument("--seed", default="20260717")
    parser.add_argument("--restarts", default="250")
    parser.add_argument("--bridge-threshold", default="0.70")
    parser.add_argument("--max-bridges", default="2")
    parser.add_argument("--bridge-count", type=int)
    parser.add_argument("--no-repeat-artist")
    parser.add_argument("--no-repeat-album")
    args = parser.parse_args()
    if bool(args.lastmix_install) == bool(args.artist_profile):
        parser.error("Supply exactly one of --lastmix-install or --artist-profile")

    settings = None
    if args.settings:
        settings = json.loads(args.settings.read_text(encoding="utf-8"))
        resolved = settings["resolved"]
        args.weights = ",".join(str(value) for value in resolved["weights"])
        args.learned_blend = args.learned_blend or str(resolved["learned_blend_fraction"])
        args.no_repeat_artist = args.no_repeat_artist or str(resolved["no_repeat_artist"])
        args.no_repeat_album = args.no_repeat_album or str(resolved["no_repeat_album"])
        args.algorithm = args.algorithm or str(settings["algorithm"])
        args.adaptive_seeds = args.adaptive_seeds or int(
            settings["preferences"]["num_seed_tracks"]
        )
    else:
        args.algorithm = args.algorithm or "static"
        args.learned_blend = args.learned_blend or "0.20"
        args.adaptive_seeds = args.adaptive_seeds or 3
        args.no_repeat_artist = args.no_repeat_artist or "5"
        args.no_repeat_album = args.no_repeat_album or "10"
    if args.algorithm not in {"static", "adaptive"}:
        parser.error(f"Algorithm {args.algorithm!r} is not supported by this one-shot optimizer")

    tools = pathlib.Path(__file__).resolve().parent
    args.output.mkdir(parents=True, exist_ok=True)
    if args.settings:
        frozen_settings = args.output / "lms-blissmixer-settings.json"
        if args.settings.resolve() != frozen_settings.resolve():
            shutil.copyfile(args.settings, frozen_settings)
        print(
            f"Captured server algorithm: {settings['algorithm']}; primary scoring uses "
            f"the sliding adaptive seed window ({args.adaptive_seeds}) and learned blend "
            f"{args.learned_blend}" if args.algorithm == "adaptive" else
            f"Captured server algorithm: {settings['algorithm']}; primary scoring uses "
            f"the resolved static sliders {args.weights}"
        )
    optimizer = [
        sys.executable, str(tools / "playlist_optimizer.py"),
        "--db", str(args.db),
        "--playlist", str(args.playlist),
        "--matrix", str(args.matrix),
        "--output", str(args.output),
        "--music-root", args.music_root,
        "--algorithm", args.algorithm,
        "--weights", args.weights,
        "--learned-blend", args.learned_blend,
        "--adaptive-seeds", str(args.adaptive_seeds),
        "--seed", args.seed,
        "--restarts", args.restarts,
        "--no-repeat-artist", args.no_repeat_artist,
        "--no-repeat-album", args.no_repeat_album,
    ]
    run(optimizer)

    frozen_profile = args.output / "lastfm-artist-profile.json"
    if args.artist_profile:
        if args.artist_profile.resolve() != frozen_profile.resolve():
            shutil.copyfile(args.artist_profile, frozen_profile)
    else:
        run([
            sys.executable, str(tools / "lastfm_artist_profile.py"),
            "--db", str(args.db),
            "--playlist", str(args.playlist),
            "--lastmix-install", str(args.lastmix_install),
            "--output", str(frozen_profile),
            "--music-root", args.music_root,
        ])

    bridge_command = [
        sys.executable, str(tools / "bridge_analyzer.py"),
        "--db", str(args.db),
        "--original", str(args.playlist),
        "--selected", str(args.output / "selected.m3u"),
        "--matrix", str(args.matrix),
        "--artist-profile", str(frozen_profile),
        "--output", str(args.output),
        "--music-root", args.music_root,
        "--algorithm", args.algorithm,
        "--weights", args.weights,
        "--learned-blend", args.learned_blend,
        "--adaptive-seeds", str(args.adaptive_seeds),
        "--threshold", args.bridge_threshold,
        "--max-bridges", args.max_bridges,
        "--no-repeat-artist", args.no_repeat_artist,
        "--no-repeat-album", args.no_repeat_album,
    ]
    if args.bridge_count is not None:
        bridge_command.extend(["--bridge-count", str(args.bridge_count)])
    run(bridge_command)
    print(f"Final candidate: {args.output / 'selected-with-bridges.m3u'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
