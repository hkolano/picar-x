# from lib.sensing import InterpreterGrayscale, SensingUltrasonic
from picarx_improved import Picarx
from driving import MovePicar
from sensing import * #SensingGrayscale, SensingUltrasonic, InterpreterGrayscale, Controller
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
# run git submodule init and git submodule update if RossROS has no files in it

class Flight():
    '''Combines classes to execute high-level functions, such as line following. '''

    def __init__(self):
        self.car = Picarx()
        self.move = MovePicar(self.car)
        self.sense = SensingGrayscale(self.car)
        self.sense_ultra = SensingUltrasonic(self.car)
        self.int = InterpreterGrayscale(self.sense)
        self.int_wall = InterpreterUltrasonic()
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
            self.move_for_line_following(loc)

    def move_for_line_following(self, loc):
        '''Moves the vehicle based on the steering; steers slower on sharper turns.'''
        str_angle = self.ctlr.steer(loc)
        if abs(str_angle) > 20:
            self.move.move(angle=str_angle, speed=25, is_cont=True)
        else:
            self.move.move(angle=str_angle, is_cont=True)


if __name__ == "__main__":
    fl = Flight()
    grayscale_bus = rossros.Bus(name="grayscale")
    ultra_bus = rossros.Bus(name="ultrasonic")
    loc_bus = rossros.Bus(name="location")
    wall_bus = rossros.Bus(name="wallsensing")
    timer_bus = rossros.Bus(name="timer")
    sensor_delay = 0.05
    interpret_delay = 0.05
    move_delay = 0.01

    # Time until timeout (I had trouble stopping the code from running with concurrent going)
    runtime = .5

    logging.getLogger().setLevel(logging.INFO)

    sensor_producer = rossros.Producer(fl.sense.get_grayscale_data, grayscale_bus, delay=sensor_delay, termination_busses=(timer_bus,), name="grayscale_producer")
    sensultra_prod = rossros.Producer(fl.sense_ultra.get_ultrasonic_data, ultra_bus, delay=sensor_delay, termination_busses=(timer_bus,), name="ultrasonic_producer")
    interpreter_consumerproducer = rossros.ConsumerProducer(fl.int.interpret_location, (grayscale_bus,), (loc_bus,), delay=interpret_delay, termination_busses=(timer_bus,), name="interpreter_consprod")
    int_ultra_consprod = rossros.ConsumerProducer(fl.int_wall.interpret_distance, (ultra_bus,), (wall_bus,), termination_busses=(timer_bus,), name="wallint_consprod")
    controller_consumer = rossros.Consumer(fl.move_for_line_following, (loc_bus,), delay=move_delay, termination_busses=(timer_bus,), name="controller_consumer")
    timer = rossros.Timer((timer_bus,), duration=5, delay=0.1, termination_busses=(timer_bus,), name="master timer")

    # prod_cons_list = [timer, sensor_producer, sensultra_prod, interpreter_consumerproducer] #, controller_consumer]
    prod_cons_list = [timer, sensultra_prod, int_ultra_consprod]
    rossros.runConcurrently(prod_cons_list)
    # with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    #     eSensor = executor.submit(fl.produce_sensor_data, grayscale_bus, sensor_delay, runtime)
    #     eInterpreter = executor.submit(fl.consume_sens_produce_loc, grayscale_bus, loc_bus, interpret_delay, runtime)
    #     eMover = executor.submit(fl.consume_loc_and_move, loc_bus, move_delay, runtime)

    # eSensor.result()
    # eInterpreter.result()
    # eMover.result()
