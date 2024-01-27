import numpy as np
import csv

class SampleData:

    def __init__(self):
        with open("data0.csv") as file:
            reader = csv.reader(file)
            data = tuple(reader)
            self.nump_arr = np.array(data)
            self.nump_arr_mul = self.nump_arr.transpose()[1].astype(dtype=np.double) * 65535
            self.rounded_nump_arr = self.nump_arr_mul.round()
            self.SAMPLE_SIGNAL = self.rounded_nump_arr.astype(dtype=np.uint16)

