
"""
Inside and Outside
Pixel Array and Scanline Test

Purpose:
    Verify direct pixel manipulation before implementing
    the Non-Zero Winding Number scanline algorithm.

NumPy stores the pixel array.
Pillow exports the image to PNG.
"""

from pathlib import Path
import math

import numpy as np
from PIL import Image

from bezier_geometry import (
    create_bezier_circle,
    flatten_bezier_circle
)


# ==========================================
# 畫布設定
# ==========================================

WIDTH = 800
HEIGHT = 600

OUTPUT_DIR = Path(__file__).resolve().parent


# ==========================================
# 建立 RGB 像素畫布
# ==========================================

def create_canvas():
    """Create an 800 x 600 white RGB canvas."""

    canvas = np.full(
        (HEIGHT, WIDTH, 3),
        255,
        dtype=np.uint8
    )

    return canvas


# ==========================================
# 掃描線檢測
# ==========================================

def scanline_intersections(subpaths, scan_y):
    """
    計算水平掃描線與一個或多個閉合子路徑之間的交點。

    座標約定：
        X 軸向右遞增。 
        Y 軸向下遞增。

    穿過方向：
        +1 = 向下的邊
        -1 = 向上的邊
    """

    intersections = []

    # 處理每個閉合子路徑
    for path in subpaths:

        count = len(path)

        for i in range(count):

            x1, y1 = path[i]
            x2, y2 = path[(i + 1) % count]

            # 水平邊不會產生交叉
            if y1 == y2:
                continue

            # 避免了對頂點的重複計數。
            if not (min(y1, y2) <= scan_y < max(y1, y2)):
                continue

            # 計算x交點座標
            x = x1 + (scan_y - y1) * (x2 - x1) / (y2 - y1)

            # 確定貫穿方向
            direction = 1 if y2 > y1 else -1

            intersections.append((x, direction))

    # 將交叉點從左到右排序
    intersections.sort(key=lambda item: item[0])

    return intersections



# ==========================================
# 迴轉數累積
# ==========================================

def winding_number_at_x(crossings, sample_x):
    """
    Calculate the winding number at a sample position.

    Crossings must be sorted by X coordinate.

    A non-zero winding number means the
    sample position is inside the filled path.
    """

    winding = 0

    # Accumulate signed crossings from left to right
    for crossing_x, direction in crossings:

        if crossing_x <= sample_x:
            winding += direction
        else:
            break

    return winding



# ==========================================
# Non-Zero Winding Scanline Fill
# ==========================================

def fill_nonzero_winding(canvas, subpaths, color=(0, 0, 0)):
    """
    Rasterize closed subpaths using the non-zero winding rule.

    Each scanline:
        1. Finds the edge intersections.
        2. Accumulates signed crossings.
        3. Fills spans where the winding number is non-zero.

    Pixel coverage is calculated manually.
    """

    height, width = canvas.shape[:2]

    filled_pixels = 0

    # Process the image one row at a time
    for y in range(height):

        # 使用像素中心，避免取樣位置落在像素邊界
        scan_y = y + 0.5

        crossings = scanline_intersections(
            subpaths,
            scan_y
        )

        winding = 0

        # Examine spans between consecutive crossings
        for i in range(len(crossings) - 1):

            current_x, direction = crossings[i]
            next_x = crossings[i + 1][0]

            # Update winding number after the current crossing
            winding += direction

            # Only non-zero winding regions are filled
            if winding == 0:
                continue

            # Convert geometric coordinates to pixel indices
            x_start = max(
                0,
                math.ceil(current_x - 0.5)
            )

            x_end = min(
                width,
                math.ceil(next_x - 0.5)
            )

            # Directly write pixels into the NumPy array
            if x_start < x_end:

                canvas[y, x_start:x_end] = color

                filled_pixels += x_end - x_start

    return filled_pixels




# ==========================================
# 像素測試
# ==========================================

