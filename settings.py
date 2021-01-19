# -*- coding: utf-8 -*-
from PySide2 import QtCore, QtGui, QtWidgets

import json
import core_functions as cf

from loading_window import LoadingWindow
from UI_settings_window import Ui_Settings


class Settings(QtWidgets.QDialog, Ui_Settings):
    """
    Settings window
    """

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)

        self.parent = parent

        # Load from file to fill the lines
        with open("settings/global_settings.json") as json_file:
            data = json.load(json_file)
        try:
            default_settings = data["overwrite"]
        except:
            default_settings = data["default"]

        self.keithley_source_address_lineEdit.setText(
            default_settings[0]["keithley_source_address"]
        )
        self.keithley_multimeter_address_lineEdit.setText(
            default_settings[0]["keithley_multimeter_address"]
        )
        self.arduino_com_address_lineEdit.setText(
            default_settings[0]["arduino_com_address"]
        )
        self.motor_number_lineEdit.setText(default_settings[0]["motor_number"])
        self.motor_offset_lineEdit.setText(default_settings[0]["motor_offset"])
        self.spectrum_integration_time_lineEdit.setText(
            default_settings[0]["spectrum_integration_time"]
        )
        self.photodiode_gain_lineEdit.setText(default_settings[0]["photodiode_gain"])
        self.photodiode_saturation_lineEdit.setText(
            default_settings[0]["photodiode_saturation"]
        )

        # Connect buttons to functions
        self.load_defaults_pushButton.clicked.connect(self.load_defaults)
        self.save_settings_pushButton.clicked.connect(self.save_settings)

    def save_settings(self):
        """
        Save the settings the user just entered
        """

        # Gather the new settings
        settings_data = {}
        settings_data["overwrite"] = []
        settings_data["overwrite"].append(
            {
                "keithley_source_address": self.keithley_source_address_lineEdit.text(),
                "keithley_multimeter_address": self.keithley_multimeter_address_lineEdit.text(),
                "arduino_com_address": self.arduino_com_address_lineEdit.text(),
                "motor_number": self.motor_number_lineEdit.text(),
                "motor_offset": self.motor_offset_lineEdit.text(),
                "spectrum_integration_time": self.spectrum_integration_time_lineEdit.text(),
                "photodiode_gain": self.photodiode_gain_lineEdit.text(),
                "photodiode_saturation": self.photodiode_saturation_lineEdit.text(),
            }
        )

        # Load the default parameter settings
        with open("settings/global_settings.json") as json_file:
            data = json.load(json_file)

        # Add the default parameters to the new settings json
        settings_data["default"] = []
        settings_data["default"] = data["default"]

        # Save the entire thing again to the settings.json file
        with open("settings/global_settings.json", "w") as json_file:
            json.dump(settings_data, json_file, indent=4)

        cf.log_message("Settings saved")

        # Close window on accepting
        self.accept()

        # Before closing the window, reinstanciate the devices with the new
        # parameters
        loading_window = LoadingWindow(self.parent)

        # Execute loading dialog
        loading_window.exec()

    def load_defaults(self):
        """
        Load default settings (in case the user messed up the own settings)
        """

        with open("settings/global_settings.json") as json_file:
            data = json.load(json_file)

        default_settings = data["default"]
        self.keithley_source_address_lineEdit.setText(
            default_settings[0]["keithley_source_address"]
        )
        self.keithley_multimeter_address_lineEdit.setText(
            default_settings[0]["keithley_multimeter_address"]
        )
        self.arduino_com_address_lineEdit.setText(
            default_settings[0]["arduino_com_address"]
        )
        self.motor_number_lineEdit.setText(default_settings[0]["motor_number"])
        self.motor_offset_lineEdit.setText(default_settings[0]["motor_offset"])
        self.spectrum_integration_time_lineEdit.setText(
            default_settings[0]["spectrum_integration_time"]
        )
        self.photodiode_gain_lineEdit.setText(default_settings[0]["photodiode_gain"])
        self.photodiode_saturation_lineEdit.setText(
            default_settings[0]["photodiode_saturation"]
        )
