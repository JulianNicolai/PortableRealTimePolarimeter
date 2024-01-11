# https://stackoverflow.com/questions/43947318/plotting-matplotlib-figure-inside-qwidget-using-qt-designer-form-and-pyqt5/44029435

# Imports
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

        # Make data
        r = 1
        u = np.linspace(0, 2 * np.pi, 13)
        v = np.linspace(0, np.pi, 13)
        x = r * np.outer(np.cos(u), np.sin(v))
        y = r * np.outer(np.sin(u), np.sin(v))
        z = r * np.outer(np.ones(np.size(u)), np.cos(v))

        # Plot the surface
        self.ax.plot_surface(x, y, z, color='linen', alpha=0.15)

        # plot circular curves over the surface
        theta = np.linspace(0, 2 * np.pi, 25)
        z = np.zeros(25)
        x = r * np.sin(theta)
        y = r * np.cos(theta)

        self.ax.plot(x, y, z, color='black', alpha=0.5)
        self.ax.plot(z, x, y, color='black', alpha=0.5)
        self.ax.plot(y, z, x, color='black', alpha=0.5)

        x_list = [-1.1,  1.1,  0.0, 0.0,  0.0, 0.0]
        y_list = [ 0.0,  0.0, -1.1, 1.1,  0.0, 0.0]
        z_list = [ 0.0,  0.0,  0.0, 0.0, -1.1, 1.1]
        str_list = ["-45", "+45", "V", "H", "L", "R"]
        for xp, yp, zp, strp in zip(x_list, y_list, z_list, str_list):
            self.ax.text(xp, yp, zp, strp, size=20, zorder=1, color='k',
                         horizontalalignment='center', verticalalignment='center')

        ## add axis lines
        zeros = np.zeros(2)
        line = np.linspace(-1.05, 1.05, 2)

        self.ax.plot(line, zeros, zeros, color='black', alpha=0.75)
        self.ax.plot(zeros, line, zeros, color='black', alpha=0.75)
        self.ax.plot(zeros, zeros, line, color='black', alpha=0.75)

        self.polarisation_line, = self.ax.plot([0, 0.15], [0, -0.52], [0, -0.43], color='red', alpha=1)
        self.polarisation_point, = self.ax.plot([0.15], [-0.52], [-0.43], 'ro')

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