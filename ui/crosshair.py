import pygame

CROSSHAIR_COLOR = (0, 255, 130)

def draw_crosshair(win, pos, user_settings):
    x, y = pos
    style = user_settings.get("crosshair_style", "cross")
    size = user_settings.get("crosshair_size", 14)
    gap = user_settings.get("crosshair_gap", 4)
    thickness = user_settings.get("crosshair_thickness", 2)

    if style == "dot":
        pygame.draw.circle(win, CROSSHAIR_COLOR, (int(x), int(y)), max(1, thickness + 1))

    elif style == "circle":
        pygame.draw.circle(win, CROSSHAIR_COLOR, (int(x), int(y)), size, thickness)

    elif style == "x":
        for dx, dy in ((-1, -1), (1, 1)):
            pygame.draw.line(win, CROSSHAIR_COLOR,
                              (x + dx * gap, y + dy * gap),
                              (x + dx * (gap + size), y + dy * (gap + size)), thickness)
        for dx, dy in ((-1, 1), (1, -1)):
            pygame.draw.line(win, CROSSHAIR_COLOR,
                              (x + dx * gap, y + dy * gap),
                              (x + dx * (gap + size), y + dy * (gap + size)), thickness)

    else: 
        pygame.draw.line(win, CROSSHAIR_COLOR, (x - gap - size, y), (x - gap, y), thickness)
        pygame.draw.line(win, CROSSHAIR_COLOR, (x + gap, y), (x + gap + size, y), thickness)
        pygame.draw.line(win, CROSSHAIR_COLOR, (x, y - gap - size), (x, y - gap), thickness)
        pygame.draw.line(win, CROSSHAIR_COLOR, (x, y + gap), (x, y + gap + size), thickness)