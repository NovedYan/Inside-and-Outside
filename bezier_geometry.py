
"""
Bézier Geometry Utilities

Construct cubic Bézier curves and convert them
into polylines using recursive midpoint subdivision.

All curve coordinates are computed manually.
"""

import math


# ==========================================
# Midpoint Subdivision
# ==========================================

def midpoint(a, b):
    """Return the midpoint of two 2D points."""
    return (
        (a[0] + b[0]) / 2,
        (a[1] + b[1]) / 2
    )


def split_bezier_half(p0, p1, p2, p3):
    """Split a cubic Bézier curve at t = 0.5."""

    m01 = midpoint(p0, p1)
    m12 = midpoint(p1, p2)
    m23 = midpoint(p2, p3)

    m012 = midpoint(m01, m12)
    m123 = midpoint(m12, m23)

    center = midpoint(m012, m123)

    left = [p0, m01, m012, center]
    right = [center, m123, m23, p3]

    return left, right


def midpoint_polyline(p0, p1, p2, p3, depth):
    """Recursively approximate a cubic Bézier with line segments."""

    if depth < 0:
        raise ValueError("Depth must be non-negative")

    if depth == 0:
        return [p0, p3]

    left, right = split_bezier_half(p0, p1, p2, p3)

    left_points = midpoint_polyline(*left, depth - 1)
    right_points = midpoint_polyline(*right, depth - 1)

    return left_points[:-1] + right_points


# ==========================================
# Four-Segment Bézier Circle
# ==========================================

def create_bezier_circle(cx, cy, radius):
    """
    Approximate a circle with four cubic Bézier segments.

    Each quarter-circle uses tangent handles
    with length 0.5523 * radius.
    """

    if radius <= 0:
        raise ValueError("Radius must be positive")

    k = 0.5523
    segments = []

    for i in range(4):

        start_angle = i * math.pi / 2
        end_angle = (i + 1) * math.pi / 2

        # Quarter-circle endpoints
        p0 = (
            cx + radius * math.cos(start_angle),
            cy + radius * math.sin(start_angle)
        )

        p3 = (
            cx + radius * math.cos(end_angle),
            cy + radius * math.sin(end_angle)
        )

        # Tangent directions at both endpoints
        t0 = (-math.sin(start_angle), math.cos(start_angle))
        t1 = (-math.sin(end_angle), math.cos(end_angle))

        # Bézier direction control points
        p1 = (
            p0[0] + k * radius * t0[0],
            p0[1] + k * radius * t0[1]
        )

        p2 = (
            p3[0] - k * radius * t1[0],
            p3[1] - k * radius * t1[1]
        )

        segments.append([p0, p1, p2, p3])

    return segments


def flatten_bezier_circle(segments, depth=6):
    """
    Convert four Bézier segments into one closed polygon.

    The closing point is omitted because the scanline
    renderer connects the final vertex to the first.
    """

    polygon = []

    for segment in segments:

        points = midpoint_polyline(*segment, depth)

        # 避免相鄰曲線在接合點產生重複頂點
        polygon.extend(points[:-1])

    return polygon
