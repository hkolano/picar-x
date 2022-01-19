import time
import logging
from logdecorator import log_on_start , log_on_end , log_on_error

from picarx_improved import *

class MovePicar():

    def __init__(self, px):
        self.car = px
        
    def move(self, dir="forward", angle=0, speed=50, duration=1):
        ''' 
        Command the car to move for a discrete amount of time. 
        Inputs:
        dir: "forward" or "backward"
        angle: >0 is right, <0 is left. Max 40 degrees.
        speed: power to pass to the car.
        duration: length of time for move, in seconds. 
        '''
        self.car.set_dir_servo_angle(angle)
        time.sleep(0.25)
        if dir == "forward":
            self.car.forward(speed)
        elif dir == "backward":
            self.car.backward(speed)
        else:
            print("Direction not recognized. Please input 'forward' or 'backward' as direction.")
        time.sleep(duration)
        self.car.stop()
        time.sleep(0.1)

    def straighten_out(self):
        ''' Straightens the car's wheels. '''
        self.car.set_dir_servo_angle(0)
        time.sleep(0.25)

    def parallel_park(self, side="right"):
        ''' Commands the car to parallel park directly to its right or left. '''
        if side == "right":
            self.move("forward", 0, 40, 0.95)
            self.move("backward", 40, 30, 2.3)
            self.move("backward", -40, 30, 0.95)
        elif side == "left":
            self.move("forward", 0, 40, 0.95)
            self.move("backward", -40, 20, 1.95)
            self.move("backward", 40, 30, 2.4)
        else:
            print("Side not recognized. Please specify 'left' or 'right' as direction.")
        self.straighten_out()

    def k_turn(self, side="right"):
        ''' Command the car to switch directions by making a k-turn. '''
        if side=="right":
            self.move(angle=40, duration=0.9)
            self.move("backward", angle=-40, duration=0.75)
            self.move(duration=0.5)
        elif side=="left":
            self.move(angle=-40, duration=0.7)
            self.move("backward", angle=40, duration=0.75)
            self.move(duration=0.5)
        else:
            print("Side not recognized. Please specify 'left' or 'right' as direction.")


if __name__ == "__main__":
    px = Picarx()
    move = MovePicar(px)
    move.k_turn("left")
