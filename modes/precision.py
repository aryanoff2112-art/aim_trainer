import random

from settings import PRECISION_ROUNDS, PRECISION_TARGET_SIZE
from target import Target
from modes.single_target import SingleTargetMode

class Precision(SingleTargetMode):
    """Like Gridshot but with very small targets, so the bullseye zone
    scoring in Target.zone_multiplier actually matters - this mode is
    about precision, not speed."""

    name = "Precision"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_size = PRECISION_TARGET_SIZE
        self.rounds = PRECISION_ROUNDS

    def spawn_target(self):
        left, top, right, bottom = self.bounds()
        x = random.randint(int(left + self.target_size), int(right - self.target_size))
        y = random.randint(int(top + self.target_size), int(bottom - self.target_size))

        target = Target(x, y, self.target_size, growth_rate=0, target_type="normal")
        target.size = self.target_size
        target.grow = False
        self.targets.append(target)

    def hud_extra(self):
        return [f"Round {self.hits}/{self.rounds}"]

    def is_finished(self):
        return self.hits >= self.rounds