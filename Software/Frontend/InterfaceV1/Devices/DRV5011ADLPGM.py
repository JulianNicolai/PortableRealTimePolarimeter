import RPi.GPIO as GPIO
import time

class MotorClock:
    # Device: DRV5011ADLPGM Hall effect sensor that monitors motor rotational speed.

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
                time.sleep(0.2)  # Debouncing
        except KeyboardInterrupt:
            self.cleanup()

    def cleanup(self):
        print("Cleaning up GPIO...")
        GPIO.cleanup()

# Usage
if __name__ == "__main__":
    hall_sensor = MotorClock(23)
    hall_sensor.run()
