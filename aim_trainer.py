import math
import random
import time
import pygame

pygame.init()

WIDTH, HEIGHT = 900, 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aim Trainer")

TARGET_INCREMENT = 400
MIN_TARGET_INCREMENT = 150      
DIFFICULTY_INTERVAL = 15        
DIFFICULTY_STEP = 25       
TARGET_EVENT = pygame.USEREVENT
TARGET_PADDING = 30
BG_COLOR = (0, 25, 40)
LIVES = 7
TOP_BAR_HEIGHT = 50
LABEL_FONT = pygame.font.SysFont("comicsans", 24)
TITLE_FONT = pygame.font.SysFont("comicsans", 60, bold=True)
MENU_FONT = pygame.font.SysFont("comicsans", 35)

class Target:

    MAX_SIZE = 40
    GROWTH_RATE = 0.2
    COLOR_1 = "red"
    COLOR_2 = "white"

    def __init__(self, x, y):

        self.x = x
        self.y = y
        self.size = 0
        self.grow = True
        self.growth_rate = Target.GROWTH_RATE

    def update(self):

        if self.size >= self.MAX_SIZE:
            self.grow = False

        if self.grow:
            self.size += self.growth_rate

        else:
            self.size -= self.growth_rate

    def draw(self, win):

        pygame.draw.circle(win, self.COLOR_2, (self.x, self.y), int(self.size))
        pygame.draw.circle(win, self.COLOR_1, (self.x, self.y), int(self.size * 0.8))
        pygame.draw.circle(win, self.COLOR_2, (self.x, self.y), int(self.size * 0.6))
        pygame.draw.circle(win, self.COLOR_1, (self.x, self.y), int(self.size * 0.4))

    def collide(self, x, y):

        distance = math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
        return distance <= self.size

