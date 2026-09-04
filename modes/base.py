import random
import time

import pygame

from settings import WIDTH, HEIGHT, TOP_BAR_HEIGHT, TARGET_PADDING, BG_COLOR, COUNTDOWN_SECONDS
from particles import spawn_burst
from ui.hud import draw_hud, draw_pause_overlay, draw_countdown, draw_bomb_flash
from ui.crosshair import draw_crosshair

ABORTED = "aborted"

MAX_DT = 0.05


class GameMode:
    """Shared plumbing for a play session: countdown, the update/draw
    loop, pausing, a sensitivity-scaled virtual cursor + crosshair,
    particles, screen shake, sound, and reaction-time bookkeeping.

    Subclasses implement mode-specific rules by overriding:
      - spawn_target()        how a new target is created
      - spawn_interval_ms()   ms between periodic spawns, or falsy to
                               spawn only via after_target_removed()
      - is_finished()         the win/lose/time-up condition
      - hud_extra()           optional extra HUD strings
      - on_target_hit()       optional custom scoring
      - on_frame()            optional per-frame logic (e.g. Tracking)
      - extra_result_fields() optional extra fields in the result dict
    """

    name = "Base"

    def __init__(self, window, clock, difficulty_name, user_settings, sound_engine):
        self.window = window
        self.clock = clock
        self.difficulty_name = difficulty_name
        self.user_settings = user_settings
        self.sound = sound_engine
        self.sensitivity = user_settings.get("sensitivity", 1.0)
        self.fps_cap = user_settings.get("fps_cap", 60)

        self.targets = []
        self.particles = []

        self.clicks = 0
        self.hits = 0
        self.misses = 0
        self.score = 0
        self.combo = 0
        self.best_combo = 0
        self.reaction_times_ms = []

        self.start_time = time.time()
        self.paused_total = 0.0
        self._pause_started_at = None
        self.paused = False

        self.shake_timer = 0.0
        self.shake_offset = (0, 0)
        self.bomb_flash_timer = 0.0

        self.cursor = [WIDTH / 2, HEIGHT / 2]
        self._spawn_accum_ms = 0.0

    def spawn_target(self):
        raise NotImplementedError

    def spawn_interval_ms(self):
        raise NotImplementedError

    def is_finished(self):
        raise NotImplementedError

    def hud_extra(self):
        return []

    def on_target_hit(self, target, reaction_ms, zone_mult=1):
        speed_bonus = 1.25 if reaction_ms < 250 else 1.0
        multiplier = (1 + self.combo // 5) * zone_mult * speed_bonus
        self.score += round(target.points * multiplier)

    def on_target_expired(self, target):
        pass

    def after_target_removed(self):
        pass

    def on_frame(self, dt, cursor_pos):
        pass

    def extra_result_fields(self):
        return {}

    def _register_outcome(self, is_hit):
        """Hook for rolling-performance tracking, e.g. adaptive difficulty."""
        pass

    def bounds(self):
        return (TARGET_PADDING, TOP_BAR_HEIGHT + TARGET_PADDING,
                WIDTH - TARGET_PADDING, HEIGHT - TARGET_PADDING)

    @property
    def elapsed_time(self):
        return time.time() - self.start_time - self.paused_total

    def toggle_pause(self):
        if self.paused:
            self.paused = False
            self.paused_total += time.time() - self._pause_started_at
            pygame.mouse.get_rel()  
        else:
            self.paused = True
            self._pause_started_at = time.time()

    def _handle_hit(self, target, click_pos):
        reaction_ms = target.register_hit() * 1000
        self.targets.remove(target)

        if target.type == "bomb":
            self.misses += 1
            self.combo = 0
            self.shake_timer = 0.25
            self.bomb_flash_timer = 0.35
            self.sound.play("bomb")
            self._register_outcome(False)
            self.on_target_expired(target)
        elif target.points <= 0:
            self.combo = 0
            self.score = max(0, self.score + target.points)
            self.sound.play(target.type)
            self._register_outcome(False)
            self.on_target_expired(target)
        else:
            self.combo += 1
            self.best_combo = max(self.best_combo, self.combo)
            self.hits += 1
            self.reaction_times_ms.append(reaction_ms)
            spawn_burst(self.particles, target.x, target.y, target.color_1)
            zone_mult = target.zone_multiplier(click_pos)
            self.on_target_hit(target, reaction_ms, zone_mult)
            self.sound.play(target.type if target.type in ("bonus", "golden", "tiny") else "hit")
            self._register_outcome(True)

        self.after_target_removed()

    def _handle_expired(self, target):
        self.targets.remove(target)
        if target.type != "bomb":
            self.misses += 1
            self.combo = 0
            self._register_outcome(False)
        self.on_target_expired(target)
        self.after_target_removed()

    def _update_shake(self, dt):
        if self.shake_timer > 0:
            self.shake_timer -= dt
            self.shake_offset = (random.randint(-6, 6), random.randint(-6, 6))
        else:
            self.shake_offset = (0, 0)

    def _draw(self, high_score):
        self.window.fill(BG_COLOR)
        for target in self.targets:
            target.draw(self.window, self.shake_offset)
        for p in self.particles:
            p.draw(self.window, self.shake_offset)

        avg_reaction = (sum(self.reaction_times_ms) / len(self.reaction_times_ms)
                         if self.reaction_times_ms else None)

        draw_hud(self.window, self.elapsed_time, self.score, self.hits, self.misses,
                 self.combo, high_score, avg_reaction, self.hud_extra())

        if self.bomb_flash_timer > 0:
            alpha = int(180 * (self.bomb_flash_timer / 0.35))
            draw_bomb_flash(self.window, alpha)

        draw_crosshair(self.window, self.cursor, self.user_settings)
        pygame.display.update()

    def _run_countdown(self):
        """Draws a 3-2-1-GO overlay before the timer starts. Returns
        "quit" if the user closed the window, "aborted" if they pressed
        Esc to bail to the menu, or True on a normal countdown finish."""
        pygame.mouse.get_rel()
        for n in range(COUNTDOWN_SECONDS, 0, -1):
            self.sound.play("countdown")
            t0 = time.time()
            while time.time() - t0 < 1.0:
                self.clock.tick(60)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "quit"
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        return ABORTED
                self.window.fill(BG_COLOR)
                draw_countdown(self.window, n)

        self.sound.play("go")
        t0 = time.time()
        while time.time() - t0 < 0.4:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return ABORTED
            self.window.fill(BG_COLOR)
            draw_countdown(self.window, 0)

        return True

    def run(self, high_score):
        """Runs this mode until finished, aborted, or the app is closed.
        Returns a result dict on completion, ABORTED if the player Esc'd
        back to the menu, or None if the whole app was closed."""
        countdown_result = self._run_countdown()
        if countdown_result is not True:
            pygame.mouse.set_visible(True)
            return None if countdown_result == "quit" else ABORTED

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True) 
        pygame.mouse.get_rel()
        self.start_time = time.time()
        self.paused_total = 0.0
        self.spawn_target()

        try:
            while True:
                dt = min(self.clock.tick(self.fps_cap) / 1000, MAX_DT)

                if self.paused:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return None
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                            self.toggle_pause()
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            return ABORTED
                    draw_pause_overlay(self.window)
                    continue

                rel = pygame.mouse.get_rel()
                left, top, right, bottom = self.bounds()
                self.cursor[0] = min(max(self.cursor[0] + rel[0] * self.sensitivity, 0), WIDTH)
                self.cursor[1] = min(max(self.cursor[1] + rel[1] * self.sensitivity, TOP_BAR_HEIGHT), HEIGHT)
                cursor_pos = (self.cursor[0], self.cursor[1])

                click = False
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return None
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                        self.toggle_pause()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        return ABORTED
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        click = True
                        self.clicks += 1

                interval = self.spawn_interval_ms()
                if interval:
                    self._spawn_accum_ms += dt * 1000
                    while self._spawn_accum_ms >= interval:
                        self._spawn_accum_ms -= interval
                        self.spawn_target()

                hit_this_click = False
                for target in self.targets[:]:
                    target.update(dt, self.bounds())

                    if target.size <= 0:
                        self._handle_expired(target)
                        continue

                    if click and not hit_this_click and target.clickable and target.collide(*cursor_pos):
                        hit_this_click = True
                        self._handle_hit(target, cursor_pos)

                for p in self.particles[:]:
                    p.update(dt)
                    if p.life <= 0:
                        self.particles.remove(p)

                self._update_shake(dt)
                if self.bomb_flash_timer > 0:
                    self.bomb_flash_timer -= dt

                self.on_frame(dt, cursor_pos)

                if self.is_finished():
                    self.sound.play("gameover")
                    return self._build_result()

                self._draw(high_score)
        finally:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)

    def _build_result(self):
        elapsed = max(self.elapsed_time, 0.001)
        speed = round(self.hits / elapsed, 2)
        precision = round((self.hits / self.clicks) * 100, 1) if self.clicks else 0.0
        total_targets = self.hits + self.misses
        target_accuracy = round((self.hits / total_targets) * 100, 1) if total_targets else 0.0
        avg_reaction = (round(sum(self.reaction_times_ms) / len(self.reaction_times_ms))
                         if self.reaction_times_ms else None)
        best_reaction = round(min(self.reaction_times_ms)) if self.reaction_times_ms else None

        result = {
            "mode": self.name,
            "difficulty": self.difficulty_name,
            "score": self.score,
            "hits": self.hits,
            "clicks": self.clicks,
            "misses": self.misses,
            "precision": precision,
            "target_accuracy": target_accuracy,
            "speed": speed,
            "avg_reaction_ms": avg_reaction,
            "best_reaction_ms": best_reaction,
            "combo": self.best_combo,
            "duration": round(elapsed, 1),
        }
        result.update(self.extra_result_fields())
        return result