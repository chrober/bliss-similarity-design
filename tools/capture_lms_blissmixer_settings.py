#!/usr/bin/env python3
"""Capture active lms-blissmixer preferences through the supported LMS CLI API."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import urllib.request


PREFERENCE_NAMES = (
    "weight_tempo", "weight_timbre", "weight_loudness", "weight_chroma",
    "use_forest", "use_adaptive_weights", "learned_blend",
    "num_seed_tracks", "seed_strict_order", "use_lastfm_weighting",
    "lastfm_weighting_weight", "no_repeat_artist", "no_repeat_album",
    "no_repeat_track",
)


def query_preference(endpoint: str, name: str, request_id: int, timeout: float) -> object:
    payload = json.dumps({
        "id": request_id,
        "method": "slim.request",
        "params": ["", ["pref", f"plugin.blissmixer:{name}", "?"]],
    }).encode("utf-8")
    request = urllib.request.Request(
        endpoint, data=payload, headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        result = json.load(response)
    if "error" in result or "_p2" not in result.get("result", {}):
        raise RuntimeError(f"Unable to read plugin.blissmixer:{name}: {result}")
    return result["result"]["_p2"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", default="http://192.168.1.111:9000")
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()
    endpoint = args.server.rstrip("/") + "/jsonrpc.js"
    preferences = {
        name: query_preference(endpoint, name, index, args.timeout)
        for index, name in enumerate(PREFERENCE_NAMES, 1)
    }
    algorithm = (
        "adaptive" if int(preferences["use_adaptive_weights"] or 0)
        else "forest" if int(preferences["use_forest"] or 0)
        else "static"
    )
    output = {
        "schema_version": 1,
        "captured_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "server": args.server.rstrip("/"),
        "namespace": "plugin.blissmixer",
        "algorithm": algorithm,
        "preferences": preferences,
        "resolved": {
            "weights": [
                int(preferences[name]) for name in (
                    "weight_tempo", "weight_timbre", "weight_loudness", "weight_chroma",
                )
            ],
            "learned_blend_fraction": int(preferences["learned_blend"]) / 100.0,
            "no_repeat_artist": int(preferences["no_repeat_artist"]),
            "no_repeat_album": int(preferences["no_repeat_album"]),
            "no_repeat_track": int(preferences["no_repeat_track"]),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    print(json.dumps({"algorithm": algorithm, **output["resolved"], "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
