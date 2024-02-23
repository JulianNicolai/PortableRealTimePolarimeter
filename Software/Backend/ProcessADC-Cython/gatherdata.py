from csv import reader
from multiprocessing import Process
from typing import Tuple
from scipy.fft import fft
# from spidev import SpiDev
import numpy as np
# import time


class GatherData(Process):

    def __init__(self, shutdown_event, active_gather_event, data_queue, num_of_cycles, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.spi = SpiDev()
        # self.spi.open(0, 0)
        # self.spi.max_speed_hz = 22000000
        # self.spi.mode = 0

        # Creates fake data in place of spi for testing logic
        self.I_theta = []
        with open('data0.csv') as file:
            for row in reader(file):
                self.I_theta.append(float(row[1]))
        self.I_theta = np.array(self.I_theta) * 65535
        self.I_theta = self.I_theta.round()
        print(self.I_theta)

        self.num_of_cycles = num_of_cycles

        self.buffer = np.ndarray(shape=(6400, 1), dtype=np.uint16)

        self.active_gather_event = active_gather_event
        self.shutdown_event = shutdown_event
        self.data_queue = data_queue

        # self.start()

    def read_adc(self, i):
        # resp = self.spi.xfer2([0x00, 0x00])
        # return (resp[0] << 8) + resp[1]
        # time.sleep(0.01)
        for j in range(1, 10000):
            a = (j - 2 * j) / j + 5 * j
        return self.I_theta[i]

    def process_data(self, num_of_cycles, num_of_samples) -> Tuple:
        data = self.buffer[0:num_of_samples]
        y = fft(data)  # MUST slice the exact number of samples. Cannot use entire buffer.
        # print(num_of_cycles, num_of_samples)
        # print(data)
        # print(y)

        # All parameters must be scaled by the number of samples taken
        # Parameters required: DC (index: 0), 2ω (index: 2*cycles), 4ω (index: 4*cycles)
        # Due to FFT symmetry, total intensity at a frequency is actually x2, except for DC (0 Hz, already symmetric)
        A0 = y[0] / num_of_samples
        A1 = y[num_of_cycles * 2] * (2 / num_of_samples)
        A2 = y[num_of_cycles * 4] * (2 / num_of_samples)

        S1 = np.real(A2) * 4
        S2 = np.imag(A2) * -4
        S3 = np.imag(A1) * -2
        S0 = 2 * np.real(A0) - S1 / 2

        return S0, S1, S2, S3

    def run(self):
        while not self.shutdown_event.is_set():
            i = 0
            self.active_gather_event.wait()
            while self.active_gather_event.is_set():
                self.buffer[i] = self.read_adc(i)
                i += 1
            data = self.process_data(self.num_of_cycles, i)
            self.data_queue.put(data)
            print(data)

    def close(self) -> None:
        # self.spi.close()
        pass
