import arcade

from car import Car
from raycast import cast_rays, draw_rays
from track import Track
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.track         = Track()
        self.car           = Car(320, 144)
        self.car_list      = arcade.SpriteList()
        self.car_list.append(self.car)
        self.ray_distances = []
        self.keys_pressed  = set()

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)
        if key == arcade.key.ESCAPE:
            self.close()

    def on_key_release(self, key, modifiers):
        self.keys_pressed.discard(key)

    def on_update(self, delta_time):
        self.car.update_physics(self.keys_pressed, self.track.is_on_track)
        self.ray_distances = cast_rays(
            self.car.center_x, self.car.center_y,
            self.car.heading,
            self.track.is_on_track,
        )

    def on_draw(self):
        self.clear()
        self.track.draw()
        draw_rays(self.car.center_x, self.car.center_y,
                  self.car.heading, self.ray_distances)
        self.car_list.draw()


def main():
    Game()
    arcade.run()


if __name__ == "__main__":
    main()