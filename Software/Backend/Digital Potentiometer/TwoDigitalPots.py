import serial
import time 
import RPi.GPIO as GPIO
import spidev
import numpy as np
import matplotlib.pyplot as plt
import threading

class Digipot:
    def __init__(self, total_resistance=100000, bus=0, device=0, max_speed_hz=500000):
        self.total_resistance = total_resistance
        self.spi = spidev.SpiDev()
        self.bus = bus
        self.spi.open(bus, device)
        self.spi.max_speed_hz = max_speed_hz

    def write_pot(self, value):
        command_byte = 0x00
        data_byte = value & 0xFF
        self.spi.xfer([command_byte, data_byte])
        self.display_resistance(value)

    def display_resistance(self, value):
        resistance = self.total_resistance * (value / 255.0)

    def close(self):
        self.spi.close()

    def sweep(self):

        while True:
            for value in range(4):
                potentiometer_spi1.write_pot(value)  
                potentiometer_spi0.write_pot(value)
                time.sleep(0.01)
            for value in range(3, -1, -1):
                potentiometer_spi1.write_pot(value) 
                potentiometer_spi0.write_pot(value)
                time.sleep(0.01)
    
try:
    potentiometer_spi0 = Digipot(bus=1, device=0)  
    potentiometer_spi1 = Digipot(bus=1, device=1)  
    potentiometer_spi0.sweep()
    
except KeyboardInterrupt:
    
    spi.close()


