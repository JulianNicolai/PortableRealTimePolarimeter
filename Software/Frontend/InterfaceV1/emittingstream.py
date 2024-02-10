from PyQt5 import QtCore


class EmittingStream(QtCore.QObject):
    """Class used to redirect stdout and stderr steams (i.e. console output/print statements) to the main thread to be
    displayed within GUI log."""

    statement = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(EmittingStream, self).__init__(parent)

    def write(self, text):
        if text != '\n':
            self.statement.emit(str(text))
