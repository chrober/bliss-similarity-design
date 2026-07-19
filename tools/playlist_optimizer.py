#!/usr/bin/env python3
"""Reproducible one-shot optimizer for an extended M3U backed by bliss.db."""

from __future__ import annotations

import argparse
import csv
import dataclasses
import functools
import hashlib
import json
import math
import pathlib
import random
import sqlite3
import statistics
import urllib.parse
from typing import Callable, Sequence

FEATURES = (
    "Tempo", "Zcr", "MeanSpectralCentroid", "StdDevSpectralCentroid",
    "MeanSpectralRolloff", "StdDevSpectralRolloff", "MeanSpectralFlatness",
    "StdDevSpectralFlatness", "MeanLoudness", "StdDevLoudness",
    "Chroma1", "Chroma2", "Chroma3", "Chroma4", "Chroma5", "Chroma6",
    "Chroma7", "Chroma8", "Chroma9", "Chroma10", "Chroma11", "Chroma12",
    "Chroma13",
)

@dataclasses.dataclass(frozen=True)
class Track:
    db_file: str
    absolute_file: str
    title: str
    artist: str
    album: str
    genre: str
    duration: int
    features: tuple[float, ...]
    block: tuple[str, ...] = ()

    @property
    def label(self) -> str:
        return f"{self.artist} — {self.title}"

@dataclasses.dataclass(frozen=True)
class ParsedM3U:
    header: str
    entries: tuple[tuple[tuple[str, ...], str], ...]
    newline: str

def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def parse_m3u(path: pathlib.Path) -> ParsedM3U:
    payload = path.read_bytes()
    newline = "\r\n" if b"\r\n" in payload else "\n"
    lines = payload.decode("utf-8-sig").splitlines()
    try:
        header_index = lines.index("#EXTM3U")
    except ValueError as error:
        raise ValueError("Expected an extended M3U containing #EXTM3U") from error
    if any(line and not line.startswith("#") for line in lines[:header_index]):
        raise ValueError("Unexpected path before #EXTM3U")
    pending: list[str] = []
    entries: list[tuple[tuple[str, ...], str]] = []
    for line in lines[header_index + 1:]:
        if not line:
            continue
        if line.startswith("#"):
            pending.append(line)
        else:
            entries.append((tuple(pending + [line]), line))
            pending.clear()
    if pending or not entries:
        raise ValueError("Invalid or empty extended M3U")
    return ParsedM3U(lines[header_index], tuple(entries), newline)

def normalize_db_file(absolute_file: str, music_root: str) -> str:
    root = music_root.rstrip("/") + "/"
    if not absolute_file.startswith(root):
        raise ValueError(f"Track is outside music root: {absolute_file}")
    return absolute_file[len(root):]

def open_readonly_db(path: pathlib.Path) -> sqlite3.Connection:
    connection = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)
    check = connection.execute("PRAGMA quick_check").fetchone()
    if not check or check[0] != "ok":
        raise ValueError(f"SQLite quick_check failed: {check}")
    return connection

def _track_from_row(row: Sequence[object], absolute_file: str, block: tuple[str, ...] = ()) -> Track:
    return Track(
        db_file=str(row[0]),
        absolute_file=absolute_file,
        title=str(row[1] or pathlib.PurePosixPath(absolute_file).stem),
        artist=str(row[2] or "Unknown Artist"),
        album=str(row[3] or ""),
        genre=str(row[4] or ""),
        duration=int(float(row[5] or 0)),
        features=tuple(float(value) for value in row[6:]),
        block=block,
    )

def load_playlist_tracks(
    connection: sqlite3.Connection, parsed: ParsedM3U, music_root: str,
) -> list[Track]:
    columns = ",".join(("File", "Title", "Artist", "Album", "Genre", "Duration") + FEATURES)
    sql = f"SELECT {columns} FROM TracksV2 WHERE File = ? AND Ignore = 0"
    result: list[Track] = []
    seen: set[str] = set()
    for block, absolute_file in parsed.entries:
        db_file = normalize_db_file(absolute_file, music_root)
        rows = connection.execute(sql, (db_file,)).fetchall()
        if len(rows) != 1:
            raise ValueError(f"Expected one usable bliss row for {db_file!r}; got {len(rows)}")
        if db_file in seen:
            raise ValueError(f"Duplicate playlist track: {db_file}")
        seen.add(db_file)
        result.append(_track_from_row(rows[0], absolute_file, block))
    return result

def load_library_tracks(connection: sqlite3.Connection, music_root: str) -> list[Track]:
    columns = ",".join(("File", "Title", "Artist", "Album", "Genre", "Duration") + FEATURES)
    sql = f"SELECT {columns} FROM TracksV2 WHERE Ignore = 0"
    return [
        _track_from_row(row, music_root.rstrip("/") + "/" + str(row[0]).lstrip("/"))
        for row in connection.execute(sql)
    ]

