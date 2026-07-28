import pygame
from .constants import *
from .entities import Snake, Food

class MenuState:
    def __init__(self, game):
        self.game = game

    def events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.game.change_state(StateID.PLAYING)
            elif event.key == pygame.K_TAB:
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
        screen.blit(play_image, ((WIDTH - play_image.get_width()) // 2, (HEIGHT - play_image.get_height()) // 2 - 16))
        quit_image = FONT.render('PRESS Q TO QUIT', True, color)
        screen.blit(quit_image, ((WIDTH - quit_image.get_width()) // 2, (HEIGHT - quit_image.get_height()) // 2 + 16))
        settings_image = FONT.render('PRESS TAB TO SETTINGS', True, color)
        screen.blit(settings_image, ((WIDTH - settings_image.get_width()) // 2, (HEIGHT - settings_image.get_height()) // 2 + 48))

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
        self.snake.reset()
        self.food.respawn(self.snake.body)

        self.move_timer = 0.0
        self.STEP_INTERVAL = self.INITIAL_SPEED
        self.is_paused = False

    def events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.is_paused = not self.is_paused
            elif not self.is_paused:
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
        if self.snake.check_self_collision():
            self.game.change_state(StateID.GAME_OVER)

    def draw(self, screen):
        theme = self.game.get_theme()
        screen.fill(theme["ui_bg"])
        game_rect = pygame.Rect(0, TOP_PANEL_HEIGHT, WIDTH, GRID_HEIGHT * CELL_SIZE)
        pygame.draw.rect(screen, theme["bg"], game_rect)

        self.draw_border(screen, theme)
        self.food.draw(screen, self.game)
        self.snake.draw(screen, self.game)
        self.draw_ui(screen, theme)

        if self.is_paused:
            self.draw_pause(screen, theme)

    def draw_border(self, screen, theme):
        border_color = theme["ui_text"]
        pygame.draw.line(screen, border_color, (0, TOP_PANEL_HEIGHT - 3), (WIDTH, TOP_PANEL_HEIGHT - 3), 4)
        pygame.draw.line(screen, border_color, (0, HEIGHT - BOTTOM_PANEL_HEIGHT + 1), (WIDTH, HEIGHT - BOTTOM_PANEL_HEIGHT + 1), 4)

    def draw_ui(self, screen, theme):
        color = theme["ui_text"]
        score_surface = FONT.render(f"SCORE: {self.score}", True, color)
        screen.blit(score_surface, (SCORE_OFFSET_X, (TOP_PANEL_HEIGHT - score_surface.get_height()) // 2))

        high_score_surface = FONT.render(f"HIGH SCORE: {self.high_score}", True, color)
        screen.blit(high_score_surface, (SCORE_OFFSET_X, HEIGHT - BOTTOM_PANEL_HEIGHT + (BOTTOM_PANEL_HEIGHT - high_score_surface.get_height()) // 2))

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
            if event.key in (pygame.K_RETURN, pygame.K_r):
                self.game.change_state(StateID.PLAYING)
            elif event.key == pygame.K_ESCAPE:
                self.game.change_state(StateID.MENU)
            elif event.key == pygame.K_TAB:
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
        screen.blit(restart_image, ((WIDTH - restart_image.get_width()) // 2, (HEIGHT - restart_image.get_height()) // 2 - 16))

        escape_image = FONT.render('ESC TO RETURN TO MENU', True, color)
        screen.blit(escape_image, ((WIDTH - escape_image.get_width()) // 2, (HEIGHT - escape_image.get_height()) // 2 + 16))

class SettingsState:
    def __init__(self, game):
        self.game = game

    def events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state(StateID.MENU)
            elif event.key == pygame.K_RETURN:
                self.game.change_state(StateID.PLAYING)

            elif event.key == pygame.K_LEFT:
                self.game.theme_index = (self.game.theme_index - 1) % len(THEMES)
                self.game.save_current_config()

            elif event.key == pygame.K_RIGHT:
                self.game.theme_index = (self.game.theme_index + 1) % len(THEMES)
                self.game.save_current_config()

            elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                self.game.graphics_mode = "SPRITES" if self.game.graphics_mode == "MINIMAL" else "MINIMAL"
                self.game.save_current_config()

            level = None
            if pygame.K_0 <= event.key <= pygame.K_9:
                level = event.key - pygame.K_0
            elif pygame.K_KP0 <= event.key <= pygame.K_KP9:
                level = event.key - pygame.K_KP0

            if level is not None:
                self.game.set_volume_level(level)
                self.game.play_sound("crunch")

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
        vol_pct = self.game.volume_level * 11

        self.draw_text(screen, f"THEME: {theme['name']}", color, -140)
        self.draw_text(screen, f"GRAPHICS: {self.game.graphics_mode}", color, -100)
        self.draw_text(screen, f"VOLUME: {self.game.volume_level} ({vol_pct}%)", color, -60)

        self.draw_text(screen, "LEFT/RIGHT: THEME", color, -20)
        self.draw_text(screen, "UP/DOWN: GRAPHICS", color, 20)
        self.draw_text(screen, "0-9: SET VOLUME", color, 60)

        self.draw_text(screen, "ESC TO MENU", color, 100)
        snake_rect = pygame.Rect((WIDTH - 128) // 2, (HEIGHT - 32) // 2 + 140, 64, 32)
        food_rect = pygame.Rect((WIDTH - 128) // 2 + 64, (HEIGHT - 32) // 2 + 140, 64, 32)
        pygame.draw.rect(screen, theme["snake"], snake_rect)
        pygame.draw.rect(screen, theme["food_common"], food_rect)