import board
import displayio
import supervisor
import time
from adafruit_pybadger import pybadger
from snake_helpers import World, Snake, GameOverException

STATE_TITLE = 0
STATE_PLAYING = 1
STATE_PAUSED = 2
STATE_GAME_OVER = 3

CURRENT_STATE = STATE_TITLE

GAME_TIME_STEP = 0.5
LAST_BUTTON_TIME = 0.0
BUTTON_COOLDOWN = 0.1
INITIAL_SNAKE_LEN = 3

display = board.DISPLAY

title_bmp = displayio.OnDiskBitmap("snake_splash.bmp")
title_tg = displayio.TileGrid(bitmap=title_bmp, pixel_shader=title_bmp.pixel_shader)
title_group = displayio.Group()
title_group.append(title_tg)

world = World(height=16, width=20)
snake = Snake(starting_location=[10, 10])
for i in range(INITIAL_SNAKE_LEN - 1):
    snake.grow()

world.add_apple(snake=snake)
game_group = displayio.Group()
game_group.append(world)

display.show(title_group)

world.draw_snake(snake)

prev_btn_vals = pybadger.button
prev_step_time = time.monotonic()

while True:
    now = time.monotonic()
    cur_btn_vals = pybadger.button  # update button sate

    if CURRENT_STATE == STATE_PLAYING:
        if LAST_BUTTON_TIME + BUTTON_COOLDOWN <= now:
            # if up button was pressed
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
            CURRENT_STATE = STATE_PAUSED

        # print(f"{now} - {prev_step_time}")

        if now >= prev_step_time + GAME_TIME_STEP:
            try:
                world.move_snake(snake)
                GAME_TIME_STEP = max(.1, .6 - (.1 * (len(snake) // 3)))
                print(f"speed = {GAME_TIME_STEP}")

            except GameOverException:
                display.show(None)
                print("\n\n\n\n\n")
                print("Game Over")
                print(f"Score: {len(snake) - INITIAL_SNAKE_LEN}\n")
                print("Start -> Play Again\nOther -> Badge")
                CURRENT_STATE = STATE_GAME_OVER

            prev_step_time = now

    elif CURRENT_STATE == STATE_PAUSED:
        if not prev_btn_vals.start and cur_btn_vals.start:
            CURRENT_STATE = STATE_PLAYING

    elif CURRENT_STATE == STATE_GAME_OVER:
        if not prev_btn_vals.start and cur_btn_vals.start:
            supervisor.set_next_code_file(__file__)
            supervisor.reload()
        if not prev_btn_vals.select and cur_btn_vals.select:
            supervisor.reload()
        if not prev_btn_vals.a and cur_btn_vals.a:
            supervisor.reload()
        if not prev_btn_vals.b and cur_btn_vals.b:
            supervisor.reload()

    if CURRENT_STATE == STATE_TITLE:
        if cur_btn_vals != prev_btn_vals:
            display.show(game_group)
            CURRENT_STATE = STATE_PLAYING
    # update the previous values
    prev_btn_vals = cur_btn_vals
