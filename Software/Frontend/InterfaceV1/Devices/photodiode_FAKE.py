import time


class PhotodiodeMeasurement:
    # Device: MAX1242BCPA ADC IC measuring photodiode voltage.

    def __init__(self):
        pass

    def read_adc(self):
        resp = self.spi.xfer2([0x00, 0x00])
        value = ((resp[0] & 0x0F) << 8) | resp[1]
        return value

    def calculate_voltage(self, adc_value, reference_voltage=3.3):
        return (adc_value * reference_voltage) / 4095

    def close(self):
        self.spi.close()