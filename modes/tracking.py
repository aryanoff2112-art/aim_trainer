import random

from settings import TRACKING_DURATION, TRACKING_TARGET_SIZE
from target import Target
from modes.base import GameMode


class Tracking(GameMode):
    """A single target moves continuously along a circular or zigzag
    path. There's nothing to click - keep the crosshair on it. Scored
    by percentage of time on-target, which is a different skill than
    the click-based modes."""

    name = "Tracking"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_size = TRACKING_TARGET_SIZE
        self.duration = TRACKING_DURATION
        self.hover_time = 0.0
        self._on_target_last_frame = False

    def spawn_interval_ms(self):
        return None

    def spawn_target(self):
        left, top, right, bottom = self.bounds()
        x = random.randint(int(left + 80), int(right - 80))
        y = random.randint(int(top + 80), int(bottom - 80))
        pattern = random.choice(["circular", "zigzag"])

        target = Target(x, y, self.target_size, growth_rate=0, target_type="normal",
                         moving=True, movement_pattern=pattern, speed_mult=1.0)
        target.size = self.target_size
        target.grow = False
        target.clickable = False 
        self.targets.append(target)

    def on_frame(self, dt, cursor_pos):
        if not self.targets:
            return
        target = self.targets[0]
        on_target = target.collide(*cursor_pos)
        if on_target:
            self.hover_time += dt
            self.score += 1
            if not self._on_target_last_frame:
                self.combo += 1
                self.best_combo = max(self.best_combo, self.combo)
        else:
            self.combo = 0
        self._on_target_last_frame = on_target

    def hud_extra(self):
        pct = round((self.hover_time / self.elapsed_time) * 100, 1) if self.elapsed_time > 0 else 0
        remaining = max(0, self.duration - self.elapsed_time)
        return [f"On-target {pct}%", f"Time left {int(remaining)}s"]

    def is_finished(self):
        return self.elapsed_time >= self.duration

    def extra_result_fields(self):
        pct = round((self.hover_time / max(self.elapsed_time, 0.001)) * 100, 1)
        return {"tracking_pct": pct}