#!/usr/bin/env python3
"""Evaluate and, only when justified, insert similarity-aware bridge tracks."""

from __future__ import annotations

import argparse
import bisect
import json
import pathlib

try:
    from .playlist_optimizer import (
        Track, learned_distance, load_library_tracks, load_matrix,
        load_playlist_tracks, open_readonly_db, parse_m3u,
        matrix_projection, quadratic_form, learned_distance_from_projection,
        repeat_violations_for_tracks, sha256_file, static_distance,
        static_multipliers, write_m3u,
    )
except ImportError:  # direct script execution
    from playlist_optimizer import (
        Track, learned_distance, load_library_tracks, load_matrix,
        load_playlist_tracks, open_readonly_db, parse_m3u,
        matrix_projection, quadratic_form, learned_distance_from_projection,
        repeat_violations_for_tracks, sha256_file, static_distance,
        static_multipliers, write_m3u,
    )


def canonical(value: str) -> str:
    return " ".join(value.casefold().split())


def empirical_percentile(value: float, sample: list[float]) -> float:
    return bisect.bisect_left(sample, value) / max(1, len(sample) - 1)


def lastfm_lookup_maps(profile: dict[str, object]) -> dict[str, dict[str, dict[str, object]]]:
    """Index the frozen per-source Last.fm results without losing edge locality."""
    result: dict[str, dict[str, dict[str, object]]] = {}
    for lookup in profile.get("lookups", []):
        if not isinstance(lookup, dict) or lookup.get("error"):
            continue
        source = canonical(str(lookup.get("source_artist", "")))
        if not source:
            continue
        result[source] = {
            canonical(str(row.get("name", ""))): row
            for row in lookup.get("artists", [])
            if isinstance(row, dict) and str(row.get("name", "")).strip()
        }
    return result


