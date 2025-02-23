import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# RGB colors
WHITE = (255, 255, 255)
RED = (150, 0, 0)
RED2 = (255, 0, 0)
BLACK = (0, 0, 0)
BUTTON_COLOR = (200, 0, 0)  # Button color

BLOCK_SIZE = 20
SPEED = 50
class SnakeGameAI:
    def __init__(self, w=1000, h=800):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.direction = Direction.RIGHT
        self.head = Point(self.w / 2, self.h / 2)
        self.snake = [
            self.head,
            Point(self.head.x - BLOCK_SIZE, self.head.y),
            Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)
        ]
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self, action):
        self.frame_iteration += 1

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = event.pos
                    if self.is_exit_button_clicked(mouse_pos):
                        pygame.quit()
                        quit()

        self._move(action)  # Update the head
        self.snake.insert(0, self.head)

        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()

        self._update_ui()
        self.clock.tick(SPEED)

        return reward, game_over, self.score

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head

        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True

        if pt in self.snake[1:]:
            return True

        return False

    def _update_ui(self):
        self.display.fill(BLACK)

        # Draw the snake as squares
        for pt in self.snake:
            pygame.draw.rect(self.display, WHITE, (pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))  # Snake square

        # Draw food as a circle with two colors
        pygame.draw.circle(self.display, RED, (self.food.x + BLOCK_SIZE // 2, self.food.y + BLOCK_SIZE // 2), BLOCK_SIZE // 2)  # Outer circle
        pygame.draw.circle(self.display, RED2, (self.food.x + BLOCK_SIZE // 2, self.food.y + BLOCK_SIZE // 2), (BLOCK_SIZE // 2) - 4)  # Inner circle

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])

        pygame.display.flip()

    def draw_exit_button(self):
        button_rect = pygame.Rect(self.w // 2 - 70, self.h // 2 + 40, 140, 50)  # Centered below the score
        pygame.draw.rect(self.display, BUTTON_COLOR, button_rect)
        text = font.render("Exit", True, WHITE)
        text_rect = text.get_rect(center=button_rect.center)
        self.display.blit(text, text_rect)

    def is_exit_button_clicked(self, mouse_pos):
        button_rect = pygame.Rect(self.w // 2 - 70, self.h // 2 + 40, 140, 50)  # Same position as in draw_exit_button
        return button_rect.collidepoint(mouse_pos)

    def _move(self, action):
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]
        else:
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)

def draw_start_screen(display):
    display.fill(BLACK)
    font = pygame.font.Font('arial.ttf', 50)
    text = font.render('Press SPACE to Start', True, WHITE)  # White text
    text_rect = text.get_rect(center=(display.get_width() // 2, display.get_height() // 2 - 50))
    display.blit(text, text_rect)

    # Draw exit button
    button_rect = pygame.Rect(display.get_width() // 2 - 70, display.get_height() // 2 + 10, 140, 50)
    pygame.draw.rect(display, BUTTON_COLOR, button_rect)
    exit_text = font.render("Exit", True, WHITE)
    exit_text_rect = exit_text.get_rect(center=button_rect.center)
    display.blit(exit_text, exit_text_rect)

    pygame.display.flip()

def draw_score_screen(display, score):
    display.fill(BLACK)
    font = pygame.font.Font('arial.ttf', 50)
    text1 = font.render(f'Game Over! Your Score: {score}', True, WHITE)
    text2 = font.render('Press SPACE to Restart', True, WHITE)
    text_rect1 = text1.get_rect(center=(display.get_width() // 2, display.get_height() // 2 - 20))
    text_rect2 = text2.get_rect(center=(display.get_width() // 2, display.get_height() // 2 + 20))
    display.blit(text1, text_rect1)
    display.blit(text2, text_rect2)

    # Draw exit button
    button_rect = pygame.Rect(display.get_width() // 2 - 70, display.get_height() // 2 + 50, 140, 50)
    pygame.draw.rect(display, BUTTON_COLOR, button_rect)
    exit_text = font.render("Exit", True, WHITE)
    exit_text_rect = exit_text.get_rect(center=button_rect.center)
    display.blit(exit_text, exit_text_rect)

    pygame.display.flip()

if __name__ == '__main__':
    game = SnakeGameAI()
    while True:
        draw_start_screen(game.display)
        game_started = False
        game_over = False
        while not game_started:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game_started = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        mouse_pos = event.pos
                        if game.is_exit_button_clicked(mouse_pos):
                            pygame.quit()
                            quit()

        while not game_over:
            reward, game_over, score = game.play_step([1, 0, 0])
            if game_over:
                draw_score_screen(game.display, score)
                while game_over:
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:  # Left mouse button
                                mouse_pos = event.pos
                                if game.is_exit_button_clicked(mouse_pos):
                                    pygame.quit()
                                    quit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                game.reset()
                                game_over = False