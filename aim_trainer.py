import math
import random
import time
import json
import os
import pygame

pygame.init()

WIDTH, HEIGHT = 900, 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aim Trainer")

TARGET_EVENT = pygame.USEREVENT
TARGET_PADDING = 30
BG_COLOR = (0, 25, 40)
TOP_BAR_HEIGHT = 50
DIFFICULTY_INTERVAL = 15
DIFFICULTY_STEP = 25
MIN_TARGET_INCREMENT = 150

LABEL_FONT = pygame.font.SysFont("comicsans", 22)
TITLE_FONT = pygame.font.SysFont("comicsans", 60, bold=True)
MENU_FONT = pygame.font.SysFont("comicsans", 35)
SMALL_FONT = pygame.font.SysFont("comicsans", 26)

STATS_FILE = "stats.json"

DIFFICULTIES = {
    "Easy": {"increment": 500, "lives": 10, "max_size": 45, "growth": 0.18},
    "Normal": {"increment": 400, "lives": 7, "max_size": 40, "growth": 0.20},
    "Hard": {"increment": 300, "lives": 5, "max_size": 32, "growth": 0.28},
}

def load_stats():
    default = {
        "high_scores": {"Easy": 0, "Normal": 0, "Hard": 0},
        "best_accuracy": 0,
        "best_speed": 0,
        "games_played": 0,
    }
    if not os.path.exists(STATS_FILE):
        return default
    try:
        with open(STATS_FILE, "r") as f:
            data = json.load(f)
        for key, val in default.items():
            data.setdefault(key, val)
        return data
    except (json.JSONDecodeError, OSError):
        return default

def save_stats(stats):
    try:
        with open(STATS_FILE, "w") as f:
            json.dump(stats, f)
    except OSError as e:
        print(f"Warning: could not save stats ({e})")
class Target:
    """A single target. type is 'normal', 'bonus' (gold, worth more) or
    'bomb' (costs a life if clicked)."""

    def __init__(self, x, y, max_size, growth_rate, target_type="normal", moving=False):
        self.x = x
        self.y = y
        self.size = 0
        self.grow = True
        self.max_size = max_size
        self.growth_rate = growth_rate
        self.type = target_type
        self.moving = moving
        self.vx = random.choice([-1, 1]) * random.uniform(60, 140) if moving else 0
        self.vy = random.choice([-1, 1]) * random.uniform(60, 140) if moving else 0

        if target_type == "bonus":
            self.color_1, self.color_2 = (212, 175, 55), (255, 250, 205)
            self.max_size = int(max_size * 0.7)
            self.growth_rate *= 1.4
            self.points = 3
        elif target_type == "bomb":
            self.color_1, self.color_2 = (20, 20, 20), (120, 0, 0)
            self.points = 0
        else:
            self.color_1, self.color_2 = (255, 0, 0), (255, 255, 255)
            self.points = 1

    def update(self, dt, bounds):
        if self.size >= self.max_size:
            self.grow = False
        if self.grow:
            self.size += self.growth_rate * 60 * dt
        else:
            self.size -= self.growth_rate * 60 * dt

        if self.moving:
            left, top, right, bottom = bounds
            self.x += self.vx * dt
            self.y += self.vy * dt
            if self.x - self.size <= left or self.x + self.size >= right:
                self.vx *= -1
                self.x = max(left + self.size, min(right - self.size, self.x))
            if self.y - self.size <= top or self.y + self.size >= bottom:
                self.vy *= -1
                self.y = max(top + self.size, min(bottom - self.size, self.y))

    def draw(self, win):
        c1, c2 = self.color_1, self.color_2
        pygame.draw.circle(win, c2, (int(self.x), int(self.y)), int(self.size))
        pygame.draw.circle(win, c1, (int(self.x), int(self.y)), int(self.size * 0.8))
        pygame.draw.circle(win, c2, (int(self.x), int(self.y)), int(self.size * 0.6))
        pygame.draw.circle(win, c1, (int(self.x), int(self.y)), int(self.size * 0.4))

    def collide(self, x, y):
        dx = x - self.x
        dy = y - self.y
        return dx * dx + dy * dy <= self.size * self.size
class Particle:

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.tau)
        speed = random.uniform(80, 220)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 0.4
        self.max_life = 0.4
        self.color = color

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def draw(self, win):
        if self.life <= 0:
            return
        alpha = max(0, self.life / self.max_life)
        radius = max(1, int(4 * alpha))
        pygame.draw.circle(win, self.color, (int(self.x), int(self.y)), radius)


def spawn_burst(particles, x, y, color, count=14):
    for _ in range(count):
        particles.append(Particle(x, y, color))

