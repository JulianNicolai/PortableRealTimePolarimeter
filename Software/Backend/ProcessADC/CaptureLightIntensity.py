# import RPi.GPIO as GPIO
import time
from multiprocessing import Event, Queue
from gatherdata import GatherData

class CaptureLightIntensity:

    def __init__(self, shutdown_event, button_pin, num_cycles):
        self.clk_val = 0
        self.NUM_CYCLES = num_cycles
        self.BUTTON_PIN = button_pin
        self.shutdown_event = shutdown_event

        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # GPIO.add_event_detect(self.BUTTON_PIN, GPIO.FALLING, callback=self.inc)

        self.active_gather_event = Event()
        self.active_gather_event.clear()

        data_queue = Queue()

        gather_process = GatherData(self.shutdown_event, self.active_gather_event, data_queue, self.NUM_CYCLES)
        gather_process.start()

    def inc(self, channel):
        if channel == 17:

            if self.clk_val < self.NUM_CYCLES:
                self.clk_val += 1
                if self.clk_val == 1:
                    self.active_gather_event.set()
                    print("Collecting samples...")
            else:
                self.clk_val = 0
                self.active_gather_event.clear()
                print(f"Computing samples...")
            print(f"i = {self.clk_val}")

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
