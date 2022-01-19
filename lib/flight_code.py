from picarx_improved import Picarx
from driving import MovePicar
from sensing import Sensing
import time

if __name__ == "__main__":
    px = Picarx()
    move = MovePicar(px)
    sens = Sensing(px)

    while True:
        print(sens.get_grayscale_data())
        time.sleep(1)
