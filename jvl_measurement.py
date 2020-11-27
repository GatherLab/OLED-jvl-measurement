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

        # Set standard parameters for autotube measurement
        self.aw_min_voltage_spinBox.setValue(-2)
        self.aw_min_voltage_spinBox.setMinimum(-50)
        self.aw_max_voltage_spinBox.setValue(5)
        self.aw_max_voltage_spinBox.setMaximum(50)
        self.aw_changeover_voltage_spinBox.setValue(2)
        self.aw_changeover_voltage_spinBox.setSingleStep(0.1)
        self.aw_low_voltage_step_spinBox.setValue(0.5)
        self.aw_low_voltage_step_spinBox.setSingleStep(0.1)
        self.aw_high_voltage_step_spinBox.setValue(0.1)
        self.aw_high_voltage_step_spinBox.setSingleStep(0.1)
        self.aw_scan_compliance_spinBox.setValue(1.05)
        self.aw_scan_compliance_spinBox.setMaximum(1.05)
        self.aw_scan_compliance_spinBox.setSingleStep(0.05)

        # Set standard parameters for Goniometer
        self.gw_offset_angle_spinBox.setValue(0)
        self.gw_offset_angle_spinBox.setMaximum(360)
        self.gw_scanning_angle_spinBox.setValue(180)
        self.gw_scanning_angle_spinBox.setMaximum(360)
        self.gw_step_angle_spinBox.setValue(1)
        self.gw_step_angle_spinBox.setMaximum(360)
        self.gw_integration_time_spinBox.setValue(300)
        self.gw_homing_time_spinBox.setValue(30)
        self.gw_moving_time_spinBox.setValue(1)
        self.gw_pulse_duration_spinBox.setValue(2)
        self.gw_voltage_or_current_spinBox.setValue(5)

        # Set standard parameters for Spectral Measurement
        self.specw_voltage_spinBox.setValue(5)
        self.specw_voltage_spinBox.setMaximum(50)

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