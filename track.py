import math
import random

import numpy as np
from arcade.shape_list import (
    ShapeElementList,
    create_rectangle_filled,
    create_line,
    create_triangles_filled_with_colors,
)

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    GRASS, GRASS_DARK, GRASS_LIGHT,
    ASPHALT, ASPHALT_MID, ASPHALT_EDGE, WHITE,
    TRACK_HALF_WIDTH,
)


class Track:
    def __init__(self):
        # Control points scaled 0.8x from the 1600x900 layout
        self.control_points = [
            (240, 144),  (1040, 144), (1200, 264), (1200, 496),
            (1080, 640), (760, 656),  (560, 560),  (680, 400),
            (464, 320),  (304, 440),  (144, 600),  (64, 400),
            (144, 224),
        ]
        self.centerline = self._build_spline(self.control_points, samples=60)
        self._build_mask()
        self._build_shapes()

    # ---------- centerline ----------

    @staticmethod
    def _catmull_rom(p0, p1, p2, p3, t):
        t2, t3 = t * t, t * t * t
        x = 0.5 * ((2 * p1[0]) +
                   (-p0[0] + p2[0]) * t +
                   (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                   (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
        y = 0.5 * ((2 * p1[1]) +
                   (-p0[1] + p2[1]) * t +
                   (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                   (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
        return (x, y)

    def _build_spline(self, points, samples=60):
        n = len(points)
        out = []
        for i in range(n):
            p0 = points[(i - 1) % n]
            p1 = points[i]
            p2 = points[(i + 1) % n]
            p3 = points[(i + 2) % n]
            for j in range(samples):
                out.append(self._catmull_rom(p0, p1, p2, p3, j / samples))
        out.append(out[0])
        return out

    # ---------- collision mask ----------

    def _build_mask(self):
        self.mask = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH), dtype=bool)
        r  = TRACK_HALF_WIDTH
        r2 = r * r
        for px, py in self.centerline:
            cx, cy = int(px), int(py)
            x0 = max(0, cx - r)
            x1 = min(SCREEN_WIDTH,  cx + r + 1)
            y0 = max(0, cy - r)
            y1 = min(SCREEN_HEIGHT, cy + r + 1)
            if x1 <= x0 or y1 <= y0:
                continue
            ys = np.arange(y0, y1)[:, None]
            xs = np.arange(x0, x1)[None, :]
            disk = (xs - px) ** 2 + (ys - py) ** 2 <= r2
            self.mask[y0:y1, x0:x1] |= disk

    def is_on_track(self, x, y):
        ix, iy = int(x), int(y)
        if 0 <= ix < SCREEN_WIDTH and 0 <= iy < SCREEN_HEIGHT:
            return bool(self.mask[iy, ix])
        return False

    # ---------- rendering ----------

    def _band_triangles(self, half_width):
        pts = self.centerline
        n = len(pts) - 1

        left, right = [], []
        for i in range(n):
            p      = pts[i]
            p_next = pts[(i + 1) % n]
            p_prev = pts[(i - 1) % n]
            tx, ty = p_next[0] - p_prev[0], p_next[1] - p_prev[1]
            tlen   = math.hypot(tx, ty) or 1.0
            tx, ty = tx / tlen, ty / tlen
            nx, ny = -ty, tx
            left.append((p[0] + nx * half_width, p[1] + ny * half_width))
            right.append((p[0] - nx * half_width, p[1] - ny * half_width))

        tris = []
        for i in range(n):
            j = (i + 1) % n
            tris.extend([left[i], right[i], right[j],
                         left[i], right[j], left[j]])
        return tris

    def _build_shapes(self):
        self.shapes = ShapeElementList()

        # Grass
        self.shapes.append(create_rectangle_filled(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
            SCREEN_WIDTH, SCREEN_HEIGHT, GRASS))

        # Pebbles off-track
        random.seed(7)
        for _ in range(2000):
            x = random.randint(0, SCREEN_WIDTH - 1)
            y = random.randint(0, SCREEN_HEIGHT - 1)
            if not self.is_on_track(x, y):
                c = random.choice([GRASS_DARK, GRASS_LIGHT, GRASS_DARK])
                r = random.randint(2, 4)
                self.shapes.append(create_rectangle_filled(x, y, r, r, c))

        # Asphalt layers: white edge > main > slightly darker mid
        for hw, color in (
            (TRACK_HALF_WIDTH + 3, ASPHALT_EDGE),
            (TRACK_HALF_WIDTH,     ASPHALT),
            (TRACK_HALF_WIDTH - 8, ASPHALT_MID),
        ):
            tris   = self._band_triangles(hw)
            colors = [color] * len(tris)
            self.shapes.append(
                create_triangles_filled_with_colors(tris, colors))

        # Start/finish twin stripes
        for lx in (268, 284):
            self.shapes.append(
                create_line(lx, 110, lx, 178, WHITE, line_width=5))

    def draw(self):
        self.shapes.draw()