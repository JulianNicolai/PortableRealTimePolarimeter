import sys
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtCore import QTimer
from emittingstream import EmittingStream
from interfaceplots import InterfacePlotter
from sys import platform
from interfaceconfig import Configuration


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

        self.establish_button_connections()

        print("System initialized. Ready to begin measurement.")

    def system_control(self):
        if self.start_stop_button.isChecked():
            self.start_stop_button.setEnabled(False)
            QTimer.singleShot(1000, lambda: self.start_stop_button.setDisabled(False))
            print("System started!")
        else:
            print("System stopped!")

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

    def save_log(self):
        timestamp = self.generate_timestamp(1)
        filename = f"logs/log-{timestamp}.txt"
        data = self.log_textbox.toPlainText()
        with open(filename, 'w') as file:
            file.write(data)
        print(f"Log saved to disc successfully to: ./{filename}")

    def output_stream_to_log(self, statement):
        timestamp = self.generate_timestamp(0)
        self.log_textbox.append(f"<span>[{timestamp}] {statement}</span>")

    def error_stream_to_log(self, statement):
        timestamp = self.generate_timestamp(0)
        self.log_textbox.append(f"<span style='color:red'>[{timestamp}] {statement}</span>")

    def establish_button_connections(self):

        self.rand_stokes_button_xyplot.clicked.connect(self.generate_random_polarisation)
        self.rand_stokes_button_barchart.clicked.connect(self.generate_random_polarisation)
        self.rand_stokes_button_xyzplot.clicked.connect(self.generate_random_polarisation)
        self.tab_widget.currentChanged.connect(self.plotter.update_plots)

        self.minus_1.clicked.connect(lambda: self.change_config_value(-1))
        self.minus_10.clicked.connect(lambda: self.change_config_value(-10))
        self.minus_100.clicked.connect(lambda: self.change_config_value(-100))
        self.minus_1000.clicked.connect(lambda: self.change_config_value(-1000))
        self.plus_1.clicked.connect(lambda: self.change_config_value(1))
        self.plus_10.clicked.connect(lambda: self.change_config_value(10))
        self.plus_100.clicked.connect(lambda: self.change_config_value(100))
        self.plus_1000.clicked.connect(lambda: self.change_config_value(1000))

        self.reset_parameters_button.clicked.connect(self.config.reset)
        self.apply_config_button.clicked.connect(self.config.apply_config)
        self.save_config_button.clicked.connect(self.config.save_config)
        self.save_log_button.clicked.connect(self.save_log)

        self.start_stop_button.clicked.connect(self.system_control)

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
