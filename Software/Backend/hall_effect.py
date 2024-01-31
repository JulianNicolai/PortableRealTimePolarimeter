import RPi.GPIO as GPIO
import time


class HallClock:
    def __init__(self, num_cycles):
        self.clk_val = 0
        self.NUM_CYCLES = num_cycles

    def inc(self, channel):
        if channel == 17:
            if self.clk_val < self.NUM_CYCLES:
                self.clk_val += 1
            else:
                self.clk_val = 0
                print(f"Compute Sample")
            print(f"i = {clock_counter.clk_val}")


clock_counter = HallClock(5)

BUTTON_PIN = 17
GPIO.setmode(GPIO.BCM)

GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=clock_counter.inc)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
