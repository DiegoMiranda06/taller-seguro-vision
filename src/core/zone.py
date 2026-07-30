"""Pure geometry: point-in-polygon over normalized (0-1) coordinates.

Zero imports from capture/, inference/ or alert/ (Reglas No Negociables #3
en CLAUDE.md) — this module only ever sees plain tuples/floats and is fully
unit-testable without a camera, model, or GPIO.
"""

from __future__ import annotations

from collections.abc import Sequence

Point = tuple[float, float]
BBox = tuple[float, float, float, float]  # x1, y1, x2, y2


def point_in_polygon(point: Point, polygon: Sequence[Point]) -> bool:
    """Ray-casting point-in-polygon test.

    Works with any consistent coordinate space (normalized 0-1 or pixels) as
    long as `point` and `polygon` use the same one. A polygon with fewer
    than 3 vertices never contains anything.
    """
    x, y = point
    n = len(polygon)
    if n < 3:
        return False

    inside = False
    x1, y1 = polygon[0]
    for i in range(1, n + 1):
        x2, y2 = polygon[i % n]
        if min(y1, y2) < y <= max(y1, y2) and x <= max(x1, x2):
            if y1 != y2:
                x_intersection = (y - y1) * (x2 - x1) / (y2 - y1) + x1
            else:
                x_intersection = x1
            if x1 == x2 or x <= x_intersection:
                inside = not inside
        x1, y1 = x2, y2
    return inside


def bbox_center(bbox: BBox) -> Point:
    """Center point of a bounding box in whatever coordinate space it's in."""
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def bbox_in_zone(bbox: BBox, polygon: Sequence[Point]) -> bool:
    """True if the center of `bbox` falls inside `polygon`.

    Using the center (rather than requiring full containment) matches how
    `calibrate_zone.py` is meant to be used: draw the red zone loosely
    around the chuck, and a hand "entering" it is judged by where the
    detected hand is centered.
    """
    return point_in_polygon(bbox_center(bbox), polygon)
