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
        self.car.set_dir_servo_angle(0)
        time.sleep(0.25)

    def parallel_park(self, side="right"):
        self.move("forward", 0, 40, 0.95)
        if side == "right":
            self.move("backward", 40, 30, 2.3)
            self.move("backward", -40, 30, 0.95)
        else:
            self.move("backward", -40, 20, 1.95)
            self.move("backward", 40, 30, 2.4)
        self.straighten_out()

    def k_turn(self, side="right"):
        if side=="right":
            self.move(angle=40, duration=1)
            self.move("backward", angle=-40, duration=1)
            self.move(angle=40, duration=1)
        else:
            self.move(angle=-40, duration=1)
            self.move("backward", angle=40, duration=1)
            self.move(angle=40, duration=1)

if __name__ == "__main__":
    px = Picarx()
    move = MovePicar(px)
    move.k_turn("right")
