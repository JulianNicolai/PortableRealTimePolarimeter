import spidev
import time


class ADCController:

    def __init__(self, bus=0, device=0, max_speed_hz=500000):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = max_speed_hz
        self.spi.mode = 0

    def read_adc(self):
        resp = self.spi.xfer2([0x00, 0x00])
        value = (resp[0] << 8) + resp[1]
        return value

    def calculate_voltage(self, adc_value, reference_voltage=4.096):
        return (adc_value * reference_voltage) / 4095

    def close(self):
        self.spi.close()


try:
    adc = ADCController()
    while True:
        adc_value = adc.read_adc()
        voltage = adc.calculate_voltage(adc_value)
        print(f"{adc_value:016b} -> {voltage:.2f} V")
        time.sleep(0.1)

except KeyboardInterrupt:
    adc.close()
