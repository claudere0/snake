import pygame
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
        screen.blit(play_image, ((WIDTH-play_image.get_width())/2, (HEIGHT-play_image.get_height())/2 - 16))
        quit_image = FONT.render('PRESS Q TO QUIT', True, (255,255,255))
        screen.blit(quit_image, ((WIDTH-quit_image.get_width())/2, (HEIGHT-quit_image.get_height())/2 + 16))

class PlayState:
    def __init__(self, game):
        self.game = game
        self.score = 0
        self.high_score = 0

    def events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.game.change_state(StateID.GAME_OVER)

    def update(self, dt):
        pass

    def draw(self, screen): 
        # screen.fill((0, 255, 0))
        screen.fill((31,31,31))
        game_rect = pygame.Rect(0, TOP_PANEL_HEIGHT, WIDTH, GRID_HEIGHT * CELL_SIZE)
        pygame.draw.rect(screen, (0, 0, 0), game_rect)

        self.draw_grid(screen)
        self.draw_ui(screen)

    def draw_grid(self, screen):
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(screen, (63,63,63), (x, TOP_PANEL_HEIGHT), (x, HEIGHT - BOTTOM_PANEL_HEIGHT))

        for y in range(TOP_PANEL_HEIGHT, HEIGHT - BOTTOM_PANEL_HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, (63,63,63), (0, y), (WIDTH, y))

    def draw_ui(self, screen):
        score_surface = FONT.render(f"SCORE: {self.score}", True, (255, 255, 255))
        screen.blit(score_surface, (16, (TOP_PANEL_HEIGHT - score_surface.get_height()) // 2))

        high_surface = FONT.render(f"HIGH SCORE: {self.high_score}", True, (255, 255, 255))
        screen.blit(high_surface, (16, HEIGHT - BOTTOM_PANEL_HEIGHT + (BOTTOM_PANEL_HEIGHT - high_surface.get_height()) // 2))

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
        screen.blit(restart_image, ((WIDTH-restart_image.get_width())/2, (HEIGHT-restart_image.get_height())/2 - 16))
        escape_image = FONT.render('ESC TO RETURN TO MENU', True, (255,255,255))
        screen.blit(escape_image, ((WIDTH-escape_image.get_width())/2, (HEIGHT-escape_image.get_height())/2 + 16))

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