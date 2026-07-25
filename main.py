import pygame
from enum import Enum, auto
pygame.init()

WIDTH = 512
HEIGHT = 512
FPS = 60
FONT = pygame.font.SysFont('monospace', 36)

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
        play_image = FONT.render('PRESS ENTER TO START', True, (255,255,255))
        screen.blit(play_image, ((WIDTH-play_image.get_width())/2, (HEIGHT-play_image.get_height())/2 - 16))
        quit_image = FONT.render('PRESS Q TO QUIT', True, (255,255,255))
        screen.blit(quit_image, ((WIDTH-quit_image.get_width())/2, (HEIGHT-quit_image.get_height())/2 + 16))


class PlayState:
    def __init__(self, game):
        self.game = game

    def events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.game.change_state(StateID.GAME_OVER)

    def update(self, dt):
        pass

    def draw(self, screen): screen.fill((0, 0, 0))

class GameOverState:
    def __init__(self, game):
        self.game = game

    def events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.game.change_state(StateID.PLAYING)

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((255,0,255))


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
        self.current_state = self.states[StateID.MENU]

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