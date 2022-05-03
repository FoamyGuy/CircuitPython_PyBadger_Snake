import board
import displayio
import supervisor
import time
from adafruit_pybadger import pybadger
from snake_helpers import World, Snake, GameOverException

GAME_TIME_STEP = 0.5
PAUSED = False
GAME_OVER = False
LAST_BUTTON_TIME = 0.0
BUTTON_COOLDOWN = 0.1

display = board.DISPLAY
world = World(height=16, width=20)
snake = Snake(starting_location=[10, 10])
snake.grow()
snake.grow()

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
    #print(now)
    if LAST_BUTTON_TIME + BUTTON_COOLDOWN <= now:
        if not prev_btn_vals.up and cur_btn_vals.up:
            if snake.direction != snake.DIRECTION_DOWN and snake.direction != snake.DIRECTION_UP:
                LAST_BUTTON_TIME = now
                snake.direction = snake.DIRECTION_UP
        # if down button was pressed
        if not prev_btn_vals.down and cur_btn_vals.down:
            if snake.direction != snake.DIRECTION_UP and snake.direction != snake.DIRECTION_DOWN:
                LAST_BUTTON_TIME = now
                snake.direction = snake.DIRECTION_DOWN
        # if right button was pressed
        if not prev_btn_vals.right and cur_btn_vals.right:
            if snake.direction != snake.DIRECTION_LEFT and snake.direction != snake.DIRECTION_RIGHT:
                LAST_BUTTON_TIME = now
                snake.direction = snake.DIRECTION_RIGHT
        # if left button was pressed
        if not prev_btn_vals.left and cur_btn_vals.left:
            if snake.direction != snake.DIRECTION_RIGHT and snake.direction != snake.DIRECTION_LEFT:
                LAST_BUTTON_TIME = now
                snake.direction = snake.DIRECTION_LEFT
    else:
        # update the previous values
        prev_btn_vals = cur_btn_vals
        continue

    if not prev_btn_vals.start and cur_btn_vals.start:
        PAUSED = not PAUSED


    #print(f"{now} - {prev_step_time}")
    if not GAME_OVER:
        if not PAUSED:
            if now >= prev_step_time + GAME_TIME_STEP:
                try:
                    world.move_snake(snake)
                    GAME_TIME_STEP = max(.1, .6 - (.1 * (len(snake)//3)))
                    #print(f"speed = {GAME_TIME_STEP}")

                except GameOverException:
                    display.show(None)
                    print("\n\n\n\n\n")
                    print("Game Over")
                    print(f"Score: {len(snake)}\n")
                    print("Press Start\nfor code.py")
                    GAME_OVER = True

                prev_step_time = now

    else:
        if not prev_btn_vals.start and cur_btn_vals.start:
            supervisor.reload()

    # update the previous values
    prev_btn_vals = cur_btn_vals