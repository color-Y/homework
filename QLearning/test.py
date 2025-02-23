import pygame
import torch
from game import SnakeGameAI, Direction, Point
from model import Linear_QNet


class Agent:
    def __init__(self):
        self.model = Linear_QNet(11, 256, 3)
        self.model.load_state_dict(torch.load("model.pth"))  # Load the trained model
        self.model.eval()  # Set the model to evaluation mode

    def get_state(self, game):
        head = game.snake[0]
        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y - 20)
        point_d = Point(head.x, head.y + 20)

        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            (dir_r and game.is_collision(point_r)) or
            (dir_l and game.is_collision(point_l)) or
            (dir_u and game.is_collision(point_u)) or
            (dir_d and game.is_collision(point_d)),
            (dir_u and game.is_collision(point_r)) or
            (dir_d and game.is_collision(point_l)) or
            (dir_l and game.is_collision(point_u)) or
            (dir_r and game.is_collision(point_d)),
            (dir_d and game.is_collision(point_r)) or
            (dir_u and game.is_collision(point_l)) or
            (dir_r and game.is_collision(point_u)) or
            (dir_l and game.is_collision(point_d)),
            dir_l, dir_r, dir_u, dir_d,
            game.food.x < game.head.x,
            game.food.x > game.head.x,
            game.food.y < game.head.y,
            game.food.y > game.head.y
        ]

        return state

    def get_action(self, state):
        state0 = torch.tensor(state, dtype=torch.float)
        prediction = self.model(state0)
        move = torch.argmax(prediction).item()
        final_move = [0, 0, 0]
        final_move[move] = 1
        return final_move


def draw_start_screen(display):
    display.fill((0, 0, 0))  # Black background
    font = pygame.font.Font('arial.ttf', 50)
    text = font.render('Press SPACE to Start', True, (255, 255, 255))  # White text
    exit_text = font.render('Press ESC to Quit', True, (255, 255, 255))  # White text for exit

    text_rect = text.get_rect(center=(display.get_width() // 2, display.get_height() // 2 - 50))
    exit_rect = exit_text.get_rect(center=(display.get_width() // 2, display.get_height() // 2 + 10))

    display.blit(text, text_rect)
    display.blit(exit_text, exit_rect)

    pygame.display.flip()


def draw_score_screen(display, score):
    display.fill((0, 0, 0))
    font = pygame.font.Font('arial.ttf', 50)

    text1 = font.render(f'Game Over! Your Score: {score}', True, (255, 255, 255))  # White text
    text2 = font.render('Press SPACE to Restart', True, (255, 255, 255))  # White text for restart
    exit_text = font.render('Press ESC to Quit', True, (255, 255, 255))  # White text for exit

    text1_rect = text1.get_rect(center=(display.get_width() // 2, display.get_height() // 2 - 20))
    text2_rect = text2.get_rect(center=(display.get_width() // 2, display.get_height() // 2 + 20))
    exit_rect = exit_text.get_rect(center=(display.get_width() // 2, display.get_height() // 2 + 70))

    display.blit(text1, text1_rect)
    display.blit(text2, text2_rect)
    display.blit(exit_text, exit_rect)

    pygame.display.flip()


def test():
    pygame.init()
    display = pygame.display.set_mode((800, 600))
    agent = Agent()
    game = SnakeGameAI()
    running = True
    game_started = False
    game_over = False
    score = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game_started and not game_over:
                        game_started = True
                    elif game_over:
                        game_over = False
                        game.reset()
                        score = 0
                if event.key == pygame.K_ESCAPE:
                    running = False

        if not game_started:
            draw_start_screen(display)
        elif game_over:
            draw_score_screen(display, score)
        else:
            state = agent.get_state(game)
            final_move = agent.get_action(state)
            reward, done, score = game.play_step(final_move)

            if done:
                game_over = True

    pygame.quit()


if __name__ == '__main__':
    test()