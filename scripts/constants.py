from enum import Enum, auto

FPS = 60
FONT_NAME = 'monospace'
FONT_SIZE = 36

CELL_SIZE = 32
GRID_WIDTH = 16
GRID_HEIGHT = 12

TOP_PANEL_HEIGHT = 64
BOTTOM_PANEL_HEIGHT = 64

WIDTH = GRID_WIDTH * CELL_SIZE
HEIGHT = TOP_PANEL_HEIGHT + (GRID_HEIGHT * CELL_SIZE) + BOTTOM_PANEL_HEIGHT

THEMES = [
    {
        "name": "CLASSIC",
        "bg": (0, 0, 0),
        "snake": (0, 255, 0),
        "food_common": (255, 0, 0),
        "food_rare": (255, 255, 0),
        "ui_text": (255, 255, 255),
        "ui_bg": (0, 0, 0)
    },
    {
        "name": "TERMINAL",
        "bg": (0, 0, 0),
        "snake": (255, 255, 255),
        "food_common": (0, 255, 0),
        "food_rare": (255, 0, 0),
        "ui_text": (0, 255, 0),
        "ui_bg": (0, 0, 0)
    },
    {
        "name": "CYBERPUNK",
        "bg": (0, 0, 255),
        "snake": (255, 255, 0),
        "food_common": (255, 0, 255),
        "food_rare": (0, 255, 255),
        "ui_text": (255, 255, 255),
        "ui_bg": (255, 0, 255)
    },
    {
        "name": "ROYAL",
        "bg": (0, 0, 255),
        "snake": (255, 255, 255),
        "food_common": (255, 255, 0),
        "food_rare": (255, 0, 255),
        "ui_text": (255, 255, 255),
        "ui_bg": (0, 0, 255)
    },
    {
        "name": "AQUA WAVE",
        "bg": (0, 255, 255),
        "snake": (0, 0, 255),
        "food_common": (255, 0, 0),
        "food_rare": (255, 255, 0),
        "ui_text": (0, 0, 0),
        "ui_bg": (255, 255, 255)
    },
    {
        "name": "ICEBERG",
        "bg": (255, 255, 255),
        "snake": (0, 255, 255),
        "food_common": (0, 0, 255),
        "food_rare": (255, 0, 255),
        "ui_text": (0, 0, 255),
        "ui_bg": (255, 255, 255)
    },
    {
        "name": "TAXI",
        "bg": (255, 255, 0),
        "snake": (0, 0, 0),
        "food_common": (255, 0, 0),
        "food_rare": (255, 0, 255),
        "ui_text": (0, 0, 0),
        "ui_bg": (255, 255, 0)
    },
    {
        "name": "VOLCANO",
        "bg": (255, 0, 0),
        "snake": (0, 0, 0),
        "food_common": (255, 255, 0),
        "food_rare": (255, 255, 255),
        "ui_text": (255, 255, 0),
        "ui_bg": (0, 0, 0)
    }
]

CONFIG_FILE = "config.json"

THEME_SPRITESHEET_SIZE = 128
SCORE_OFFSET_X = 16

class StateID(Enum):
    MENU = auto()
    PLAYING = auto()
    GAME_OVER = auto()
    SETTINGS = auto()