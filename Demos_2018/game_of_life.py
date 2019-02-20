#!/usr/bin/env python3
"""Rules

 - Any live cell with fewer than two live neighbors dies, as if caused by underpopulation
 - Any live cell with fewer than two or three live neighbors lives on to the next generation
 - Any live cell with more than three live neighbors dies, as if by overpopulation
 - Any dead cell with exactly three live neighbors becomes a live cell, as if reproduction
"""
import asyncio
import time
from sense_hat import SenseHat
from signal import pause
import random
loop = asyncio.get_event_loop()

hat = SenseHat()

# dimensions of PiHat led grid
ROWS = 8
COLS = 8

#
# Pixel uses (x,y) origin in bottom left corner (math coordinates)
# This is easier to use since students should think this way already.
# 
class Pixel:
    def clipColor(self,color):
        if (color < 0): return 0
        if (color > 255): return 255
        return color
    
    
    def __init__(self,x,y,r=0,g=0,b=0):
        self._x = (x%ROWS)
        self._y = (y%COLS)
        self._r = self.clipColor(r)
        self._g = self.clipColor(g)
        self._b = self.clipColor(b)
        
    def setColorFromPixel(self,pixel):
        self._r=pixel._r
        self._g=pixel._g
        self._b=pixel._b
        
    def show(self):
        hat.set_pixel(self._x,ROWS-1-self._y,self._r,self._g,self._b)
        
    def read(self):
        (self._r,self._g,self._b)=hat.get_pixel(self._x,ROWS-1-self._y)
    def color(self):
        return (self._r,self._g,self._b)
    def setColorRGB(self,r,g,b):
        self._r = self.clipColor(r)
        self._g = self.clipColor(g)
        self._b = self.clipColor(b)

# Conway's Game of Life
# :::RULES BEGIN:::
class LifeRule:
    def __init__(self,game,x,y):
        self.game = game
        self.x = x
        self.y = y

    def aliveAt(self,x,y):
        (r,g,b)=self.game.oldPixels[x%ROWS][y%COLS].color()
        return max(r,g,b) > 0

    def alive(self):
        return self.aliveAt(self.x,self.y)

    def neighbors(self):
        count = 0
        for dx in range(-1,2):
            for dy in range(-1,2):
                if dx == 0 and dy == 0: continue
                xx = self.x + dx
                yy = self.y + dy
                if self.aliveAt(xx,yy):
                    count = count + 1
        return count
    
    def update(self):
        me = int(self.alive())
        ee = self.neighbors()
        if me:
            if (ee < 2 or ee > 3):
                self.die()
                return
        else:
            if (ee == 3):
                self.born()
                return
        if me:
            self.live()
        else:
            self.die()
            
    def die(self):
        self.game.newPixels[self.x][self.y].setColorRGB(0,0,0)
    def born(self):
        self.game.newPixels[self.x][self.y].setColorRGB(255,255,255)
    def live(self):
        (r,g,b)=self.game.oldPixels[self.x][self.y].color()
        self.game.newPixels[self.x][self.y].setColorRGB(r,g,b)

class FixedRule(LifeRule):
    def __init__(self, game, x, y):
        LifeRule.__init__(self,game,x,y)
    def update(self):
        if (self.aliveAt(self.x,self.y)):
            self.born()
        else:
            self.die()
    
class ScrollLeftRule(LifeRule):
    def __init__(self, game, x, y):
        LifeRule.__init__(self,game,x,y)
    def update(self):
        if (self.aliveAt(self.x+1,self.y)):
            self.born()
        else:
            self.die()

class ScrollUpRule(LifeRule):
    def __init__(self, game, x, y):
        LifeRule.__init__(self,game,x,y)
    def update(self):
        if (self.aliveAt(self.x,self.y-1)):
            self.born()
        else:
            self.die()

class ColorLifeRule(LifeRule):
    def __init__(self, game, x, y):
        LifeRule.__init__(self,game,x,y)
        
    def born(self):
        self.game.newPixels[self.x][self.y].setColorRGB(1+10*self.x,1+10*self.y,1+10*self.x+10*self.y)

    def live(self):
        (r,g,b)=self.game.oldPixels[self.x][self.y].color()
        (r,g,b)=(max(32,r),max(32,g),max(32,b))
        (r,g,b) = ((r+10*self.x) % 256,(g+10*self.y)%256,(b) % 256)
        self.game.newPixels[self.x][self.y].setColorRGB(r,g,b)

#:::RULES END:::

#Change rules here to one of the above
SELECTED_RULE = LifeRule
        
class Game:
    def __init__(self, ascii):
        # Change rule here to see how they work
        self.rules = [ [ SELECTED_RULE(self,x,y) for y in range(COLS) ] for x in range(ROWS) ]

        self.newPixels = [ [ Pixel(x,y) for y in range(COLS) ] for x in range(ROWS) ]
        self.oldPixels = [ [ Pixel(x,y) for y in range(COLS) ] for x in range(ROWS) ]
        for x in range(ROWS):
            for y in range(COLS):
                if ascii[ROWS-1-y][x] == 'x': self.rules[x][y].born()

    def swap(self):
        tmp = self.oldPixels
        self.oldPixels = self.newPixels
        self.newPixels = tmp

    def show(self):
        for x in range(ROWS):
            for y in range(COLS):
                self.newPixels[x][y].show()
    def update(self):
        self.swap()
        for x in range(ROWS):
            for y in range(COLS):
                self.rules[x][y].update()
        self.show() 
        
    def play(self):
        while True:
            self.update()
            time.sleep(0.2)


blank = [
    "........",
    "........",
    "........",
    "........",
    "........",
    "........",
    "........",
    "........"
    ]
block = [
    "........",
    ".xx.....",
    ".xx.....",
    "........",
    "........",
    "........",
    "........",
    "........"]

blinker = [
    "........",
    "..x.....",
    "..x.....",
    "..x.....",
    "........",
    "........",
    "........",
    "........"]
blink2 = [
    "........",
    "..xx....",
    "..xx....",
    "....xx..",
    "....xx..",
    "........",
    "........",
    "........"
    ]
glider = [
    "..x.....",
    "x.x.....",
    ".xx.....",
    "........",
    "........",
    "........",
    "........",
    "........"
]

# choose initial layout (block, blinker, etc)
hat.clear()
game = Game(glider)
game.play()
