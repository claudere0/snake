import pygame
from random import randint
from pygame.math import Vector2
from .constants import TOP_PANEL_HEIGHT, GRID_HEIGHT, GRID_WIDTH, CELL_SIZE

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

    def move(self):
        self.direction = self.next_direction

        new_head = self.body[0] + self.direction

        new_head.x %= GRID_WIDTH
        new_head.y %= GRID_HEIGHT

        self.body.insert(0, new_head)

        if self.grow_pending:
            self.grow_pending = False
        else:
            self.body.pop()

    def draw(self, screen, game):
        if game.graphics_mode == "SPRITES":
            self.draw_sprites(screen, game)
        else:
            self.draw_minimal(screen, game.get_theme())

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

            else: # body
                prev_seg = self.fix_teleport_vector(self.body[i - 1] - segment)
                next_seg = self.fix_teleport_vector(self.body[i + 1] - segment)

                if prev_seg.x == next_seg.x or prev_seg.y == next_seg.y:
                    tx, ty = (2, 0) # default segment

                else: # rotate
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

    def check_self_collision(self):
        return self.head in self.body[1:]

class Food:
    def __init__(self):
        self.pos = Vector2(0, 0)
        self.type = 'common'
        self.value = 1

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
        self.type = 'rare' if randint(1, 9) == 8 else 'common'

    def draw(self, screen, game):
        if game.graphics_mode == "SPRITES":
            self.draw_sprites(screen, game)
        else:
            self.draw_minimal(screen, game.get_theme())

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