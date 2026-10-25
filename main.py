
import asyncio
import random
import pygame

# Game settings
CELL = 40
COLS, ROWS = 30, 17
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL

SNAKE_COLOR = (144, 238, 144)
FOOD_COLOR = (255, 50, 50)
BG_COLOR = (0, 0, 0)
TEXT_COLOR = (255, 255, 255)

SPEED = 100
FOOD_LIFETIME = 5000
FOOD_PROB = 0.04


def create_food(snake, foods):
    occupied = set(snake)
    occupied.update(food["pos"] for food in foods)

    available = [
        (x, y)
        for x in range(COLS)
        for y in range(ROWS)
        if (x, y) not in occupied
    ]

    if available:
        return {
            "pos": random.choice(available),
            "time": pygame.time.get_ticks()
        }
    return None


def reset_game():
    snake = [(5, 5)]
    direction = (1, 0)
    foods = []
    score = 1
    growth = 0
    game_over = False
    last_move = pygame.time.get_ticks()

    return snake, direction, foods, score, growth, game_over, last_move


async def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game")

    font = pygame.font.SysFont("Arial", 28)
    big_font = pygame.font.SysFont("Arial", 55, bold=True)

    snake, direction, foods, score, growth, game_over, last_move = (
        reset_game()
    )

    running = True

    while running:
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_RETURN:
                    (
                        snake, direction, foods, score,
                        growth, game_over, last_move
                    ) = reset_game()

                elif event.key == pygame.K_SPACE and not game_over:
                    growth += 1

                elif not game_over:
                    directions = {
                        pygame.K_LEFT: (-1, 0),
                        pygame.K_RIGHT: (1, 0),
                        pygame.K_UP: (0, -1),
                        pygame.K_DOWN: (0, 1)
                    }

                    if event.key in directions:
                        direction = directions[event.key]

        # Move the snake at fixed intervals
        if not game_over and now - last_move >= SPEED:
            last_move = now

            head_x, head_y = snake[0]
            dx, dy = direction
            new_head = (head_x + dx, head_y + dy)

            snake.insert(0, new_head)

            # Check whether food was eaten
            eaten = next(
                (food for food in foods
                 if food["pos"] == new_head),
                None
            )

            if eaten:
                foods.remove(eaten)
                score += 1
                growth += 1

            # Keep the tail when the snake grows
            if growth > 0:
                growth -= 1
            else:
                snake.pop()

            # Wall and self-collision detection
            x, y = new_head

            if (
                x < 0 or x >= COLS
                or y < 0 or y >= ROWS
                or new_head in snake[1:]
            ):
                game_over = True

            # Random food generation
            if not game_over and random.random() < FOOD_PROB:
                food = create_food(snake, foods)
                if food:
                    foods.append(food)

        # Remove expired food
        foods = [
            food for food in foods
            if now - food["time"] < FOOD_LIFETIME
        ]

        # Draw the game
        screen.fill(BG_COLOR)

        for x, y in snake:
            pygame.draw.rect(
                screen,
                SNAKE_COLOR,
                (x * CELL + 1, y * CELL + 1,
                 CELL - 2, CELL - 2)
            )

        for food in foods:
            x, y = food["pos"]
            pygame.draw.rect(
                screen,
                FOOD_COLOR,
                (x * CELL + 5, y * CELL + 5,
                 CELL - 10, CELL - 10)
            )

        score_text = font.render(
            f"Score: {score}", True, TEXT_COLOR
        )
        screen.blit(score_text, (10, 10))

        if game_over:
            title = big_font.render(
                f"Game Over: {score}", True, TEXT_COLOR
            )
            restart_text = font.render(
                "Press ENTER to restart", True, TEXT_COLOR
            )

            screen.blit(
                title,
                title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            )
            screen.blit(
                restart_text,
                restart_text.get_rect(
                    center=(WIDTH // 2, HEIGHT // 2 + 25)
                )
            )

        pygame.display.flip()

        # Required for Pygbag's browser event loop
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
