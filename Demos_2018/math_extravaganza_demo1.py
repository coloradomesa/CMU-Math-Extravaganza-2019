#!/usr/env/python3
from sense_hat import SenseHat
hat = SenseHat()
print("Press CTRL-C to stop...")
while True:
    hat.show_message("Math Extravaganza 2018".upper())
