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

    def __init__(self, sensor, sensitivity=500, polarity=1):
        ''' Initialize line interpreter. 
        Inputs:
        sensor: the Sensing object
        sensitivity: how different light & dark readings are
        polarity: 1 - line is darker; 2 - line is lighter'''
        self.sensor = sensor
        self.sensitivity = sensitivity
        self.polarity = polarity

    def calibrate(self):
        input("Place the sensor over the floor.")
        floor_data = self.sensor.get_grayscale_data()
        input("Place the sensor over the line.")
        line_data = self.sensor.get_grayscale_data()
        input("Place the sensor centered on the line.")
        middle_data = self.sensor.get_grayscale_data()
        print("floor: {} \n line: {} \n middle: {} \n", floor_data, line_data, middle_data)

