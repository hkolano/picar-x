from picarx_improved import Picarx
from driving import MovePicar
from sensing import Sensing, Interpreter, Controller
import time

class Flight():
    '''Combines classes to execute high-level functions, such as line following. '''

    def __init__(self):
        self.car = Picarx()
        self.move = MovePicar(self.car)
        self.sense = Sensing(self.car)
        self.int = Interpreter(self.sense)
        self.ctlr = Controller(self.car, scaling_factor=40)

        # self.int.calibrate()
        self.int.load_calibration('kitchen_floor_day.pkl')

    def follow_line(self):
        while True:
            data = self.sense.get_grayscale_data()
            # print(data)
            loc = self.int.interpret_location(data)
            # print(loc)
            str_angle = self.ctlr.steer(loc)
            if abs(str_angle) > 20:
                self.move.move(angle=str_angle, speed=25, is_cont=True)
            else:
                self.move.move(angle=str_angle, is_cont=True)


if __name__ == "__main__":
    fl = Flight()
    fl.follow_line()