def load_matrix(path: pathlib.Path) -> tuple[tuple[float, ...], ...]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw = payload.get("m", payload) if isinstance(payload, dict) else payload
    if isinstance(raw, dict) and "data" in raw:
        dimensions = raw.get("dim")
        if dimensions != [len(FEATURES), len(FEATURES)]:
            raise ValueError(f"Unexpected learned matrix dimensions: {dimensions}")
        values = raw["data"]
        raw = [
            values[index:index + len(FEATURES)]
            for index in range(0, len(values), len(FEATURES))
        ]
    if len(raw) != len(FEATURES) or any(len(row) != len(FEATURES) for row in raw):
        raise ValueError(f"Expected a {len(FEATURES)}x{len(FEATURES)} learned matrix")
    matrix = tuple(tuple(float(value) for value in row) for row in raw)
    if any(not math.isfinite(value) for row in matrix for value in row):
        raise ValueError("Learned matrix contains non-finite values")
    asymmetry = max(
        abs(matrix[i][j] - matrix[j][i])
        for i in range(len(FEATURES)) for j in range(len(FEATURES))
    )
    if asymmetry > 1e-7:
        raise ValueError(f"Learned matrix is not symmetric (max asymmetry {asymmetry})")
    return matrix

def static_multipliers(weights: Sequence[float]) -> tuple[float, ...]:
    if len(weights) != 4 or any(weight < 0 for weight in weights) or sum(weights) <= 0:
        raise ValueError("Static weights must be four non-negative values with a positive sum")
    tempo, timbre, loudness, chroma = (weight / sum(weights) * 100 for weight in weights)
    return (
        tempo / 4,
        *(timbre / 30 for _ in range(7)),
        *(loudness / 9 for _ in range(2)),
        *(chroma / 57 for _ in range(13)),
    )

def static_distance(left: Track, right: Track, multipliers: Sequence[float]) -> float:
    return sum(
        ((a - b) * scale) ** 2
        for a, b, scale in zip(left.features, right.features, multipliers)
    )

def learned_distance(
    left: Track, right: Track, matrix: Sequence[Sequence[float]],
) -> float:
    delta = tuple(a - b for a, b in zip(left.features, right.features))
    value = sum(
        delta[i] * matrix[i][j] * delta[j]
        for i in range(len(delta)) for j in range(len(delta))
    )
    return max(0.0, value)

def matrix_projection(
    features: Sequence[float], matrix: Sequence[Sequence[float]],
) -> tuple[float, ...]:
    return tuple(
        sum(row[column] * features[column] for column in range(len(features)))
        for row in matrix
    )

def quadratic_form(features: Sequence[float], projection: Sequence[float]) -> float:
    return sum(value * projected for value, projected in zip(features, projection))

def learned_distance_from_projection(
    projected_features: Sequence[float], projection: Sequence[float],
    projected_quadratic: float, other_features: Sequence[float],
    other_quadratic: float,
) -> float:
    """Compute (x-y)'M(x-y) from a cached Mx and x'Mx/y'My."""
    cross = sum(value * projected for value, projected in zip(other_features, projection))
    return max(0.0, projected_quadratic + other_quadratic - 2.0 * cross)

class AdaptiveScorer:
    """Mirror bliss-mixer's adaptive multi-seed Mahalanobis scorer.

    Each next-track decision uses the final ``max_seeds`` tracks already in the
    route. With two or more seeds, bliss-rs population-variance weights are
    blended with the learned matrix. With one seed, bliss-mixer uses only the
    learned matrix.
    """

    def __init__(
        self, tracks: Sequence[Track], learned_matrix: Sequence[Sequence[float]],
        learned_blend: float = 0.20, max_seeds: int = 3,
    ) -> None:
        if not 0 <= learned_blend <= 1:
            raise ValueError("learned_blend must be between zero and one")
        if max_seeds < 1:
            raise ValueError("max_seeds must be at least one")
        self.tracks = tracks
        self.learned_matrix = learned_matrix
        self.learned_blend = learned_blend
        self.max_seeds = max_seeds

    @staticmethod
    def variance_weights(seed_features: Sequence[Sequence[float]]) -> tuple[float, ...]:
        if len(seed_features) < 2:
            raise ValueError("variance weights require at least two seeds")
        count = float(len(seed_features))
        means = tuple(statistics.fmean(values) for values in zip(*seed_features))
        variances = tuple(
            sum((seed[index] - means[index]) ** 2 for seed in seed_features) / count
            for index in range(len(means))
        )
        inverse = tuple(1.0 / (value + 1e-6) for value in variances)
        scale = len(means) / sum(inverse)
        return tuple(value * scale for value in inverse)

    def score_next(self, seed_indices: tuple[int, ...], candidate_index: int) -> float:
        seeds = seed_indices[-self.max_seeds:]
        return self._score_next(seeds, candidate_index)

    @functools.lru_cache(maxsize=None)
    def _score_next(self, seeds: tuple[int, ...], candidate_index: int) -> float:
        if not seeds:
            raise ValueError("adaptive scoring requires at least one seed")
        seed_features = [self.tracks[index].features for index in seeds]
        mean = tuple(statistics.fmean(values) for values in zip(*seed_features))
        candidate = self.tracks[candidate_index].features
        delta = tuple(left - right for left, right in zip(mean, candidate))
        learned_squared = sum(
            delta[i] * self.learned_matrix[i][j] * delta[j]
            for i in range(len(delta)) for j in range(len(delta))
        )
        if len(seeds) == 1:
            return math.sqrt(max(0.0, learned_squared))
        variance_squared = sum(
            weight * value * value
            for weight, value in zip(self.variance_weights(seed_features), delta)
        )
        blended_squared = (
            self.learned_blend * learned_squared
            + (1.0 - self.learned_blend) * variance_squared
        )
        return math.sqrt(max(0.0, blended_squared))

    def route_legs(self, route: Sequence[int]) -> list[float]:
        return [
            self.score_next(tuple(route[max(0, position - self.max_seeds):position]), route[position])
            for position in range(1, len(route))
        ]

