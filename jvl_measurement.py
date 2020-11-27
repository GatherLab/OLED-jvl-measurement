from UI_main_window import Ui_MainWindow
from UI_settings_window import Ui_Settings

from PySide2 import QtCore, QtGui, QtWidgets


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """
    This class contains the logic of the program and is explicitly seperated
    from the UI classes
    """

    def __init__(self):
        """
        Initialise instance
        """
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.actionOptions.triggered.connect(self.show_settings)

    def show_settings(self):
        self.SettingsWindow = QtWidgets.QWidget()
        ui = Ui_Settings()
        ui.setupUi(self.SettingsWindow)
        self.SettingsWindow.show()


# ---------------------------------------------------------------------------- #
# -------------------- This is to execute the program ------------------------ #
# ---------------------------------------------------------------------------- #
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    # ui.setupUi(aMainWindow)
    ui.show()
    sys.exit(app.exec_())