import sys
import time
from datetime import datetime
from typing import Union

import numpy as np
import pyqtgraph
from PyQt5 import QtWidgets, QtCore, uic, QtGui
from pyqtgraph.widgets import PlotWidget
from pyqtgraph import ViewBox, AxisItem, mkPen, BarGraphItem, opengl

from EmittingStream import EmittingStream
from calculate import Calculator
from sys import platform


class Interface(QtWidgets.QMainWindow):

    path_linux = "/home/polarimeter/Documents/PortableRealTimePolarimeter/Software/Frontend/InterfaceV1/gui.ui"
    path_windows = "gui.ui"
    linux_flag = False
    def __init__(self):
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

        self.rand_stokes_button_xyplot.clicked.connect(self.generate_random_polarisation)
        self.rand_stokes_button_barchart.clicked.connect(self.generate_random_polarisation)
        self.rand_stokes_button_xyzplot.clicked.connect(self.generate_random_polarisation)
        self.tabWidget.currentChanged.connect(self.update_plots)

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

        self.calc = Calculator(256)
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

        # axis = opengl.GLAxisItem()
        # self.poincare_sphere_opengl_widget.addItem(axis)
        grid = opengl.GLGridItem()
        grid.setSize(5, 5, 5)
        grid.setColor("#00000040")
        self.poincare_sphere_opengl_widget.addItem(grid)
        self.poincare_sphere_opengl_widget.setBackgroundColor('w')

        # # Attempt to draw poincare sphere manually
        # RADIUS = 1
        # x_sphere_data = np.linspace(-RADIUS, RADIUS, 256)
        # y_sphere_data = x_sphere_data
        # z_sphere_data = np.zeros((256, 256))
        #
        # i = 0
        # for x in x_sphere_data:
        #     j = 0
        #     for y in y_sphere_data:
        #         z_sphere_data[i, j] = np.sqrt(RADIUS ** 2 - x ** 2 - y ** 2)
        #         j += 1
        #     i += 1
        #
        # z_sphere_data_neg = -z_sphere_data
        # colors = (1,1,256)
        # hemisphere0 = opengl.GLSurfacePlotItem(x_sphere_data, y_sphere_data, z_sphere_data, smooth=False, colors=colors)
        # hemisphere1 = opengl.GLSurfacePlotItem(x_sphere_data, y_sphere_data, z_sphere_data_neg, smooth=False, colors=colors)
        # self.poincare_sphere_opengl_widget.addItem(hemisphere0)
        # self.poincare_sphere_opengl_widget.addItem(hemisphere1)

        # # Send print output stream to log display (enable for production only!)
        # stream_out = EmittingStream()
        # stream_out.statement.connect(self.output_stream_to_log)
        # sys.stdout = stream_out

        # stream_err = EmittingStream()
        # stream_err.statement.connect(self.error_stream_to_log)
        # sys.stderr = stream_err

        self.start_stop_button.clicked.connect(self.system_control)

        print("System initialized. Ready to begin measurement.")

    def system_control(self):
        print("System started!")

    def output_stream_to_log(self, statement):
        timestamp = datetime.now().strftime("%y-%m-%d %H:%M:%S")
        self.log_textbox.append(f"<span>[{timestamp}] {statement}</span>")

    def error_stream_to_log(self, statement):
        timestamp = datetime.now().strftime("%y-%m-%d %H:%M:%S")
        self.log_textbox.append(f"<span style='color:red'>[{timestamp}] {statement}</span>")

    def generate_random_polarisation(self):
        self.calc.generate_random_polarisation()
        self.update_plots()

    def update_plots(self):

        tab_index = self.tabWidget.currentIndex()
        if 0 <= tab_index <= 2:
            S0, S1, S2, S3 = self.calc.get_stokes_params()
            DOP = self.calc.get_dop()
            right_handed = True if S3 > 0 else False

            if tab_index == 0:
                self.s0_value_xyplot.setText(f'{S0:+.5f}')
                self.s1_value_xyplot.setText(f'{S1:+.5f}')
                self.s2_value_xyplot.setText(f'{S2:+.5f}')
                self.s3_value_xyplot.setText(f'{S3:+.5f}')
                self.dop_value_xyplot.setText(f'{DOP * 100:.2f}%')
                if right_handed:
                    self.handedness_value_xyplot.setText("RIGHT")
                else:
                    self.handedness_value_xyplot.setText("LEFT")

                x, y = self.calc.get_polarisation_ellipse_xy_data()
                self.polarisation_ellipse_plot.setData(x, y)  # Used to update plot in realtime

            elif tab_index == 1:
                self.s0_value_barchart.setText(f'{S0:+.5f}')
                self.s1_value_barchart.setText(f'{S1:+.5f}')
                self.s2_value_barchart.setText(f'{S2:+.5f}')
                self.s3_value_barchart.setText(f'{S3:+.5f}')
                self.dop_value_barchart.setText(f'{DOP * 100:.2f}%')
                if right_handed:
                    self.handedness_value_barchart.setText("RIGHT")
                else:
                    self.handedness_value_barchart.setText("LEFT")

                stokes_y = self.calc.get_stokes_params()
                self.stokes_bar_graph.setOpts(height=stokes_y)  # Used to update bar graph in realtime

            else:
                self.s0_value_xyzplot.setText(f'{S0:+.5f}')
                self.s1_value_xyzplot.setText(f'{S1:+.5f}')
                self.s2_value_xyzplot.setText(f'{S2:+.5f}')
                self.s3_value_xyzplot.setText(f'{S3:+.5f}')
                self.dop_value_xyzplot.setText(f'{DOP * 100:.2f}%')
                if right_handed:
                    self.handedness_value_xyzplot.setText("RIGHT")
                else:
                    self.handedness_value_xyzplot.setText("LEFT")

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