def distance_matrix(
    tracks: Sequence[Track], distance: Callable[[Track, Track], float],
) -> list[list[float]]:
    size = len(tracks)
    result = [[0.0] * size for _ in range(size)]
    for i in range(size):
        for j in range(i + 1, size):
            result[i][j] = result[j][i] = distance(tracks[i], tracks[j])
    return result

def percentile_matrix(matrix: Sequence[Sequence[float]]) -> list[list[float]]:
    pairs = sorted(
        (matrix[i][j], i, j)
        for i in range(len(matrix)) for j in range(i + 1, len(matrix))
    )
    result = [[0.0] * len(matrix) for _ in matrix]
    denominator = max(1, len(pairs) - 1)
    for rank, (_, i, j) in enumerate(pairs):
        result[i][j] = result[j][i] = rank / denominator
    return result

def blend_matrices(
    left: Sequence[Sequence[float]], right: Sequence[Sequence[float]], right_weight: float,
) -> list[list[float]]:
    return [
        [
            (1 - right_weight) * left[i][j] + right_weight * right[i][j]
            for j in range(len(left))
        ]
        for i in range(len(left))
    ]

def repeat_violations_for_tracks(
    sequence: Sequence[Track], artist_window: int, album_window: int,
) -> list[dict[str, object]]:
    violations: list[dict[str, object]] = []
    last_artist: dict[str, int] = {}
    last_album: dict[str, int] = {}
    for position, track in enumerate(sequence):
        artist = track.artist.casefold().strip()
        album = track.album.casefold().strip()
        if artist_window > 0 and artist in last_artist:
            distance = position - last_artist[artist]
            if distance <= artist_window:
                violations.append({
                    "kind": "artist", "value": track.artist,
                    "positions": [last_artist[artist] + 1, position + 1],
                    "distance": distance,
                })
        if album_window > 0 and album and album in last_album:
            distance = position - last_album[album]
            if distance <= album_window:
                violations.append({
                    "kind": "album", "value": track.album,
                    "positions": [last_album[album] + 1, position + 1],
                    "distance": distance,
                })
        last_artist[artist] = position
        if album:
            last_album[album] = position
    return violations

def route_repeat_violations(
    route: Sequence[int], tracks: Sequence[Track],
    artist_window: int, album_window: int,
) -> list[dict[str, object]]:
    return repeat_violations_for_tracks(
        [tracks[index] for index in route], artist_window, album_window,
    )

def route_score(
    route: Sequence[int], matrix: Sequence[Sequence[float]], tracks: Sequence[Track],
    max_weight: float = 2.0, artist_window: int = 0, album_window: int = 0,
) -> float:
    legs = [matrix[left][right] for left, right in zip(route, route[1:])]
    score = sum(legs) + max_weight * max(legs, default=0.0)
    for left, right in zip(route, route[1:]):
        if tracks[left].artist.casefold() == tracks[right].artist.casefold():
            score += 0.20
        if tracks[left].album and tracks[left].album.casefold() == tracks[right].album.casefold():
            score += 0.35
    score += 100.0 * len(
        route_repeat_violations(route, tracks, artist_window, album_window)
    )
    return score

def greedy_route(
    matrix: Sequence[Sequence[float]], tracks: Sequence[Track], rng: random.Random,
    artist_window: int, album_window: int,
) -> list[int]:
    remaining = set(range(len(matrix)))
    route = [rng.randrange(len(matrix))]
    remaining.remove(route[0])
    while remaining:
        feasible = [
            candidate for candidate in remaining
            if not route_repeat_violations(
                route + [candidate], tracks, artist_window, album_window,
            )
        ]
        ranked = sorted(
            feasible or remaining,
            key=lambda candidate: matrix[route[-1]][candidate],
        )
        width = min(4, len(ranked))
        pick = ranked[int((rng.random() ** 2) * width)]
        route.append(pick)
        remaining.remove(pick)
    return route

