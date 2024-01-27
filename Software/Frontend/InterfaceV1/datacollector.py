from multiprocessing import Process, Event, Pipe
from multiprocessing.connection import Connection

import numpy as np
from Devices.photodiode_FAKE import Photodiode


class DataCollector(Process):

    def __init__(self,
                 buffer_size: int,
                 frame_buffer_data_0: np.ndarray,
                 frame_buffer_data_1: np.ndarray,
                 pipe_connection_sender: Connection,
                 collect_data_event: Event,
                 init_shutdown_event: Event):
        super().__init__()

        self.collect_data_event = collect_data_event
        self.init_shutdown_event = init_shutdown_event
        self.pipe_connection_sender = pipe_connection_sender
        self.buffer_size = buffer_size

        self.frame_buffer_data_0 = frame_buffer_data_0
        self.frame_buffer_data_1 = frame_buffer_data_1
        self.current_frame_buffer = self.frame_buffer_data_0
        self.photodiode = Photodiode()

    def swap_buffer(self):
        if self.current_frame_buffer is self.frame_buffer_data_1:
            self.current_frame_buffer = self.frame_buffer_data_0
        else:
            self.current_frame_buffer = self.frame_buffer_data_1

    def run(self):

        while not self.init_shutdown_event.is_set():

            i = 0
            while self.collect_data_event.is_set():
                if i >= self.buffer_size - 1:
                    i = 0
                    self.swap_buffer()
                    self.pipe_connection_sender.send(0)

                self.current_frame_buffer[i] = self.photodiode.read_adc()
                i += 1

    def stop(self):
        self.pipe_connection_sender.close()
        self.terminate()
