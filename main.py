import pygame
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

class StateID(Enum):
    MENU = auto()
    PLAYING = auto()
    GAME_OVER = auto()

class MenuState:
    def __init__(self, game):
        self.game = game

    def events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.game.change_state(StateID.PLAYING)

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((0,0,255))
        self.draw_message(screen)
        
    def draw_message(self, screen):
        play_image = FONT.render('PRESS ENTER TO START', True, (255,255,255))
        screen.blit(play_image, ((WIDTH-play_image.get_width())//2, (HEIGHT-play_image.get_height())//2 - 16))
        quit_image = FONT.render('PRESS Q TO QUIT', True, (255,255,255))
        screen.blit(quit_image, ((WIDTH-quit_image.get_width())//2, (HEIGHT-quit_image.get_height())//2 + 16))

class PlayState:
    def __init__(self, game):
        self.game = game
        self.score = 0
        self.high_score = 0

        self.snake = Snake()

        self.move_timer = 0.0
        self.STEP_INTERVAL = 0.1

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

    def draw(self, screen): 
        # screen.fill((0, 255, 0))
        screen.fill((31,31,31))
        game_rect = pygame.Rect(0, TOP_PANEL_HEIGHT, WIDTH, GRID_HEIGHT * CELL_SIZE)
        pygame.draw.rect(screen, (0, 0, 0), game_rect)

        self.draw_grid(screen)
        self.snake.draw(screen)
        self.draw_ui(screen)

    def draw_grid(self, screen):
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(screen, (63,63,63), (x, TOP_PANEL_HEIGHT), (x, HEIGHT - BOTTOM_PANEL_HEIGHT))

        for y in range(TOP_PANEL_HEIGHT, HEIGHT - BOTTOM_PANEL_HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, (63,63,63), (0, y), (WIDTH, y))

    def draw_ui(self, screen):
        score_surface = FONT.render(f"SCORE: {self.score}", True, (255, 255, 255))
        screen.blit(score_surface, (16, (TOP_PANEL_HEIGHT - score_surface.get_height()) // 2))

        high_score_surface = FONT.render(f"HIGH SCORE: {self.high_score}", True, (255, 255, 255))
        screen.blit(high_score_surface, (16, HEIGHT - BOTTOM_PANEL_HEIGHT + (BOTTOM_PANEL_HEIGHT - high_score_surface.get_height()) // 2))

class GameOverState:
    def __init__(self, game):
        self.game = game

    def events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.game.change_state(StateID.PLAYING)
            if event.key == pygame.K_ESCAPE:
                self.game.change_state(StateID.MENU)

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((255,0,0))
        self.draw_message(screen)

    def draw_message(self, screen):
        restart_image = FONT.render('PRESS R TO RESTART', True, (255,255,255))
        screen.blit(restart_image, ((WIDTH-restart_image.get_width())//2, (HEIGHT-restart_image.get_height())//2 - 16))
        escape_image = FONT.render('ESC TO RETURN TO MENU', True, (255,255,255))
        screen.blit(escape_image, ((WIDTH-escape_image.get_width())//2, (HEIGHT-escape_image.get_height())//2 + 16))

class Snake:
    def __init__(self):
        # load head, body, tail
        # pygame.mixer.Sound cruch_sound
        self.reset()

    def reset(self):
        self.body = [Vector2(5, 5), Vector2(4, 5), Vector2(3, 5)]
        self.direction = Vector2(1,0)
        self.next_direction = Vector2(1,0)

        self.new_block = False

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

    def update(self):
        if self.new_block:
            pass # body increase logic, and in the end self.new_block = False
        else:
            pass # move ?

    def add_block(self):
        self.new_block = True

    # def play_crunch_sound(self):
    #     self.crunch_sound.play()

    def move(self):
        self.direction = self.next_direction

        new_head = self.body[0] + self.direction
        self.body.insert(0, new_head)
        self.body.pop()

    def draw(self, screen):
        for segment in self.body:
            rect = pygame.Rect(
                segment.x * CELL_SIZE,
                TOP_PANEL_HEIGHT + (segment.y * CELL_SIZE), CELL_SIZE, CELL_SIZE
            )
            pygame.draw.rect(screen, (0, 255, 0), rect)

            # more complex draw logic for images

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('snake')
        self.clock = pygame.time.Clock()

        self.states = {
            StateID.MENU: MenuState(self),
            StateID.PLAYING: PlayState(self),
            StateID.GAME_OVER: GameOverState(self)
        }
        # self.current_state = self.states[StateID.MENU]
        self.current_state = self.states[StateID.PLAYING]

        self.running = True

    def change_state(self, new_state_id):
        self.current_state = self.states[new_state_id]


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