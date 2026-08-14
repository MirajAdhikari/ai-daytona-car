import os
import numpy as np
import arcade
import matplotlib.pyplot as plt

from car import Car
from raycast import cast_rays, draw_rays
from track import Track
from neural_net import NeuralNetwork
from ga import GeneticAlgorithm
from constants import (SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE,
                       RAY_LENGTH, MAX_SPEED)

POP_SIZE = 20


class Game(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        os.makedirs("assets", exist_ok=True)
        os.makedirs("saved",  exist_ok=True)

        self.track        = Track()
        self.generation   = 1
        self.best_ever    = 0.0
        self.history_best = []
        self.history_avg  = []

        sample_net = NeuralNetwork()
        self.ga    = GeneticAlgorithm(POP_SIZE, sample_net.genome_length)
        self._spawn_generation()

    def _spawn_generation(self):
        self.cars     = []
        self.car_list = arcade.SpriteList()
        for genome in self.ga.population:
            car = Car(320, 144)
            net = NeuralNetwork()
            net.set_genome(genome)
            car.neural_net = net
            self.cars.append(car)
            self.car_list.append(car)

    def on_update(self, delta_time):
        alive_cars = [c for c in self.cars if c.alive]

        for car in alive_cars:
            ray_distances = cast_rays(car.center_x, car.center_y,
                                      car.heading, self.track.is_on_track)
            inputs      = np.array(ray_distances + [car.speed])
            inputs[:9] /= RAY_LENGTH
            inputs[9]  /= MAX_SPEED

            outputs = car.neural_net.forward(inputs)
            car.update_physics_ai(float(outputs[0]), float(outputs[1]),
                                  self.track.is_on_track)

            on_finish = self.track.crossed_finish(car.center_x, car.center_y)
            if on_finish and not car._on_finish_last_frame:
                if car._distance_since_spawn > 500:
                    car.laps   += 1
                    car.fitness += 5000
                    car._distance_since_spawn = 0
            car._on_finish_last_frame = on_finish

        if not alive_cars:
            fitnesses = [c.fitness for c in self.cars]
            gen_best  = max(fitnesses)
            gen_avg   = sum(fitnesses) / len(fitnesses)
            max_laps  = max(c.laps for c in self.cars)

            self.history_best.append(gen_best)
            self.history_avg.append(gen_avg)

            if gen_best > self.best_ever:
                self.best_ever = gen_best
                best_car = max(self.cars, key=lambda c: c.fitness)
                np.save("saved/best_genome.npy",
                        best_car.neural_net.get_genome())
                print(f"  --> new best saved ({self.best_ever:.0f})")

            print(f"Gen {self.generation:>3} | best: {gen_best:>8.0f} "
                  f"| avg: {gen_avg:>8.0f} "
                  f"| all-time: {self.best_ever:>8.0f} "
                  f"| max laps: {max_laps}")

            self.ga.evolve(fitnesses)
            self.generation += 1
            self._spawn_generation()

    def on_draw(self):
        self.clear()
        self.track.draw()
        self.car_list.draw()

        alive = [c for c in self.cars if c.alive]
        if alive:
            best  = max(alive, key=lambda c: c.fitness)
            dists = cast_rays(best.center_x, best.center_y,
                              best.heading, self.track.is_on_track)
            draw_rays(best.center_x, best.center_y, best.heading, dists)

        arcade.draw_text(
            f"Gen {self.generation}   "
            f"Alive {len(alive)}/{POP_SIZE}   "
            f"Best {self.best_ever:.0f}",
            10, 10, (255, 255, 255), 14
        )

    def save_fitness_graph(self):
        plt.figure(figsize=(10, 5))
        plt.plot(self.history_best, label="Best fitness",
                 color="#E62828", linewidth=2)
        plt.plot(self.history_avg,  label="Avg fitness",
                 color="#4A90D9", linewidth=1.5, linestyle="--")
        plt.xlabel("Generation")
        plt.ylabel("Fitness")
        plt.title("AI Car — Fitness over Generations")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig("assets/fitness_graph.png", dpi=150)
        plt.close()
        print("  --> assets/fitness_graph.png saved")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.save_fitness_graph()
            self.close()


def main():
    Game()
    arcade.run()


if __name__ == "__main__":
    main()