#!/usr/bin/env python3
"""Validate an extended M3U's structure, uniqueness, and referenced local files."""

from __future__ import annotations

import argparse
import hashlib
import pathlib

from playlist_optimizer import lms_file_url


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("playlist", type=pathlib.Path)
    parser.add_argument("--expected-count", type=int)
    parser.add_argument("--check-files", action="store_true")
    parser.add_argument(
        "--require-lms-blocks", action="store_true",
        help="Require #EXTURL/#EXTINF/path blocks and exact Lyrion file-URL escaping",
    )
    args = parser.parse_args()

    payload = args.playlist.read_bytes()
    lines = payload.decode("utf-8-sig").splitlines()
    try:
        header_index = lines.index("#EXTM3U")
    except ValueError as error:
        raise ValueError("Playlist does not contain #EXTM3U") from error
    if any(line and not line.startswith("#") for line in lines[:header_index]):
        raise ValueError("Unexpected path before #EXTM3U")
    tracks = [
        line for line in lines[header_index + 1:]
        if line and not line.startswith("#")
    ]
    if args.require_lms_blocks:
        for index, line in enumerate(lines):
            if not line or line.startswith("#"):
                continue
            if index < 2 or not lines[index - 2].startswith("#EXTURL:") \
                    or not lines[index - 1].startswith("#EXTINF:"):
                raise ValueError(f"Track does not have an adjacent #EXTURL/#EXTINF block: {line}")
            expected_url = "#EXTURL:" + lms_file_url(line)
            if lines[index - 2] != expected_url:
                raise ValueError(
                    f"EXTURL does not match Lyrion serialization for {line}: {lines[index - 2]}"
                )
    if args.expected_count is not None and len(tracks) != args.expected_count:
        raise ValueError(f"Expected {args.expected_count} tracks; found {len(tracks)}")
    if len(tracks) != len(set(tracks)):
        raise ValueError("Playlist contains duplicate paths")
    if args.check_files:
        missing = [track for track in tracks if not pathlib.Path(track).is_file()]
        if missing:
            raise ValueError(f"{len(missing)} referenced files are missing; first: {missing[0]}")
    digest = hashlib.sha256(payload).hexdigest()
    print(
        f"ok tracks={len(tracks)} unique={len(set(tracks))} "
        f"lms_blocks={args.require_lms_blocks} sha256={digest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
