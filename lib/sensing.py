from fileinput import close
from statistics import mean
from picarx_improved import Picarx
import pickle

class Sensing():

    def __init__(self, car):
        ''' Initialize sensor suite
        Input car: Picarx object '''
        self.car = car
        self.S0 = car.S0
        self.S1 = car.S1
        self.S2 = car.S2

    def get_grayscale_data(self):
        ''' Read the 3 grayscale values and return them as a list '''
        adc_value_list = []
        adc_value_list.append(self.S0.read())
        adc_value_list.append(self.S1.read())
        adc_value_list.append(self.S2.read())
        return adc_value_list

class Interpreter():

    def __init__(self, sensor, polarity=1, thresh_close=1000, thresh_far = 600):
        ''' Initialize line interpreter. 
        Inputs:
        sensor: the Sensing object
        polarity: 1 - line is lighter; -1 - line is darker
        thresh_close: more extreme than thresh_close indicates the line
        thresh_far: more extreme than thresh_far indicates the floor'''
        self.sensor = sensor
        self.thresh_close = thresh_close
        self.thresh_far = thresh_far
        self.polarity = polarity

    def calibrate(self):
        ''' Run to set self.thresh values and self.polarity via 
        a calibration routine with the user. '''
        # Get grayscale values for the floor and the line
        input("Place all 3 sensors over the floor and hit enter.")
        floor_data = self.sensor.get_grayscale_data()
        floor_avg = mean(floor_data)
        input("Place all 3 sensors over the line and hit enter.")
        line_data = self.sensor.get_grayscale_data()
        line_avg = mean(line_data)
        print("floor: ", floor_data, "\n line: ", line_data)
        input("Place the robot at the start of the track and hit enter.")

        # Define polarity based on which had more light
        light_diff = line_avg - floor_avg
        if light_diff > 0:
            self.polarity = 1
        else:
            self.polarity = -1

        # Define thresholds based on difference
        one_third_range = abs(light_diff)/3
        if self.polarity == 1:
            self.thresh_close = line_avg - one_third_range
            self.thresh_far = floor_avg + one_third_range
        if self.polarity == -1:
            self.thresh_close = line_avg + one_third_range
            self.thresh_far = floor_avg - one_third_range

        print("polarity is: ", self.polarity)
        print("Close threshold: ", self.thresh_close, "Far threshold: ", self.thresh_far)
        
    def interpret_location(self, gray_data):
        ''' Interprets grayscale data and returns a guess as to where
         the robot is in reference to the line.
        Returns:
        pos: number on interval [-1 1] (positive = robot is too far right)'''
        closeness_vector = []
        pos = 0
        if self.polarity == 1:
            for val in gray_data:
                if val < self.thresh_far:
                    closeness_vector.append(1)
                elif self.thresh_far < val < self.thresh_close:
                    closeness_vector.append(2)
                else:
                    closeness_vector.append(3)
        
        # if center sensor is over line
        if closeness_vector[1] == 3:
            if closeness_vector[0] == closeness_vector[2]:
                pos = 0
                print("Centered!")
            elif closeness_vector[0] > closeness_vector[2]:
                pos = 0.33
                print("slightly right...")
            elif closeness_vector[0] < closeness_vector[2]:
                pos = -0.33
                print("slightly left...")
        # if center sensor is slightly off the line
        elif closeness_vector[1] == 2:
            if closeness_vector[0] > 1:
                pos = 0.67
                print("Pretty right")
            elif closeness_vector[2] > 1:
                pos = -0.67
                print("Pretty left")
        # if center sensor is completely off the line
        elif closeness_vector[1] == 1:
            if closeness_vector[0] > 1:
                pos = 1.0
                print("VERY RIGHT")
            elif closeness_vector[2] > 1:
                pos = -1.0
                print("VERY LEFT")
            else:
                print("HELP! I'VE LOST THE LINE!!!")
        else:
            print("wtf how did you get here? vec is ", closeness_vector)

        return pos

    def save_calibration(self, filename):
        # Open a file and use dump()
        with open(filename, 'wb') as file:
            # A new file will be created
            pickle.dump([self.polarity, self.thresh_close, self.thresh_far], file)

    def load_calibration(self, filename):
        with open(filename, 'rb') as file:
            [self.polarity, self.thresh_close, self.thresh_far] = pickle.load(file)
            print("Light calibration loaded: \n Polarity: ", self.polarity, "\n Far Threshold: ", self.thresh_far, "\n Close Threshold: ", self.thresh_close)

class Controller():

    def __init__(self, car, scaling_factor=20):
        ''' scaling_factor: multiply location [-1 1] by s.f. to get steering angle (max 40)
        car: picarx object '''
        self.scaling = scaling_factor
        self.car = car

    def steer(self, location):
        '''Input:
        location: value on [-1 1] (positive: robot too far right) 
        describing location of robot wrt the line'''
        steer_angle = location*self.scaling*-1
        return steer_angle