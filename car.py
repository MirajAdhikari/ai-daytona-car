import math

import arcade
from PIL import Image, ImageDraw

from constants import (
    MAX_SPEED, REVERSE_MAX, BASE_ACCEL, BRAKE_FORCE, REVERSE_ACCEL,
    FRICTION, TURN_RATE,
    CAR_WIDTH, CAR_HEIGHT, CAR_HALF_L, CAR_HALF_W,
)

_CAR_TEXTURE = None


def _car_texture():
    global _CAR_TEXTURE
    if _CAR_TEXTURE is None:
        img = Image.new("RGBA", (CAR_WIDTH, CAR_HEIGHT), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rectangle([1, 2, CAR_WIDTH - 2, CAR_HEIGHT - 3], fill=(220, 40, 50))
        for wx in (4, CAR_WIDTH - 11):
            d.rectangle([wx, 0, wx + 7, 2],                      fill=(20, 20, 20))
            d.rectangle([wx, CAR_HEIGHT - 2, wx + 7, CAR_HEIGHT - 1], fill=(20, 20, 20))
        d.rectangle([3, CAR_HEIGHT // 2 - 1, CAR_WIDTH - 12,
                     CAR_HEIGHT // 2 + 1], fill=(245, 245, 245))
        d.rectangle([CAR_WIDTH - 13, 4, CAR_WIDTH - 5, CAR_HEIGHT - 5],
                    fill=(40, 50, 70))
        _CAR_TEXTURE = arcade.Texture(img)
    return _CAR_TEXTURE


class Car(arcade.Sprite):
    """
    Heading convention:
      * self._heading is in RADIANS, math/CCW-positive, 0 = facing +x.
      * self.angle (from Sprite) is in DEGREES, arcade/CW-positive.
      * Because arcade has Y-up but rotates CW, the two differ by a sign:
            self.angle = -math.degrees(self._heading)
      * All physics and raycasting uses self._heading (exposed as `heading`).
    """

    def __init__(self, x, y):
        super().__init__(_car_texture(), center_x=float(x), center_y=float(y))
        self.speed     = 0.0
        self.steer     = 0.0
        self.throttle  = 0.0
        self._heading  = 0.0

    @property
    def heading(self):
        return self._heading

    def update_physics(self, keys, on_track_func):
        # --- steering (smoothed) ---
        target_steer = 0.0
        if arcade.key.LEFT  in keys or arcade.key.A in keys: target_steer -= 1.0
        if arcade.key.RIGHT in keys or arcade.key.D in keys: target_steer += 1.0
        smoothing = 0.19 if target_steer != 0 else 0.25
        self.steer += (target_steer - self.steer) * smoothing
        self.steer = max(-1.0, min(1.0, self.steer))

        # --- throttle (smoothed, ranges -1..+1: W=+1, S=-1, both/neither=0) ---
        target_throttle = 0.0
        if arcade.key.UP   in keys or arcade.key.W in keys: target_throttle += 1.0
        if arcade.key.DOWN in keys or arcade.key.S in keys: target_throttle -= 1.0
        rate = 0.15
        if target_throttle > self.throttle:
            self.throttle = min(self.throttle + rate, target_throttle)
        elif target_throttle < self.throttle:
            self.throttle = max(self.throttle - rate, target_throttle)

        # --- accel / brake / reverse ---
        if self.throttle > 0:
            self.speed += BASE_ACCEL * self.throttle
        elif self.throttle < 0:
            if self.speed > 0.4:
                # moving forward while S pressed -> brake hard
                self.speed -= BRAKE_FORCE * abs(self.throttle)
            else:
                # stopped or already reversing -> gentler reverse accel
                self.speed += REVERSE_ACCEL * self.throttle

        self.speed *= FRICTION
        self.speed = max(REVERSE_MAX, min(MAX_SPEED, self.speed))

        # --- turn heading ---
        # steer>0 means RIGHT. In Y-up world a right turn is CW = heading DECREASES.
        # dir_sign flips turning when reversing.
        speed_factor = min(abs(self.speed) / 3.5, 1.0)
        dir_sign     = 1 if self.speed >= 0 else -1
        self._heading -= self.steer * TURN_RATE * speed_factor * dir_sign

        # --- sync sprite angle (arcade CW degrees) ---
        self.angle = -math.degrees(self._heading)

        # --- movement + axis-slide collision ---
        dx = self.speed * math.cos(self._heading)
        dy = self.speed * math.sin(self._heading)
        nx, ny = self.center_x + dx, self.center_y + dy

        if self._footprint_on_track(nx, ny, on_track_func):
            self.center_x, self.center_y = nx, ny
        elif self._footprint_on_track(nx, self.center_y, on_track_func):
            self.center_x = nx
            self.speed *= 0.68
        elif self._footprint_on_track(self.center_x, ny, on_track_func):
            self.center_y = ny
            self.speed *= 0.68
        else:
            self.speed *= 0.28

    def _footprint_on_track(self, x, y, on_track_func):
        c, s = math.cos(self._heading), math.sin(self._heading)
        for ox, oy in ((CAR_HALF_L, CAR_HALF_W), (CAR_HALF_L, -CAR_HALF_W),
                       (-CAR_HALF_L, CAR_HALF_W), (-CAR_HALF_L, -CAR_HALF_W)):
            if not on_track_func(x + ox * c - oy * s, y + ox * s + oy * c):
                return False
        return True