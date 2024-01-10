import sys
from PyQt5 import QtWidgets
from gui import Interface


class Main:

    def __init__(self, argv):
        app = QtWidgets.QApplication(argv)
        window = Interface()
        window.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    Main(sys.argv)
