import sys
from datetime import datetime
from multiprocessing import Event, Pipe, shared_memory

import numpy as np
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtCore import QTimer, QThread, pyqtSlot

from datacollector import DataCollector
from emittingstream import EmittingStream
from interfaceplots import InterfacePlotter
from sys import platform
from interfaceconfig import Configuration
from interprocesscommhub import InterprocessCommunicationHub


class Interface(QtWidgets.QMainWindow):

    PATH_LINUX = "/home/polarimeter/Documents/PortableRealTimePolarimeter/Software/Frontend/InterfaceV1/gui.ui"
    PATH_WINDOWS = "gui.ui"

    def __init__(self, in_production_flag: bool):

        super(Interface, self).__init__()  # Call the inherited classes __init__ method

        self.IN_PRODUCTION = in_production_flag

        if platform == "win32":
            self.linux_flag = False
            path = self.PATH_WINDOWS
        else:
            self.linux_flag = True
            path = self.PATH_LINUX

        uic.loadUi(path, self)  # Load the .ui file
        self.setFixedSize(self.size())  # Disables window resizing
        self.setWindowTitle("Real-Time Portable Polarimeter")
        self.move(0, 0)  # Move frame to top left of screen

        if self.linux_flag:
            self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # Used to hide window frame
            self.showMaximized()  # Used to fullscreen the interface.

        if self.IN_PRODUCTION:
            # Send print output stream to log display (enable for production only!)
            stream_out = EmittingStream()
            stream_out.statement.connect(self.output_stream_to_log)
            sys.stdout = stream_out

            stream_err = EmittingStream()
            stream_err.statement.connect(self.error_stream_to_log)
            sys.stderr = stream_err

        self.config = Configuration(self)

        self.plotter = InterfacePlotter(self)

        self.rand_stokes_button_xyplot.clicked.connect(self.generate_random_polarisation)
        self.rand_stokes_button_barchart.clicked.connect(self.generate_random_polarisation)
        self.rand_stokes_button_xyzplot.clicked.connect(self.generate_random_polarisation)
        self.tab_widget.currentChanged.connect(self.update_plots)

        self.minus_1.clicked.connect(lambda: self.change_config_value(-1))
        self.minus_10.clicked.connect(lambda: self.change_config_value(-10))
        self.minus_100.clicked.connect(lambda: self.change_config_value(-100))
        self.minus_1000.clicked.connect(lambda: self.change_config_value(-1000))
        self.plus_1.clicked.connect(lambda: self.change_config_value(1))
        self.plus_10.clicked.connect(lambda: self.change_config_value(10))
        self.plus_100.clicked.connect(lambda: self.change_config_value(100))
        self.plus_1000.clicked.connect(lambda: self.change_config_value(1000))

        self.reset_parameters_button.clicked.connect(self.reset_config_parameters)
        self.apply_config_button.clicked.connect(self.apply_config_parameters)
        self.save_config_button.clicked.connect(self.save_config_parameters)
        self.save_log_button.clicked.connect(self.save_log)

        self.start_stop_button.clicked.connect(self.system_control)

        self.collect_data_event = Event()
        self.init_shutdown_event = Event()

        self.buffer_size = 6400

        buffer = np.ndarray(shape=(self.buffer_size,), dtype=np.uint16)
        shared_memory_space_0 = shared_memory.SharedMemory(create=True, size=buffer.nbytes)
        shared_memory_space_1 = shared_memory.SharedMemory(create=True, size=buffer.nbytes)
        self.frame_buffer_data_0 = np.ndarray(shape=buffer.shape, dtype=buffer.dtype, buffer=shared_memory_space_0.buf)
        self.frame_buffer_data_1 = np.ndarray(shape=buffer.shape, dtype=buffer.dtype, buffer=shared_memory_space_1.buf)
        self.current_frame_buffer = self.frame_buffer_data_1

        self.data_collector = None

        # self.start_workers()

        print("System initialized. Ready to begin measurement.")

    def system_control(self):
        if self.start_stop_button.isChecked():
            self.start_stop_button.setEnabled(False)
            self.collect_data_event.set()
            QTimer.singleShot(1000, lambda: self.start_stop_button.setDisabled(False))
            print("System started!")
        else:
            self.collect_data_event.clear()
            print("System stopped!")

    def start_workers(self):

        self.collect_data_event.clear()
        self.init_shutdown_event.clear()

        self.inter_comm_hub_worker = InterprocessCommunicationHub(
            self.collect_data_event,
            self.init_shutdown_event
        )
        self.pipe_connection_sender = self.inter_comm_hub_worker.get_pipe_connection_sender()
        self.inter_comm_hub_thread = QThread()
        self.inter_comm_hub_worker.moveToThread(self.inter_comm_hub_thread)
        self.inter_comm_hub_thread.started.connect(self.inter_comm_hub_worker.listen)
        self.inter_comm_hub_worker.signal.connect(self.process_filled_buffer)
        self.inter_comm_hub_thread.start()

        self.data_collector = DataCollector(self.buffer_size,
                                            self.frame_buffer_data_0,
                                            self.frame_buffer_data_1,
                                            self.pipe_connection_sender,
                                            self.collect_data_event,
                                            self.init_shutdown_event)
        self.data_collector.start()

    @pyqtSlot(int)
    def process_filled_buffer(self, value: int):
        self.swap_buffer()
        # num_of_cycles = self.config.get_rotations_per_frame()
        # num_of_samples = self.config.get_samples_per_frame()
        num_of_cycles = 64
        num_of_samples = 6400
        self.plotter.calc.calculate_stokes_from_measurements(self.current_frame_buffer, num_of_cycles, num_of_samples)

    def swap_buffer(self):
        if self.current_frame_buffer is self.frame_buffer_data_1:
            self.current_frame_buffer = self.frame_buffer_data_0
        else:
            self.current_frame_buffer = self.frame_buffer_data_1

    def output_stream_to_log(self, statement):
        timestamp = self.generate_timestamp(0)
        self.log_textbox.append(f"<span>[{timestamp}] {statement}</span>")

    def error_stream_to_log(self, statement):
        timestamp = self.generate_timestamp(0)
        self.log_textbox.append(f"<span style='color:red'>[{timestamp}] {statement}</span>")

    def generate_random_polarisation(self):
        self.plotter.generate_random_polarisation()
        self.plotter.update_plots()

    def change_config_value(self, value):
        if self.motor_speed_button.isChecked():
            new_value = self.motor_speed_value.value() + value
            self.config.update_motor_speed_percent(new_value)
        elif self.rotations_frame_button.isChecked():
            new_value = self.rotations_frame_value.value() + value
            self.config.update_rotations_per_frame(new_value)
        else:
            new_value = self.samples_rotation_value.value() + value
            self.config.update_samples_per_rotation(new_value)

    def reset_config_parameters(self):
        self.config.reset()

    def apply_config_parameters(self):
        self.config.apply_config()

    def save_config_parameters(self):
        self.config.save_config()

    def save_log(self):
        timestamp = self.generate_timestamp(1)
        filename = f"logs/log-{timestamp}.txt"
        data = self.log_textbox.toPlainText()
        with open(filename, 'w') as file:
            file.write(data)
        print(f"Log saved to disc successfully to: ./{filename}")

    def update_plots(self):
        self.plotter.update_plots()

    def plot_polarisation_ellipse(self):
        self.plotter.plot_polarisation_ellipse()

    def plot_stokes_parameters(self):
        self.plotter.plot_stokes_parameters()

    def plot_stokes_vector(self, x, y, z):
        self.plotter.plot_stokes_vector(x, y, z)

    @staticmethod
    def generate_timestamp(format_type):
        if format_type == 0:
            format_string = "%y-%m-%d %H:%M:%S"
        else:
            format_string = "%y%m%dT%H%M%S"
        return datetime.now().strftime(format_string)

    def __del__(self):

        # Restore sys.stdout and sys.stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
