import serial
from time import sleep
import struct

ser = serial.Serial('/dev/ttyS0', baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=10)

while 1:
    start_bit = ser.read()
    if start_bit == b'$':
        while start_bit == b'$':
            start_bit = ser.read()
        data = start_bit + ser.read(23)
        size = len(data)
        try:
            unpacked = struct.unpack("IIffff", data)
            print(f"S: {unpacked[0]} | dt: {unpacked[1]} | S0: {unpacked[2]:.5f} | S1: {unpacked[2]:.5f} | S2: {unpacked[2]:.5f} | S3: {unpacked[2]:.5f}")
        except struct.error as e:
            print(size)
            print(e)
            print(data)
