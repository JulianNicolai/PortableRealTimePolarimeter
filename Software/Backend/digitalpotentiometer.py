import spidev
import time

class digipot:
    def __init__(self, total_resistance=100000, bus=0, device=0, max_speed_hz=500000):
        self.total_resistance = total_resistance
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
        print(f"Current resistance: {resistance:0.2f} ohms")

    def close(self):
        self.spi.close()

try:
    potentiometer = digipot()
    value = input("Please enter a value between 0 and 254: ")
    potentiometer.write_pot(int(value))
except ValueError:
    print("Invalid input! Please enter a numeric value.")
except KeyboardInterrupt:
    potentiometer.close()
