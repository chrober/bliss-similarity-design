from __future__ import annotations

import json
import dataclasses
import pathlib
import tempfile
import unittest

from tools.playlist_optimizer import (
    AdaptiveScorer,
    FEATURES,
    Track,
    load_matrix,
    lms_file_url,
    learned_distance,
    learned_distance_from_projection,
    matrix_projection,
    optimize_arc_route,
    optimize_adaptive_route,
    optimize_route,
    parse_m3u,
    static_multipliers,
    quadratic_form,
    route_repeat_violations,
    write_m3u,
)
from tools.bridge_analyzer import artist_evidence


def track(index: int) -> Track:
    features = [0.0] * len(FEATURES)
    features[0] = float(index)
    features[1] = float(index % 2)
    return Track(
        db_file=f"artist/album/{index}.flac",
        absolute_file=f"/music/artist/album/{index}.flac",
        title=f"Track {index}",
        artist=f"Artist {index}",
        album="Album",
        genre="Rock",
        duration=180,
        features=tuple(features),
        block=(f"#EXTINF:180,Artist {index} - Track {index}", f"/music/artist/album/{index}.flac"),
    )


class PlaylistOptimizerTests(unittest.TestCase):
    def test_m3u_round_trip_preserves_entry_blocks(self) -> None:
        tracks = [track(0), track(1)]
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "test.m3u"
            write_m3u(path, tracks, "\r\n")
            parsed = parse_m3u(path)
            self.assertEqual(parsed.newline, "\r\n")
            self.assertEqual(parsed.entries[0][0], tracks[0].block)
            self.assertEqual(len(parsed.entries), 2)

    def test_parser_accepts_lyrion_curtrack_before_header(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "test.m3u"
            path.write_text(
                "#CURTRACK 16\n#EXTM3U\n#EXTINF:180,Track\n/music/track.flac\n",
                encoding="utf-8-sig",
            )
            parsed = parse_m3u(path)
        self.assertEqual(parsed.header, "#EXTM3U")
        self.assertEqual(parsed.entries[0][1], "/music/track.flac")

    def test_new_track_block_matches_lyrion_format(self) -> None:
        absolute_file = (
            "/mnt/usbHD/music/The Dresden Dolls/2006 - Yes, Virginia/"
            "09 - The Dresden Dolls - Shores of California.mp3"
        )
        added = dataclasses.replace(
            track(0), absolute_file=absolute_file, title="Shores of California",
            duration=215, block=(),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "test.m3u"
            write_m3u(path, [added], "\n")
            parsed = parse_m3u(path)
        self.assertEqual(
            parsed.entries[0][0],
            (
                "#EXTURL:file:///mnt/usbHD/music/The%20Dresden%20Dolls/"
                "2006%20-%20Yes,%20Virginia/09%20-%20The%20Dresden%20Dolls%20-%20"
                "Shores%20of%20California.mp3",
                "#EXTINF:215,Shores of California",
                absolute_file,
            ),
        )
        self.assertEqual(lms_file_url(absolute_file), parsed.entries[0][0][0][8:])

    def test_bridge_artist_evidence_prefers_edge_local_over_collection(self) -> None:
        lookups = {
            "artist a": {
                "local artist": {"name": "Local Artist", "match": 0.8, "rank": 2},
                "both artist": {"name": "Both Artist", "match": 0.7, "rank": 3},
            },
            "artist b": {
                "both artist": {"name": "Both Artist", "match": 0.9, "rank": 1},
            },
        }
        global_similar = {
            "global artist": {
                "support_count": 10, "match_sum": 8.0, "best_rank": 1,
                "support_seeds": ["Many Artists"],
            },
        }
        both = artist_evidence(
            "Both Artist", "Artist A", "Artist B", lookups, global_similar, set(),
        )
        local = artist_evidence(
            "Local Artist", "Artist A", "Artist B", lookups, global_similar, set(),
        )
        fallback = artist_evidence(
            "Global Artist", "Artist A", "Artist B", lookups, global_similar, set(),
        )
        self.assertEqual((both["scope"], both["tier"]), ("edge-both", 1))
        self.assertEqual((local["scope"], local["tier"]), ("edge-one", 2))
        self.assertEqual((fallback["scope"], fallback["tier"]), ("collection-fallback", 3))

    def test_static_weights_match_blissmixer_scaling(self) -> None:
        values = static_multipliers((20, 28, 3, 49))
        self.assertEqual(len(values), len(FEATURES))
        self.assertAlmostEqual(values[0], 5.0)
        self.assertTrue(all(abs(value - 28 / 30) < 1e-12 for value in values[1:8]))
        self.assertTrue(all(abs(value - 3 / 9) < 1e-12 for value in values[8:10]))
        self.assertTrue(all(abs(value - 49 / 57) < 1e-12 for value in values[10:]))

    def test_ndarray_matrix_wrapper_loads(self) -> None:
        size = len(FEATURES)
        payload = {"m": {"data": [float(i == j) for i in range(size) for j in range(size)],
                         "dim": [size, size], "v": 1}}
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "matrix.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            matrix = load_matrix(path)
        self.assertEqual(len(matrix), size)
        self.assertEqual(matrix[0][0], 1.0)
        self.assertEqual(matrix[0][1], 0.0)

    def test_cached_learned_distance_matches_direct_quadratic(self) -> None:
        left, right = track(2), track(5)
        matrix = tuple(
            tuple(1.0 if row == column else 0.01 for column in range(len(FEATURES)))
            for row in range(len(FEATURES))
        )
        projection = matrix_projection(left.features, matrix)
        right_projection = matrix_projection(right.features, matrix)
        cached = learned_distance_from_projection(
            left.features, projection, quadratic_form(left.features, projection),
            right.features, quadratic_form(right.features, right_projection),
        )
        self.assertAlmostEqual(cached, learned_distance(left, right, matrix))

    def test_adaptive_scorer_matches_bliss_variance_formula(self) -> None:
        tracks = [track(index) for index in range(3)]
        identity = tuple(
            tuple(float(row == column) for column in range(len(FEATURES)))
            for row in range(len(FEATURES))
        )
        scorer = AdaptiveScorer(tracks, identity, learned_blend=0.20, max_seeds=3)
        self.assertAlmostEqual(scorer.score_next((0,), 1), 2.0 ** 0.5)
        weights = scorer.variance_weights([tracks[0].features, tracks[2].features])
        self.assertAlmostEqual(sum(weights), len(FEATURES))
        mean = tuple(
            (left + right) / 2
            for left, right in zip(tracks[0].features, tracks[2].features)
        )
        variance_squared = sum(
            weight * (value - candidate) ** 2
            for weight, value, candidate in zip(weights, mean, tracks[1].features)
        )
        expected = (0.20 * 1.0 + 0.80 * variance_squared) ** 0.5
        self.assertAlmostEqual(scorer.score_next((0, 2), 1), expected)

    def test_searches_are_deterministic_exact_permutations(self) -> None:
        tracks = [track(index) for index in range(7)]
        matrix = [[float((left - right) ** 2) for right in range(7)] for left in range(7)]
        first = optimize_route(matrix, tracks, seed=42, restarts=12)
        second = optimize_route(matrix, tracks, seed=42, restarts=12)
        arc = optimize_arc_route(matrix, tracks, seed=43, restarts=12)
        self.assertEqual(first, second)
        self.assertEqual(sorted(first), list(range(7)))
        self.assertEqual(sorted(arc), list(range(7)))

    def test_search_enforces_artist_and_album_windows(self) -> None:
        tracks = [track(index) for index in range(8)]
        tracks[5] = dataclasses.replace(
            tracks[5], artist=tracks[0].artist, album=tracks[0].album,
        )
        tracks = [
            dataclasses.replace(item, album=f"Album {index}")
            if index not in (0, 5) else item
            for index, item in enumerate(tracks)
        ]
        matrix = [[float((left - right) ** 2) for right in range(8)] for left in range(8)]
        route = optimize_route(
            matrix, tracks, seed=99, restarts=30,
            artist_window=2, album_window=4,
        )
        self.assertEqual(
            route_repeat_violations(route, tracks, artist_window=2, album_window=4),
            [],
        )

    def test_adaptive_search_is_deterministic_and_repeat_safe(self) -> None:
        tracks = [track(index) for index in range(8)]
        tracks[5] = dataclasses.replace(
            tracks[5], artist=tracks[0].artist, album="Other album",
        )
        identity = tuple(
            tuple(float(row == column) for column in range(len(FEATURES)))
            for row in range(len(FEATURES))
        )
        scorer = AdaptiveScorer(tracks, identity, learned_blend=0.20, max_seeds=3)
        first = optimize_adaptive_route(
            scorer, tracks, seed=77, restarts=12, artist_window=2, album_window=0,
        )
        second = optimize_adaptive_route(
            scorer, tracks, seed=77, restarts=12, artist_window=2, album_window=0,
        )
        self.assertEqual(first, second)
        self.assertEqual(sorted(first), list(range(8)))
        self.assertEqual(route_repeat_violations(first, tracks, 2, 0), [])


if __name__ == "__main__":
    unittest.main()
