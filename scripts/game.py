import pygame
from .constants import *
from .config_manager import *
from .assets_manager import AssetManager
from .states import MenuState, PlayState, GameOverState, SettingsState

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('snake')
        self.clock = pygame.time.Clock()

        self.assets = AssetManager()
        self.sounds = {}
        self.load_sounds()
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)

        self.config = load_config()
        self.theme_index = self.config.get("theme_index", 0)
        self.graphics_mode = self.config.get("graphics_mode", "MINIMAL")
        self.volume_level = self.config.get("volume", 2)

        self.update_volume()

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
        except FileNotFoundError:
            print("Warning: file sound/crunch.wav not found!")
            self.sounds["crunch"] = None

    def play_sound(self, sound_name):
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()

    def update_volume(self):
        float_volume = (self.volume_level * 11) / 100.0
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(float_volume)

    def set_volume_level(self, level):
        self.volume_level = level
        self.update_volume()
        self.save_current_config()

    def get_theme(self):
        return THEMES[self.theme_index]

    def save_current_config(self):
        play_state = self.states[StateID.PLAYING]
        save_config(self.theme_index, play_state.high_score, self.graphics_mode, self.volume_level)


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