def format_time(secs):

    minutes = int(secs // 60)
    seconds = int(secs % 60)
    milliseconds = int((secs * 10) % 10)

    return f"{minutes:02d}:{seconds:02d}.{milliseconds}"

def get_middle(surface):

    return (WIDTH - surface.get_width()) // 2

def load_high_score():

    try:

        with open("highscore.txt", "r") as file:
            return int(file.read())
        
    except:

        return 0

def save_high_score(score):

    with open("highscore.txt", "w") as file:
        file.write(str(score))

def draw_top_bar(win, elapsed_time, targets_pressed, misses, high_score, level):

    pygame.draw.rect(win, "grey", (0, 0, WIDTH, TOP_BAR_HEIGHT))

    speed = round(targets_pressed / elapsed_time, 1) if elapsed_time > 0 else 0

    time_label = LABEL_FONT.render(
        f"Time: {format_time(elapsed_time)}", True, "black"
    )
    speed_label = LABEL_FONT.render(
        f"Speed: {speed} t/s", True, "black"
    )
    hits_label = LABEL_FONT.render(
        f"Hits: {targets_pressed}", True, "black"
    )
    lives_label = LABEL_FONT.render(
        f"Lives: {LIVES - misses}", True, "black"
    )
    high_label = LABEL_FONT.render(
    f"High Score: {high_score}", True, "black"
    )
    level_label = LABEL_FONT.render(
    f"Level: {level + 1}", True, "black"
    )

    win.blit(time_label, (10, 10))
    win.blit(speed_label, (215, 10))
    win.blit(hits_label, (445, 10))
    win.blit(lives_label, (645, 10))
    win.blit(high_label, (730, 10))
    win.blit(level_label, (560, 10))

def draw(win, targets, elapsed_time, targets_pressed, misses, high_score, level):

    win.fill(BG_COLOR)

    for target in targets:
        target.draw(win)

    draw_top_bar(win, elapsed_time, targets_pressed, misses, high_score, level)

    pygame.display.update()

def end_screen(win, elapsed_time, targets_pressed, clicks, high_score):

    win.fill(BG_COLOR)

    speed = round(targets_pressed / elapsed_time, 1) if elapsed_time > 0 else 0
    accuracy = round((targets_pressed / clicks) * 100, 1) if clicks > 0 else 0

    labels = [
        LABEL_FONT.render(f"Game Over!", True, "white"),
        LABEL_FONT.render(f"Time: {format_time(elapsed_time)}", True, "white"),
        LABEL_FONT.render(f"Hits: {targets_pressed}", True, "white"),
        LABEL_FONT.render(f"Speed: {speed} t/s", True, "white"),
        LABEL_FONT.render(f"Accuracy: {accuracy}%", True, "white"),
        LABEL_FONT.render(f"High Score: {high_score}", True, "gold"),
        LABEL_FONT.render("Press R to Restart", True, "yellow"),
        LABEL_FONT.render("Press ESC to Quit", True, "red"),
        
    ]

    y = 120
    for label in labels:

        win.blit(label, (get_middle(label), y))
        y += 50

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

   
def start_menu(win):

    while True:

        win.fill(BG_COLOR)

        title = TITLE_FONT.render("AIM TRAINER", True, "white")
        start = MENU_FONT.render("Press SPACE to Start", True, "green")
        quit_game = MENU_FONT.render("Press ESC to Quit", True, "red")
        high = MENU_FONT.render(
            f"High Score: {load_high_score()}",
            True,
            "yellow"
        )

        win.blit(title, (get_middle(title), 120))
        win.blit(start, (get_middle(start), 250))
        win.blit(quit_game, (get_middle(quit_game), 310))
        win.blit(high, (get_middle(high), 390))

        pygame.display.update()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:

                    return

                elif event.key == pygame.K_ESCAPE:

                    pygame.quit()
                    exit()

def main():

    run = True
    clock = pygame.time.Clock()
    start_menu(WINDOW)

    pygame.time.set_timer(TARGET_EVENT, TARGET_INCREMENT)
    Target.GROWTH_RATE = 0.2

    targets = []
    high_score = load_high_score()

    start_time = time.time()
    current_spawn_rate = TARGET_INCREMENT
    last_level = 0
    targets_pressed = 0
    clicks = 0
    misses = 0

    while run:

        clock.tick(60)

        elapsed_time = time.time() - start_time

        level = int(elapsed_time // DIFFICULTY_INTERVAL)

        if level > last_level:


            last_level = level

            current_spawn_rate = max(
                MIN_TARGET_INCREMENT,
                current_spawn_rate - DIFFICULTY_STEP
            )

            pygame.time.set_timer(TARGET_EVENT, current_spawn_rate)

            Target.GROWTH_RATE += 0.03

        click = False
        mouse_pos = (0, 0)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                run = False

            elif event.type == TARGET_EVENT:

                x = random.randint(
                    TARGET_PADDING + Target.MAX_SIZE,
                    WIDTH - TARGET_PADDING - Target.MAX_SIZE,
                )
                y = random.randint(
                    TOP_BAR_HEIGHT + TARGET_PADDING + Target.MAX_SIZE,
                    HEIGHT - TARGET_PADDING - Target.MAX_SIZE,
                )

                targets.append(Target(x, y))

            elif event.type == pygame.MOUSEBUTTONDOWN:

                click = True
                clicks += 1
                mouse_pos = pygame.mouse.get_pos()

        for target in targets[:]:

            target.update()

            if target.size <= 0:

                targets.remove(target)
                misses += 1
                continue

            if click and target.collide(*mouse_pos):

                targets.remove(target)
                targets_pressed += 1

        if misses >= LIVES:

            if targets_pressed > high_score:

                high_score = targets_pressed
                save_high_score(high_score)

            return end_screen(WINDOW, elapsed_time, targets_pressed, clicks, high_score)
           

        draw(WINDOW, targets, elapsed_time, targets_pressed, misses, high_score, last_level)

    pygame.quit()

if __name__ == "__main__":

    while True:

        if not main():

            break

    