import math
import random
import time

import pygame

TARGET_STYLES = {
    "normal":  {"points": 1, "color_1": (255, 0, 0),    "color_2": (255, 255, 255), "size_mult": 1.0,  "growth_mult": 1.0},
    "bonus":   {"points": 3, "color_1": (212, 175, 55), "color_2": (255, 250, 205), "size_mult": 0.7,  "growth_mult": 1.4},
    "bomb":    {"points": 0, "color_1": (20, 20, 20),   "color_2": (120, 0, 0),     "size_mult": 1.0,  "growth_mult": 1.0},
    "tiny":    {"points": 2, "color_1": (40, 120, 220), "color_2": (200, 230, 255), "size_mult": 0.45, "growth_mult": 1.2},
    "golden":  {"points": 5, "color_1": (255, 200, 0),  "color_2": (255, 255, 255), "size_mult": 0.6,  "growth_mult": 2.2},
    "decoy":   {"points": 0, "color_1": (90, 90, 90),   "color_2": (180, 180, 180), "size_mult": 1.0,  "growth_mult": 1.0},
    "reverse": {"points": -2, "color_1": (150, 0, 90),  "color_2": (230, 150, 200), "size_mult": 0.85, "growth_mult": 1.0},
}


class Target:
    """A single target. `target_type` keys into TARGET_STYLES.

    Reaction time is measured from construction to the moment the
    target registers a hit, using time.perf_counter() for sub-ms
    precision. Movement, when enabled, follows `movement_pattern`
    ("bounce", "horizontal", "vertical", "circular", "zigzag", "random").
    """

    def __init__(self, x, y, max_size, growth_rate, target_type="normal",
                 moving=False, movement_pattern="bounce", speed_mult=1.0):
        style = TARGET_STYLES.get(target_type, TARGET_STYLES["normal"])

        self.x = x
        self.y = y
        self.size = 0
        self.grow = True
        self.max_size = int(max_size * style["size_mult"])
        self.growth_rate = growth_rate * style["growth_mult"]
        self.type = target_type
        self.points = style["points"]
        self.color_1 = style["color_1"]
        self.color_2 = style["color_2"]
        self.clickable = True

        self.moving = moving
        self.movement_pattern = movement_pattern if moving else "bounce"

        base_speed = random.uniform(60, 140) * speed_mult
        self.vx = random.choice([-1, 1]) * base_speed if moving else 0
        self.vy = random.choice([-1, 1]) * base_speed if moving else 0

        # per-pattern state
        self._circular_center = (x, y)
        self._circular_radius = random.uniform(50, 110)
        self._circular_angle = random.uniform(0, math.tau)
        self._circular_speed = random.choice([-1, 1]) * random.uniform(1.2, 2.4)
        self._zigzag_start_y = y
        self._zigzag_t = 0.0
        self._zigzag_amplitude = random.uniform(30, 70)
        self._zigzag_freq = random.uniform(2.0, 4.0)
        self._random_timer = random.uniform(0.4, 1.0)

        if movement_pattern == "horizontal":
            self.vy = 0
        elif movement_pattern == "vertical":
            self.vx = 0

        self.spawn_time = time.perf_counter()
        self.hit_time = None

    def register_hit(self):
        """Marks the target as hit and returns the reaction time in seconds."""
        self.hit_time = time.perf_counter()
        return self.hit_time - self.spawn_time

    def zone_multiplier(self, click_pos):
        """Bullseye scoring: center/middle/edge -> 3x/2x/1x."""
        if self.size <= 0:
            return 1
        dx = click_pos[0] - self.x
        dy = click_pos[1] - self.y
        ratio = math.sqrt(dx * dx + dy * dy) / self.size
        if ratio <= 0.35:
            return 3
        if ratio <= 0.7:
            return 2
        return 1

    def update(self, dt, bounds):
        if self.size >= self.max_size:
            self.grow = False
        if self.grow:
            self.size += self.growth_rate * 60 * dt
        else:
            self.size -= self.growth_rate * 60 * dt

        if self.moving:
            self._move(dt, bounds)

    def _move(self, dt, bounds):
        left, top, right, bottom = bounds
        pattern = self.movement_pattern

        if pattern == "circular":
            self._circular_angle += self._circular_speed * dt
            cx, cy = self._circular_center
            r = self._circular_radius
            self.x = min(max(cx + math.cos(self._circular_angle) * r, left + self.size), right - self.size)
            self.y = min(max(cy + math.sin(self._circular_angle) * r, top + self.size), bottom - self.size)
            return

        if pattern == "zigzag":
            self._zigzag_t += dt
            self.x += self.vx * dt
            self.y = self._zigzag_start_y + math.sin(self._zigzag_t * self._zigzag_freq) * self._zigzag_amplitude
            self.y = min(max(self.y, top + self.size), bottom - self.size)
            if self.x - self.size <= left or self.x + self.size >= right:
                self.vx *= -1
                self.x = max(left + self.size, min(right - self.size, self.x))
            return

        if pattern == "random":
            self._random_timer -= dt
            if self._random_timer <= 0:
                self._random_timer = random.uniform(0.4, 1.0)
                angle = random.uniform(0, math.tau)
                speed = math.hypot(self.vx, self.vy) or 100
                self.vx = math.cos(angle) * speed
                self.vy = math.sin(angle) * speed

        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.x - self.size <= left or self.x + self.size >= right:
            self.vx *= -1
            self.x = max(left + self.size, min(right - self.size, self.x))
        if self.y - self.size <= top or self.y + self.size >= bottom:
            self.vy *= -1
            self.y = max(top + self.size, min(bottom - self.size, self.y))

    def draw(self, win, offset=(0, 0)):
        ox, oy = offset
        cx, cy = int(self.x + ox), int(self.y + oy)
        pygame.draw.circle(win, self.color_2, (cx, cy), int(self.size))
        pygame.draw.circle(win, self.color_1, (cx, cy), int(self.size * 0.8))
        pygame.draw.circle(win, self.color_2, (cx, cy), int(self.size * 0.6))
        pygame.draw.circle(win, self.color_1, (cx, cy), int(self.size * 0.4))

    def collide(self, x, y):
        dx = x - self.x
        dy = y - self.y
        return dx * dx + dy * dy <= self.size * self.size