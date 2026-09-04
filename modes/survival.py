import random

from settings import (DIFFICULTIES, DIFFICULTY_INTERVAL, DIFFICULTY_STEP,
                       MIN_TARGET_INCREMENT, MOVEMENT_PATTERNS)
from target import Target
from modes.base import GameMode

TARGET_ROLL_TABLE = [
    ("bomb", 1, 6),
    ("bonus", 1, 14),
    ("tiny", 2, 10),
    ("decoy", 2, 8),
    ("reverse", 3, 5),
    ("golden", 3, 4),
]

ADAPTIVE_WINDOW = 10 


class Survival(GameMode):
    """The original endless mode: targets grow and shrink, you lose a
    life on a miss, and difficulty ramps up both on a timer and
    adaptively based on how well you're currently doing. Bonus/bomb/
    tiny/decoy/reverse/golden targets and movement appear at higher
    levels."""

    name = "Survival"

    def __init__(self, window, clock, difficulty_name, user_settings, sound_engine):
        super().__init__(window, clock, difficulty_name, user_settings, sound_engine)
        settings = DIFFICULTIES[difficulty_name]
        self.lives = settings["lives"]
        self.max_size = settings["max_size"]
        self.growth_rate = settings["growth"]
        self.current_spawn_rate = settings["increment"]
        self.last_level = 0
        self._recent_outcomes = [] 
        self._adaptive_factor = 1.0 

    def spawn_interval_ms(self):
        return self.current_spawn_rate * self._adaptive_factor

    def _register_outcome(self, is_hit):
        self._recent_outcomes.append(is_hit)
        self._recent_outcomes = self._recent_outcomes[-ADAPTIVE_WINDOW:]
        if len(self._recent_outcomes) < ADAPTIVE_WINDOW:
            return

        rolling_accuracy = sum(self._recent_outcomes) / len(self._recent_outcomes)
        if rolling_accuracy > 0.9:
            self._adaptive_factor = max(0.75, self._adaptive_factor - 0.05)
        elif rolling_accuracy < 0.6:
            self._adaptive_factor = min(1.3, self._adaptive_factor + 0.05)

    def _update_level(self):
        level = int(self.elapsed_time // DIFFICULTY_INTERVAL)
        if level > self.last_level:
            self.last_level = level
            self.current_spawn_rate = max(MIN_TARGET_INCREMENT,
                                           self.current_spawn_rate - DIFFICULTY_STEP)
            self.growth_rate += 0.03
            self.sound.play("levelup")
        return level

    def _choose_target_type(self, level):
        options = [(t, w) for t, min_lvl, w in TARGET_ROLL_TABLE if level >= min_lvl]
        if not options or random.random() > 0.35:
            return "normal"
        types, weights = zip(*options)
        return random.choices(types, weights=weights, k=1)[0]

    def spawn_target(self):
        level = self._update_level()
        left, top, right, bottom = self.bounds()
        x = random.randint(int(left + self.max_size), int(right - self.max_size))
        y = random.randint(int(top + self.max_size), int(bottom - self.max_size))

        target_type = self._choose_target_type(level)
        moving = level >= 2 and random.random() < 0.5
        pattern = random.choice(MOVEMENT_PATTERNS) if moving else "bounce"
        speed_mult = 1.6 if (moving and level >= 4 and random.random() < 0.3) else 1.0

        self.targets.append(Target(x, y, self.max_size, self.growth_rate, target_type,
                                    moving, pattern, speed_mult))

    def hud_extra(self):
        return [f"Lvl {self.last_level + 1}", f"Lives {self.lives - self.misses}"]

    def is_finished(self):
        return self.misses >= self.lives