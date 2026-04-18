import math

import arcade

from constants import NUM_RAYS, RAY_LENGTH, RAY_SPREAD, RAY_STEP, CAR_HALF_L

# Pre-compute per-ray angular offsets (degrees from car heading)
if NUM_RAYS > 1:
    _RAY_OFFSETS = [
        -RAY_SPREAD / 2 + i * RAY_SPREAD / (NUM_RAYS - 1)
        for i in range(NUM_RAYS)
    ]
else:
    _RAY_OFFSETS = [0.0]


def _ray_origin(car_x, car_y, car_angle):
    """Rays emanate from the front bumper, not the car's center."""
    return (car_x + math.cos(car_angle) * CAR_HALF_L,
            car_y + math.sin(car_angle) * CAR_HALF_L)


def cast_rays(car_x, car_y, car_angle, on_track_func):
    """Return distance from the front of the car to the nearest off-track
    hit for each of NUM_RAYS rays. RAY_LENGTH if no hit within range."""
    ox, oy = _ray_origin(car_x, car_y, car_angle)
    distances = []
    for off_deg in _RAY_OFFSETS:
        a  = car_angle + math.radians(off_deg)
        dx = math.cos(a)
        dy = math.sin(a)
        hit = RAY_LENGTH
        d = 0.0
        while d < RAY_LENGTH:
            if not on_track_func(ox + dx * d, oy + dy * d):
                hit = d
                break
            d += RAY_STEP
        distances.append(hit)
    return distances


def draw_rays(car_x, car_y, car_angle, distances):
    ox, oy = _ray_origin(car_x, car_y, car_angle)
    for off_deg, dist in zip(_RAY_OFFSETS, distances):
        a  = car_angle + math.radians(off_deg)
        ex = ox + dist * math.cos(a)
        ey = oy + dist * math.sin(a)
        if   dist > 140: color = (0, 255, 100)
        elif dist > 70:  color = (255, 190, 40)
        else:            color = (255, 70, 70)
        arcade.draw_line(ox, oy, ex, ey, color, line_width=3)