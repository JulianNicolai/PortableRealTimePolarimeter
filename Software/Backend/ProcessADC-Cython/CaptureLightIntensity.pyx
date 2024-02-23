from typing import Tuple
import RPi.GPIO as GPIO
from spidev import SpiDev
from multiprocessing import Process
from scipy.fft import fft
import numpy as np
import cython as c


class CaptureLightIntensity(Process):

    def __init__(self, shutdown_event, data_queue, hall_pin, num_cycles, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clk_val = 0
        self.NUM_CYCLES = num_cycles * 2
        self.HALL_PIN = hall_pin
        self.buffer_size = 40000
        self.shutdown_event = shutdown_event

        self.spi = SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 20000000
        self.spi.mode = 0

        self.data_queue = data_queue

        self.buffer = np.ndarray(shape=(self.buffer_size, 1), dtype=np.uint16)

    def read_adc(self, sample_num) -> None:
        resp = self.spi.xfer2([0x00, 0x00])
        self.buffer[sample_num] = (resp[0] << 8) + resp[1]

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

            return S0, S1, S2, S3, num_of_samples
        else:
            return 0, 0, 0, 0, 0

    def run(self) -> None:

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        while not self.shutdown_event.is_set():
                try:

                    sample_num = 0
                    clock_val = 0
                    GPIO.wait_for_edge(self.HALL_PIN, GPIO.RISING)
                    old_signal = 1

                    while 1:

                        new_signal = GPIO.input(self.HALL_PIN)

                        if not old_signal == new_signal:
                            old_signal = new_signal
                            clock_val += 1
                            if clock_val >= self.NUM_CYCLES:
                                break

                        self.read_adc(sample_num)
                        sample_num += 1

                    data = self.process_data(self.NUM_CYCLES, sample_num)
                    self.data_queue.put(data)

                except Exception as e:
                    print(e)

    def close(self) -> None:
        self.spi.close()
        GPIO.cleanup()
