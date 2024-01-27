from PyQt5.QtCore import pyqtSignal, QObject
from multiprocessing import Pipe, Event


class InterprocessCommunicationHub(QObject):

    signal = pyqtSignal(int)

    def __init__(
            self,
            collect_data_event: Event,
            init_shutdown_event: Event,
            *args,
            **kwargs
    ) -> None:
        super(InterprocessCommunicationHub, self).__init__(*args, **kwargs)
        self.pipe_connection_receiver, self.pipe_connection_sender = Pipe()
        self.collect_data_event = collect_data_event
        self.init_shutdown_event = init_shutdown_event

    def listen(self) -> None:

        while not self.init_shutdown_event.is_set():

            msg = self.pipe_connection_receiver.recv()

            # ignore error: "Cannot find reference 'emit' in 'pyqtSignal | pyqtSignal'"
            self.signal.emit(msg)

    def get_pipe_connection_sender(self):
        return self.pipe_connection_sender

    def close(self) -> None:
        self.pipe_connection_receiver.close()