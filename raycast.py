import math
import pygame

def cast_rays(x, y, angle, on_track_func, NUM_RAYS=8, RAY_LENGTH=220):
    """Improved raycasting - more accurate and smooth"""
    distances = []
    
    for i in range(NUM_RAYS):
        ray_angle = angle + math.radians(-60 + (i * 120 / (NUM_RAYS - 1)))
        dx = math.cos(ray_angle)
        dy = math.sin(ray_angle)
        
        distance = RAY_LENGTH
        step = 2.0  # finer steps for smoother feel
        
        for dist in range(0, int(RAY_LENGTH), int(step)):
            check_x = x + dx * dist
            check_y = y + dy * dist
            
            if not on_track_func(check_x, check_y):
                distance = dist
                break
                
        distances.append(distance)
    
    return distances


def draw_rays(screen, x, y, angle, distances, CAR_HALF_L=12):
    """Draw smooth, clean rays"""
    c = math.cos(angle)
    s = math.sin(angle)
    car_front_x = x + CAR_HALF_L * c
    car_front_y = y + CAR_HALF_L * s

    for i, dist in enumerate(distances):
        ray_angle = angle + math.radians(-60 + (i * 120 / (len(distances) - 1)))
        dx = math.cos(ray_angle)
        dy = math.sin(ray_angle)
        
        end_x = car_front_x + dist * dx
        end_y = car_front_y + dist * dy
        
        # Smooth color gradient
        color = (0, 255, 0) if dist > 100 else (255, 100, 0) if dist > 50 else (255, 50, 50)
        pygame.draw.line(screen, color, 
                        (int(car_front_x), int(car_front_y)), 
                        (int(end_x), int(end_y)), 
                        3)  # thicker line for better visibility