import board
import displayio
import time
from adafruit_pybadger import pybadger
from snake_helpers import World, Snake, GameOverException

GAME_TIME_STEP = 0.5
PAUSED = False
GAME_OVER = False

display = board.DISPLAY
world = World(height=16, width=20)
snake = Snake(starting_location=[10, 10])

world.add_apple(snake=snake)
main_group = displayio.Group()
main_group.append(world)

display.show(main_group)

world.draw_snake(snake)

prev_btn_vals = pybadger.button
prev_step_time = time.monotonic()
while True:
    now = time.monotonic()
    #print(pybadger.button)
    cur_btn_vals = pybadger.button  # update button sate
    # if up button was pressed
    if not prev_btn_vals.up and cur_btn_vals.up:
        snake.direction = snake.DIRECTION_UP
    # if down button was pressed
    if not prev_btn_vals.down and cur_btn_vals.down:
        snake.direction = snake.DIRECTION_DOWN
    # if right button was pressed
    if not prev_btn_vals.right and cur_btn_vals.right:
        snake.direction = snake.DIRECTION_RIGHT
    # if left button was pressed
    if not prev_btn_vals.left and cur_btn_vals.left:
        snake.direction = snake.DIRECTION_LEFT

    if not prev_btn_vals.start and cur_btn_vals.start:
        PAUSED = not PAUSED
    # update the previous values
    prev_btn_vals = cur_btn_vals

    #print(f"{now} - {prev_step_time}")
    if not GAME_OVER:
        if not PAUSED:
            if now >= prev_step_time + GAME_TIME_STEP:
                try:
                    world.move_snake(snake)
                except GameOverException:
                    display.show(None)
                    print("\n\n\n\n\n")
                    print("Game Over")
                    print(f"Score: {snake.size}\n")
                    print("Press Reset\nto Play Again")
                    GAME_OVER = True
                prev_step_time = now