def artist_evidence(
    artist: str,
    left_artist: str | None,
    right_artist: str | None,
    lookups: dict[str, dict[str, dict[str, object]]],
    global_similar: dict[str, dict[str, object]],
    original_artists: set[str],
) -> dict[str, object]:
    """Rank edge-local Last.fm evidence before collection-wide fallbacks."""
    candidate = canonical(artist)
    endpoint_sources = list(dict.fromkeys(
        canonical(value) for value in (left_artist, right_artist) if value
    ))
    local_hits = [
        (source, lookups[source][candidate])
        for source in endpoint_sources
        if candidate in lookups.get(source, {})
    ]
    if local_hits:
        match_sum = sum(float(row.get("match", 0.0)) for _, row in local_hits)
        best_rank = min(int(row.get("rank", 10**9)) for _, row in local_hits)
        scope = "edge-both" if len(local_hits) == len(endpoint_sources) == 2 else "edge-one"
        tier = 1 if scope == "edge-both" else 2
        return {
            "scope": scope,
            "tier": tier,
            "support_count": len(local_hits),
            "support_sources": [source for source, _ in local_hits],
            "match_sum": match_sum,
            "best_rank": best_rank,
            "rank_key": (tier, -len(local_hits), -match_sum, best_rank),
        }

    global_row = global_similar.get(candidate)
    if global_row:
        support_count = int(global_row.get("support_count", 0))
        match_sum = float(global_row.get("match_sum", 0.0))
        best_rank = int(global_row.get("best_rank", 10**9))
        return {
            "scope": "collection-fallback",
            "tier": 3,
            "support_count": support_count,
            "support_sources": list(global_row.get("support_seeds", [])),
            "match_sum": match_sum,
            "best_rank": best_rank,
            "rank_key": (3, -support_count, -match_sum, best_rank),
        }
    if candidate in original_artists:
        return {
            "scope": "original-artist-fallback", "tier": 4,
            "support_count": 0, "support_sources": [], "match_sum": 0.0,
            "best_rank": 10**9, "rank_key": (4, 0, 0.0, 10**9),
        }
    return {
        "scope": "bliss-only-fallback", "tier": 5,
        "support_count": 0, "support_sources": [], "match_sum": 0.0,
        "best_rank": 10**9, "rank_key": (5, 0, 0.0, 10**9),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=pathlib.Path, required=True)
    parser.add_argument("--original", type=pathlib.Path, required=True)
    parser.add_argument("--selected", type=pathlib.Path, required=True)
    parser.add_argument("--matrix", type=pathlib.Path, required=True)
    parser.add_argument("--artist-profile", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--music-root", default="/mnt/usbHD/music/")
    parser.add_argument("--algorithm", choices=("static", "adaptive"), default="static")
    parser.add_argument("--weights", default="20,28,3,49")
    parser.add_argument("--learned-blend", type=float, default=0.20)
    parser.add_argument("--adaptive-seeds", type=int, default=3)
    parser.add_argument("--threshold", type=float, default=0.70)
    parser.add_argument("--max-bridges", type=int, default=2)
    parser.add_argument(
        "--bridge-count", type=int,
        help="Insert exactly this many additional tracks instead of threshold-gated auto mode",
    )
    parser.add_argument("--no-repeat-artist", type=int, default=5)
    parser.add_argument("--no-repeat-album", type=int, default=10)
    args = parser.parse_args()
    if args.bridge_count is not None and args.bridge_count < 0:
        parser.error("--bridge-count must be zero or greater")
    if args.adaptive_seeds < 1:
        parser.error("--adaptive-seeds must be at least one")
    weights = tuple(float(value) for value in args.weights.split(","))

    original_m3u = parse_m3u(args.original)
    selected_m3u = parse_m3u(args.selected)
    connection = open_readonly_db(args.db)
    try:
        original = load_playlist_tracks(connection, original_m3u, args.music_root)
        selected = load_playlist_tracks(connection, selected_m3u, args.music_root)
        library = load_library_tracks(connection, args.music_root)
    finally:
        connection.close()
    if {track.db_file for track in original} != {track.db_file for track in selected}:
        raise ValueError("Selected playlist is not an exact permutation of the original")

    profile = json.loads(args.artist_profile.read_text(encoding="utf-8"))
    source_artists = list(dict.fromkeys(track.artist for track in original))
    if {canonical(value) for value in source_artists} != {
        canonical(value) for value in profile["source_artists"]
    }:
        raise ValueError("Artist profile was not built from the full original-playlist artist set")

    matrix = load_matrix(args.matrix)
    selected_files = {track.db_file for track in selected}
    learned_quadratics: dict[str, float] = {}
    learned_projections: dict[str, tuple[float, ...]] = {}
    for track in [*library, *selected]:
        if track.db_file in learned_quadratics:
            continue
        projection = matrix_projection(track.features, matrix)
        learned_quadratics[track.db_file] = quadratic_form(track.features, projection)
        if args.algorithm == "adaptive" or track.db_file in selected_files:
            learned_projections[track.db_file] = projection

    def fast_learned(left: Track, right: Track) -> float:
        if left.db_file in learned_projections:
            projected, other = left, right
        elif right.db_file in learned_projections:
            projected, other = right, left
        else:
            return learned_distance(left, right, matrix)
        return learned_distance_from_projection(
            projected.features,
            learned_projections[projected.db_file],
            learned_quadratics[projected.db_file],
            other.features,
            learned_quadratics[other.db_file],
        )

    def adaptive_distance(seeds: list[Track], candidate: Track) -> float:
        seeds = seeds[-args.adaptive_seeds:]
        if not seeds:
            raise ValueError("Adaptive bridge scoring requires at least one seed")
        count = float(len(seeds))
        mean = tuple(sum(track.features[i] for track in seeds) / count for i in range(23))
        mean_projection = tuple(
            sum(learned_projections[track.db_file][i] for track in seeds) / count
            for i in range(23)
        )
        mean_quadratic = quadratic_form(mean, mean_projection)
        learned_squared = learned_distance_from_projection(
            mean, mean_projection, mean_quadratic,
            candidate.features, learned_quadratics[candidate.db_file],
        )
        if len(seeds) == 1:
            return learned_squared ** 0.5
        variances = tuple(
            sum((track.features[i] - mean[i]) ** 2 for track in seeds) / count
            for i in range(23)
        )
        inverse = tuple(1.0 / (value + 1e-6) for value in variances)
        scale = 23.0 / sum(inverse)
        variance_squared = sum(
            inverse[i] * scale * (mean[i] - candidate.features[i]) ** 2
            for i in range(23)
        )
        return max(
            0.0,
            args.learned_blend * learned_squared
            + (1.0 - args.learned_blend) * variance_squared,
        ) ** 0.5

    if args.algorithm == "adaptive":
        direct_raw = [
            adaptive_distance(
                selected[max(0, position - args.adaptive_seeds):position],
                selected[position],
            )
            for position in range(1, len(selected))
        ]
        # A route-only sample would force its largest leg to percentile 1.0 and
        # make automatic bridging self-triggering. Instead, build a frozen
        # reference distribution from every curated candidate evaluated under
        # each actual selected-route seed context.
        adaptive_sample = sorted(
            adaptive_distance(
                selected[max(0, position - args.adaptive_seeds):position],
                candidate,
            )
            for position in range(1, len(selected))
            for candidate in original
            if candidate.db_file not in {
                seed.db_file
                for seed in selected[max(0, position - args.adaptive_seeds):position]
            }
        )

        def contextual_cost(seeds: list[Track], candidate: Track) -> float:
            return empirical_percentile(
                adaptive_distance(seeds, candidate), adaptive_sample,
            )

        gaps = [
            {
                "position": position,
                "left": selected[position - 1].label,
                "right": selected[position].label,
                "cost": empirical_percentile(direct_raw[position - 1], adaptive_sample),
                "raw_adaptive_distance": direct_raw[position - 1],
            }
            for position in range(1, len(selected))
        ]
    else:
        multipliers = static_multipliers(weights)
        static_sample = sorted(
            static_distance(original[i], original[j], multipliers)
            for i in range(len(original)) for j in range(i + 1, len(original))
        )
        learned_sample = sorted(
            fast_learned(original[i], original[j])
            for i in range(len(original)) for j in range(i + 1, len(original))
        )

        def fused(left: Track, right: Track) -> float:
            static = empirical_percentile(static_distance(left, right, multipliers), static_sample)
            learned = empirical_percentile(fast_learned(left, right), learned_sample)
            return (1 - args.learned_blend) * static + args.learned_blend * learned

        gaps = [
            {
                "position": position,
                "left": left.label,
                "right": right.label,
                "cost": fused(left, right),
            }
            for position, (left, right) in enumerate(zip(selected, selected[1:]), 1)
        ]
    gaps.sort(key=lambda gap: gap["cost"], reverse=True)
    triggering = [gap for gap in gaps if gap["cost"] > args.threshold]
    explicit_mode = args.bridge_count is not None
    requested_bridges = args.bridge_count if explicit_mode else args.max_bridges
    maximum_slots = len(gaps) + 2
    if requested_bridges > maximum_slots:
        parser.error(f"At most {maximum_slots} bridges can be inserted into this playlist")
    endpoint_slots = [
        {
            "position": 0, "left": None, "right": selected[0].label,
            "cost": None, "slot": "start",
        },
        {
            "position": len(selected), "left": selected[-1].label, "right": None,
            "cost": None, "slot": "end",
        },
    ]
    gaps_to_consider = (
        gaps + endpoint_slots
        if explicit_mode and requested_bridges > len(gaps)
        else gaps if explicit_mode
        else triggering
    )

    similar = profile.get("similar_artists", {})
    lookup_maps = lastfm_lookup_maps(profile)
    originals = {canonical(artist) for artist in source_artists}
    curated_files = {track.db_file for track in original}
    curated_identities = {(canonical(track.artist), canonical(track.title)) for track in original}

    selected_with_bridges = list(selected)
    proposals: list[dict[str, object]] = []
    used_bridge_files: set[str] = set()
    inserted = 0
    for gap in gaps_to_consider:
        if inserted >= requested_bridges:
            break
        slot = str(gap.get("slot", "internal"))
        if slot == "start":
            left, right = None, selected[0]
        elif slot == "end":
            left, right = selected[-1], None
        else:
            gap_index = int(gap["position"]) - 1
            left, right = selected[gap_index], selected[gap_index + 1]
        insert_at = (
            0 if slot == "start"
            else len(selected_with_bridges) if slot == "end"
            else next(
                index for index, item in enumerate(selected_with_bridges)
                if item.db_file == left.db_file
            ) + 1
        )
        endpoint_sources = {
            canonical(value) for value in (
                left.artist if left else None,
                right.artist if right else None,
            ) if value
        }
        local_artist_pool = {
            candidate_artist
            for source in endpoint_sources
            for candidate_artist in lookup_maps.get(source, {})
        }
        candidates: list[
            tuple[tuple[object, ...], Track, float, float, dict[str, object]]
        ] = []
        for track in library:
            if local_artist_pool and canonical(track.artist) not in local_artist_pool:
                continue
            if track.db_file in curated_files:
                continue
            if track.db_file in used_bridge_files:
                continue
            if (canonical(track.artist), canonical(track.title)) in curated_identities:
                continue
            tentative = list(selected_with_bridges)
            tentative.insert(insert_at, track)
            if args.algorithm == "adaptive":
                left_cost = (
                    contextual_cost(
                        selected_with_bridges[
                            max(0, insert_at - args.adaptive_seeds):insert_at
                        ],
                        track,
                    )
                    if left else 0.0
                )
                right_cost = (
                    contextual_cost(
                        tentative[
                            max(0, insert_at + 1 - args.adaptive_seeds):insert_at + 1
                        ],
                        right,
                    )
                    if right else 0.0
                )
            else:
                left_cost = fused(left, track) if left else 0.0
                right_cost = fused(track, right) if right else 0.0
            evidence = artist_evidence(
                track.artist,
                left.artist if left else None,
                right.artist if right else None,
                lookup_maps,
                similar,
                originals,
            )
            key = (
                *evidence["rank_key"],
                max(left_cost, right_cost),
                left_cost + right_cost,
                track.artist.casefold(),
                track.title.casefold(),
                track.db_file,
            )
            if repeat_violations_for_tracks(
                tentative, args.no_repeat_artist, args.no_repeat_album,
            ):
                continue
            candidates.append((key, track, left_cost, right_cost, evidence))
        candidates.sort(key=lambda item: item[0])
        acceptable = [
            item for item in candidates
            if max(item[2], item[3]) <= args.threshold and item[2] + item[3] <= 1.30
        ]
        if not acceptable:
            continue
        local_acceptable = [
            item for item in acceptable
            if str(item[4]["scope"]).startswith("edge-")
        ]
        if local_acceptable:
            selection_pool = local_acceptable
            fallback_reason = None
        elif not local_artist_pool:
            selection_pool = acceptable
            fallback_reason = "endpoint-lastfm-artist-pool-empty"
        else:
            # Local Last.fm evidence exists for this edge, but none of its
            # library tracks passed the acoustic and repeat gates. Do not let
            # collection-wide evidence silently replace that local context.
            continue
        _, bridge, left_cost, right_cost, evidence = selection_pool[0]
        insert_at = (
            0 if slot == "start"
            else len(selected_with_bridges) if slot == "end"
            else next(
                index for index, track in enumerate(selected_with_bridges)
                if track.db_file == left.db_file
            ) + 1
        )
        selected_with_bridges.insert(insert_at, bridge)
        used_bridge_files.add(bridge.db_file)
        inserted += 1
        proposals.append({
            "between": [
                left.label if left else "START",
                right.label if right else "END",
            ],
            "direct_cost": gap["cost"],
            "bridge": bridge.label,
            "bridge_file": bridge.db_file,
            "artist_tier": evidence["tier"],
            "artist_scope": evidence["scope"],
            "artist_support_sources": evidence["support_sources"],
            "artist_match_sum": evidence["match_sum"],
            "local_artist_pool_count": len(local_artist_pool),
            "local_acceptable_track_count": len(local_acceptable),
            "used_collection_fallback": fallback_reason is not None,
            "fallback_reason": fallback_reason,
            "left_cost": left_cost,
            "right_cost": right_cost,
            "detour_cost": left_cost + right_cost,
        })

    if explicit_mode and inserted != requested_bridges:
        raise ValueError(
            f"Requested exactly {requested_bridges} bridges, but only {inserted} "
            "acceptable repeat-safe bridges were found"
        )
    final_repeat_violations = repeat_violations_for_tracks(
        selected_with_bridges, args.no_repeat_artist, args.no_repeat_album,
    )
    if final_repeat_violations:
        raise AssertionError(
            f"Final playlist has {len(final_repeat_violations)} repeat-window violations"
        )

    args.output.mkdir(parents=True, exist_ok=True)
    final_path = args.output / "selected-with-bridges.m3u"
    write_m3u(
        final_path,
        selected_with_bridges,
        selected_m3u.newline,
    )
    decision = (
        "explicit-count" if explicit_mode and proposals
        else "explicit-zero" if explicit_mode
        else "inserted" if proposals
        else "not-needed" if not triggering
        else "no-acceptable-bridge"
    )
    result = {
        "schema_version": 1,
        "inputs": {
            "selected_sha256": sha256_file(args.selected),
            "artist_profile_sha256": sha256_file(args.artist_profile),
            "algorithm": args.algorithm,
            "adaptive_seeds": args.adaptive_seeds,
            "learned_blend": args.learned_blend,
            "static_weights": list(weights),
            "static_weights_used": args.algorithm == "static",
            "threshold": args.threshold,
            "max_bridges": args.max_bridges,
            "bridge_count_requested": args.bridge_count,
            "bridge_mode": "explicit" if explicit_mode else "automatic",
            "no_repeat_artist": args.no_repeat_artist,
            "no_repeat_album": args.no_repeat_album,
            "artist_profile_input": "edge-local lookups with full original-artist aggregation as fallback",
            "source_artist_count": len(source_artists),
            "lastfm_successful_lookups": profile.get("successful_lookups"),
            "lastfm_global_error": profile.get("global_error"),
        },
        "decision": decision,
        "triggering_gap_count": len(triggering),
        "bridge_count": len(proposals),
        "repeat_violations": final_repeat_violations,
        "top_gaps": gaps[:5],
        "proposals": proposals,
        "output_sha256": sha256_file(final_path),
    }
    (args.output / "bridge-analysis.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Bridge-track analysis",
        "",
        f"Decision: **{decision}**",
        "",
        f"- Threshold: {args.threshold:.2f}",
        f"- Acoustic algorithm: {args.algorithm}",
        f"- Adaptive seed window / learned blend: {args.adaptive_seeds} / {args.learned_blend:.2f}",
        f"- Static sliders used: {'yes' if args.algorithm == 'static' else 'no'}",
        f"- Worst selected gap: {gaps[0]['cost']:.6f}",
        f"- Gaps above threshold: {len(triggering)}",
        f"- Bridges inserted: {len(proposals)}",
        f"- Mode: {'explicit count' if explicit_mode else 'automatic threshold'}",
        f"- Repeat windows, artist / album: {args.no_repeat_artist} / {args.no_repeat_album}",
        f"- Artist-profile sources: all {len(source_artists)} distinct original-playlist artists",
        "- Artist selection: edge-local Last.fm only when endpoint evidence exists; collection profile only when the endpoint artist pool is empty",
        f"- Successful Last.fm lookups: {profile.get('successful_lookups')}",
    ]
    if profile.get("global_error"):
        lines.append(f"- Last.fm limitation: {profile['global_error']}")
    lines.extend(["", "## Five largest gaps", ""])
    for gap in gaps[:5]:
        lines.append(
            f"- {gap['left']} -> {gap['right']}: {gap['cost']:.6f}"
        )
    lines.extend([""])
    if args.algorithm == "adaptive":
        lines.extend([
            "Adaptive costs are percentiles against a frozen reference containing every curated",
            "candidate under every selected-route seed context. Each proposed incoming leg is scored",
            "from the actual preceding seed window; the outgoing leg is then rescored with the",
            "bridge included in that window. Static slider weights do not enter these scores.",
            "",
        ])
    if explicit_mode:
        lines.extend([
            "Explicit mode inserts the requested count across the largest suitable gaps while",
            "preserving the repeat windows and acoustic acceptance limits.",
        ])
    else:
        lines.extend([
            "Automatic mode considers a bridge only above the threshold. This prevents adding songs",
            "merely because the library contains a mathematically plausible detour.",
        ])
    lines.extend([
        "For each gap, artists returned by either endpoint's Last.fm lookup are considered first,",
        "with dual-endpoint support preferred. The full original-playlist artist profile is used",
        "only when the endpoint Last.fm artist pool itself is empty; original-artist",
        "and Bliss-only candidates remain later fallbacks.",
        "",
    ])
    (args.output / "BRIDGE_ANALYSIS.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "decision": decision,
        "worst_gap": gaps[0]["cost"],
        "bridges": len(proposals),
        "output": str(final_path),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