def improve_route(
    route: Sequence[int], matrix: Sequence[Sequence[float]], tracks: Sequence[Track],
    artist_window: int, album_window: int,
) -> list[int]:
    best = list(route)
    best_score = route_score(
        best, matrix, tracks, artist_window=artist_window, album_window=album_window,
    )
    changed = True
    while changed:
        changed = False
        candidates: list[list[int]] = []
        for start in range(len(best) - 1):
            for end in range(start + 1, len(best)):
                candidates.append(best[:start] + list(reversed(best[start:end + 1])) + best[end + 1:])
        for source in range(len(best)):
            shortened = best[:source] + best[source + 1:]
            for destination in range(len(shortened) + 1):
                candidates.append(shortened[:destination] + [best[source]] + shortened[destination:])
        for candidate in candidates:
            score = route_score(
                candidate, matrix, tracks,
                artist_window=artist_window, album_window=album_window,
            )
            if score + 1e-12 < best_score:
                best, best_score, changed = candidate, score, True
        # Reversing an open route is equivalent; canonicalize for reproducible ties.
        if tuple(reversed(best)) < tuple(best):
            best.reverse()
    return best

def optimize_route(
    matrix: Sequence[Sequence[float]], tracks: Sequence[Track],
    seed: int, restarts: int, artist_window: int = 0, album_window: int = 0,
) -> list[int]:
    rng = random.Random(seed)
    starts = [list(range(len(tracks))), list(reversed(range(len(tracks))))]
    starts.extend(
        greedy_route(matrix, tracks, rng, artist_window, album_window)
        for _ in range(restarts)
    )
    best: list[int] | None = None
    best_score = math.inf
    for start in starts:
        candidate = improve_route(
            start, matrix, tracks, artist_window, album_window,
        )
        score = route_score(
            candidate, matrix, tracks,
            artist_window=artist_window, album_window=album_window,
        )
        if score < best_score or (score == best_score and tuple(candidate) < tuple(best or ())):
            best, best_score = candidate, score
    assert best is not None
    violations = route_repeat_violations(best, tracks, artist_window, album_window)
    if violations:
        raise ValueError(
            f"No feasible route found for artist window {artist_window} and "
            f"album window {album_window}; best route has {len(violations)} violations"
        )
    return best

def adaptive_route_score(
    route: Sequence[int], scorer: AdaptiveScorer, tracks: Sequence[Track],
    max_weight: float = 2.0, artist_window: int = 0, album_window: int = 0,
) -> float:
    legs = scorer.route_legs(route)
    score = sum(legs) + max_weight * max(legs, default=0.0)
    score += 100.0 * len(
        route_repeat_violations(route, tracks, artist_window, album_window)
    )
    return score

def greedy_adaptive_route(
    scorer: AdaptiveScorer, tracks: Sequence[Track], rng: random.Random,
    artist_window: int, album_window: int,
) -> list[int]:
    remaining = set(range(len(tracks)))
    route = [rng.randrange(len(tracks))]
    remaining.remove(route[0])
    while remaining:
        feasible = [
            candidate for candidate in remaining
            if not route_repeat_violations(
                route + [candidate], tracks, artist_window, album_window,
            )
        ]
        seeds = tuple(route[-scorer.max_seeds:])
        ranked = sorted(
            feasible or remaining,
            key=lambda candidate: (scorer.score_next(seeds, candidate), candidate),
        )
        width = min(4, len(ranked))
        pick = ranked[int((rng.random() ** 2) * width)]
        route.append(pick)
        remaining.remove(pick)
    return route

def improve_adaptive_route(
    route: Sequence[int], scorer: AdaptiveScorer, tracks: Sequence[Track],
    artist_window: int, album_window: int,
    intensity: Sequence[float] | None = None,
) -> list[int]:
    def objective(candidate: Sequence[int]) -> float:
        value = adaptive_route_score(
            candidate, scorer, tracks,
            artist_window=artist_window, album_window=album_window,
        )
        if intensity is not None:
            value += 0.12 * sum(
                abs(intensity[index] - target)
                for index, target in zip(candidate, arc_targets(len(candidate)))
            )
        return value

    best = list(route)
    best_score = objective(best)
    changed = True
    while changed:
        changed = False
        candidates: list[list[int]] = []
        for start in range(len(best) - 1):
            for end in range(start + 1, len(best)):
                candidates.append(
                    best[:start] + list(reversed(best[start:end + 1])) + best[end + 1:]
                )
        for source in range(len(best)):
            shortened = best[:source] + best[source + 1:]
            for destination in range(len(shortened) + 1):
                candidates.append(
                    shortened[:destination] + [best[source]] + shortened[destination:]
                )
        for candidate in candidates:
            score = objective(candidate)
            if score + 1e-12 < best_score:
                best, best_score, changed = candidate, score, True
        if sorted(best) != list(range(len(tracks))):
            raise AssertionError("Adaptive local search produced a non-permutation")
    return best

