from typing import Union
from pyqtgraph import ViewBox, AxisItem, mkPen, BarGraphItem, PlotWidget
from polcalc import PolarisationStateTracker


class InterfacePlotter:

    def __init__(self, interface):

        self.interface = interface

        self.interface.polarisation_ellipse_widget.disableAutoRange(ViewBox.XYAxes)
        self.interface.polarisation_ellipse_widget.setRange(yRange=(-1, 1), xRange=(-1, 1))
        # self.set_widget_titles(self.polarisation_ellipse_widget, left_text="2Ey0", bottom_text="2Ex0")
        self.polarisation_ellipse_plot = self.interface.polarisation_ellipse_widget.plot(pen=mkPen(color='red', width=3))
        self.interface.polarisation_ellipse_widget.getPlotItem().layout.setContentsMargins(0, 0, 0, 30)
        self.interface.polarisation_ellipse_widget.showGrid(x=True, y=True, alpha=0.4)
        self.interface.polarisation_ellipse_widget.setBackground('w')
        self.interface.polarisation_ellipse_widget.hideButtons()
        black_pen = mkPen(color='black', width=4)
        self.interface.polarisation_ellipse_widget.getAxis('bottom').setTextPen(black_pen)
        self.interface.polarisation_ellipse_widget.getAxis('left').setTextPen(black_pen)
        self.interface.polarisation_ellipse_widget.setMouseEnabled(x=False, y=False)

        self.calc = PolarisationStateTracker()
        self.generate_random_polarisation()
        self.update_plots()

        self.stokes_parameters_plot = self.interface.stokes_parameters_widget.plot()
        self.interface.stokes_parameters_widget.getPlotItem().layout.setContentsMargins(0, 0, 0, 30)
        self.interface.stokes_parameters_widget.setMouseEnabled(x=False, y=False)
        self.interface.stokes_parameters_widget.setRange(yRange=(-1, 1))
        self.interface.stokes_parameters_widget.showGrid(x=True, y=True, alpha=0.4)
        self.interface.stokes_parameters_widget.hideButtons()
        self.interface.stokes_parameters_widget.setBackground('w')
        self.interface.stokes_parameters_widget.getAxis('bottom').setTextPen(black_pen)
        self.interface.stokes_parameters_widget.getAxis('left').setTextPen(black_pen)
        self.interface.stokes_parameters_widget.setMouseEnabled(x=False, y=False)
        self.interface.stokes_parameters_widget.getAxis('bottom').setTicks([[(1, "S0"), (2, "S1"), (3, "S2"), (4, "S3")]])

        stokes_x = [1, 2, 3, 4]
        stokes_y = [0, 0, 0, 0]
        self.stokes_bar_graph = BarGraphItem(x=stokes_x, height=stokes_y, width=0.8, brush='r')
        self.interface.stokes_parameters_widget.addItem(self.stokes_bar_graph)

    def generate_random_polarisation(self):
        self.calc.generate_random_polarisation()

    def update_plots(self):

        tab_index = self.interface.tab_widget.currentIndex()
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
                self.interface.s0_value_xyplot.setText(S0_value_str)
                self.interface.s1_value_xyplot.setText(S1_value_str)
                self.interface.s2_value_xyplot.setText(S2_value_str)
                self.interface.s3_value_xyplot.setText(S3_value_str)
                self.interface.dop_value_xyplot.setText(DOP_value_str)
                self.interface.handedness_value_xyplot.setText(handed_value_str)
                self.plot_polarisation_ellipse()

            elif tab_index == 1:
                self.interface.s0_value_barchart.setText(S0_value_str)
                self.interface.s1_value_barchart.setText(S1_value_str)
                self.interface.s2_value_barchart.setText(S2_value_str)
                self.interface.s3_value_barchart.setText(S3_value_str)
                self.interface.dop_value_barchart.setText(DOP_value_str)
                self.interface.handedness_value_barchart.setText(handed_value_str)
                self.plot_stokes_parameters()

            else:
                self.interface.s0_value_xyzplot.setText(S0_value_str)
                self.interface.s1_value_xyzplot.setText(S1_value_str)
                self.interface.s2_value_xyzplot.setText(S2_value_str)
                self.interface.s3_value_xyzplot.setText(S3_value_str)
                self.interface.dop_value_xyzplot.setText(DOP_value_str)
                self.interface.handedness_value_xyzplot.setText(handed_value_str)
                self.plot_stokes_vector(S2/S0, S1/S0, S3/S0)

    def plot_polarisation_ellipse(self):
        x, y = self.calc.get_polarisation_ellipse_xy_data()
        self.polarisation_ellipse_plot.setData(x, y)  # Used to update plot in realtime

    def plot_stokes_parameters(self):
        stokes_y = self.calc.get_stokes_params()
        self.stokes_bar_graph.setOpts(height=stokes_y)  # Used to update bar graph in realtime

    def plot_stokes_vector(self, x, y, z):
        line = self.interface.poincare_sphere_widget.canvas.polarisation_line
        line.set_data([0, x], [0, y])
        line.set_3d_properties([0, z])
        point = self.interface.poincare_sphere_widget.canvas.polarisation_point
        point.set_data([x], [y])
        point.set_3d_properties([z])
        self.interface.poincare_sphere_widget.canvas.fig.canvas.draw_idle()

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
