#!/usr/bin/env python3
"""Freeze a Last.fm similar-artist profile from every artist in an input M3U."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from playlist_optimizer import load_playlist_tracks, open_readonly_db, parse_m3u


def canonical(value: str) -> str:
    return " ".join(value.casefold().split())


def read_lastmix_api_key(path: pathlib.Path) -> str:
    root = ET.parse(path).getroot()
    values = [
        element.text.strip()
        for element in root.iter()
        if element.tag.rsplit("}", 1)[-1] == "id2" and element.text and element.text.strip()
    ]
    if len(values) != 1:
        raise ValueError(f"Expected exactly one LastMix id2 API key in {path}; got {len(values)}")
    # LastMix::LFM::aid() removes UUID separators before making anonymous API calls.
    return values[0].replace("-", "")


def query_similar(artist: str, api_key: str, limit: int, timeout: float) -> dict[str, object]:
    parameters = urllib.parse.urlencode({
        "method": "artist.getsimilar",
        "artist": artist,
        "api_key": api_key,
        "limit": limit,
        "autocorrect": 1,
        "format": "json",
    })
    request = urllib.request.Request(
        "https://ws.audioscrobbler.com/2.0/?" + parameters,
        headers={"User-Agent": "BlissPlaylistOptimizerPrototype/1.0"},
    )
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            try:
                payload = json.loads(error.read().decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                payload = None
            if isinstance(payload, dict) and "error" in payload:
                return payload
            last_error = error
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as error:
            last_error = error
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Last.fm query failed for {artist!r}: {last_error}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=pathlib.Path, required=True)
    parser.add_argument("--playlist", type=pathlib.Path, required=True)
    parser.add_argument("--lastmix-install", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--music-root", default="/mnt/usbHD/music/")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()

    parsed = parse_m3u(args.playlist)
    connection: sqlite3.Connection = open_readonly_db(args.db)
    try:
        tracks = load_playlist_tracks(connection, parsed, args.music_root)
    finally:
        connection.close()
    source_artists = list(dict.fromkeys(track.artist for track in tracks))
    api_key = read_lastmix_api_key(args.lastmix_install)

    lookups: list[dict[str, object]] = []
    aggregate: dict[str, dict[str, object]] = {}
    global_error: str | None = None
    for source in source_artists:
        payload = (
            {"error": 10, "message": global_error}
            if global_error
            else query_similar(source, api_key, args.limit, args.timeout)
        )
        error = payload.get("message") if "error" in payload else None
        if payload.get("error") == 10 and not global_error:
            global_error = str(error)
        rows = payload.get("similarartists", {}).get("artist", []) if not error else []
        normalized_rows: list[dict[str, object]] = []
        for rank, row in enumerate(rows, 1):
            name = str(row.get("name", "")).strip()
            if not name:
                continue
            match = float(row.get("match", 0.0))
            normalized = {
                "name": name,
                "mbid": str(row.get("mbid", "")),
                "match": match,
                "rank": rank,
            }
            normalized_rows.append(normalized)
            key = canonical(name)
            artist = aggregate.setdefault(key, {
                "name": name,
                "mbid": str(row.get("mbid", "")),
                "support_seeds": [],
                "matches": [],
                "ranks": [],
            })
            artist["support_seeds"].append(source)
            artist["matches"].append(match)
            artist["ranks"].append(rank)
        lookups.append({
            "source_artist": source,
            "error": error,
            "returned": len(normalized_rows),
            "artists": normalized_rows,
        })

    for artist in aggregate.values():
        matches = artist.pop("matches")
        ranks = artist.pop("ranks")
        artist["support_count"] = len(artist["support_seeds"])
        artist["match_sum"] = sum(matches)
        artist["match_max"] = max(matches)
        artist["best_rank"] = min(ranks)
        artist["mean_rank"] = sum(ranks) / len(ranks)

    output = {
        "schema_version": 1,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "service": "Last.fm artist.getSimilar",
        "query_policy": {
            "input": "all distinct artists from the original playlist",
            "limit_per_artist": args.limit,
            "autocorrect": True,
            "api_key_source": str(args.lastmix_install.resolve()),
            "api_key_stored": False,
        },
        "playlist_artist_count": len(source_artists),
        "source_artists": source_artists,
        "successful_lookups": sum(not lookup["error"] for lookup in lookups),
        "global_error": global_error,
        "lookups": lookups,
        "similar_artists": aggregate,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_artists": len(source_artists),
        "successful": output["successful_lookups"],
        "similar_artists": len(aggregate),
        "output": str(args.output),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
