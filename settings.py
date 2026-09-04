import pygame

pygame.init()

WIDTH, HEIGHT = 900, 600
TOP_BAR_HEIGHT = 50
TARGET_PADDING = 30
BG_COLOR = (0, 25, 40)

DIFFICULTY_INTERVAL = 15   
DIFFICULTY_STEP = 25       
MIN_TARGET_INCREMENT = 150 

LABEL_FONT = pygame.font.SysFont("comicsans", 19)
TITLE_FONT = pygame.font.SysFont("comicsans", 56, bold=True)
MENU_FONT = pygame.font.SysFont("comicsans", 30)
SMALL_FONT = pygame.font.SysFont("comicsans", 20)
BIG_FONT = pygame.font.SysFont("comicsans", 90, bold=True)

DIFFICULTIES = {
    "Easy": {"increment": 500, "lives": 10, "max_size": 45, "growth": 0.18},
    "Normal": {"increment": 400, "lives": 7, "max_size": 40, "growth": 0.20},
    "Hard": {"increment": 300, "lives": 5, "max_size": 32, "growth": 0.28},
}

GRIDSHOT_DURATION = 60     
GRIDSHOT_TARGET_SIZE = 28 

FLICK_ROUNDS = 20
FLICK_TARGET_SIZE = 24

REACTION_ROUNDS = 20
REACTION_TARGET_SIZE = 30
REACTION_DELAY_RANGE = (0.6, 2.0)   

PRECISION_ROUNDS = 20
PRECISION_TARGET_SIZE = 14

TRACKING_DURATION = 45
TRACKING_TARGET_SIZE = 26

MOVEMENT_PATTERNS = ["bounce", "horizontal", "vertical", "circular", "zigzag", "random"]

COUNTDOWN_SECONDS = 3

STATS_FILE = "stats.json"
SETTINGS_FILE = "user_settings.json"
MAX_SESSION_HISTORY = 50