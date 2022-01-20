from picarx_improved import Picarx
from driving import MovePicar
from sensing import Sensing, Interpreter, Controller
import time

class Flight():

    def __init__(self):
        self.car = Picarx()
        self.move = MovePicar(self.car)
        self.sense = Sensing(self.car)
        self.int = Interpreter(self.sense)
        self.ctlr = Controller(self.car, scaling_factor=30)

        # self.int.calibrate()
        self.int.load_calibration('kitchen_floor_day.pkl')

    def follow_line(self):
        x = 0
        while True:
            data = self.sense.get_grayscale_data()
            print(data)
            loc = self.int.interpret_location(data)
            print(loc)
            str_angle = self.ctlr.steer(loc)
            self.move.move(angle=str_angle, is_cont=True)
            x += 1
        # self.car.stop()


if __name__ == "__main__":
    fl = Flight()
    fl.follow_line()
