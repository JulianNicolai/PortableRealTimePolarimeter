from PyQt5.QtCore import pyqtSignal, QObject
from multiprocessing import Event
import serial
import struct


class SerialReceiver(QObject):
    """
    The SerialReceiver object is seperate thread on the same process as the Interface
    that receives serial packets from the RPi Pico and forwards them to the
    Interface which handles the display.
    """
    signal = pyqtSignal(tuple)

    def __init__(
            self,
            *args,
            **kwargs
    ) -> None:
        super(SerialReceiver, self).__init__(*args, **kwargs)
        self.ser = serial.Serial('/dev/ttyS0', baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS, timeout=10)
        # self.ser = serial.Serial('COM1', baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
        #                 bytesize=serial.EIGHTBITS, timeout=10)

    def listen(self) -> None:

        while 1:

            start_bit = self.ser.read()
            if start_bit == b'$':
                while start_bit == b'$':
                    start_bit = self.ser.read()
                data = start_bit + self.ser.read(23)
                size = len(data)
                try:
                    unpacked = struct.unpack("IIffff", data)
                    # print(f"S: {unpacked[0]} | dt: {unpacked[1]} | S0: {unpacked[2]:.5f} | S1: {unpacked[2]:.5f} | S2: {unpacked[2]:.5f} | S3: {unpacked[2]:.5f}")
                    # emits the message that triggers the data_recv() function in the Interface
                    # ignore error: "Cannot find reference 'emit' in 'pyqtSignal | pyqtSignal'"
                    self.signal.emit(unpacked)
                except struct.error as e:
                    print(f"Packet Size: {size}\nError: {e}\nData: {data}")