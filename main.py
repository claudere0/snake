import pygame
import json, os
from random import randint
from pygame.math import Vector2
from enum import Enum, auto
pygame.mixer.pre_init(44100,-16,2,512)
pygame.init()

FPS = 60
FONT = pygame.font.SysFont('monospace', 36)

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
        "name": "MONOCHROME",
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
        "name": "ICE",
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

def load_config():
    default_config = {"theme_index": 0, "high_score": 0, "graphics_mode": "MINIMAL"}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return default_config
    else:
        save_config(default_config["theme_index"], default_config["high_score"])
        return default_config

def save_config(theme_index, high_score, graphics_mode):
    data = {
        "theme_index": theme_index,
        "high_score": high_score,
        "graphics_mode": graphics_mode
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

class StateID(Enum):
    MENU = auto()
    PLAYING = auto()
    GAME_OVER = auto()
    SETTINGS = auto()

class MenuState:
    def __init__(self, game):
        self.game = game

    def events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.game.change_state(StateID.PLAYING)
            if event.key == pygame.K_TAB:
                self.game.change_state(StateID.SETTINGS)

    def update(self, dt):
        pass

    def draw(self, screen):
        theme = self.game.get_theme()
        screen.fill(theme["bg"])
        self.draw_message(screen, theme)
        
    def draw_message(self, screen, theme):
        color = theme["ui_text"]
        play_image = FONT.render('PRESS ENTER TO START', True, color)
        screen.blit(play_image, ((WIDTH-play_image.get_width())//2, (HEIGHT-play_image.get_height())//2 - 16))
        quit_image = FONT.render('PRESS Q TO QUIT', True, color)
        screen.blit(quit_image, ((WIDTH-quit_image.get_width())//2, (HEIGHT-quit_image.get_height())//2 + 16))
        settings_image = FONT.render('PRESS TAB TO SETTINGS', True, color)
        screen.blit(settings_image, ((WIDTH-settings_image.get_width())//2, (HEIGHT-settings_image.get_height())//2 + 48))

class PlayState:
    def __init__(self, game):
        self.game = game
        self.score = 0
        self.high_score = self.game.config.get("high_score", 0)

        self.snake = Snake()
        self.food = Food()
        self.food.respawn(self.snake.body)

        self.move_timer = 0.0
        self.INITIAL_SPEED = 0.125
        self.MIN_SPEED = 0.084
        self.SPEED_STEP = 0.0005
        
        self.STEP_INTERVAL = self.INITIAL_SPEED

        self.is_paused = False

    def reset_game(self):
        self.score = 0
        self.food.respawn(self.snake.body)
        self.snake.reset()
        self.move_timer = 0.0
        self.STEP_INTERVAL = self.INITIAL_SPEED
        self.is_paused = False

    def events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.is_paused = not self.is_paused
            if not self.is_paused:
                self.snake.handle_input(event)

    def update(self, dt):
        if self.is_paused:
            return

        self.move_timer += dt

        if self.move_timer >= self.STEP_INTERVAL:
            self.move_timer -= self.STEP_INTERVAL
            self.snake.move()
            self.check_food_collision()
            self.collision()

    def check_food_collision(self):
        if self.snake.head == self.food.pos:
            self.snake.grow()
            self.score += self.food.value

            self.game.play_sound("crunch")
            self.food.respawn(self.snake.body)

            self.STEP_INTERVAL = max(self.MIN_SPEED, self.STEP_INTERVAL - self.SPEED_STEP)

            if self.score > self.high_score:
                self.high_score = self.score
                self.game.save_current_config()

    def collision(self):
        if self.snake.check_wall_collision() or self.snake.check_self_collision():
            self.game.change_state(StateID.GAME_OVER)

    def draw(self, screen): 
        theme = self.game.get_theme()
        screen.fill(theme["ui_bg"])
        game_rect = pygame.Rect(0, TOP_PANEL_HEIGHT, WIDTH, GRID_HEIGHT * CELL_SIZE)
        pygame.draw.rect(screen, theme["bg"], game_rect)

        self.draw_grid(screen)
        self.draw_border(screen, theme)
        self.food.draw(screen, self.game)
        self.snake.draw(screen, self.game)
        self.draw_ui(screen, theme)

        if self.is_paused:
            self.draw_pause(screen, theme)

    def draw_grid(self, screen):
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(screen, (0, 0, 0), (x, TOP_PANEL_HEIGHT), (x, HEIGHT - BOTTOM_PANEL_HEIGHT))

        for y in range(TOP_PANEL_HEIGHT, HEIGHT - BOTTOM_PANEL_HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, (0, 0, 0), (0, y), (WIDTH, y))

    def draw_border(self, screen, theme):
        border_color = theme["ui_text"]
        pygame.draw.line(screen, border_color, (0, TOP_PANEL_HEIGHT - 3), (WIDTH, TOP_PANEL_HEIGHT - 3), 4)
        pygame.draw.line(screen, border_color, (0, HEIGHT - BOTTOM_PANEL_HEIGHT + 1), (WIDTH, HEIGHT - BOTTOM_PANEL_HEIGHT + 1), 4)

    def draw_ui(self, screen, theme):
        color = theme["ui_text"]
        score_surface = FONT.render(f"SCORE: {self.score}", True, color)
        screen.blit(score_surface, (16, (TOP_PANEL_HEIGHT - score_surface.get_height()) // 2))

        high_score_surface = FONT.render(f"HIGH SCORE: {self.high_score}", True, color)
        screen.blit(high_score_surface, (16, HEIGHT - BOTTOM_PANEL_HEIGHT + (BOTTOM_PANEL_HEIGHT - high_score_surface.get_height()) // 2))

    def draw_pause(self, screen, theme):
        color = theme["ui_text"]
        pause_surface = FONT.render("PAUSED", True, color)

        x = (WIDTH - pause_surface.get_width()) // 2
        y = (HEIGHT - pause_surface.get_height()) // 2
        
        screen.blit(pause_surface, (x, y))

class GameOverState:
    def __init__(self, game):
        self.game = game

    def events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_r:
                self.game.change_state(StateID.PLAYING)
            if event.key == pygame.K_ESCAPE:
                self.game.change_state(StateID.MENU)
            if event.key == pygame.K_TAB:
                self.game.change_state(StateID.SETTINGS)

    def update(self, dt):
        pass

    def draw(self, screen):
        theme = self.game.get_theme()
        screen.fill(theme["bg"])
        self.draw_message(screen, theme)

    def draw_message(self, screen, theme):
        color = theme["ui_text"]
        restart_image = FONT.render('PRESS ENTER TO RESTART', True, color)
        screen.blit(restart_image, ((WIDTH-restart_image.get_width())//2, (HEIGHT-restart_image.get_height())//2 - 16))

        escape_image = FONT.render('ESC TO RETURN TO MENU', True, color)
        screen.blit(escape_image, ((WIDTH-escape_image.get_width())//2, (HEIGHT-escape_image.get_height())//2 + 16))

class SettingsState:
    def __init__(self, game):
        self.game = game

    def events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state(StateID.MENU)
            if event.key == pygame.K_RETURN:
                self.game.change_state(StateID.PLAYING)

            if event.key == pygame.K_LEFT:
                self.game.theme_index = (self.game.theme_index - 1) % len(THEMES)
                self.game.save_current_config()

            if event.key == pygame.K_RIGHT:
                self.game.theme_index = (self.game.theme_index + 1) % len(THEMES)
                self.game.save_current_config()

            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                if self.game.graphics_mode == "MINIMAL":
                    self.game.graphics_mode = "SPRITES"
                else:
                    self.game.graphics_mode = "MINIMAL"
                self.game.save_current_config()

    def update(self, dt):
        pass

    def draw(self, screen):
        theme = self.game.get_theme()
        screen.fill(theme["bg"])
        self.draw_ui(screen, theme)
        
    def draw_text(self, screen, text, color, y_offset):
        rendered_text = FONT.render(text, True, color)
        x = (WIDTH - rendered_text.get_width()) // 2
        y = (HEIGHT - rendered_text.get_height()) // 2 + y_offset
        screen.blit(rendered_text, (x, y))

    def draw_ui(self, screen, theme):
        color = theme["ui_text"]

        self.draw_text(screen, f"THEME: {theme['name']}", color, -100)
        self.draw_text(screen, f"GRAPHICS: {self.game.graphics_mode}", color, -60)
        self.draw_text(screen, "LEFT/RIGHT: THEME", color, -20)
        self.draw_text(screen, "UP/DOWN: GRAPHICS", color, 20)
        self.draw_text(screen, "ESC TO MENU", color, 60)

        snake_rect = pygame.Rect((WIDTH - 128) // 2, (HEIGHT - 32) // 2 + 100, 64, 32)
        food_rect = pygame.Rect((WIDTH - 128) // 2 + 64, (HEIGHT - 32) // 2 + 100, 64, 32)
        pygame.draw.rect(screen, theme["snake"], snake_rect)
        pygame.draw.rect(screen, theme["food_common"], food_rect)

class Snake:
    def __init__(self):
        self.HEAD_MAP = {
            (1, 0):  (2, 1),  # right
            (0, -1): (3, 1),  # up
            (-1, 0): (0, 1),  # left
            (0, 1):  (1, 1)   # down
        }

        self.TAIL_MAP = {
            (1, 0):  (2, 3),  # right
            (0, -1): (3, 3),  # up
            (-1, 0): (0, 3),  # left
            (0, 1):  (1, 3)   # down
        }

        self.color = (0,255,0) # default snake color
        self.reset()

    def reset(self):
        self.body = [Vector2(5, 5), Vector2(4, 5), Vector2(3, 5)]
        self.direction = Vector2(1,0)
        self.next_direction = Vector2(1,0)
        self.grow_pending = False

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and self.direction.y != 1:
                self.next_direction = Vector2(0, -1)
            elif event.key == pygame.K_DOWN and self.direction.y != -1:
                self.next_direction = Vector2(0, 1)
            elif event.key == pygame.K_LEFT and self.direction.x != 1:
                self.next_direction = Vector2(-1, 0)
            elif event.key == pygame.K_RIGHT and self.direction.x != -1:
                self.next_direction = Vector2(1, 0)

    def grow(self):
        self.grow_pending = True

    # def play_crunch_sound(self):
    #     self.crunch_sound.play()

    def move(self):
        self.direction = self.next_direction

        new_head = self.body[0] + self.direction

        # if you want to block teleport, just comment next 2 lines of code, and uncomment wall collision
        new_head.x = new_head.x % GRID_WIDTH
        new_head.y = new_head.y % GRID_HEIGHT

        self.body.insert(0, new_head)

        if self.grow_pending:
            self.grow_pending = False
        else:
            self.body.pop()

    def draw(self, screen, game):
        theme = game.get_theme()

        if game.graphics_mode == "SPRITES":
            self.draw_sprites(screen, game)
        else:
            self.draw_minimal(screen, theme)

    def draw_minimal(self, screen, theme):
        for segment in self.body:
            rect = pygame.Rect(
                segment.x * CELL_SIZE,
                TOP_PANEL_HEIGHT + (segment.y * CELL_SIZE), 
                CELL_SIZE, CELL_SIZE
            )
            pygame.draw.rect(screen, theme["snake"], rect)

    def draw_sprites(self, screen, game):
        theme_idx = game.theme_index

        for i, segment in enumerate(self.body):
            rect = pygame.Rect(
                segment.x * CELL_SIZE,
                TOP_PANEL_HEIGHT + (segment.y * CELL_SIZE),
                CELL_SIZE, CELL_SIZE
            )

            if i == 0:
                dir_key = (int(self.direction.x), int(self.direction.y))
                tx, ty = self.HEAD_MAP.get(dir_key, (0, 1))

            elif i == len(self.body) - 1:
                tail_dir = self.fix_teleport_vector(self.body[i - 1] - segment)
                dir_key = (int(tail_dir.x), int(tail_dir.y))
                tx, ty = self.TAIL_MAP.get(dir_key, (0, 3))

            # body
            else:
                prev_seg = self.fix_teleport_vector(self.body[i - 1] - segment)
                next_seg = self.fix_teleport_vector(self.body[i + 1] - segment)

                # default segment
                if prev_seg.x == next_seg.x or prev_seg.y == next_seg.y:
                    tx, ty = (2, 0)

                # rotate
                else:
                    px, py = int(prev_seg.x), int(prev_seg.y)
                    nx, ny = int(next_seg.x), int(next_seg.y)

                    if (px == -1 and ny == 1) or (py == 1 and nx == -1):
                        tx, ty = (0, 2)
                    elif (px == 1 and ny == 1) or (py == 1 and nx == 1):
                        tx, ty = (1, 2)
                    elif (px == -1 and ny == -1) or (py == -1 and nx == -1):
                        tx, ty = (2, 2)
                    elif (px == 1 and ny == -1) or (py == -1 and nx == 1):
                        tx, ty = (3, 2)
                    else:
                        tx, ty = (0, 2)

            sprite = game.assets.get_tile(theme_idx, tx, ty)
            if sprite:
                screen.blit(sprite, rect)
            else:
                self.draw_minimal(screen, game.get_theme())

    def fix_teleport_vector(self, vec):
        if vec.x > 1: vec.x = -1
        elif vec.x < -1: vec.x = 1
        if vec.y > 1: vec.y = -1
        elif vec.y < -1: vec.y = 1
        return vec

    @property
    def head(self):
        return self.body[0]

    def check_wall_collision(self):
        # return not (0 <= self.head.x < GRID_WIDTH and 0 <= self.head.y < GRID_HEIGHT)
        return False

    def check_self_collision(self):
        return self.head in self.body[1:]

class Food:
    def __init__(self):
        self.pos = Vector2(0, 0)
        self.type = 'common'
        self.value = 1
        self.color = (255,0,0) if self.type == 'common' else (255,255,0)

    def respawn(self, snake_body):
        self.rarity()
        self.value = 1 if self.type == 'common' else 10
        while True:
            rx = randint(0, GRID_WIDTH - 1)
            ry = randint(0, GRID_HEIGHT - 1)
            new_pos = Vector2(rx, ry)

            if new_pos not in snake_body:
                self.pos = new_pos
                break

    def rarity(self):
        if randint(1, 9) == 8:
            self.type = 'rare'
        else:
            self.type = 'common'

    def draw(self, screen, game):
        theme = game.get_theme()

        if game.graphics_mode == "SPRITES":
            self.draw_sprites(screen, game)
        else:
            self.draw_minimal(screen, theme)

    def draw_minimal(self, screen, theme):
        color = theme["food_common"] if self.type == 'common' else theme["food_rare"]
        rect = pygame.Rect(
            self.pos.x * CELL_SIZE,
            TOP_PANEL_HEIGHT + (self.pos.y * CELL_SIZE),
            CELL_SIZE, CELL_SIZE
        )
        pygame.draw.rect(screen, color, rect)

    def draw_sprites(self, screen, game):
        tile_x = 0 if self.type == 'common' else 1
        tile_y = 0

        sprite = game.assets.get_tile(game.theme_index, tile_x, tile_y)

        if sprite:
            rect = pygame.Rect(
                self.pos.x * CELL_SIZE,
                TOP_PANEL_HEIGHT + (self.pos.y * CELL_SIZE),
                CELL_SIZE, CELL_SIZE
            )
            screen.blit(sprite, rect)
        else:
            self.draw_minimal(screen, game.get_theme())

class AssetManager:
    def __init__(self):
        self.spritesheet = None
        self.load_spritesheet()

    def load_spritesheet(self):
        path = "images/theme_spritesheet.png"
        if os.path.exists(path):
            try:
                self.spritesheet = pygame.image.load(path).convert_alpha()
                print("Spritesheet loaded successfully!")
                return
            except Exception as e:
                print(f"Error loading spritesheet: {e}")
        print("Warning: theme_spritesheet.png not found!")

    def get_tile(self, theme_index, tile_x, tile_y):
        if not self.spritesheet:
            return None

        theme_base_x = (theme_index % 4) * 128
        theme_base_y = (theme_index // 4) * 128

        pixel_x = theme_base_x + (tile_x * CELL_SIZE)
        pixel_y = theme_base_y + (tile_y * CELL_SIZE)

        tile = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        tile.blit(self.spritesheet, (0, 0), (pixel_x, pixel_y, CELL_SIZE, CELL_SIZE))
        return tile

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('snake')
        self.clock = pygame.time.Clock()

        self.assets = AssetManager()
        self.sounds = {}
        self.load_sounds()

        self.config = load_config()
        self.theme_index = self.config.get("theme_index", 0)
        self.graphics_mode = self.config.get("graphics_mode", "MINIMAL")

        self.states = {
            StateID.MENU: MenuState(self),
            StateID.PLAYING: PlayState(self),
            StateID.GAME_OVER: GameOverState(self),
            StateID.SETTINGS: SettingsState(self)
        }
        self.current_state = self.states[StateID.MENU]
        self.running = True

    def change_state(self, new_state_id):
        if new_state_id == StateID.PLAYING:
            self.states[StateID.PLAYING].reset_game()

        self.current_state = self.states[new_state_id]

    def load_sounds(self):
        try:
            self.sounds["crunch"] = pygame.mixer.Sound("sound/crunch.wav")
            self.sounds["crunch"].set_volume(0.25) 
        except FileNotFoundError:
            print("Warning: file sound/crunch.wav not found!")
            self.sounds["crunch"] = None

    def play_sound(self, sound_name):
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()

    def get_theme(self):
        return THEMES[self.theme_index]

    def save_current_config(self):
        play_state = self.states[StateID.PLAYING]
        save_config(self.theme_index, play_state.high_score, self.graphics_mode)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.running = False
            self.current_state.events(event)

    def update(self, dt):
        self.current_state.update(dt)

    def draw(self):
        self.current_state.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update(dt)
            self.draw()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()