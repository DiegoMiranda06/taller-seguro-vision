"""Pure geometry tests — no camera, model, or GPIO involved."""

from __future__ import annotations

import pytest

from src.core.zone import bbox_center, bbox_in_zone, point_in_polygon

SQUARE = [(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)]


def test_point_inside_polygon_is_true():
    assert point_in_polygon((0.5, 0.5), SQUARE) is True


def test_point_outside_polygon_is_false():
    assert point_in_polygon((0.05, 0.05), SQUARE) is False
    assert point_in_polygon((0.95, 0.95), SQUARE) is False


def test_point_far_outside_is_false():
    assert point_in_polygon((-1.0, -1.0), SQUARE) is False


def test_degenerate_polygon_never_contains_anything():
    assert point_in_polygon((0.5, 0.5), [(0.0, 0.0), (1.0, 1.0)]) is False
    assert point_in_polygon((0.5, 0.5), []) is False


def test_bbox_center_is_midpoint():
    assert bbox_center((0.0, 0.0, 1.0, 1.0)) == (0.5, 0.5)
    assert bbox_center((0.2, 0.4, 0.4, 0.6)) == pytest.approx((0.3, 0.5))


def test_bbox_in_zone_true_when_center_inside():
    bbox = (0.4, 0.4, 0.6, 0.6)  # center = (0.5, 0.5), inside SQUARE
    assert bbox_in_zone(bbox, SQUARE) is True


def test_bbox_in_zone_false_when_center_outside():
    bbox = (0.0, 0.0, 0.1, 0.1)  # center = (0.05, 0.05), outside SQUARE
    assert bbox_in_zone(bbox, SQUARE) is False


def test_bbox_partially_overlapping_zone_judged_by_center_only():
    # Bbox straddles the zone edge but its center is just outside — the
    # design choice (documented in zone.py) is to judge by center, not by
    # any-overlap, so this must be False.
    bbox = (0.1, 0.1, 0.25, 0.25)  # center = (0.175, 0.175), outside SQUARE
    assert bbox_in_zone(bbox, SQUARE) is False
