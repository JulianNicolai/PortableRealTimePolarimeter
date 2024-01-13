import sys
from datetime import datetime
from typing import Union
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtCore import QTimer
from pyqtgraph.widgets import PlotWidget
from pyqtgraph import ViewBox, AxisItem, mkPen, BarGraphItem
from emittingstream import EmittingStream
from polcalc import PolarisationStateTracker
from sys import platform
from interfaceconfig import Configuration


class Interface(QtWidgets.QMainWindow):

    path_linux = "/home/polarimeter/Documents/PortableRealTimePolarimeter/Software/Frontend/InterfaceV1/gui.ui"
    path_windows = "gui.ui"
    linux_flag = False

    def __init__(self, in_production_flag: bool):
        super(Interface, self).__init__()  # Call the inherited classes __init__ method
        if platform == "win32":
            path = self.path_windows
        else:
            self.linux_flag = True
            path = self.path_linux
        uic.loadUi(path, self)  # Load the .ui file
        self.setFixedSize(self.size())  # Disables window resizing
        self.setWindowTitle("Real-Time Portable Polarimeter")
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # Used to hide window frame
        self.move(0, 0)  # Move frame to top left of screen
        if self.linux_flag:
            self.showMaximized()

        self.IN_PRODUCTION = in_production_flag

        if self.IN_PRODUCTION:
            # Send print output stream to log display (enable for production only!)
            stream_out = EmittingStream()
            stream_out.statement.connect(self.output_stream_to_log)
            sys.stdout = stream_out

            stream_err = EmittingStream()
            stream_err.statement.connect(self.error_stream_to_log)
            sys.stderr = stream_err

        self.rand_stokes_button_xyplot.clicked.connect(self.generate_random_polarisation)
        self.rand_stokes_button_barchart.clicked.connect(self.generate_random_polarisation)
        self.rand_stokes_button_xyzplot.clicked.connect(self.generate_random_polarisation)
        self.tab_widget.currentChanged.connect(self.update_plots)

        self.config = Configuration(self)

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

        self.polarisation_ellipse_widget.disableAutoRange(ViewBox.XYAxes)
        self.polarisation_ellipse_widget.setRange(yRange=(-1, 1), xRange=(-1, 1))
        # self.set_widget_titles(self.polarisation_ellipse_widget, left_text="2Ey0", bottom_text="2Ex0")
        self.polarisation_ellipse_plot = self.polarisation_ellipse_widget.plot(pen=mkPen(color='red', width=3))
        self.polarisation_ellipse_widget.getPlotItem().layout.setContentsMargins(0, 0, 0, 30)
        self.polarisation_ellipse_widget.showGrid(x=True, y=True, alpha=0.4)
        self.polarisation_ellipse_widget.setBackground('w')
        self.polarisation_ellipse_widget.hideButtons()
        black_pen = mkPen(color='black', width=4)
        self.polarisation_ellipse_widget.getAxis('bottom').setTextPen(black_pen)
        self.polarisation_ellipse_widget.getAxis('left').setTextPen(black_pen)
        self.polarisation_ellipse_widget.setMouseEnabled(x=False, y=False)

        self.calc = PolarisationStateTracker()
        self.calc.generate_random_polarisation()
        self.update_plots()

        self.stokes_parameters_plot = self.stokes_parameters_widget.plot()
        self.stokes_parameters_widget.getPlotItem().layout.setContentsMargins(0, 0, 0, 30)
        self.stokes_parameters_widget.setMouseEnabled(x=False, y=False)
        self.stokes_parameters_widget.setRange(yRange=(-1, 1))
        self.stokes_parameters_widget.showGrid(x=True, y=True, alpha=0.4)
        self.stokes_parameters_widget.hideButtons()
        self.stokes_parameters_widget.setBackground('w')
        self.stokes_parameters_widget.getAxis('bottom').setTextPen(black_pen)
        self.stokes_parameters_widget.getAxis('left').setTextPen(black_pen)
        self.stokes_parameters_widget.setMouseEnabled(x=False, y=False)
        self.stokes_parameters_widget.getAxis('bottom').setTicks([[(1, "S0"), (2, "S1"), (3, "S2"), (4, "S3")]])

        stokes_x = [1, 2, 3, 4]
        stokes_y = [0, 0, 0, 0]
        self.stokes_bar_graph = BarGraphItem(x=stokes_x, height=stokes_y, width=0.8, brush='r')
        self.stokes_parameters_widget.addItem(self.stokes_bar_graph)

        self.start_stop_button.clicked.connect(self.system_control)

        print("System initialized. Ready to begin measurement.")

    def system_control(self):
        if self.start_stop_button.isChecked():
            self.start_stop_button.setEnabled(False)
            QTimer.singleShot(1000, lambda: self.start_stop_button.setDisabled(False))
            print("System started!")
        else:
            print("System stopped!")

    def output_stream_to_log(self, statement):
        timestamp = datetime.now().strftime("%y-%m-%d %H:%M:%S")
        self.log_textbox.append(f"<span>[{timestamp}] {statement}</span>")

    def error_stream_to_log(self, statement):
        timestamp = datetime.now().strftime("%y-%m-%d %H:%M:%S")
        self.log_textbox.append(f"<span style='color:red'>[{timestamp}] {statement}</span>")

    def generate_random_polarisation(self):
        self.calc.generate_random_polarisation()
        self.update_plots()

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
        timestamp = datetime.now().strftime("%y%m%dT%H%M%S")
        filename = f"logs/log-{timestamp}.txt"
        data = self.log_textbox.toPlainText()
        with open(filename, 'w') as file:
            file.write(data)
        print(f"Log saved to disc successfully to: ./{filename}")

    def update_plots(self):

        tab_index = self.tab_widget.currentIndex()
        if 0 <= tab_index <= 2:
            S0, S1, S2, S3 = self.calc.get_stokes_params()
            DOP = self.calc.get_dop()
            right_handed = True if S3 > 0 else False

            S0_value_str = f'{S0:+.5f}'
            S1_value_str = f'{S1:+.5f}'
            S2_value_str = f'{S2:+.5f}'
            S3_value_str = f'{S3:+.5f}'
            DOP_value_str = f'{DOP * 100:.2f}%'
            handed_value_str = "RIGHT" if right_handed else "LEFT"

            if tab_index == 0:
                self.s0_value_xyplot.setText(S0_value_str)
                self.s1_value_xyplot.setText(S1_value_str)
                self.s2_value_xyplot.setText(S2_value_str)
                self.s3_value_xyplot.setText(S3_value_str)
                self.dop_value_xyplot.setText(DOP_value_str)
                self.handedness_value_xyplot.setText(handed_value_str)
                self.plot_polarisation_ellipse()

            elif tab_index == 1:
                self.s0_value_barchart.setText(S0_value_str)
                self.s1_value_barchart.setText(S1_value_str)
                self.s2_value_barchart.setText(S2_value_str)
                self.s3_value_barchart.setText(S3_value_str)
                self.dop_value_barchart.setText(DOP_value_str)
                self.handedness_value_barchart.setText(handed_value_str)
                self.plot_stokes_parameters()

            else:
                self.s0_value_xyzplot.setText(S0_value_str)
                self.s1_value_xyzplot.setText(S1_value_str)
                self.s2_value_xyzplot.setText(S2_value_str)
                self.s3_value_xyzplot.setText(S3_value_str)
                self.dop_value_xyzplot.setText(DOP_value_str)
                self.handedness_value_xyzplot.setText(handed_value_str)
                self.plot_stokes_vector(S2/S0, S1/S0, S3/S0)

    def plot_polarisation_ellipse(self):
        x, y = self.calc.get_polarisation_ellipse_xy_data()
        self.polarisation_ellipse_plot.setData(x, y)  # Used to update plot in realtime

    def plot_stokes_parameters(self):
        stokes_y = self.calc.get_stokes_params()
        self.stokes_bar_graph.setOpts(height=stokes_y)  # Used to update bar graph in realtime

    def plot_stokes_vector(self, x, y, z):
        line = self.poincare_sphere_widget.canvas.polarisation_line
        line.set_data([0, x], [0, y])
        line.set_3d_properties([0, z])
        point = self.poincare_sphere_widget.canvas.polarisation_point
        point.set_data([x], [y])
        point.set_3d_properties([z])
        self.poincare_sphere_widget.canvas.fig.canvas.draw_idle()

    @staticmethod
    def set_widget_titles(
            widget: PlotWidget,
            left_text: str = "",
            left_units: Union[str, None] = None,
            bottom_text: str = "",
            bottom_units: Union[str, None] = None
    ) -> None:
        """
        Method to set the titles, axis, and format of pyqtgraph plots (i.e. frequency/spectrum plot)
        :param widget: pyqtgraph PlotWidget to modify
        :param left_text: String on left vertical axis
        :param left_units: String for left vertical axis units
        :param bottom_text: String for bottom horizontal axis
        :param bottom_units: String for bottom horizontal units
        :return: None
        """
        label_style = {'color': '#999', 'font-size': '10pt'}
        left_axis = AxisItem('left')
        left_axis.setLabel(text=left_text, units=left_units, **label_style)
        bottom_axis = AxisItem('bottom')
        bottom_axis.setLabel(text=bottom_text, units=bottom_units, **label_style)
        bottom_axis.enableAutoSIPrefix(False)
        widget.setAxisItems(axisItems={'left': left_axis, 'bottom': bottom_axis})

    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
