import spidev
import time
import random


class TIAGainControl:
    def __init__(self, total_resistance=100000, bus=0, device=0, max_speed_hz=1000000):
        self.total_resistance = total_resistance  # Set the total resistance to 100kΩ
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = max_speed_hz

        self.address_word = 0x20
        self.read_word = 0x00
        self.write_word = 0x0C

        self.current_value = 36

    def write_value(self, value):
        if 0 <= value <= 255:
            command_byte = self.address_word | self.write_word
            data_byte = value & 0xFF
            self.spi.xfer([command_byte, data_byte])

    def read_value(self):
        command_byte = self.address_word | self.read_word
        data_byte = 0xFF
        value = self.spi.xfer([command_byte, data_byte])
        if value & 512 == 512:
            return value & 255

    def display_resistance(self, value):
        # Calculate the resistance based on the wiper position
        resistance = self.total_resistance * (value / 255.0)
        print(f"Current resistance: {resistance:.2f} ohms")

    def close(self):
        self.spi.close()


# Usage
if __name__ == "__main__":

    potentiometer = TIAGainControl()

    try:
        while True:
            recv_value = potentiometer.read_value()
            print(f"Received value: {recv_value}")
            time.sleep(1)
            value = random.randint(0, 255)
            print(f"Setting value to: {value}")
            potentiometer.write_value(value)
            time.sleep(1)

    except KeyboardInterrupt:
        potentiometer.close()