def format_time(secs):
    minutes = int(secs // 60)
    seconds = int(secs % 60)
    milliseconds = int((secs * 10) % 10)
    return f"{minutes:02d}:{seconds:02d}.{milliseconds}"

def get_middle(surface):
    return (WIDTH - surface.get_width()) // 2

def draw_top_bar(win, elapsed_time, score, targets_pressed, misses, lives, high_score, level, combo):
    pygame.draw.rect(win, "grey", (0, 0, WIDTH, TOP_BAR_HEIGHT))

    speed = round(targets_pressed / elapsed_time, 1) if elapsed_time > 0 else 0

    parts = [
        f"Time: {format_time(elapsed_time)}",
        f"Speed: {speed} t/s",
        f"Score: {score}",
        f"Lives: {lives - misses}",
        f"Lvl: {level + 1}",
        f"Combo x{combo}",
        f"Best: {high_score}",
    ]
    x = 8
    for part in parts:
        label = LABEL_FONT.render(part, True, "black")
        win.blit(label, (x, 12))
        x += label.get_width() + 18

def draw(win, targets, particles, elapsed_time, score, targets_pressed, misses, lives,
         high_score, level, combo, shake_offset):
    win.fill(BG_COLOR)

    ox, oy = shake_offset
    render_surface = win
    for target in targets:
        target.x += ox
        target.y += oy
        target.draw(render_surface)
        target.x -= ox
        target.y -= oy

    for p in particles:
        p.x += ox
        p.y += oy
        p.draw(render_surface)
        p.x -= ox
        p.y -= oy

    draw_top_bar(win, elapsed_time, score, targets_pressed, misses, lives, high_score, level, combo)
    pygame.display.update()

def draw_pause_overlay(win):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    win.blit(overlay, (0, 0))
    label = MENU_FONT.render("PAUSED", True, "white")
    hint = SMALL_FONT.render("Press P to resume", True, "yellow")
    win.blit(label, (get_middle(label), HEIGHT // 2 - 40))
    win.blit(hint, (get_middle(hint), HEIGHT // 2 + 10))
    pygame.display.update()

def end_screen(win, elapsed_time, score, targets_pressed, clicks, high_score, stats):
    win.fill(BG_COLOR)

    speed = round(targets_pressed / elapsed_time, 1) if elapsed_time > 0 else 0
    accuracy = round((targets_pressed / clicks) * 100, 1) if clicks > 0 else 0

    labels = [
        LABEL_FONT.render("Game Over!", True, "white"),
        LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", True, "white"),
        LABEL_FONT.render(f"Score: {score}", True, "white"),
        LABEL_FONT.render(f"Hits: {targets_pressed}", True, "white"),
        LABEL_FONT.render(f"Speed: {speed} t/s", True, "white"),
        LABEL_FONT.render(f"Accuracy: {accuracy}%", True, "white"),
        LABEL_FONT.render(f"High Score: {high_score}", True, "gold"),
        LABEL_FONT.render(f"Best Accuracy: {stats['best_accuracy']}%", True, "cyan"),
        LABEL_FONT.render(f"Best Speed: {stats['best_speed']} t/s", True, "cyan"),
        LABEL_FONT.render(f"Games Played: {stats['games_played']}", True, "white"),
        LABEL_FONT.render("Press R to Restart", True, "yellow"),
        LABEL_FONT.render("Press ESC to Quit", True, "red"),
    ]

    y = 90
    for label in labels:
        win.blit(label, (get_middle(label), y))
        y += 40

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

def start_menu(win, stats):
    """Returns the chosen difficulty name, or exits the program."""
    difficulty_names = list(DIFFICULTIES.keys())
    selected = 1 

    while True:
        win.fill(BG_COLOR)

        title = TITLE_FONT.render("AIM TRAINER", True, "white")
        start = MENU_FONT.render("Press SPACE to Start", True, "green")
        change = SMALL_FONT.render("<- / -> to change difficulty", True, "white")
        diff_label = MENU_FONT.render(difficulty_names[selected], True, "orange")
        quit_game = MENU_FONT.render("Press ESC to Quit", True, "red")
        high = MENU_FONT.render(
            f"High Score: {stats['high_scores'][difficulty_names[selected]]}",
            True,
            "yellow",
        )

        win.blit(title, (get_middle(title), 100))
        win.blit(diff_label, (get_middle(diff_label), 210))
        win.blit(change, (get_middle(change), 255))
        win.blit(start, (get_middle(start), 320))
        win.blit(quit_game, (get_middle(quit_game), 380))
        win.blit(high, (get_middle(high), 450))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return difficulty_names[selected]
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                elif event.key == pygame.K_LEFT:
                    selected = (selected - 1) % len(difficulty_names)
                elif event.key == pygame.K_RIGHT:
                    selected = (selected + 1) % len(difficulty_names)

def main():
    stats = load_stats()
    clock = pygame.time.Clock()

    difficulty_name = start_menu(WINDOW, stats)
    settings = DIFFICULTIES[difficulty_name]

    LIVES = settings["lives"]
    MAX_SIZE = settings["max_size"]
    growth_rate = settings["growth"]
    current_spawn_rate = settings["increment"]

    pygame.time.set_timer(TARGET_EVENT, current_spawn_rate)

    targets = []
    particles = []
    high_score = stats["high_scores"][difficulty_name]

    start_time = time.time()
    paused_total = 0.0
    pause_started_at = None
    paused = False

    last_level = 0
    targets_pressed = 0
    clicks = 0
    misses = 0
    score = 0
    combo = 0
    shake_timer = 0.0
    shake_offset = (0, 0)

    run = True
    while run:
        dt = clock.tick(60) / 1000 

        if paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    paused = False
                    paused_total += time.time() - pause_started_at
            draw_pause_overlay(WINDOW)
            continue

        elapsed_time = time.time() - start_time - paused_total
        level = int(elapsed_time // DIFFICULTY_INTERVAL)

        if level > last_level:
            last_level = level
            current_spawn_rate = max(MIN_TARGET_INCREMENT, current_spawn_rate - DIFFICULTY_STEP)
            pygame.time.set_timer(TARGET_EVENT, current_spawn_rate)
            growth_rate += 0.03

        click = False
        mouse_pos = (0, 0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                paused = True
                pause_started_at = time.time()

            elif event.type == TARGET_EVENT:
                x = random.randint(TARGET_PADDING + MAX_SIZE, WIDTH - TARGET_PADDING - MAX_SIZE)
                y = random.randint(
                    TOP_BAR_HEIGHT + TARGET_PADDING + MAX_SIZE, HEIGHT - TARGET_PADDING - MAX_SIZE
                )

                roll = random.random()
                if level >= 1 and roll < 0.06:
                    target_type = "bomb"
                elif level >= 1 and roll < 0.20:
                    target_type = "bonus"
                else:
                    target_type = "normal"

                moving = level >= 2 and random.random() < 0.5

                targets.append(Target(x, y, MAX_SIZE, growth_rate, target_type, moving))

            elif event.type == pygame.MOUSEBUTTONDOWN:
                click = True
                clicks += 1
                mouse_pos = pygame.mouse.get_pos()

        bounds = (TARGET_PADDING, TOP_BAR_HEIGHT + TARGET_PADDING, WIDTH - TARGET_PADDING, HEIGHT - TARGET_PADDING)

        hit_this_click = False
        for target in targets[:]:
            target.update(dt, bounds)

            if target.size <= 0:
                targets.remove(target)
                if target.type != "bomb":
                    misses += 1
                    combo = 0
                continue

            if click and not hit_this_click and target.collide(*mouse_pos):
                targets.remove(target)
                hit_this_click = True  

                if target.type == "bomb":
                    misses += 1
                    combo = 0
                    shake_timer = 0.25
                else:
                    combo += 1
                    multiplier = 1 + combo // 5
                    score += target.points * multiplier
                    targets_pressed += 1
                    color = target.color_1
                    spawn_burst(particles, target.x, target.y, color)

        for p in particles[:]:
            p.update(dt)
            if p.life <= 0:
                particles.remove(p)

        if shake_timer > 0:
            shake_timer -= dt
            shake_offset = (random.randint(-6, 6), random.randint(-6, 6))
        else:
            shake_offset = (0, 0)

        if misses >= LIVES:
            accuracy = round((targets_pressed / clicks) * 100, 1) if clicks > 0 else 0
            speed = round(targets_pressed / elapsed_time, 1) if elapsed_time > 0 else 0

            if score > high_score:
                high_score = score
                stats["high_scores"][difficulty_name] = high_score
            stats["best_accuracy"] = max(stats["best_accuracy"], accuracy)
            stats["best_speed"] = max(stats["best_speed"], speed)
            stats["games_played"] += 1
            save_stats(stats)

            return end_screen(WINDOW, elapsed_time, score, targets_pressed, clicks, high_score, stats)

        draw(WINDOW, targets, particles, elapsed_time, score, targets_pressed, misses, LIVES,
             high_score, last_level, combo, shake_offset)

    pygame.quit()
    return False

if __name__ == "__main__":
    while True:
        if not main():
            break