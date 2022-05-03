import random
import adafruit_imageload
from displayio import TileGrid

X = 0
Y = 1


class Snake:
    DIRECTION_UP = 0
    DIRECTION_DOWN = 1
    DIRECTION_RIGHT = 2
    DIRECTION_LEFT = 3

    def __init__(self, starting_location=[10, 10]):
        self.locations = [starting_location]
        self.direction = self.DIRECTION_UP

    def grow(self):
        if self.direction == self.DIRECTION_UP:
            new_segment = [self.tail[X], self.tail[Y]+1]
        elif self.direction == self.DIRECTION_DOWN:
            new_segment = [self.tail[X], self.tail[Y] - 1]
        elif self.direction == self.DIRECTION_LEFT:
            new_segment = [self.tail[X]+1, self.tail[Y]]
        elif self.direction == self.DIRECTION_RIGHT:
            new_segment = [self.tail[X]-1, self.tail[Y]]
        self.locations.append(new_segment)
    def get_next_tile(self):
        pass

    @property
    def size(self):
        return len(self.locations)

    def __len__(self):
        return len(self.locations)

    @property
    def head(self):
        return self.locations[0]

    @property
    def tail(self):
        return self.locations[-1]


class World(TileGrid):
    EMPTY_SPRITE_INDEX = 0
    SNAKE_SPRITE_INDEX = 1
    APPLE_SPRITE_INDEX = 2

    def __init__(self, width=20, height=16):
        self.spritesheet_bmp, self.spritesheet_palette = adafruit_imageload.load("snake_spritesheet.bmp")
        self.spritesheet_palette.make_transparent(0)
        super().__init__(bitmap=self.spritesheet_bmp,
                         pixel_shader=self.spritesheet_palette,
                         width=width, height=height,
                         tile_width=8, tile_height=8,
                         default_tile=0)

    def draw_snake(self, snake):
        for location in snake.locations:
            self[location] = self.SNAKE_SPRITE_INDEX

    def move_snake(self, snake):

        prev_loc = tuple(snake.head)
        next_loc = [prev_loc[X], prev_loc[Y]]
        if snake.direction == snake.DIRECTION_UP:
            if snake.head[Y] > 0:
                next_loc[Y] -= 1
            else:
                return

        if snake.direction == snake.DIRECTION_DOWN:
            if snake.head[Y] < self.height - 1:
                next_loc[Y] += 1
            else:
                return

        if snake.direction == snake.DIRECTION_LEFT:
            if snake.head[X] > 0:
                next_loc[X] -= 1
            else:
                return

        if snake.direction == snake.DIRECTION_RIGHT:
            if snake.head[X] < self.width - 1:
                next_loc[X] += 1
            else:
                return

        if self[tuple(next_loc)] == self.APPLE_SPRITE_INDEX:
            #print("hitting apple")
            snake.locations.insert(0, next_loc)
            self.add_apple(snake=snake)
        elif self[tuple(next_loc)] == self.SNAKE_SPRITE_INDEX:
            raise GameOverException("Game Over")
        else:
            snake.locations[0] = next_loc
            #print("moving")
            for i, location in enumerate(snake.locations):
                if i != 0:  # already did the head
                    _tmp = tuple(location)
                    snake.locations[i][X] = prev_loc[X]
                    snake.locations[i][Y] = prev_loc[Y]
                    prev_loc = _tmp

                if i == len(snake.locations) - 1:  # tail
                    self[prev_loc] = self.EMPTY_SPRITE_INDEX

        self.draw_snake(snake)

    def add_apple(self, location=None, snake=None):
        if snake is None:
            raise AttributeError("Must pass snake")
        while location is None or location in snake.locations:
            location = [random.randint(0, self.width-1), random.randint(0, self.height-1)]

        #print(f"new apple location: {location}")
        self[tuple(location)] = self.APPLE_SPRITE_INDEX


class GameOverException(Exception):
    def __init__(self, message):
        super().__init__(message)
