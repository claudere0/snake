import pygame
import os
from .constants import THEME_SPRITESHEET_SIZE, CELL_SIZE

class AssetManager:
    def __init__(self):
        self.spritesheet = None
        self.sounds = {}
        
        self.load_spritesheet()
        self.load_sounds()

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

        pixel_x = (theme_index % 4) * THEME_SPRITESHEET_SIZE + (tile_x * CELL_SIZE)
        pixel_y = (theme_index // 4) * THEME_SPRITESHEET_SIZE + (tile_y * CELL_SIZE)

        return self.spritesheet.subsurface(pygame.Rect(pixel_x, pixel_y, CELL_SIZE, CELL_SIZE))

    def load_sounds(self):
        try:
            self.sounds["crunch"] = pygame.mixer.Sound("sound/crunch.wav")
        except FileNotFoundError:
            print("Warning: file sound/crunch.wav not found!")
            self.sounds["crunch"] = None

    def play_sound(self, sound_name):
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()
            
    def set_volume(self, volume):
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(volume)
