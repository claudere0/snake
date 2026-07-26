import pygame
import json, os
from random import randint
from pygame.math import Vector2
from enum import Enum, auto
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
    default_config = {"theme_index": 0, "high_score": 0}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return default_config
    return default_config

def save_config(theme_index, high_score):
    data = {
        "theme_index": theme_index,
        "high_score": high_score
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
        self.high_score = 0

        self.snake = Snake()
        self.food = Food()
        self.food.respawn(self.snake.body)

        self.move_timer = 0.0
        self.STEP_INTERVAL = 0.1

    def reset_game(self):
        self.score = 0
        self.food.respawn(self.snake.body)
        self.snake.reset()
        self.move_timer = 0.0

    def events(self, event):
        self.snake.handle_input(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.game.change_state(StateID.GAME_OVER)

    def update(self, dt):
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
            self.food.respawn(self.snake.body)

            if self.score > self.high_score:
                self.high_score = self.score

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
        self.food.draw(screen, theme)
        self.snake.draw(screen, theme)
        self.draw_ui(screen, theme)

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

    def update(self, dt):
        pass

    def draw(self, screen):
        theme = self.game.get_theme()
        screen.fill(theme["bg"])
        self.draw_message(screen, theme)
        
    def draw_message(self, screen, theme):
        color = theme["ui_text"]
        play_image = FONT.render(f"THEME: {theme['name']}", True, color)
        screen.blit(play_image, ((WIDTH - play_image.get_width()) // 2, (HEIGHT - play_image.get_height()) // 2 - 64))

        prompt_image = FONT.render('ARROWS TO CHANGE THEME', True, color)
        screen.blit(prompt_image, ((WIDTH - prompt_image.get_width()) // 2, (HEIGHT - prompt_image.get_height()) // 2 - 24))

        snake_rect = pygame.Rect((WIDTH - 128) // 2, (HEIGHT - 32) // 2 + 20, 64, 32)
        food_rect = pygame.Rect((WIDTH - 128) // 2 + 64, (HEIGHT - 32) // 2 + 20, 64, 32)
        pygame.draw.rect(screen, theme["snake"], snake_rect)
        pygame.draw.rect(screen, theme["food_common"], food_rect)

        escape_image = FONT.render('ESC TO RETURN TO MENU', True, color)
        screen.blit(escape_image, ((WIDTH - escape_image.get_width()) // 2, (HEIGHT - escape_image.get_height()) // 2 + 64))

class Snake:
    def __init__(self):
        # load head, body, tail
        # pygame.mixer.Sound cruch_sound
        self.color = (0,255,0)
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
        self.body.insert(0, new_head)

        if self.grow_pending:
            self.grow_pending = False
        else:
            self.body.pop()

    def draw(self, screen, theme):
        for segment in self.body:
            rect = pygame.Rect(
                segment.x * CELL_SIZE,
                TOP_PANEL_HEIGHT + (segment.y * CELL_SIZE), CELL_SIZE, CELL_SIZE
            )
            pygame.draw.rect(screen, theme["snake"], rect)

            # more complex draw logic for images

    @property
    def head(self):
        return self.body[0]

    def check_wall_collision(self):
        return not (0 <= self.head.x < GRID_WIDTH and 0 <= self.head.y < GRID_HEIGHT)

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

    def draw(self, screen, theme):
        color = theme["food_common"] if self.type == 'common' else theme["food_rare"]
        rect = pygame.Rect(
            self.pos.x * CELL_SIZE,
            TOP_PANEL_HEIGHT + (self.pos.y * CELL_SIZE),
            CELL_SIZE,
            CELL_SIZE
        )
        pygame.draw.rect(screen, color, rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('snake')
        self.clock = pygame.time.Clock()

        self.config = load_config()
        self.theme_index = self.config.get("theme_index", 0)

        self.states = {
            StateID.MENU: MenuState(self),
            StateID.PLAYING: PlayState(self),
            StateID.GAME_OVER: GameOverState(self),
            StateID.SETTINGS: SettingsState(self)
        }
        self.current_state = self.states[StateID.MENU]
        load_config()
        self.running = True

    def change_state(self, new_state_id):
        if new_state_id == StateID.PLAYING:
            self.states[StateID.PLAYING].reset_game()

        self.current_state = self.states[new_state_id]

    def get_theme(self):
        return THEMES[self.theme_index]

    def save_current_config(self):
        play_state = self.states[StateID.PLAYING]
        save_config(self.theme_index, play_state.high_score)

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