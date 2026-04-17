import pygame
import math

class Car:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.angle = 0.0
        self.speed = 0.0
        self.steer = 0.0

        # New: Variable throttle system
        self.throttle_input = 0.0      # how hard the player is pressing (0.0 to 1.0)
        self.current_throttle = 0.0    # smoothed throttle value

        # Physics settings
        self.MAX_SPEED = 9.0
        self.REVERSE_MAX = -5.5
        self.BASE_ACCEL = 0.18         # base acceleration when throttle is full
        self.BRAKE = 0.42
        self.REVERSE_ACCEL = 0.11
        self.FRICTION = 0.955
        self.TURN_RATE = 0.055
        self.STEER_RESPONSE = 0.19
        self.STEER_RETURN = 0.25

        # Create car sprite
        w, h = 34, 17
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (220, 40, 50), (1, 1, w-2, h-2), border_radius=4)
        pygame.draw.rect(self.image, (40, 50, 70), (w-13, 4, 8, h-8))
        pygame.draw.rect(self.image, (245, 245, 245), (3, h//2-1, w-15, 2))

    def update(self, keys, on_track_func):
        """Update car with variable acceleration"""
        
        # === Steering (unchanged) ===
        target_steer = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            target_steer -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            target_steer += 1.0

        if target_steer == 0:
            self.steer += (0 - self.steer) * self.STEER_RETURN
        else:
            self.steer += (target_steer - self.steer) * self.STEER_RESPONSE
        self.steer = max(-1.0, min(1.0, self.steer))

        # === Variable Throttle Input ===
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.throttle_input = min(self.throttle_input + 0.12, 1.0)   # ramp up
        else:
            self.throttle_input = max(self.throttle_input - 0.15, 0.0)   # ramp down

        # Smooth the actual throttle
        self.current_throttle = self.current_throttle * 0.75 + self.throttle_input * 0.25

        # === Acceleration & Braking ===
        if self.throttle_input > 0.05:                    # forward throttle
            accel_amount = self.BASE_ACCEL * self.current_throttle
            self.speed += accel_amount

        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:     # braking / reverse
            if self.speed > 0.4:
                self.speed -= self.BRAKE                  # strong brake
            else:
                self.speed -= self.REVERSE_ACCEL          # go into reverse

        # Natural friction
        self.speed *= self.FRICTION
        self.speed = max(self.REVERSE_MAX, min(self.MAX_SPEED, self.speed))

        # === Turning (depends on speed) ===
        speed_factor = min(abs(self.speed) / 3.5, 1.0)
        dir_sign = 1 if self.speed >= 0 else -1
        self.angle += self.steer * self.TURN_RATE * speed_factor * dir_sign

        # === Movement + Collision ===
        dx = self.speed * math.cos(self.angle)
        dy = self.speed * math.sin(self.angle)
        new_x = self.x + dx
        new_y = self.y + dy

        if self.is_on_track(new_x, new_y, on_track_func):
            self.x, self.y = new_x, new_y
        elif self.is_on_track(new_x, self.y, on_track_func):
            self.x = new_x
            self.speed *= 0.68
        elif self.is_on_track(self.x, new_y, on_track_func):
            self.y = new_y
            self.speed *= 0.68
        else:
            self.speed *= 0.28

    def is_on_track(self, x, y, on_track_func):
        c = math.cos(self.angle)
        s = math.sin(self.angle)
        CAR_HALF_L = 12
        CAR_HALF_W = 6
        
        for ox, oy in [(CAR_HALF_L, CAR_HALF_W), (CAR_HALF_L, -CAR_HALF_W),
                       (-CAR_HALF_L, CAR_HALF_W), (-CAR_HALF_L, -CAR_HALF_W)]:
            if not on_track_func(x + ox * c - oy * s, y + ox * s + oy * c):
                return False
        return True

    def draw(self, screen):
        rotated = pygame.transform.rotate(self.image, -math.degrees(self.angle))
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated, rect)