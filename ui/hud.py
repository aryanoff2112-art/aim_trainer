import pygame

from settings import WIDTH, HEIGHT, TOP_BAR_HEIGHT, LABEL_FONT, MENU_FONT, SMALL_FONT, BIG_FONT

def format_time(secs):
    minutes = int(secs // 60)
    seconds = int(secs % 60)
    milliseconds = int((secs * 10) % 10)
    return f"{minutes:02d}:{seconds:02d}.{milliseconds}"

def draw_hud(win, elapsed_time, score, hits, misses, combo, high_score, avg_reaction_ms, extra_labels):
    pygame.draw.rect(win, "grey", (0, 0, WIDTH, TOP_BAR_HEIGHT))

    speed = round(hits / elapsed_time, 1) if elapsed_time > 0 else 0
    reaction_str = f"{int(avg_reaction_ms)}ms" if avg_reaction_ms is not None else "--"

    parts = [
        f"Time {format_time(elapsed_time)}",
        f"Score {score}",
        f"Speed {speed}t/s",
        f"React {reaction_str}",
        f"Combo x{combo}",
        f"Best {high_score}",
    ] + extra_labels

    x = 8
    for part in parts:
        label = LABEL_FONT.render(part, True, "black")
        win.blit(label, (x, 14))
        x += label.get_width() + 12

def draw_pause_overlay(win):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    win.blit(overlay, (0, 0))

    label = MENU_FONT.render("PAUSED", True, "white")
    hint = SMALL_FONT.render("Press P to resume, ESC to quit to menu", True, "yellow")
    win.blit(label, ((WIDTH - label.get_width()) // 2, HEIGHT // 2 - 40))
    win.blit(hint, ((WIDTH - hint.get_width()) // 2, HEIGHT // 2 + 10))

    pygame.display.update()

def draw_countdown(win, seconds_left, background_drawn=True):
    if not background_drawn:
        win.fill((0, 25, 40))

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 90))
    win.blit(overlay, (0, 0))

    text = "GO!" if seconds_left <= 0 else str(seconds_left)
    color = "lime" if seconds_left <= 0 else "white"
    label = BIG_FONT.render(text, True, color)
    win.blit(label, ((WIDTH - label.get_width()) // 2, (HEIGHT - label.get_height()) // 2))

    pygame.display.update()

def draw_bomb_flash(win, alpha):
    if alpha <= 0:
        return
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((255, 0, 0, int(min(255, alpha))))
    win.blit(overlay, (0, 0))

    label = MENU_FONT.render("BOMB!", True, "white")
    win.blit(label, ((WIDTH - label.get_width()) // 2, HEIGHT // 2 - 20))