def optimize_adaptive_route(
    scorer: AdaptiveScorer, tracks: Sequence[Track], seed: int, restarts: int,
    artist_window: int = 0, album_window: int = 0,
    intensity: Sequence[float] | None = None,
) -> list[int]:
    rng = random.Random(seed)
    starts = [list(range(len(tracks))), list(reversed(range(len(tracks))))]
    if intensity is not None:
        starts.append(sorted(range(len(tracks)), key=lambda index: intensity[index]))
    starts.extend(
        greedy_adaptive_route(scorer, tracks, rng, artist_window, album_window)
        for _ in range(restarts)
    )
    best = min(
        (
            improve_adaptive_route(
                route, scorer, tracks, artist_window, album_window, intensity,
            )
            for route in starts
        ),
        key=lambda route: (
            adaptive_route_score(
                route, scorer, tracks,
                artist_window=artist_window, album_window=album_window,
            ) + (
                0.12 * sum(
                    abs(intensity[index] - target)
                    for index, target in zip(route, arc_targets(len(route)))
                )
                if intensity is not None else 0.0
            ),
            tuple(route),
        ),
    )
    violations = route_repeat_violations(best, tracks, artist_window, album_window)
    if violations:
        raise ValueError(
            f"No feasible adaptive route found; best route has {len(violations)} violations"
        )
    return best

def intensity_values(tracks: Sequence[Track]) -> list[float]:
    feature_indexes = (0, 1, 2, 4, 8)
    ranks = [[0.0] * len(tracks) for _ in feature_indexes]
    for output, feature_index in zip(ranks, feature_indexes):
        ordered = sorted(range(len(tracks)), key=lambda index: tracks[index].features[feature_index])
        for rank, track_index in enumerate(ordered):
            output[track_index] = rank / max(1, len(tracks) - 1)
    return [statistics.fmean(values) for values in zip(*ranks)]

def arc_targets(size: int) -> list[float]:
    peak = max(1, round((size - 1) * 0.70))
    return [
        0.25 + 0.60 * index / peak
        if index <= peak
        else 0.85 - 0.50 * (index - peak) / max(1, size - 1 - peak)
        for index in range(size)
    ]

def arc_score(
    route: Sequence[int], matrix: Sequence[Sequence[float]], tracks: Sequence[Track],
    intensity: Sequence[float], artist_window: int, album_window: int,
) -> float:
    placement = sum(
        abs(intensity[track_index] - target)
        for track_index, target in zip(route, arc_targets(len(route)))
    )
    return route_score(
        route, matrix, tracks,
        artist_window=artist_window, album_window=album_window,
    ) + 0.12 * placement

def improve_arc_route(
    route: Sequence[int], matrix: Sequence[Sequence[float]], tracks: Sequence[Track],
    intensity: Sequence[float], artist_window: int, album_window: int,
) -> list[int]:
    best = list(route)
    best_score = arc_score(
        best, matrix, tracks, intensity, artist_window, album_window,
    )
    changed = True
    while changed:
        changed = False
        candidates: list[list[int]] = []
        for start in range(len(best) - 1):
            for end in range(start + 1, len(best)):
                candidates.append(
                    best[:start] + list(reversed(best[start:end + 1])) + best[end + 1:]
                )
        for source in range(len(best)):
            shortened = best[:source] + best[source + 1:]
            for destination in range(len(shortened) + 1):
                candidates.append(
                    shortened[:destination] + [best[source]] + shortened[destination:]
                )
        for candidate in candidates:
            score = arc_score(
                candidate, matrix, tracks, intensity, artist_window, album_window,
            )
            if score + 1e-12 < best_score:
                best, best_score, changed = candidate, score, True
        if sorted(best) != list(range(len(tracks))):
            raise AssertionError("Local search produced a route that is not a track permutation")
    return best

def optimize_arc_route(
    matrix: Sequence[Sequence[float]], tracks: Sequence[Track],
    seed: int, restarts: int, artist_window: int = 0, album_window: int = 0,
) -> list[int]:
    rng = random.Random(seed)
    intensity = intensity_values(tracks)
    starts = [sorted(range(len(tracks)), key=lambda index: intensity[index])]
    starts.extend(
        greedy_route(matrix, tracks, rng, artist_window, album_window)
        for _ in range(restarts)
    )
    best = min(
        (
            improve_arc_route(
                route, matrix, tracks, intensity, artist_window, album_window,
            )
            for route in starts
        ),
        key=lambda route: (
            arc_score(
                route, matrix, tracks, intensity, artist_window, album_window,
            ),
            tuple(route),
        ),
    )
    violations = route_repeat_violations(best, tracks, artist_window, album_window)
    if violations:
        raise ValueError(
            f"No feasible arc route found; best route has {len(violations)} violations"
        )
    return best

