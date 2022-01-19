import time
import logging
from logdecorator import log_on_start , log_on_end , log_on_error

from picarx_improved import *

class MovePicar():

    def __init__(self, px):
        self.car = px
        
    def move(self, dir="forward", angle=0, speed=50, duration=1):
        self.car.set_dir_servo_angle(angle)
        time.sleep(0.25)
        if dir == "forward":
            self.car.forward(speed)
        else:
            self.car.backward(speed)
        time.sleep(duration)
        self.car.stop()
        time.sleep(0.1)

    def straighten_out(self):
        self.car.set_servo_angle(0)
        time.sleep(0.25)

    def parallel_park(self, side):
        self.move("forward", 0, 40, 0.7)
        if side == "right":
            self.move("backward", 40, 25, 1)

if __name__ == "__main__":
    px = Picarx()
    move = MovePicar(px)
    move.move("forward", 0, 50, 0.5)
    move.move("backward", 0, 50, 0.5)
    move.move("forward", 20, 50, 1)