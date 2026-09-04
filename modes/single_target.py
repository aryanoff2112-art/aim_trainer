import random
import time

from modes.base import GameMode


class SingleTargetMode(GameMode):
    """Shared behavior for modes that keep exactly one target on screen,
    replacing it the instant it's removed - optionally after a short
    delay (e.g. Reaction mode's randomized gap between targets)."""

    respawn_delay_range = None  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pending_spawn_at = None

    def spawn_interval_ms(self):
        return None  

    def after_target_removed(self):
        if self.targets:
            return
        if self.respawn_delay_range:
            delay = random.uniform(*self.respawn_delay_range)
            self._pending_spawn_at = time.time() + delay
        else:
            self.spawn_target()

    def on_frame(self, dt, cursor_pos):
        if self._pending_spawn_at is not None and time.time() >= self._pending_spawn_at:
            self._pending_spawn_at = None
            self.spawn_target()