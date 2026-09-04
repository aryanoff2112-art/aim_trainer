import random

from settings import REACTION_ROUNDS, REACTION_TARGET_SIZE, REACTION_DELAY_RANGE
from target import Target
from modes.single_target import SingleTargetMode

class Reaction(SingleTargetMode):
    """A target appears at a random spot after a randomized delay; click
    it as fast as possible. Isolates pure reaction time from aiming
    skill by giving the target a fixed, generous size."""

    name = "Reaction"
    respawn_delay_range = REACTION_DELAY_RANGE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_size = REACTION_TARGET_SIZE
        self.rounds = REACTION_ROUNDS

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