def test_scanline(canvas):
    """為一行水平像素上色."""
    
    
    # ==========================================
    # 交叉測試
    # ==========================================

    rectangle = [
        (200, 150),
        (600, 150),
        (600, 450),
        (200, 450)
    ]

    #一組閉合子路徑
    subpaths = [rectangle]

    # 像素中心採樣
    scan_y = 300.5

    crossings = scanline_intersections(subpaths, scan_y)

    print("\nScanline Intersection Test")
    print("Scanline Y:", scan_y)
    print("Intersection Count:", len(crossings))

    for x, direction in crossings:
        print(f"X = {x:.2f}, Direction = {direction:+d}")
    
    
    # ==========================================
    # Winding Number Validation
    # ==========================================

    test_positions = [150.5, 400.5, 650.5]

    print("\nWinding Number Test")

    for sample_x in test_positions:

        winding = winding_number_at_x(
            crossings,
            sample_x
        )

        inside = winding != 0

        print(
            f"X = {sample_x:.1f}, "
            f"Winding = {winding:+d}, "
            f"Inside = {inside}"
        )




    y = 300
    x_start = 200
    x_end = 600

    # 直接指定黑色 RGB 值
    canvas[y, x_start:x_end + 1] = [0, 0, 0]

    print("Scanline Y:", y)
    print("Start X:", x_start)
    print("End X:", x_end)
    print("Colored Pixels:", x_end - x_start + 1)


# ==========================================
# Nested Subpaths and Orientation Test
# ==========================================

def test_nested_subpaths():
    """
    Compare two nested closed paths.

    Case A: Both paths have the same direction.
    Case B: The inner path has the opposite direction.

    Both cases use the non-zero winding rule.
    """

    outer = [
        (200, 150),
        (600, 150),
        (600, 450),
        (200, 450)
    ]

    inner = [
        (300, 220),
        (500, 220),
        (500, 380),
        (300, 380)
    ]

    experiments = [
        ("same_direction", [outer, inner]),
        ("opposite_direction", [outer, inner[::-1]])
    ]

    for name, subpaths in experiments:

        canvas = create_canvas()

        # Apply the custom scanline fill
        filled_pixels = fill_nonzero_winding(
            canvas,
            subpaths
        )

        # Measure the winding number at the center
        crossings = scanline_intersections(
            subpaths,
            300.5
        )

        center_winding = winding_number_at_x(
            crossings,
            400.5
        )

        # Save and display the result
        output_path = OUTPUT_DIR / f"experiment_2_{name}.png"

        image = Image.fromarray(canvas)
        image.save(output_path)
        image.show()

        print(f"\nOrientation Test: {name}")
        print("Center Winding Number:", center_winding)
        print("Filled Pixels:", filled_pixels)
        print("Image Saved:", output_path)



# ==========================================
# Self-Intersecting Five-Point Star
# ==========================================

def create_pentagram(cx=400, cy=300, radius=220):
    """
    Create a self-intersecting five-pointed star.

    Only five outer vertices are used.
    The path visits every second vertex.
    """

    vertices = []

    # Generate five equally spaced points on a circle
    for i in range(5):

        angle = -math.pi / 2 + i * 2 * math.pi / 5

        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)

        vertices.append((x, y))

    # Connect every second vertex
    visiting_order = [0, 2, 4, 1, 3]

    star_path = [vertices[i] for i in visiting_order]

    return star_path



# ==========================================
# Pentagram Winding Fill Validation
# ==========================================

def test_pentagram():
    """
    Fill a self-intersecting pentagram using
    the custom non-zero winding scanline renderer.
    """

    star = create_pentagram()

    canvas = create_canvas()

    # One closed self-intersecting subpath
    subpaths = [star]

    filled_pixels = fill_nonzero_winding(
        canvas,
        subpaths
    )

    # Measure winding number near the geometric center
    crossings = scanline_intersections(
        subpaths,
        300.5
    )

    center_winding = winding_number_at_x(
        crossings,
        400.5
    )

    output_path = OUTPUT_DIR / "experiment_3_pentagram.png"

    image = Image.fromarray(canvas)
    image.save(output_path)
    image.show()

    print("\nPentagram Validation")
    print("Vertex Count:", len(star))
    print("Center Winding Number:", center_winding)
    print("Center Inside:", center_winding != 0)
    print("Filled Pixels:", filled_pixels)
    print("Image Saved:", output_path)


# ==========================================
# Bézier Circle Rasterization
# ==========================================

