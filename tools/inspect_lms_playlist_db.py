#!/usr/bin/env python3
"""Read-only comparison of LMS track rows and playlist-file stat metadata."""

from __future__ import annotations

import argparse
import os
import pathlib
import sqlite3


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=pathlib.Path)
    parser.add_argument("playlist", nargs="+", type=pathlib.Path)
    args = parser.parse_args()

    connection = sqlite3.connect(
        f"{args.database.resolve().as_uri()}?mode=ro", uri=True,
    )
    try:
        tables = [
            row[0] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
        ]
        print("playlist-related tables:", [
            table for table in tables if "playlist" in table.casefold()
        ])
        columns = [
            row[1] for row in connection.execute("PRAGMA table_info(tracks)")
        ]
        print("tracks columns:", columns)
        wanted = [
            name for name in (
                "id", "url", "title", "timestamp", "filesize", "content_type",
                "extid", "remote", "audio", "seen",
            )
            if name in columns
        ]
        for playlist in args.playlist:
            stat = os.stat(playlist)
            print(
                f"filesystem path={playlist} size={stat.st_size} "
                f"mtime={stat.st_mtime} mtime_ns={stat.st_mtime_ns}"
            )
            url_suffix = str(playlist).replace("'", "''")
            rows = connection.execute(
                f"SELECT {','.join(wanted)} FROM tracks WHERE url LIKE ?",
                (f"%{url_suffix.split('/')[-1].replace(' ', '%')}%",),
            ).fetchall()
            print("database rows:", [dict(zip(wanted, row)) for row in rows])
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
