import pygame
import random
import numpy as np
import os
import shutil

pygame.init()

BASE_DIR = os.path.join(os.path.dirname(__file__), 'assets')

LOGO_PATH = os.path.join(BASE_DIR, 'imgs', 'Slythera_logo.png')
SNAKE_GRAPHICS_PATH = os.path.join(BASE_DIR, 'imgs', 'snake_graphics.png')
STONE_PATH = os.path.join(BASE_DIR, 'imgs', 'stone_obstacle.png')
GAME_OVER_PATH = os.path.join(BASE_DIR, 'imgs', 'game_over.png')
ARROW_ICON_PATH = os.path.join(BASE_DIR, 'imgs', 'arrow_icon.png')
FONT_PATH = os.path.join(BASE_DIR, 'fonts', 'EBGaramond-Regular.ttf')

SANDY = (150, 130, 100)
BROWN = (110, 90, 70)
EARTHY = (60, 45, 35)

BLOCK_SIZE = 40
MAX_STONES = 9
SPEED = 15

RIGHT = (1, 0)
DOWN = (0, 1)
LEFT = (-1, 0)
UP = (0, -1)

DIRECTIONS = [RIGHT, DOWN, LEFT, UP]

class SnakeGame:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.stats_height = 50
        self.display = pygame.display.set_mode((self.w, self.h + self.stats_height))
        pygame.display.set_caption('Slythera')
        pygame.display.set_icon(pygame.image.load(LOGO_PATH))
        self.clock = pygame.time.Clock()
        self.sprite_sheet = pygame.image.load(SNAKE_GRAPHICS_PATH).convert_alpha()
        self.stone_img = pygame.image.load(STONE_PATH).convert_alpha()
        self.load_sprites()
        self.reset()

    def main_menu(self):
        font_title = pygame.font.Font(FONT_PATH, 64)
        font_btn = pygame.font.Font(FONT_PATH, 36)

        logo = pygame.image.load(LOGO_PATH).convert_alpha()
        logo = pygame.transform.scale(logo, (200, 200))

        while True:
            self.display.fill(SANDY)
            title_text = font_title.render("Slythera", True, BROWN)
            self.display.blit(title_text, ((self.w - title_text.get_width()) // 2, 40))
            self.display.blit(logo, ((self.w - logo.get_width()) // 2, 130))
            new_game_rect = pygame.Rect(self.w // 2 - 100, 350, 200, 50)
            load_game_rect = pygame.Rect(self.w // 2 - 100, 420, 200, 50)

            pygame.draw.rect(self.display, BROWN, new_game_rect)
            pygame.draw.rect(self.display, BROWN, load_game_rect)

            new_game_text = font_btn.render("New Game", True, SANDY)
            load_game_text = font_btn.render("Load Game", True, SANDY)

            self.display.blit(new_game_text, (new_game_rect.centerx - new_game_text.get_width() // 2,
                                            new_game_rect.centery - new_game_text.get_height() // 2))
            self.display.blit(load_game_text, (load_game_rect.centerx - load_game_text.get_width() // 2,
                                            load_game_rect.centery - load_game_text.get_height() // 2))

            mouse_pos = pygame.mouse.get_pos()
            if new_game_rect.collidepoint(mouse_pos) or load_game_rect.collidepoint(mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if new_game_rect.collidepoint(event.pos):
                        self.delete_model()
                        return "new"
                    elif load_game_rect.collidepoint(event.pos):
                        return "load"

            self.clock.tick(30)

    def load_sprites(self):
        tile_size = 64

        def get_rect(col, row):
            return pygame.Rect(col * tile_size, row * tile_size, tile_size, tile_size)

        self.sprites = {
            "head_up": self.sprite_sheet.subsurface(get_rect(3, 0)),
            "head_right": self.sprite_sheet.subsurface(get_rect(4, 0)),
            "head_down": self.sprite_sheet.subsurface(get_rect(4, 1)),
            "head_left": self.sprite_sheet.subsurface(get_rect(3, 1)),

            "body_horizontal": self.sprite_sheet.subsurface(get_rect(1, 0)),
            "body_vertical": self.sprite_sheet.subsurface(get_rect(2, 1)),

            "tail_up": self.sprite_sheet.subsurface(get_rect(4, 3)),
            "tail_right": self.sprite_sheet.subsurface(get_rect(3, 3)),
            "tail_down": self.sprite_sheet.subsurface(get_rect(3, 2)),
            "tail_left": self.sprite_sheet.subsurface(get_rect(4, 2)),

            "turn_right_down": self.sprite_sheet.subsurface(get_rect(2, 0)),
            "turn_down_left": self.sprite_sheet.subsurface(get_rect(2, 2)),
            "turn_left_up": self.sprite_sheet.subsurface(get_rect(0, 1)),
            "turn_up_right": self.sprite_sheet.subsurface(get_rect(0, 0)),

            "apple": self.sprite_sheet.subsurface(get_rect(0, 3)),
        }

    def reset(self):
        self.direction = RIGHT
        self.head = [self.w // 2, self.h // 2]
        self.snake = [
            self.head[:],
            [self.head[0] - BLOCK_SIZE, self.head[1]],
            [self.head[0] - (2 * BLOCK_SIZE), self.head[1]]
        ]
        self.stones = []
        self.score = 0
        self.place_food()
        self.frame_iteration = 0

    def place_food(self):
        while True:
            x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            self.food = [x, y]
            if self.food not in self.snake and self.food not in getattr(self, "stones", []):
                break

    def game_over(self, image_path=GAME_OVER_PATH):
        img = pygame.image.load(image_path).convert_alpha()
        max_width = self.w // 2
        max_height = self.h // 2
        orig_width, orig_height = img.get_size()

        scale = min(max_width / orig_width, max_height / orig_height)
        new_width = int(orig_width * scale)
        new_height = int(orig_height * scale)

        img = pygame.transform.scale(img, (new_width, new_height))
        x = (self.w - new_width) // 2
        y = (self.h - new_height) // 2

        self.display.blit(img, (x, y))
        pygame.display.flip()

    def delete_model(self):
        model_dir = os.path.join(os.path.dirname(__file__), 'models')
        if os.path.exists(model_dir):
            for filename in os.listdir(model_dir):
                file_path = os.path.join(model_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")

    def step(self, action, game_number=0, record=0):
        self.frame_iteration += 1
        self.agent_game_number = game_number
        self.agent_record = record

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0, True, 'quit'
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if hasattr(self, 'arrow_button_rect') and self.arrow_button_rect.collidepoint(event.pos):
                        return 0, True, 'menu'
                    else:
                        grid_x = (event.pos[0] // BLOCK_SIZE) * BLOCK_SIZE
                        grid_y = (event.pos[1] // BLOCK_SIZE) * BLOCK_SIZE
                        if grid_y < self.h:
                            if [grid_x, grid_y] not in self.snake and [grid_x, grid_y] != self.food:
                                if [grid_x, grid_y] not in self.stones:
                                    if len(self.stones) < MAX_STONES:
                                        self.stones.append([grid_x, grid_y])

        self.move(action)
        self.snake.insert(0, self.head[:])

        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            self.render(game_number, record)
            self.game_over()
            return -10, True, self.score

        reward = 0
        if self.head == self.food:
            self.score += 1
            reward = 10
            self.place_food()
        else:
            self.snake.pop()

        self.render(game_number, record)
        return reward, False, self.score

    def move(self, action):
        idx = DIRECTIONS.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = self.direction
        elif np.array_equal(action, [0, 1, 0]):
            new_dir = DIRECTIONS[(idx + 1) % 4]
        else:
            new_dir = DIRECTIONS[(idx - 1) % 4]

        self.direction = new_dir
        x, y = self.head
        dx, dy = self.direction
        self.head = [x + dx * BLOCK_SIZE, y + dy * BLOCK_SIZE]

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        if pt in self.snake[1:] or pt in getattr(self, "stones", []):
            return True
        return not (0 <= pt[0] < self.w and 0 <= pt[1] < self.h)

    def show_stats(self, game_number, record):
        pygame.draw.rect(
            self.display,
            EARTHY,
            pygame.Rect(0, self.h, self.w, self.stats_height)
        )

        font = pygame.font.Font(FONT_PATH, 28)
        padding_top = 5
        padding_between = 10
        start_x = 10
        text_y = self.h + padding_top

        game_text = font.render(f"Game {game_number}", True, SANDY)
        score_text = font.render(f"(Score {self.score},", True, SANDY)
        record_text = font.render(f"Record {record})", True, SANDY)

        self.display.blit(game_text, (start_x, text_y))
        self.display.blit(score_text, (start_x + game_text.get_width() + padding_between, text_y))
        self.display.blit(record_text, (
            start_x + game_text.get_width() + padding_between + score_text.get_width() + padding_between,
            text_y
        ))

        arrow_size = 40
        arrow_x = self.w - arrow_size
        arrow_y = self.h + (self.stats_height - arrow_size) // 2

        if not hasattr(self, 'arrow_icon'):
            self.arrow_icon = pygame.image.load(ARROW_ICON_PATH).convert_alpha()
            self.arrow_icon = pygame.transform.scale(self.arrow_icon, (arrow_size, arrow_size))
        self.arrow_button_rect = pygame.Rect(arrow_x, arrow_y, arrow_size, arrow_size)
        self.display.blit(self.arrow_icon, (arrow_x, arrow_y))

        mouse_pos = pygame.mouse.get_pos()
        if self.arrow_button_rect.collidepoint(mouse_pos) or self.arrow_button_rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def render(self, game_number=0, record=0):
        self.display.fill(SANDY)

        pygame.draw.rect(self.display, BROWN, pygame.Rect(0, 0, self.w, self.h), 5)

        # Draw snake
        for i, pt in enumerate(self.snake):
            x, y = pt
            if y >= self.h:
                continue

            if i == 0:
                dx = x - self.snake[1][0]
                dy = y - self.snake[1][1]
                if dx > 0:
                    sprite = self.sprites["head_right"]
                elif dx < 0:
                    sprite = self.sprites["head_left"]
                elif dy > 0:
                    sprite = self.sprites["head_down"]
                else:
                    sprite = self.sprites["head_up"]
            elif i == len(self.snake) - 1:
                prev = self.snake[i - 1]
                dx = prev[0] - x
                dy = prev[1] - y
                if dx > 0:
                    sprite = self.sprites["tail_left"]
                elif dx < 0:
                    sprite = self.sprites["tail_right"]
                elif dy > 0:
                    sprite = self.sprites["tail_up"]
                else:
                    sprite = self.sprites["tail_down"]
            else:
                prev = self.snake[i - 1]
                nxt = self.snake[i + 1]
                if prev[0] == nxt[0]:
                    sprite = self.sprites["body_vertical"]
                elif prev[1] == nxt[1]:
                    sprite = self.sprites["body_horizontal"]
                else:
                    if (prev[0] < x and nxt[1] < y) or (nxt[0] < x and prev[1] < y):
                        sprite = self.sprites["turn_down_left"]
                    elif (prev[0] < x and nxt[1] > y) or (nxt[0] < x and prev[1] > y):
                        sprite = self.sprites["turn_right_down"]
                    elif (prev[0] > x and nxt[1] < y) or (nxt[0] > x and prev[1] < y):
                        sprite = self.sprites["turn_left_up"]
                    else:
                        sprite = self.sprites["turn_up_right"]

            scaled = pygame.transform.scale(sprite, (BLOCK_SIZE, BLOCK_SIZE))
            self.display.blit(scaled, (x, y))

        # Draw apple
        if self.food[1] < self.h:
            apple = pygame.transform.scale(self.sprites["apple"], (BLOCK_SIZE, BLOCK_SIZE))
            self.display.blit(apple, (self.food[0], self.food[1]))

        # Draw stones
        for stone in self.stones:
            stone_scaled = pygame.transform.scale(self.stone_img, (BLOCK_SIZE, BLOCK_SIZE))
            self.display.blit(stone_scaled, (stone[0], stone[1]))

        # Draw stats 
        self.show_stats(game_number, record)

        pygame.display.flip()
        self.clock.tick(SPEED)
