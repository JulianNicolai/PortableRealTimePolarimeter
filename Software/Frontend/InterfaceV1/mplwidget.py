# https://stackoverflow.com/questions/43947318/plotting-matplotlib-figure-inside-qwidget-using-qt-designer-form-and-pyqt5/44029435

from PyQt5 import QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import matplotlib
import numpy as np

# Ensure using PyQt5 backend
matplotlib.use('QT5Agg')


# Matplotlib canvas class to create figure
class MplCanvas(Canvas):
    def __init__(self):

        self.fig = Figure((439, 439))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.fig.subplots_adjust(0, 0, 1, 1)
        self.ax.axis('off')
        self.ax.set_box_aspect((1, 1, 0.9), zoom=1.6)
        self.ax.invert_yaxis()

        # Make spherical surface data
        sphere_surface_numpoints = 13
        r = 1
        u = np.linspace(0, 2 * np.pi, sphere_surface_numpoints)
        v = np.linspace(0, np.pi, sphere_surface_numpoints)
        x = r * np.outer(np.cos(u), np.sin(v))
        y = r * np.outer(np.sin(u), np.sin(v))
        z = r * np.outer(np.ones(np.size(u)), np.cos(v))

        # Plot the spherical surface
        self.ax.plot_surface(x, y, z, color='linen', alpha=0.15)

        # Plot circular curves over the surface
        circular_lines_numpoints = 25
        theta = np.linspace(0, 2 * np.pi, circular_lines_numpoints)
        z = np.zeros(circular_lines_numpoints)
        x = r * np.sin(theta)
        y = r * np.cos(theta)

        line_alpha = 0.5
        line_color = 'black'
        self.ax.plot(x, y, z, color=line_color, alpha=line_alpha)  # Plot XY plane
        self.ax.plot(z, x, y, color=line_color, alpha=line_alpha)  # Plot ZX plane
        self.ax.plot(y, z, x, color=line_color, alpha=line_alpha)  # Plot YZ plane

        neg = -r - 0.1
        pos = r + 0.1
        x_list = [neg, pos, 0.0, 0.0, 0.0, 0.0]
        y_list = [0.0, 0.0, neg, pos, 0.0, 0.0]
        z_list = [0.0, 0.0, 0.0, 0.0, neg, pos]
        str_list = ["-45", "+45", "V", "H", "L", "R"]
        for xp, yp, zp, strp in zip(x_list, y_list, z_list, str_list):
            self.ax.text(xp, yp, zp, strp, size=20, zorder=1, color='k',
                         horizontalalignment='center', verticalalignment='center')

        # Plot axis lines
        axis_lines_numpoints = 2
        zeros = np.zeros(axis_lines_numpoints)
        line = np.linspace(-1.05, 1.05, axis_lines_numpoints)

        self.ax.plot(line, zeros, zeros, color=line_color, alpha=line_alpha)  # Plot X axis
        self.ax.plot(zeros, line, zeros, color=line_color, alpha=line_alpha)  # Plot Y axis
        self.ax.plot(zeros, zeros, line, color=line_color, alpha=line_alpha)  # Plot Z axis

        # Plot vector and red point. Using dummy data, will be updated using current polarisation.
        self.polarisation_line, = self.ax.plot([0, 0.75], [0, 0.75], [0, 0.75], color='red')
        self.polarisation_point, = self.ax.plot([0.75], [0.75], [0.75], 'ro')

        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        Canvas.updateGeometry(self)


# Matplotlib widget
class MplWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)   # Inherit from QWidget
        self.canvas = MplCanvas()                  # Create canvas object
        self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
