import RPi.GPIO as GPIO
import time

class DRV5011ADLPGM:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def wait_for_magnetic_field(self):
        print("Waiting for magnetic field detection...")
        GPIO.wait_for_edge(self.pin, GPIO.FALLING)
        print("Magnetic field detected!")

    def run(self):
        try:
            while True:
                self.wait_for_magnetic_field()
        except KeyboardInterrupt:
            self.cleanup()

    def cleanup(self):
        print("Cleaning up GPIO...")
        GPIO.cleanup()

# Usage
if __name__ == "__main__":
    hall_sensor = DRV5011ADLPGM(23)
    DRV5011ADLPGM.run()
