from picarx_improved import Picarx
from driving import MovePicar
from sensing import Sensing, Interpreter, Controller
import time
import concurrent.futures
from messagebus import MessageBus
import logging
from logdecorator import log_on_start , log_on_end , log_on_error
from readerwriterlock import rwlock
import sys

class Flight():
    '''Combines classes to execute high-level functions, such as line following. '''

    def __init__(self):
        self.car = Picarx()
        self.move = MovePicar(self.car)
        self.sense = Sensing(self.car)
        self.int = Interpreter(self.sense)
        self.ctlr = Controller(self.car, scaling_factor=40)

        # self.int.calibrate()
        self.int.load_calibration('table_afternoon.pkl')

    def follow_line(self):
        while True:
            data = self.sense.get_grayscale_data()
            # print(data)
            loc = self.int.interpret_location(data)
            # print(loc)
            str_angle = self.ctlr.steer(loc)
            if abs(str_angle) > 5:
                self.move.move(angle=str_angle, speed=25, is_cont=True)
            else:
                self.move.move(angle=str_angle, is_cont=True)

    @log_on_start(logging.INFO, "Starting sensor publisher")
    def produce_sensor_data(self, bus, delay_time, runtime):
        start_time = time.time()
        while time.time() - start_time < runtime:
            data = self.sense.get_grayscale_data()
            bus.write_msg(data)
            time.sleep(delay_time)

    @log_on_start(logging.INFO, "Starting interpreter sub/pub")
    def consume_sens_produce_loc(self, read_bus, write_bus, delay_time, runtime):
        start_time = time.time()
        while time.time() - start_time < runtime:
            data = read_bus.read_msg()
            loc = self.int.interpret_location(data)
            write_bus.write_msg(loc)
            time.sleep(delay_time)

    @log_on_start(logging.INFO, "Starting mover sub")
    @log_on_error(logging.INFO, "problem in consume and move")
    def consume_loc_and_move(self, read_bus, delay_time, runtime):
        start_time = time.time()
        while time.time() - start_time < runtime:
            loc = read_bus.read_msg()
            logging.DEBUG("Location: ", loc)
            str_angle = self.ctlr.steer(loc)
            if abs(str_angle) > 20:
                self.move.move(angle=str_angle, speed=25, is_cont=True)
            else:
                self.move.move(angle=str_angle, is_cont=True)
            time.sleep(delay_time)


if __name__ == "__main__":
    fl = Flight()
    grayscale_bus = MessageBus()
    loc_bus = MessageBus()
    sensor_delay = 0.01
    interpret_delay = 0.01
    runtime = 2

    logging.getLogger().setLevel(logging.DEBUG)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        eSensor = executor.submit(fl.produce_sensor_data, grayscale_bus, sensor_delay, runtime)
        eInterpreter = executor.submit(fl.consume_sens_produce_loc, grayscale_bus, loc_bus, interpret_delay, runtime)
        eMover = executor.submit(fl.consume_loc_and_move, loc_bus, interpret_delay, runtime)

    eSensor.result()
    eInterpreter.result()
    eMover.result()
    # sys.exit(1)
