import pygame

from settings import WIDTH, HEIGHT, BG_COLOR, DIFFICULTIES, TITLE_FONT, MENU_FONT, SMALL_FONT

MODES = ["Survival", "Gridshot", "Flick", "Reaction", "Precision", "Tracking"]

MODE_DESCRIPTIONS = {
    "Survival": "Endless - grow/shrink targets, limited lives",
    "Gridshot": "60s - one target, instant replace",
    "Flick": "20 hits - far-apart targets, wide flicks",
    "Reaction": "20 hits - randomized delay, pure reaction time",
    "Precision": "20 hits - tiny targets, bullseye scoring",
    "Tracking": "45s - follow a moving target, no clicking",
}

MODE_HAS_DIFFICULTY = {
    "Survival": True,
    "Gridshot": False,
    "Flick": False,
    "Reaction": False,
    "Precision": False,
    "Tracking": False,
}

def get_middle(surface):
    return (WIDTH - surface.get_width()) // 2

def mode_and_difficulty_menu(win, stats):
    """Lets the player pick a training mode and difficulty, or jump to
    Settings/Dashboard. Returns (action, mode_name, difficulty_name)
    where action is 'start', 'settings', or 'dashboard'. Exits the
    process on ESC/quit from this screen."""
    mode_names = MODES
    difficulty_names = list(DIFFICULTIES.keys())
    mode_index = 0
    difficulty_index = 1  
    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
        win.fill(BG_COLOR)

        mode_has_difficulty = MODE_HAS_DIFFICULTY[mode_names[mode_index]]

        title = TITLE_FONT.render("AIM TRAINER", True, "white")
        mode_label = MENU_FONT.render(f"Mode: {mode_names[mode_index]}", True, "cyan")
        mode_desc = SMALL_FONT.render(MODE_DESCRIPTIONS[mode_names[mode_index]], True, "white")
        mode_hint = SMALL_FONT.render("Up / Down: change mode", True, "white")
        if mode_has_difficulty:
            diff_label = MENU_FONT.render(f"Difficulty: {difficulty_names[difficulty_index]}", True, "orange")
            diff_hint = SMALL_FONT.render("Left / Right: change difficulty", True, "white")
        else:
            diff_label = MENU_FONT.render("Difficulty: N/A", True, "grey")
            diff_hint = SMALL_FONT.render("(this mode has a fixed difficulty)", True, "white")
        start = MENU_FONT.render("SPACE to Start", True, "green")
        other = SMALL_FONT.render("C: Settings   D: Dashboard   ESC: Quit", True, "yellow")

        effective_difficulty = difficulty_names[difficulty_index] if mode_has_difficulty else "Normal"
        key = f"{mode_names[mode_index]}:{effective_difficulty}"
        high = MENU_FONT.render(f"Best: {stats['high_scores'].get(key, 0)}", True, "yellow")

        win.blit(title, (get_middle(title), 30))
        win.blit(mode_label, (get_middle(mode_label), 120))
        win.blit(mode_desc, (get_middle(mode_desc), 160))
        win.blit(mode_hint, (get_middle(mode_hint), 190))
        win.blit(diff_label, (get_middle(diff_label), 240))
        win.blit(diff_hint, (get_middle(diff_hint), 278))
        win.blit(start, (get_middle(start), 330))
        win.blit(high, (get_middle(high), 380))
        win.blit(other, (get_middle(other), 460))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "start", mode_names[mode_index], effective_difficulty
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                elif event.key == pygame.K_UP:
                    mode_index = (mode_index - 1) % len(mode_names)
                elif event.key == pygame.K_DOWN:
                    mode_index = (mode_index + 1) % len(mode_names)
                elif event.key == pygame.K_LEFT and mode_has_difficulty:
                    difficulty_index = (difficulty_index - 1) % len(difficulty_names)
                elif event.key == pygame.K_RIGHT and mode_has_difficulty:
                    difficulty_index = (difficulty_index + 1) % len(difficulty_names)
                elif event.key == pygame.K_c:
                    return "settings", None, None
                elif event.key == pygame.K_d:
                    return "dashboard", None, None