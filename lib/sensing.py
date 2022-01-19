from statistics import mean
from picarx_improved import Picarx

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
        thresh_close: more extreme than thresh_close = line
        thresh_far: more extreme than thresh_far = floor'''
        self.sensor = sensor
        self.thresh_close = thresh_close
        self.thresh_far = thresh_far
        self.polarity = polarity

    def calibrate(self):
        ''' Run to set self.thresh values and self.polarity via 
        a calibration routine with the user. '''
        # Get grayscale values for the floor and the line
        input("Place the sensor over the floor and hit enter.")
        floor_data = self.sensor.get_grayscale_data()
        floor_avg = mean(floor_data)
        input("Place the sensor over the line and hit enter.")
        line_data = self.sensor.get_grayscale_data()
        line_avg = mean(line_data)
        print("floor: ", floor_data, "\n line: ", line_data)

        # Define polarity based on which had more light
        light_diff = line_avg - floor_avg
        if light_diff > 0:
            self.polarity = 1
        else:
            self.polarity = -1

        # Define threshold based on difference
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
        position: number on interval [-1 1] (positive = too far left) 
        indicating position of robot with respect to line'''
        if self.polarity == 1:
            center_of_light = (gray_data[0]*1 + gray_data[1]*2 + gray_data[2]*3)/sum(gray_data)
            print("center of light: ", center_of_light)