def route_statistics(
    route: Sequence[int], matrix: Sequence[Sequence[float]], tracks: Sequence[Track],
    artist_window: int = 0, album_window: int = 0,
) -> dict[str, object]:
    legs = [matrix[left][right] for left, right in zip(route, route[1:])]
    worst_index = max(range(len(legs)), key=legs.__getitem__) if legs else 0
    return {
        "objective": route_score(route, matrix, tracks),
        "transition_sum": sum(legs),
        "transition_mean": statistics.fmean(legs) if legs else 0.0,
        "worst_transition": max(legs, default=0.0),
        "worst_transition_position": worst_index + 1,
        "worst_transition_labels": (
            [tracks[route[worst_index]].label, tracks[route[worst_index + 1]].label]
            if legs else []
        ),
        "same_artist_adjacencies": sum(
            tracks[left].artist.casefold() == tracks[right].artist.casefold()
            for left, right in zip(route, route[1:])
        ),
        "repeat_violations": route_repeat_violations(
            route, tracks, artist_window, album_window,
        ),
    }

def adaptive_route_statistics(
    route: Sequence[int], scorer: AdaptiveScorer, tracks: Sequence[Track],
    artist_window: int = 0, album_window: int = 0,
) -> dict[str, object]:
    legs = scorer.route_legs(route)
    worst_index = max(range(len(legs)), key=legs.__getitem__) if legs else 0
    return {
        "objective": adaptive_route_score(
            route, scorer, tracks,
            artist_window=artist_window, album_window=album_window,
        ),
        "transition_sum": sum(legs),
        "transition_mean": statistics.fmean(legs) if legs else 0.0,
        "worst_transition": max(legs, default=0.0),
        "worst_transition_position": worst_index + 1,
        "worst_transition_labels": (
            [tracks[route[worst_index]].label, tracks[route[worst_index + 1]].label]
            if legs else []
        ),
        "same_artist_adjacencies": sum(
            tracks[left].artist.casefold() == tracks[right].artist.casefold()
            for left, right in zip(route, route[1:])
        ),
        "repeat_violations": route_repeat_violations(
            route, tracks, artist_window, album_window,
        ),
    }

def track_block(track: Track) -> tuple[str, ...]:
    if track.block:
        return track.block
    return (
        f"#EXTURL:{lms_file_url(track.absolute_file)}",
        f"#EXTINF:{track.duration},{track.title}",
        track.absolute_file,
    )

def lms_file_url(absolute_file: str) -> str:
    """Serialize a POSIX path like Slim::Utils::Misc::fileURLFromPath()."""
    if not absolute_file.startswith("/"):
        raise ValueError(f"Expected an absolute POSIX path: {absolute_file}")
    # LMS uses URI::file. URI 1.35 preserves RFC reserved characters and its
    # mark set, but escapes spaces, apostrophes, percent signs, hashes and UTF-8.
    safe = ";/?:@&=+$,[]-_.!~*()"
    return "file://" + urllib.parse.quote(absolute_file, safe=safe)

def write_m3u(
    path: pathlib.Path, tracks: Sequence[Track], newline: str,
    preamble: Sequence[str] = (),
) -> None:
    lines = ["#EXTM3U", *preamble]
    for track in tracks:
        lines.extend(track_block(track))
    payload = newline.join(lines) + newline
    path.write_bytes(b"\xef\xbb\xbf" + payload.encode("utf-8"))

def write_pairwise_csv(
    path: pathlib.Path, tracks: Sequence[Track],
    static: Sequence[Sequence[float]], learned: Sequence[Sequence[float]],
    fused: Sequence[Sequence[float]],
) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("left", "right", "static_squared", "learned_squared", "fused_percentile"))
        for i in range(len(tracks)):
            for j in range(i + 1, len(tracks)):
                writer.writerow((tracks[i].label, tracks[j].label, static[i][j], learned[i][j], fused[i][j]))

def write_adaptive_transitions_csv(
    path: pathlib.Path, tracks: Sequence[Track], route: Sequence[int],
    scorer: AdaptiveScorer,
) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("position", "seed_tracks", "next_track", "adaptive_distance"))
        for position in range(1, len(route)):
            seed_indices = route[max(0, position - scorer.max_seeds):position]
            writer.writerow((
                position + 1,
                " | ".join(tracks[index].label for index in seed_indices),
                tracks[route[position]].label,
                scorer.score_next(tuple(seed_indices), route[position]),
            ))