def test_bezier_circle():
    """
    Construct a circle from four cubic Bézier segments,
    flatten the curves, and rasterize the result.
    """

    circle_segments = create_bezier_circle(
        cx=400,
        cy=300,
        radius=190
    )

    # Convert Bézier curves into a closed polygon
    circle_path = flatten_bezier_circle(
        circle_segments,
        depth=6
    )

    canvas = create_canvas()

    # Use the custom non-zero winding scanline renderer
    filled_pixels = fill_nonzero_winding(
        canvas,
        [circle_path]
    )

    # Validate the center winding number
    crossings = scanline_intersections(
        [circle_path],
        300.5
    )

    center_winding = winding_number_at_x(
        crossings,
        400.5
    )

    output_path = OUTPUT_DIR / "experiment_4_bezier_circle.png"

    image = Image.fromarray(canvas)
    image.save(output_path)
    image.show()

    print("\nBézier Circle Validation")
    print("Bézier Segments:", len(circle_segments))
    print("Polyline Vertices:", len(circle_path))
    print("Center Winding Number:", center_winding)
    print("Center Inside:", center_winding != 0)
    print("Filled Pixels:", filled_pixels)
    print("Image Saved:", output_path)


# ==========================================
# Concentric Bézier Circles
# ==========================================

def test_concentric_bezier_circles():
    """
    Compare two concentric Bézier paths using
    the non-zero winding scanline renderer.

    Experiment A: Same traversal direction.
    Experiment B: Reversed inner traversal direction.

    Geometry remains unchanged between experiments.
    """

    # Create outer and inner circle geometry
    outer_segments = create_bezier_circle(
        cx=400, cy=300, radius=190
    )

    inner_segments = create_bezier_circle(
        cx=400, cy=300, radius=100
    )

    # Convert each cubic Bézier circle into a polygon
    outer_path = flatten_bezier_circle(
        outer_segments, depth=6
    )

    inner_path = flatten_bezier_circle(
        inner_segments, depth=6
    )

    # Only reverse the traversal order of the inner path
    experiments = [
        ("same_direction", [outer_path, inner_path]),
        ("opposite_direction", [outer_path, inner_path[::-1]])
    ]

    for name, subpaths in experiments:

        canvas = create_canvas()

        # Rasterize both subpaths using non-zero winding
        filled_pixels = fill_nonzero_winding(
            canvas,
            subpaths
        )

        # Measure winding number at the center
        crossings = scanline_intersections(
            subpaths,
            300.5
        )

        center_winding = winding_number_at_x(
            crossings,
            400.5
        )

        # Export rasterized result
        output_path = OUTPUT_DIR / f"experiment_5_{name}.png"

        image = Image.fromarray(canvas)
        image.save(output_path)
        image.show()

        print(f"\nConcentric Circle Test: {name}")
        print("Outer Bézier Segments:", len(outer_segments))
        print("Inner Bézier Segments:", len(inner_segments))
        print("Outer Vertices:", len(outer_path))
        print("Inner Vertices:", len(inner_path))
        print("Center Winding Number:", center_winding)
        print("Center Inside:", center_winding != 0)
        print("Filled Pixels:", filled_pixels)
        print("Image Saved:", output_path)



# ==========================================
# 主程式
# ==========================================

def main():

    print("Inside and Outside - Pixel Array Test")

    canvas = create_canvas()

    print("Canvas Shape:", canvas.shape)
    print("Data Type:", canvas.dtype)

    test_scanline(canvas)

    output_path = OUTPUT_DIR / "experiment_0_scanline.png"

    # 將像素數組轉換為影像
    image = Image.fromarray(canvas)

    # 儲存渲染影像
    image.save(output_path)

    # 使用預設影像檢視器顯示結果
    image.show()

    print("Image Saved:", output_path)
    
    # ==========================================
    # Rectangle Fill Validation
    # ==========================================

    rectangle = [
        (200, 150),
        (600, 150),
        (600, 450),
        (200, 450)
    ]

    # Create a fresh white canvas
    filled_canvas = create_canvas()

    # Apply the custom scanline fill algorithm
    pixel_count = fill_nonzero_winding(
        filled_canvas,
        [rectangle],
        color=(0, 0, 0)
    )

    filled_path = OUTPUT_DIR / "experiment_1_rectangle_fill.png"

    filled_image = Image.fromarray(filled_canvas)

    filled_image.save(filled_path)
    filled_image.show()

    print("\nRectangle Fill Validation")
    print("Filled Pixels:", pixel_count)
    print("Image Saved:", filled_path)



if __name__ == "__main__":
    main()
    
    # Validate multi-subpath winding behavior
    test_nested_subpaths()
    
    # Validate the non-zero winding rule on a pentagram
    test_pentagram()
    
    # Validate the four-segment Bézier circle
    test_bezier_circle()
    
    # Compare concentric circle traversal directions
    test_concentric_bezier_circles()
