#!/usr/bin/env python3
"""Compare Python adaptive weights with a running shipped bliss-mixer binary."""

from __future__ import annotations

import argparse
import json
import pathlib
import urllib.request

try:
    from .playlist_optimizer import (
        AdaptiveScorer, load_matrix, load_playlist_tracks, open_readonly_db,
        parse_m3u, sha256_file,
    )
except ImportError:
    from playlist_optimizer import (
        AdaptiveScorer, load_matrix, load_playlist_tracks, open_readonly_db,
        parse_m3u, sha256_file,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=pathlib.Path, required=True)
    parser.add_argument("--playlist", type=pathlib.Path, required=True)
    parser.add_argument("--matrix", type=pathlib.Path, required=True)
    parser.add_argument("--endpoint", default="http://127.0.0.1:12111")
    parser.add_argument("--binary", type=pathlib.Path)
    parser.add_argument("--music-root", default="/mnt/usbHD/music/")
    parser.add_argument("--seed-count", type=int, default=3)
    parser.add_argument("--learned-blend", type=int, default=20)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()

    parsed = parse_m3u(args.playlist)
    connection = open_readonly_db(args.db)
    try:
        tracks = load_playlist_tracks(connection, parsed, args.music_root)
    finally:
        connection.close()
    seeds = tracks[:args.seed_count]
    matrix = load_matrix(args.matrix)
    variance = AdaptiveScorer.variance_weights([track.features for track in seeds])
    alpha = args.learned_blend / 100.0
    expected = [
        alpha * matrix[index][index] + (1.0 - alpha) * variance[index]
        for index in range(len(variance))
    ]
    payload = json.dumps({
        "count": 1, "filtergenre": 0, "filterxmas": 0, "min": 0, "max": 0,
        "maxbpmdiff": 0, "tracks": [track.db_file for track in seeds],
        "previous": [], "shuffle": 0, "forest": 0, "adaptiveweights": 1,
        "learnedblend": args.learned_blend, "debug": 1, "norepart": 0,
        "norepalb": 0, "genregroups": [], "allgenres": 0,
    }).encode("utf-8")
    request = urllib.request.Request(
        args.endpoint.rstrip("/") + "/api/mix", data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        response.read()
        debug = json.loads(response.headers["X-Bliss-Debug"])
    actual = [float(row["weight"]) for row in debug["weights"]]
    differences = [abs(left - right) for left, right in zip(expected, actual)]
    result = {
        "schema_version": 1,
        "algorithm": debug["algorithm"],
        "seed_files": [track.db_file for track in seeds],
        "seed_count": len(seeds),
        "learned_blend_percent": args.learned_blend,
        "max_absolute_diagonal_difference": max(differences),
        "expected_diagonal": expected,
        "binary_diagonal": actual,
        "db_sha256": sha256_file(args.db),
        "matrix_sha256": sha256_file(args.matrix),
        "playlist_sha256": sha256_file(args.playlist),
        "binary_sha256": sha256_file(args.binary) if args.binary else None,
    }
    if debug["num_seeds"] != len(seeds) or max(differences) > 1e-5:
        raise AssertionError(f"Adaptive parity check failed: {result}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    print(json.dumps({
        "algorithm": result["algorithm"],
        "max_difference": result["max_absolute_diagonal_difference"],
        "output": str(args.output),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
