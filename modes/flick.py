import random

from settings import FLICK_ROUNDS, FLICK_TARGET_SIZE
from target import Target
from modes.single_target import SingleTargetMode


class Flick(SingleTargetMode):
    """Targets appear one at a time in alternating corners, far apart,
    forcing a fast wide flick rather than a small correction. Ends after
    a fixed number of hits."""

    name = "Flick"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_size = FLICK_TARGET_SIZE
        self.rounds = FLICK_ROUNDS
        self._last_quadrant = None

    def _quadrant_center(self, q):
        left, top, right, bottom = self.bounds()
        pad = self.target_size + 10
        corners = {
            0: (left + pad, top + pad),
            1: (right - pad, top + pad),
            2: (left + pad, bottom - pad),
            3: (right - pad, bottom - pad),
        }
        return corners[q]

    def spawn_target(self):
        choices = [q for q in range(4) if q != self._last_quadrant]
        q = random.choice(choices)
        self._last_quadrant = q
        x, y = self._quadrant_center(q)

        target = Target(x, y, self.target_size, growth_rate=0, target_type="normal")
        target.size = self.target_size
        target.grow = False
        self.targets.append(target)

    def hud_extra(self):
        return [f"Hits {self.hits}/{self.rounds}"]

    def is_finished(self):
        return self.hits >= self.rounds