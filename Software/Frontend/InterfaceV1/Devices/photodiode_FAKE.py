from sample_data import SampleData
from numpy import random


class Photodiode:
    # Device: AD677JNZ ADC used for measuring photodiode voltage.

    def __init__(self):
        self.sample_data = SampleData().SAMPLE_SIGNAL
        self.i = 0
        self.length = self.sample_data.size

    def read_adc(self):
        self.i = self.i + 1 if self.i < self.length - 1 else 0
        point = self.sample_data[self.i] + round(random.normal(0, 500))
        return point if point <= 65535 else 65535

    def calculate_voltage(self, adc_value, reference_voltage=3.3):
        return (adc_value * reference_voltage) / 4095

    def close(self):
        pass