import pygame
import sys
import random
import math
from car import Car
from raycast import cast_rays, draw_rays

# Initialize Pygame
pygame.init()

WIDTH, HEIGHT = 1600, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Car - Raycast Sensors")
clock = pygame.time.Clock()

# ====================== TRACK SETUP ======================
GRASS        = (52, 140, 62)
GRASS_DARK   = (38, 115, 48)
GRASS_LIGHT  = (75, 160, 85)
ASPHALT      = (60, 62, 70)
ASPHALT_DARK = (48, 50, 58)
ASPHALT_MID  = (72, 74, 82)
ASPHALT_PEB  = (95, 97, 105)
EDGE         = (240, 240, 240)
WHITE        = (250, 250, 250)

TRACK_WIDTH = 80

control_points = [
    (300, 180), (1300, 180), (1500, 330), (1500, 620),
    (1350, 800), (950, 820), (700, 700), (850, 500),
    (580, 400), (380, 550), (180, 750), (80, 500), (180, 280)
]

def catmull_rom(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t +
               (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
               (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
    y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t +
               (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
               (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
    return (x, y)

def build_spline(points, samples=40):
    n = len(points)
    out = []
    for i in range(n):
        p0 = points[(i - 1) % n]
        p1 = points[i]
        p2 = points[(i + 1) % n]
        p3 = points[(i + 2) % n]
        for j in range(samples):
            out.append(catmull_rom(p0, p1, p2, p3, j / samples))
    return out

centerline = build_spline(control_points, samples=40)
int_center = [(int(p[0]), int(p[1])) for p in centerline]

def build_mask_at_width(width):
    m = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.lines(m, (255, 255, 255, 255), True, int_center, width)
    for p in int_center:
        pygame.draw.circle(m, (255, 255, 255, 255), p, width // 2)
    return pygame.mask.from_surface(m)

track_mask    = build_mask_at_width(TRACK_WIDTH)
interior_mask = build_mask_at_width(TRACK_WIDTH - 10)

def on_track(x, y):
    ix, iy = int(x), int(y)
    if 0 <= ix < WIDTH and 0 <= iy < HEIGHT:
        return bool(track_mask.get_at((ix, iy)))
    return False

def build_track_surface():
    surf = pygame.Surface((WIDTH, HEIGHT))
    surf.fill(GRASS)
    
    # Light grass texture (much less blocky)
    random.seed(7)
    for _ in range(800):                    # reduced number
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, HEIGHT - 1)
        if not on_track(x, y):
            c = random.choice([GRASS_DARK, GRASS_LIGHT])
            pygame.draw.circle(surf, c, (x, y), random.randint(1, 3))   # smaller dots

    # Clean white edges
    pygame.draw.lines(surf, EDGE, True, int_center, TRACK_WIDTH + 8)
    for p in int_center:
        pygame.draw.circle(surf, EDGE, p, (TRACK_WIDTH + 8) // 2)

    # Main asphalt - clean and smooth
    pygame.draw.lines(surf, ASPHALT, True, int_center, TRACK_WIDTH)
    for p in int_center:
        pygame.draw.circle(surf, ASPHALT, p, TRACK_WIDTH // 2)

    # Very subtle asphalt texture (much less noisy)
    random.seed(42)
    for _ in range(4000):                   # reduced and lighter
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, HEIGHT - 1)
        if on_track(x, y):                  # only on road
            if random.random() < 0.25:      # only 25% chance
                shade = random.randint(-12, 8)
                color = (
                    max(40, min(80, ASPHALT[0] + shade)),
                    max(40, min(80, ASPHALT[1] + shade)),
                    max(40, min(80, ASPHALT[2] + shade))
                )
                surf.set_at((x, y), color)

    # Start/Finish line
    for line_x in (335, 355):
        y = 142
        while y < 219:
            pygame.draw.line(surf, WHITE, (line_x, y), (line_x, min(y + 5, 218)), 6)
            y += 12

    return surf

track_bg = build_track_surface()

# ====================== GAME SETUP ======================
car = Car(400.0, 180.0)

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    keys = pygame.key.get_pressed()

    # Update car
    car.update(keys, on_track)

    # Raycasting
    ray_distances = cast_rays(car.x, car.y, car.angle, on_track)

    # Drawing
    screen.blit(track_bg, (0, 0))
    draw_rays(screen, car.x, car.y, car.angle, ray_distances)
    car.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()