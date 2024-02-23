from typing import Tuple
import RPi.GPIO as GPIO
from spidev import SpiDev
import time
from multiprocessing import Event, Process
from scipy.fft import fft
import numpy as np


class CaptureLightIntensity(Process):

    def __init__(self, shutdown_event, data_queue, hall_pin, num_cycles, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clk_val = 0
        self.NUM_CYCLES = num_cycles
        self.HALL_PIN = hall_pin
        self.buffer_size = 25000
        self.shutdown_event = shutdown_event

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.HALL_PIN, GPIO.FALLING, callback=self.inc)

        self.spi = SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 20000000
        self.spi.mode = 0

        # self.active_gather_event = Event()
        # self.active_gather_event.clear()
        self.active_gathering = 0

        self.data_queue = data_queue

        self.buffer = np.ndarray(shape=(self.buffer_size, 1), dtype=np.uint16)

    def inc(self, channel):
        if channel == self.HALL_PIN:
            if self.clk_val < self.NUM_CYCLES:
                self.clk_val += 1
                if self.clk_val == 1:
                    # self.active_gather_event.set()
                    self.active_gathering = 1
            else:
                self.clk_val = 0
                # self.active_gather_event.clear()
                self.active_gathering = 0

    def read_adc(self):
        resp = self.spi.xfer2([0x00, 0x00])
        return (resp[0] << 8) + resp[1]

    def process_data(self, num_of_cycles, num_of_samples) -> Tuple:
        if num_of_samples < self.buffer_size:
            data = self.buffer[0:num_of_samples]
            y = fft(data)  # MUST slice the exact number of samples. Cannot use entire buffer.

            A0 = y[0] / num_of_samples
            A1 = y[num_of_cycles * 2] * (2 / num_of_samples)
            A2 = y[num_of_cycles * 4] * (2 / num_of_samples)

            S1 = np.real(A2) * 4
            S2 = np.imag(A2) * -4
            S3 = np.imag(A1) * -2
            S0 = 2 * np.real(A0) - S1 / 2

            return S0, S1, S2, S3
        else:
            return 0, 0, 0, 0

    def run(self) -> None:

        while not self.shutdown_event.is_set():

            sample_num = 0
            # self.active_gather_event.wait()
            try:
                # while self.active_gather_event.is_set():
                while self.active_gathering:
                    self.buffer[sample_num] = self.read_adc()
                    sample_num += 1
                data = self.process_data(self.NUM_CYCLES, sample_num)
                self.data_queue.put(data)
            except Exception:
                pass

    def close(self) -> None:
        self.spi.close()
        GPIO.cleanup()
