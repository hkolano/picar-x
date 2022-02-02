from picarx_improved import Picarx
from driving import MovePicar
from sensing import SensingGrayscale, Interpreter, Controller
import time
import concurrent.futures
from messagebus import MessageBus
import logging
from logdecorator import log_on_start , log_on_end , log_on_error
from readerwriterlock import rwlock
import sys 
import os

_path1 = os.getcwd() + '/lib'
_path2 = os.getcwd() + '/RossROS'
sys.path.append(_path1)
sys.path.append(_path2)

import rossros

class Flight():
    '''Combines classes to execute high-level functions, such as line following. '''

    def __init__(self):
        self.car = Picarx()
        self.move = MovePicar(self.car)
        self.sense = SensingGrayscale(self.car)
        self.int = Interpreter(self.sense)
        self.ctlr = Controller(self.car, scaling_factor=40)

        # self.int.calibrate()

        # Save or load calibration data from a pickle file
        # self.int.save_calibration('new_cal_data.pkl')
        # self.int.load_calibration('new_cal_data.pkl')

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

    def move_for_line_following(self, loc):
        '''Moves the vehicle based on the steering; steers slower on sharper turns.'''
        str_angle = self.ctlr.steer(loc)
        if abs(str_angle) > 20:
            self.move.move(angle=str_angle, speed=25, is_cont=True)
        else:
            self.move.move(angle=str_angle, is_cont=True)


    @log_on_start(logging.INFO, "Starting sensor publisher")
    def produce_sensor_data(self, bus, delay_time, runtime):
        start_time = time.time()
        while time.time() - start_time < runtime:
            data = self.sense.get_grayscale_data()
            bus.set_message(data, "produce_sensor_data")
            time.sleep(delay_time)

    @log_on_start(logging.INFO, "Starting interpreter sub/pub")
    def consume_sens_produce_loc(self, read_bus, write_bus, delay_time, runtime):
        start_time = time.time()
        while time.time() - start_time < runtime:
            data = read_bus.get_message("consume_sens_produce_loc")
            loc = self.int.interpret_location(data)
            write_bus.set_message(loc, "consume_sens_produce_loc")
            time.sleep(delay_time)

    @log_on_start(logging.INFO, "Starting mover sub")
    def consume_loc_and_move(self, read_bus, delay_time, runtime):
        start_time = time.time()
        while time.time() - start_time < runtime:
            loc = read_bus.get_message("consume_loc_and_move")
            self.move_for_line_following(loc)
            time.sleep(delay_time)


if __name__ == "__main__":
    fl = Flight()
    grayscale_bus = rossros.Bus(name="grayscale")
    loc_bus = rossros.Bus(name="location")
    timer_bus = rossros.Bus(name="timer")
    sensor_delay = 0.01
    interpret_delay = 0.01
    move_delay = 0.01

    # Time until timeout (I had trouble stopping the code from running with concurrent going)
    runtime = .5

    logging.getLogger().setLevel(logging.INFO)

    sensor_producer = rossros.Producer(fl.sense.get_grayscale_data, grayscale_bus, delay=sensor_delay, termination_busses=(timer_bus,), name="grayscale_producer")
    interpreter_consumerproducer = rossros.ConsumerProducer(fl.int.interpret_location, (grayscale_bus,), (loc_bus,), delay=interpret_delay, termination_busses=(timer_bus,), name="interpreter_consprod")
    controller_consumer = rossros.Consumer(fl.move_for_line_following, (loc_bus,), delay=move_delay, termination_busses=(timer_bus,), name="controller_consumer")
    timer = rossros.Timer((timer_bus,), duration=0.5, delay=0.1, termination_busses=(timer_bus,), name="master timer")

    prod_cons_list = [timer, sensor_producer, interpreter_consumerproducer, controller_consumer]
    rossros.runConcurrently(prod_cons_list)
    # with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    #     eSensor = executor.submit(fl.produce_sensor_data, grayscale_bus, sensor_delay, runtime)
    #     eInterpreter = executor.submit(fl.consume_sens_produce_loc, grayscale_bus, loc_bus, interpret_delay, runtime)
    #     eMover = executor.submit(fl.consume_loc_and_move, loc_bus, move_delay, runtime)

    # eSensor.result()
    # eInterpreter.result()
    # eMover.result()
