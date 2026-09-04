import pygame

from settings import WIDTH, HEIGHT
from settings_store import load_settings
from stats import load_stats, save_stats, record_session
from achievements import check_achievements
from audio import SoundEngine
from ui.menu import mode_and_difficulty_menu
from ui.settings_menu import settings_menu
from ui.dashboard import show_dashboard
from ui.end_screen import show_end_screen
from modes.base import ABORTED
from modes.survival import Survival
from modes.gridshot import Gridshot
from modes.flick import Flick
from modes.reaction import Reaction
from modes.precision import Precision
from modes.tracking import Tracking

pygame.display.set_caption("Aim Trainer")

MODE_CLASSES = {
    "Survival": Survival,
    "Gridshot": Gridshot,
    "Flick": Flick,
    "Reaction": Reaction,
    "Precision": Precision,
    "Tracking": Tracking,
}

def make_window(user_settings):
    flags = pygame.FULLSCREEN if user_settings.get("fullscreen") else 0
    return pygame.display.set_mode((WIDTH, HEIGHT), flags)

def run():
    stats = load_stats()
    user_settings = load_settings()
    sound = SoundEngine(user_settings)
    clock = pygame.time.Clock()
    window = make_window(user_settings)

    while True:
        action, mode_name, difficulty_name = mode_and_difficulty_menu(window, stats)

        if action == "settings":
            was_fullscreen = user_settings.get("fullscreen", False)
            user_settings = settings_menu(window, user_settings)
            sound = SoundEngine(user_settings)
            if user_settings.get("fullscreen", False) != was_fullscreen:
                window = make_window(user_settings)
            continue

        if action == "dashboard":
            show_dashboard(window, stats)
            continue

        mode_cls = MODE_CLASSES[mode_name]
        session = mode_cls(window, clock, difficulty_name, user_settings, sound)

        key = f"{mode_name}:{difficulty_name}"
        high_score = stats["high_scores"].get(key, 0)

        result = session.run(high_score)
        if result is None:
            return  
        if result == ABORTED:
            continue 

        stats = record_session(stats, result)
        newly_unlocked = check_achievements(result, stats)
        save_stats(stats)

        for ach in newly_unlocked:
            sound.play("achievement")

        keep_going = show_end_screen(window, result, stats, newly_unlocked)
        if not keep_going:
            return

if __name__ == "__main__":
    run()
    pygame.quit()