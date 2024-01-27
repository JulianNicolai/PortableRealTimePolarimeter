from Devices.photodiode_FAKE import Photodiode
from Devices.hallsensor import HallSensor
from Devices.digitalpot import DigitalPotentiometer

class Devices:

    def __init__(self, hall_sensor_pin, spi_bus=0, spi_device=0):

        self.photodiode = Photodiode()
        self.hall_sensor = HallSensor(hall_sensor_pin)
        self.digital_potentiometer = DigitalPotentiometer(bus=spi_bus, device=spi_device)