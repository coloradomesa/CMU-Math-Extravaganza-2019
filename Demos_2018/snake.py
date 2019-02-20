#!/usr/env/python3
"""
Snake.py by Joel Cressy
Run on a raspberry pi with attached senseHAT or python environment setup with a senseHAT emulator
"""
import asyncio
import time
from sense_hat import SenseHat
from sense_emu import SenseHat as SenseEmu
from signal import pause
import random
loop = asyncio.get_event_loop()

SNAKE_BODY_COLOR = [255,255,255] # R, G, B
SNAKE_FOOD_COLOR = [255,0,0] # R, G, B

class BodyCollideException(Exception):
    """Raised when snake's head collides with its own body"""
    pass


class WallCollideException(Exception):
    """Raised when snake's head collides with play area walls"""
    pass


class BodyOutgrownException(Exception):
    """Raised when snake's body outgrows bounds of play area"""
    pass


class SnakeBody:
    """Standard snake body segment"""
    
    #these constants serve as enumerated functions which can direct the movement functions around an 8x8 grid
    UP = lambda loc: (loc[0], loc[1]-1)
    DOWN = lambda loc: (loc[0], loc[1]+1)
    LEFT = lambda loc: (loc[0]-1, loc[1])
    RIGHT = lambda loc: (loc[0]+1, loc[1])
    move_opposite = {
        UP: DOWN,
        DOWN: UP,
        LEFT: RIGHT,
        RIGHT: LEFT
    }
    move_left = {
        UP: LEFT,
        DOWN: RIGHT,
        LEFT: DOWN,
        RIGHT: UP
    }
    move_right = {
        UP: RIGHT,
        DOWN: LEFT,
        LEFT: UP,
        RIGHT: DOWN
    }
    
    def __init__(self, x=4, y=4, direction=UP):
        if x not in range(0, 8) or y not in range(0, 8):
            raise BodyOutgrownException("Unhandled: Body ({}, {}) has extended outside of the bounds of the play area and must be appended to either side of the tail".format(x, y))
        self.location = (x, y)
        self.direction = direction

    def move(self):
        """move a body segment based on its set direction"""
        self.location = self.direction(self.location)


class SnakeHead(SnakeBody):
    def __init__(self, *args, **kwargs):
        SnakeBody.__init__(self, *args, **kwargs)
        self.body = [] # list of SnakeBody

    def move(self):
        """Moves and updates the directions of the snake's body segments"""
        SnakeBody.move(self)
        for body in self.body:
            body.move()
        parent_direction = self.direction
        for body in self.body:
            new_direction = body.direction
            body.direction = parent_direction
            parent_direction = new_direction
        if self.location in [x.location for x in self.body]:
            raise BodyCollideException("Game Over, snake's head collided with its body!")
        if not all([x in range(0, 8) for x in self.location]):
            raise WallCollideException("Game Over, snake's head collided with the wall!")

    def eat_food(self):
        """grows snake's body by 1 and moves body peice in opposite direction of snake direction"""
        ref = self
        if len(self.body) > 0:
            ref = self.body[-1]
        try:
            self.body.append(
                SnakeBody(
                    self.move_opposite[ref.direction](ref.location)[0],
                    self.move_opposite[ref.direction](ref.location)[1],
                    ref.direction
                )
            )
        except BodyOutgrownException as e:
            move_direction = self.move_left
            try:
                self.body.append(
                    SnakeBody(
                        move_direction[ref.direction](ref.location)[0],
                        move_direction[ref.direction](ref.location)[1],
                        self.move_opposite[move_direction[ref.direction]]
                    )
                )
            except BodyOutgrownException as e:
                move_direction = self.move_right
                self.body.append(
                    SnakeBody(
                        move_direction[ref.direction](ref.location)[0],
                        move_direction[ref.direction](ref.location)[1],
                        self.move_opposite[move_direction[ref.direction]]
                    )
                )
                pass
            pass
                    


class SnakeGame:
    directions = { # used to translate events to enumerated functions in SnakeBody
        'up': SnakeBody.UP,
        'down': SnakeBody.DOWN,
        'left': SnakeBody.LEFT,
        'right': SnakeBody.RIGHT
    }
    GAMESPEED = 0.300 # seconds per screen update
    
    def __init__(self, hat):
        self.hat = hat
        self.gamerunning = False
        self.food = (0, 0)
        self.snake = SnakeHead()
        self._move_food()

    def reset(self):
        """Reset game state but keep running"""
        self.gamerunning = True
        self.food = (0, 0)
        self._move_food()
        self.snake = SnakeHead()

    @asyncio.coroutine # main loop is asynchronus to capture joystick inputs inbetween screen updates
    def _main_loop(self):
        while self.gamerunning:
            self._update_screen()
            yield from asyncio.sleep(self.GAMESPEED)
            try:
                self.snake.move()
            except Exception as e:
                print(e)
                print("Final length of snake: {}".format(len(self.snake.body)+1))
                self.gamerunning = False
                self.hat.show_message("GAME OVER", text_colour=[255, 0, 0])
                self.hat.show_letter('?', text_colour=[0, 0, 255])
                input("Play again? [ENTER]")
                self.reset()
            if self.snake.location == self.food:
                self.snake.eat_food()
                self._move_food()
            if len(self.snake.body) >=63:
                self.gamerunning = False
                self.hat.show_message("YOU WIN!", text_colour=[0, 255, 0])
                exit()
            
    def _update_screen(self):
        """Re-draw all pixels on the screen after clearing"""
        self.hat.clear()
        self.hat.set_pixel(self.snake.location[0], self.snake.location[1], SNAKE_BODY_COLOR[0], SNAKE_BODY_COLOR[1], SNAKE_BODY_COLOR[2])
        for body in self.snake.body:
            self.hat.set_pixel(int(body.location[0]), int(body.location[1]), SNAKE_BODY_COLOR[0], SNAKE_BODY_COLOR[1], SNAKE_BODY_COLOR[2])
        self.hat.set_pixel(self.food[0], self.food[1], SNAKE_FOOD_COLOR[0], SNAKE_FOOD_COLOR[1], SNAKE_FOOD_COLOR[2])

    def run(self):
        """Run the game"""
        self.hat.show_letter('3')
        time.sleep(0.5)
        self.hat.show_letter('2')
        time.sleep(0.5)
        self.hat.show_letter('1')
        time.sleep(0.5)
        self._update_screen()
        self.hat.stick.direction_any = self.move_event
        self.gamerunning = True
        loop.run_until_complete(self._main_loop())

    def _move_food(self):
        """Randomly select new food location"""
        while True:
            self.food = (random.choice(range(0,8)), random.choice(range(0, 8)))
            if self.food != self.snake.location and self.food not in [x.location for x in self.snake.body]:
                break

    def move_event(self, event):
        """Register this function as an event handler for all joystick directions"""
        if event.action in ('pressed', 'held'):
            self.snake.direction = self.directions.get(event.direction, self.snake.direction)

if __name__ == "__main__":
    game = SnakeGame(SenseHat()) # Change SenseHat() to SenseEmu() to switch between physical and simulated
    game.run()
