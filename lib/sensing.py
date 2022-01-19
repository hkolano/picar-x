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