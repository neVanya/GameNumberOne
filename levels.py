from settings import *

# Система уровней
LEVELS = {
    1: {
        "name": "Начальный уровень",
        "platforms": [
            (0, HEIGHT - 40, WIDTH, 40, "ground"),
            (100, 450, 200, 20, "ground"),
            (400, 350, 150, 20, "moving"),
            (200, 250, 200, 20, "bouncing"),
        ],
        "coins": [
            (150, 400, 10, "normal"),
            (450, 300, 10, "normal"),
            (250, 200, 10, "silver"),
        ],
        "enemies": [
            (300, 400, "patrol"),
        ],
        "player_start": (100, 400),
        "background": "sky",
        "required_score": 20,
    },

    2: {
        "name": "Лесная зона",
        "platforms": [
            (0, HEIGHT - 40, WIDTH, 40, "ground"),
            (50, 450, 150, 20, "ground"),
            (300, 400, 120, 20, "moving"),
            (500, 350, 100, 20, "ground"),
            (200, 300, 80, 20, "bouncing"),
            (400, 250, 150, 20, "ground"),
            (100, 200, 100, 20, "moving"),
        ],
        "coins": [
            (180, 420, 10, "normal"),
            (350, 380, 10, "normal"),
            (550, 330, 10, "silver"),
            (240, 280, 10, "normal"),
            (450, 230, 50, "gold"),
        ],
        "enemies": [
            (200, 400, "patrol"),
            (450, 350, "chaser"),
        ],
        "player_start": (50, 400),
        "background": "forest",
        "required_score": 80,
    },

    3: {
        "name": "Опасная территория",
        "platforms": [
            (0, HEIGHT - 40, WIDTH, 40, "ground"),
            (100, 450, 80, 20, "ground"),
            (250, 420, 80, 20, "moving"),
            (400, 400, 80, 20, "ground"),
            (550, 380, 80, 20, "moving"),
            (200, 320, 100, 20, "ground"),
            (400, 300, 80, 20, "bouncing"),
            (100, 250, 80, 20, "ground"),
            (300, 200, 120, 20, "moving"),
        ],
        "coins": [
            (140, 430, 10, "normal"),
            (290, 400, 10, "silver"),
            (440, 380, 10, "normal"),
            (590, 360, 10, "normal"),
            (240, 300, 10, "normal"),
            (440, 280, 10, "silver"),
            (140, 230, 50, "gold"),
            (350, 180, 10, "normal"),
        ],
        "enemies": [
            (300, 400, "patrol"),
            (150, 320, "chaser"),
            (500, 200, "shooter"),
        ],
        "player_start": (100, 400),
        "background": "danger",
        "required_score": 150,
    },
}

# Фоны для уровней
BACKGROUNDS = {
    "sky": SKY_BLUE,
    "forest": (34, 139, 34),
    "danger": (139, 0, 0),
}


def get_level_data(level_num):
    return LEVELS.get(level_num, LEVELS[1])


def get_background_color(bg_name):
    return BACKGROUNDS.get(bg_name, SKY_BLUE)