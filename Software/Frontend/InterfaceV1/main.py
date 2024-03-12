import sys
from PyQt5 import QtWidgets
from interface import Interface


class Main:

    IN_PRODUCTION = True

    def __init__(self, argv):
        app = QtWidgets.QApplication(argv)
        window = Interface(self.IN_PRODUCTION)
        window.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    Main(sys.argv)
