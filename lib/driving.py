import time
import logging
from logdecorator import log_on_start , log_on_end , log_on_error

from picarx_improved import *

class MovePicar():

    def __init__(self, px):
        self.car = px
        
    @log_on_error(logging.INFO, "error in MOVE function")
    @log_on_start(logging.DEBUG, "move command starting!")
    def move(self, dir="forward", angle=0, speed=50, duration=1, is_cont=False):
        ''' 
        Command the car to move for a discrete amount of time. 
        Inputs:
        dir: "forward" or "backward"
        angle: >0 is right, <0 is left. Max 40 degrees.
        speed: power to pass to the car.
        duration: length of time for move, in seconds. 
        is_cont: "is continuous" -- True for continuous motion, False for discrete motions. 
        '''
        self.car.set_dir_servo_angle(angle)
        if not is_cont:
            time.sleep(0.25)
        if dir == "forward":
            self.car.forward(speed)
        elif dir == "backward":
            self.car.backward(speed)
        else:
            print("Direction not recognized. Please input 'forward' or 'backward' as direction.")
        if not is_cont:
            # If a discrete motion, continue for the duration and then stop.
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

    def drive(self):
        ''' Allows user to command parallel parking or k-turns in a loop. '''
        self.in_drive_mode = True
        print("Entered driving mode.")
        while self.in_drive_mode == True:
            print("Please select a movement option: \n 1:  Parallel park \n 2:  K-turn \n 3:  Straighten wheels \n 4: Exit driving mode")
            usr_cmd = input("Select movement number: ")
            # Make sure input is an integer
            try:
                usr_cmd = int(usr_cmd)
            except:
                usr_cmd = "no"

            # Parse user input
            if usr_cmd == 1: # Parallel Parking
                dir = input("Choose a direction to park: \n r: right \n l: left \n")
                if dir == 'r':
                    # print("executing ppark right")
                    self.parallel_park("right")
                elif dir == 'l':
                    # print('executing ppark left')
                    self.parallel_park("left")
                else:
                    print("Direction not found. Please type 'r' or 'l'.")
            elif usr_cmd == 2: # K turn
                dir = input("Choose a direction to turn: \n r: right \n l: left \n")
                if dir == 'r':
                    # print("executing kturn right")
                    self.k_turn("right")
                elif dir == 'l':
                    # print('executing kturn left')
                    self.k_turn("left")
                else:
                    print("Direction not found. Please type 'r' or 'l'.")
            elif usr_cmd == 3:
                self.straighten_out()
            elif usr_cmd == 4:
                print("Exiting drive mode.")
                self.in_drive_mode = False
            else:
                print("Command not recognized. Please choose from the available options.")


if __name__ == "__main__":
    px = Picarx()
    move = MovePicar(px)
    move.drive()
