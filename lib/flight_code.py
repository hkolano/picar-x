from picarx_improved import Picarx
from driving import MovePicar
from sensing import Sensing, Interpreter, Controller
import time

if __name__ == "__main__":
    px = Picarx()
    move = MovePicar(px)
    sens = Sensing(px)
    int = Interpreter(sens)
    ctlr = Controller(px)

    int.calibrate()
    int.save_calibration('headphonecase.pxl')

    while True:
        data = sens.get_grayscale_data()
        print(data)
        loc = int.interpret_location(data)
        print(loc)
        ctlr.steer(loc)
        time.sleep(.5)