def render_report(
    inputs: dict[str, object], candidates: dict[str, dict[str, object]],
    selected: str, tracks: Sequence[Track], routes: dict[str, list[int]],
) -> str:
    lines = [
        "# Playlist optimization run",
        "",
        "This directory is a deterministic run artifact. The source playlist is treated as a fixed set;",
        "candidate M3Us reorder its exact extended-M3U blocks without changing track metadata.",
        "",
        "## Inputs",
        "",
        f"- Playlist SHA-256: {inputs['playlist_sha256']}",
        f"- bliss.db SHA-256: {inputs['db_sha256']}",
        f"- Learned matrix SHA-256: {inputs['matrix_sha256']}",
        f"- Algorithm: {inputs['algorithm']}",
        (
            f"- Captured static weights (unused by adaptive scoring): {inputs['weights']}"
            if inputs["algorithm"] == "adaptive" else
            f"- Static weights: {inputs['weights']}"
        ),
        f"- Learned blend: {inputs['learned_blend']}",
        f"- Adaptive sliding seed count: {inputs['adaptive_seeds']}",
        f"- Random seed / restarts: {inputs['seed']} / {inputs['restarts']}",
        f"- No-repeat artist / album windows: {inputs['no_repeat_artist']} / {inputs['no_repeat_album']}",
        f"- Curated tracks: {len(tracks)}",
        "",
        "## Candidate comparison",
        "",
        "| Candidate | Primary objective | Mean leg | Worst leg | Arc error | Repeat violations |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, data in candidates.items():
        stats = data["primary"]
        lines.append(
            f"| {name} | {stats['objective']:.6f} | {stats['transition_mean']:.6f} | "
            f"{stats['worst_transition']:.6f} | {data['arc_error']:.6f} | "
            f"{len(stats['repeat_violations'])} |"
        )
    lines.extend([
        "",
        f"Selected candidate: **{selected}**.",
        "",
        "Selection rule: choose the arc route only when its primary objective is within 8% of the",
        "best primary route and it improves positional energy-arc error by at least 10%; otherwise",
        "choose the primary route. Bridge insertion is a separate, explicitly reported stage.",
        "",
        "## Selected order",
        "",
    ])
    for position, index in enumerate(routes[selected], 1):
        lines.append(f"{position}. {tracks[index].label}")
    lines.extend(["", "## Worst selected transition", ""])
    worst = candidates[selected]["primary"]
    labels = worst["worst_transition_labels"]
    lines.append(f"{labels[0]} -> {labels[1]} at primary cost {worst['worst_transition']:.6f}.")
    lines.extend([
        "",
        "## Reproduction",
        "",
        "Run python tools/playlist_optimizer.py --help from the repository root. Supply immutable",
        "copies of the playlist, bliss.db, and learned matrix; the hashes above make drift visible.",
        "",
    ])
    return "\n".join(lines)

def parse_weights(value: str) -> tuple[float, float, float, float]:
    try:
        weights = tuple(float(item) for item in value.split(","))
    except ValueError as error:
        raise argparse.ArgumentTypeError("Weights must be comma-separated numbers") from error
    if len(weights) != 4:
        raise argparse.ArgumentTypeError("Expected four weights: tempo,timbre,loudness,chroma")
    return weights  # type: ignore[return-value]

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=pathlib.Path, required=True)
    parser.add_argument("--playlist", type=pathlib.Path, required=True)
    parser.add_argument("--matrix", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--music-root", default="/mnt/usbHD/music/")
    parser.add_argument("--algorithm", choices=("static", "adaptive"), default="static")
    parser.add_argument("--weights", type=parse_weights, default=(20.0, 28.0, 3.0, 49.0))
    parser.add_argument("--learned-blend", type=float, default=0.20)
    parser.add_argument("--adaptive-seeds", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20260717)
    parser.add_argument("--restarts", type=int, default=250)
    parser.add_argument("--no-repeat-artist", type=int, default=5)
    parser.add_argument("--no-repeat-album", type=int, default=10)
    args = parser.parse_args()
    if not 0 <= args.learned_blend <= 1:
        parser.error("--learned-blend must be between zero and one")
    if args.no_repeat_artist < 0 or args.no_repeat_album < 0:
        parser.error("No-repeat windows must be zero or greater")
    if args.adaptive_seeds < 1:
        parser.error("--adaptive-seeds must be at least one")

    args.output.mkdir(parents=True, exist_ok=True)
    parsed = parse_m3u(args.playlist)
    connection = open_readonly_db(args.db)
    try:
        tracks = load_playlist_tracks(connection, parsed, args.music_root)
    finally:
        connection.close()
    learned_metric = load_matrix(args.matrix)
    original = list(range(len(tracks)))
    intensity = intensity_values(tracks)
    targets = arc_targets(len(tracks))
    adaptive_scorer: AdaptiveScorer | None = None
    static_artifacts: tuple[
        list[list[float]], list[list[float]], list[list[float]]
    ] | None = None
    if args.algorithm == "adaptive":
        adaptive_scorer = AdaptiveScorer(
            tracks, learned_metric, args.learned_blend, args.adaptive_seeds,
        )
        routes = {
            "original": original,
            "adaptive": optimize_adaptive_route(
                adaptive_scorer, tracks, args.seed + 3, args.restarts,
                args.no_repeat_artist, args.no_repeat_album,
            ),
            "adaptive-arc": optimize_adaptive_route(
                adaptive_scorer, tracks, args.seed + 4, max(50, args.restarts // 2),
                args.no_repeat_artist, args.no_repeat_album, intensity,
            ),
        }
        primary_name, arc_name = "adaptive", "adaptive-arc"
    else:
        multipliers = static_multipliers(args.weights)
        static_raw = distance_matrix(tracks, lambda a, b: static_distance(a, b, multipliers))
        learned_raw = distance_matrix(tracks, lambda a, b: learned_distance(a, b, learned_metric))
        static_percentiles = percentile_matrix(static_raw)
        learned_percentiles = percentile_matrix(learned_raw)
        fused = blend_matrices(static_percentiles, learned_percentiles, args.learned_blend)
        static_artifacts = (static_raw, learned_raw, fused)
        routes = {
            "original": original,
            "static": optimize_route(
                static_percentiles, tracks, args.seed + 1, args.restarts,
                args.no_repeat_artist, args.no_repeat_album,
            ),
            "learned": optimize_route(
                learned_percentiles, tracks, args.seed + 2, args.restarts,
                args.no_repeat_artist, args.no_repeat_album,
            ),
            "fused": optimize_route(
                fused, tracks, args.seed + 3, args.restarts,
                args.no_repeat_artist, args.no_repeat_album,
            ),
            "arc": optimize_arc_route(
                fused, tracks, args.seed + 4, max(50, args.restarts // 2),
                args.no_repeat_artist, args.no_repeat_album,
            ),
        }
        primary_name, arc_name = "fused", "arc"

    candidates: dict[str, dict[str, object]] = {}
    for name, route in routes.items():
        if sorted(route) != list(range(len(tracks))):
            raise AssertionError(f"Candidate {name} is not an exact permutation of the curated set")
        if adaptive_scorer is not None:
            primary_stats = adaptive_route_statistics(
                route, adaptive_scorer, tracks,
                args.no_repeat_artist, args.no_repeat_album,
            )
            metric_stats: dict[str, object] = {"adaptive": primary_stats}
        else:
            static_stats = route_statistics(
                route, static_percentiles, tracks,
                args.no_repeat_artist, args.no_repeat_album,
            )
            learned_stats = route_statistics(
                route, learned_percentiles, tracks,
                args.no_repeat_artist, args.no_repeat_album,
            )
            fused_stats = route_statistics(
                route, fused, tracks,
                args.no_repeat_artist, args.no_repeat_album,
            )
            primary_stats = fused_stats
            metric_stats = {
                "static": static_stats, "learned": learned_stats, "fused": fused_stats,
            }
        candidates[name] = {
            **metric_stats,
            "primary": primary_stats,
            "arc_error": sum(
                abs(intensity[index] - target) for index, target in zip(route, targets)
            ),
            "order": [tracks[index].db_file for index in route],
            "labels": [tracks[index].label for index in route],
        }
        write_m3u(
            args.output / f"candidate-{name}.m3u",
            [tracks[index] for index in route],
            parsed.newline,
        )

    primary_stats = candidates[primary_name]["primary"]
    arc_stats = candidates[arc_name]["primary"]
    primary_score = float(primary_stats["objective"])  # type: ignore[index]
    arc_score_value = float(arc_stats["objective"])  # type: ignore[index]
    primary_arc_error = float(candidates[primary_name]["arc_error"])
    arc_error_value = float(candidates[arc_name]["arc_error"])
    selected = (
        arc_name
        if arc_score_value <= primary_score * 1.08 and arc_error_value <= primary_arc_error * 0.90
        else primary_name
    )
    write_m3u(
        args.output / "selected.m3u",
        [tracks[index] for index in routes[selected]],
        parsed.newline,
    )
    if adaptive_scorer is not None:
        write_adaptive_transitions_csv(
            args.output / "dynamic-transitions.csv",
            tracks, routes[selected], adaptive_scorer,
        )
    else:
        assert static_artifacts is not None
        write_pairwise_csv(
            args.output / "pairwise.csv", tracks, *static_artifacts,
        )

    inputs = {
        "playlist": str(args.playlist.resolve()),
        "playlist_sha256": sha256_file(args.playlist),
        "db": str(args.db.resolve()),
        "db_sha256": sha256_file(args.db),
        "matrix": str(args.matrix.resolve()),
        "matrix_sha256": sha256_file(args.matrix),
        "algorithm": args.algorithm,
        "weights": list(args.weights),
        "learned_blend": args.learned_blend,
        "adaptive_seeds": args.adaptive_seeds,
        "seed": args.seed,
        "restarts": args.restarts,
        "no_repeat_artist": args.no_repeat_artist,
        "no_repeat_album": args.no_repeat_album,
        "music_root": args.music_root,
    }
    run = {
        "schema_version": 1,
        "inputs": inputs,
        "selected": selected,
        "candidates": candidates,
    }
    (args.output / "run.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.output / "REPORT.md").write_text(
        render_report(inputs, candidates, selected, tracks, routes),
        encoding="utf-8",
    )
    print(json.dumps({"selected": selected, "tracks": len(tracks), "output": str(args.output)}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
