import spidev
import time


class PhotodiodeMeasurement:
    # Device: MAX1242BCPA ADC IC measuring photodiode voltage.

    def __init__(self, bus=0, device=0, max_speed_hz=500000):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = max_speed_hz
        self.spi.mode = 0

    def read_adc(self):
        resp = self.spi.xfer2([0x00, 0x00])
        value = ((resp[0] & 0x0F) << 8) | resp[1]
        return value

    def calculate_voltage(self, adc_value, reference_voltage=3.3):
        return (adc_value * reference_voltage) / 4095

    def close(self):
        self.spi.close()


# Example usage
if __name__ == "__main__":

    adc = PhotodiodeMeasurement()

    try:
        while True:
            adc_value = adc.read_adc()
            print("ADC Value: %d" % adc_value)
            voltage = adc.calculate_voltage(adc_value)
            print("Potentiometer Voltage: %.2f V" % voltage)
            time.sleep(0.5)

    except KeyboardInterrupt:
        adc.close()
