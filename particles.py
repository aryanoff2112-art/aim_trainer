import math
import random

import pygame

_ALPHA_BUCKET = 16
_surface_cache = {}


def _get_particle_surface(radius, alpha, color):
    bucket_alpha = max(1, (alpha // _ALPHA_BUCKET) * _ALPHA_BUCKET)
    key = (radius, bucket_alpha, color)
    surf = _surface_cache.get(key)
    if surf is None:
        size = radius * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*color, bucket_alpha), (radius, radius), radius)
        _surface_cache[key] = surf
    return surf


class Particle:
    """Small dot used for the hit-burst effect. Alpha genuinely fades via
    a per-pixel-alpha surface, rather than only shrinking the radius."""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.tau)
        speed = random.uniform(80, 220)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 0.4
        self.max_life = 0.4
        self.color = color

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def draw(self, surface, offset=(0, 0)):
        if self.life <= 0:
            return
        fade = max(0.0, self.life / self.max_life)
        alpha = int(255 * fade)
        radius = max(1, int(4 * fade) + 1)

        particle_surf = _get_particle_surface(radius, alpha, self.color)

        ox, oy = offset
        surface.blit(particle_surf, (int(self.x - radius + ox), int(self.y - radius + oy)))


def spawn_burst(particles, x, y, color, count=14):
    for _ in range(count):
        particles.append(Particle(x, y, color))