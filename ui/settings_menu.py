import pygame

from settings import WIDTH, HEIGHT, BG_COLOR, TITLE_FONT, MENU_FONT, SMALL_FONT
from settings_store import save_settings
from ui.crosshair import draw_crosshair
from ui.menu import get_middle

CROSSHAIR_STYLES = ["cross", "x", "dot", "circle"]
SENSITIVITY_STEPS = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0]
FPS_STEPS = [60, 120, 144, 240, 0]  # 0 = uncapped

def _closest_index(options, value):
    return min(range(len(options)), key=lambda i: abs(options[i] - value))

def _fps_label(fps):
    return "Uncapped" if fps == 0 else str(fps)

def settings_menu(win, user_settings):
    style_index = (CROSSHAIR_STYLES.index(user_settings["crosshair_style"])
                   if user_settings.get("crosshair_style") in CROSSHAIR_STYLES else 0)
    sens_index = _closest_index(SENSITIVITY_STEPS, user_settings.get("sensitivity", 1.0))
    size = user_settings.get("crosshair_size", 14)
    sound_on = user_settings.get("sound_enabled", True)
    fps_index = (FPS_STEPS.index(user_settings["fps_cap"])
                 if user_settings.get("fps_cap") in FPS_STEPS else 0)
    fullscreen = user_settings.get("fullscreen", False)
    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
        win.fill(BG_COLOR)

        title = TITLE_FONT.render("SETTINGS", True, "white")
        style_label = MENU_FONT.render(f"Crosshair: {CROSSHAIR_STYLES[style_index]}", True, "cyan")
        style_hint = SMALL_FONT.render("Left / Right to change", True, "white")
        size_label = MENU_FONT.render(f"Size: {size}", True, "cyan")
        size_hint = SMALL_FONT.render("[ and ] to change", True, "white")
        sens_label = MENU_FONT.render(f"Sensitivity: {SENSITIVITY_STEPS[sens_index]}", True, "cyan")
        sens_hint = SMALL_FONT.render("- and + to change", True, "white")
        sound_label = MENU_FONT.render(f"Sound: {'On' if sound_on else 'Off'}", True, "cyan")
        sound_hint = SMALL_FONT.render("M to toggle", True, "white")
        fps_label = MENU_FONT.render(f"FPS Cap: {_fps_label(FPS_STEPS[fps_index])}", True, "cyan")
        fps_hint = SMALL_FONT.render("F to cycle", True, "white")
        display_label = MENU_FONT.render(
            f"Display: {'Fullscreen' if fullscreen else 'Windowed'}", True, "cyan")
        display_hint = SMALL_FONT.render("V to toggle", True, "white")
        back = SMALL_FONT.render("ESC / BACKSPACE to save and return", True, "yellow")

        win.blit(title, (get_middle(title), 20))
        win.blit(style_label, (get_middle(style_label), 90))
        win.blit(style_hint, (get_middle(style_hint), 126))
        win.blit(size_label, (get_middle(size_label), 164))
        win.blit(size_hint, (get_middle(size_hint), 200))
        win.blit(sens_label, (get_middle(sens_label), 238))
        win.blit(sens_hint, (get_middle(sens_hint), 274))
        win.blit(sound_label, (get_middle(sound_label), 312))
        win.blit(sound_hint, (get_middle(sound_hint), 348))
        win.blit(fps_label, (get_middle(fps_label), 386))
        win.blit(fps_hint, (get_middle(fps_hint), 422))
        win.blit(display_label, (get_middle(display_label), 460))
        win.blit(display_hint, (get_middle(display_hint), 496))
        win.blit(back, (get_middle(back), 530))

        preview = {
            "crosshair_style": CROSSHAIR_STYLES[style_index],
            "crosshair_size": size,
            "crosshair_gap": user_settings.get("crosshair_gap", 4),
            "crosshair_thickness": user_settings.get("crosshair_thickness", 2),
        }
        draw_crosshair(win, (WIDTH // 2, 560), preview)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    user_settings["crosshair_style"] = CROSSHAIR_STYLES[style_index]
                    user_settings["crosshair_size"] = size
                    user_settings["sensitivity"] = SENSITIVITY_STEPS[sens_index]
                    user_settings["sound_enabled"] = sound_on
                    user_settings["fps_cap"] = FPS_STEPS[fps_index]
                    user_settings["fullscreen"] = fullscreen
                    save_settings(user_settings)
                    return user_settings
                elif event.key == pygame.K_LEFT:
                    style_index = (style_index - 1) % len(CROSSHAIR_STYLES)
                elif event.key == pygame.K_RIGHT:
                    style_index = (style_index + 1) % len(CROSSHAIR_STYLES)
                elif event.key == pygame.K_LEFTBRACKET:
                    size = max(4, size - 2)
                elif event.key == pygame.K_RIGHTBRACKET:
                    size = min(40, size + 2)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    sens_index = max(0, sens_index - 1)
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    sens_index = min(len(SENSITIVITY_STEPS) - 1, sens_index + 1)
                elif event.key == pygame.K_m:
                    sound_on = not sound_on
                elif event.key == pygame.K_f:
                    fps_index = (fps_index + 1) % len(FPS_STEPS)
                elif event.key == pygame.K_v:
                    fullscreen = not fullscreen