from PyQt5 import QtCore


class EmittingStream(QtCore.QObject):

    statement = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(EmittingStream, self).__init__(parent)

    def write(self, text):
        if text != '\n':
            self.statement.emit(str(text))
