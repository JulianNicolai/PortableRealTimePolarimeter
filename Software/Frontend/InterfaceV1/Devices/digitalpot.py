import spidev
import time


class DigitalPotentiometer:
    def __init__(self, total_resistance=100000, bus=0, device=0, max_speed_hz=500000):
        self.total_resistance = total_resistance  # Set the total resistance to 100kΩ
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = max_speed_hz

    def write_pot(self, value):
        command_byte = 0x00
        data_byte = value & 0xFF
        self.spi.xfer([command_byte, data_byte])
        self.display_resistance(value)

    def display_resistance(self, value):
        # Calculate the resistance based on the wiper position
        resistance = self.total_resistance * (value / 255.0)
        print(f"Current resistance: {resistance:.2f} ohms")

    def sweep(self, sweep_range=256, delay=0.01):
        for i in range(sweep_range):
            self.write_pot(i)
            time.sleep(delay)
        for i in range(sweep_range - 1, -1, -1):
            self.write_pot(i)
            time.sleep(delay)

    def close(self):
        self.spi.close()


# Usage
if __name__ == "__main__":

    potentiometer = MotorControl()

    try:
        while True:
            potentiometer.sweep()
    except KeyboardInterrupt:
        potentiometer.close()
