import pygame

from settings import WIDTH, HEIGHT, BG_COLOR, LABEL_FONT, SMALL_FONT
from ui.menu import get_middle
from recommendations import recommend_training

def _reaction_str(ms):
    return f"{ms}ms" if ms is not None else "--"

def show_end_screen(win, result, stats, newly_unlocked):
    win.fill(BG_COLOR)

    lines = [
        ("Session Complete", "white"),
        (f"Mode: {result['mode']}  ({result['difficulty']})", "white"),
        (f"Score: {result['score']}", "white"),
        (f"Hits: {result['hits']}   Clicks: {result['clicks']}", "white"),
        (f"Precision: {result['precision']}%   Target Accuracy: {result['target_accuracy']}%", "white"),
        (f"Speed: {result['speed']} t/s", "white"),
        (f"Avg Reaction: {_reaction_str(result['avg_reaction_ms'])}   "
         f"Best: {_reaction_str(result['best_reaction_ms'])}", "white"),
        (f"Best Combo: x{result['combo']}", "white"),
    ]

    if "tracking_pct" in result:
        lines.append((f"On-Target: {result['tracking_pct']}%", "white"))

    lines.append((f"All-time Best Reaction: {_reaction_str(stats['best_reaction_ms'])}", "gold"))
    lines.append((f"Games Played: {stats['games_played']}", "gold"))

    _, _, tip = recommend_training(result)
    lines.append((tip, "cyan"))

    if newly_unlocked:
        lines.append(("Achievement Unlocked!", "orange"))
        for ach in newly_unlocked:
            lines.append((f"  {ach['name']} - {ach['desc']}", "orange"))

    lines.append(("Recent Sessions", "cyan"))

    y = 12
    for text, color in lines:
        label = LABEL_FONT.render(text, True, color)
        win.blit(label, (get_middle(label), y))
        y += 22

    recent = stats["sessions"][-3:][::-1]
    for session in recent:
        line = (f"{session['date']}  {session['mode'][:4]}  "
                f"score {session['score']}  prec {session['precision']}%")
        label = SMALL_FONT.render(line, True, "white")
        win.blit(label, (get_middle(label), y))
        y += 20

    footer1 = LABEL_FONT.render("Press R to Restart", True, "yellow")
    footer2 = LABEL_FONT.render("Press ESC to Quit", True, "red")
    win.blit(footer1, (get_middle(footer1), HEIGHT - 50))
    win.blit(footer2, (get_middle(footer2), HEIGHT - 26))

    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return False