from typing import Tuple
import RPi.GPIO as GPIO
import time
from multiprocessing import Event, Queue, Process
from scipy.fft import fft
import numpy as np


class CaptureLightIntensity(Process):

    def __init__(self, shutdown_event, button_pin, num_cycles, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clk_val = 0
        self.NUM_CYCLES = num_cycles
        self.BUTTON_PIN = button_pin
        self.shutdown_event = shutdown_event

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.BUTTON_PIN, GPIO.FALLING, callback=self.inc)

        self.spi = SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 15000000
        self.spi.mode = 0

        self.active_gather_event = Event()
        self.active_gather_event.clear()

        self.data_queue = Queue()

        self.buffer = np.ndarray(shape=(25000, 1), dtype=np.uint16)

        # gather_process = GatherData(self.shutdown_event, self.active_gather_event, data_queue, self.NUM_CYCLES)
        # gather_process.start()

    def inc(self, channel):
        if channel == 17:
            if self.clk_val < self.NUM_CYCLES:
                self.clk_val += 1
                if self.clk_val == 1:
                    self.active_gather_event.set()
                    # print("Collecting samples...")
            else:
                self.clk_val = 0
                self.active_gather_event.clear()
                # print(f"Computing samples...")
            print(f"i = {self.clk_val}")

    def read_adc(self):
        resp = self.spi.xfer2([0x00, 0x00])
        return (resp[0] << 8) + resp[1]

    def process_data(self, num_of_cycles, num_of_samples) -> Tuple:
        data = self.buffer[0:num_of_samples]
        y = fft(data)  # MUST slice the exact number of samples. Cannot use entire buffer.
        print("Processing...")
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

    def run(self) -> None:

        while not self.shutdown_event.is_set():

            sample_num = 0
            self.active_gather_event.wait()

            while self.active_gather_event.is_set():
                self.buffer[sample_num] = self.read_adc()
                sample_num += 1
            data = self.process_data(self.NUM_CYCLES, sample_num)
            # self.data_queue.put(data)
            print(data)

    def close(self) -> None:
        self.spi.close()
        GPIO.cleanup()


if __name__ == "__main__":

    shutdown_event = Event()
    shutdown_event.clear()

    clock_counter = CaptureLightIntensity(shutdown_event, 17, 5)

    try:
        while True:
            time.sleep(0.2)
            clock_counter.inc(17)
    except KeyboardInterrupt:
        shutdown_event.set()
        # GPIO.cleanup()
