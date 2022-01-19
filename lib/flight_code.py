from picarx_improved import Picarx
from driving import MovePicar
from sensing import Sensing, Interpreter
import time

if __name__ == "__main__":
    px = Picarx()
    move = MovePicar(px)
    sens = Sensing(px)
    int = Interpreter(sens)

    int.calibrate()

    while True:
        data = sens.get_grayscale_data()
        print(data)
        print(int.interpret_location(data))
        time.sleep(1)
