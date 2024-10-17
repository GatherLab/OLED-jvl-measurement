from PySide6 import QtWidgets

import json
import os
import core_functions as cf
from pathlib import Path

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
        default_settings = cf.read_global_settings()

        self.keithley_source_address_lineEdit.setText(
            str(default_settings["keithley_source_address"])
        )
        self.keithley_multimeter_address_lineEdit.setText(
            str(default_settings["keithley_multimeter_address"])
        )
        self.arduino_com_address_lineEdit.setText(
            str(default_settings["arduino_com_address"])
        )
        self.motor_number_lineEdit.setText(str(default_settings["motor_number"]))
        self.motor_speed_spinBox.setMinimum(0)
        self.motor_speed_spinBox.setMaximum(20)
        self.motor_speed_spinBox.setValue(float(default_settings["motor_speed"]))
        self.motor_offset_lineEdit.setText(str(default_settings["motor_offset"]))
        # self.spectrum_integration_time_lineEdit.setText(
        # str(default_settings["spectrum_integration_time"])
        # )

        self.non_linearity_correction_toggleSwitch.setChecked(
            default_settings["spectrometer_non_linearity_correction"]
        )

        # self.photodiode_cutoff_lineEdit.setText(
        # str(default_settings["photodiode_cutoff"])
        # )
        self.photodiode_saturation_lineEdit.setText(
            str(default_settings["photodiode_saturation"])
        )
        self.oled_on_time_lineEdit.setText(str(default_settings["oled_on_time"]))
        self.multimeter_latency_lineEdit.setText(
            str(default_settings["multimeter_latency"])
        )

        # self.photodiode_area_lineEdit.setText(str(default_settings["photodiode_area"]))
        # self.photodiode_peak_response_lineEdit.setText(
        #     str(default_settings["photodiode_peak_response"])
        # )
        # self.amplifier_resistance_lineEdit.setText(
        #     str(default_settings["amplifier_resistance"])
        # )
        # self.oled_area_lineEdit.setText(str(default_settings["oled_area"]))
        # self.distance_photodiode_oled_lineEdit.setText(
        #     str(default_settings["distance_photodiode_oled"])
        # )
        self.default_saving_path_lineEdit.setText(
            str(default_settings["default_saving_path"])
        )
        self.auto_test_minimum_voltage_lineEdit.setText(
            str(default_settings["auto_test_minimum_voltage"])
        )
        self.auto_test_maximum_voltage_lineEdit.setText(
            str(default_settings["auto_test_maximum_voltage"])
        )
        self.auto_test_prebias_voltage_lineEdit.setText(
            str(default_settings["pre_bias_voltage"])
        )

        # Connect buttons to functions
        self.load_defaults_pushButton.clicked.connect(self.load_defaults)
        self.save_settings_pushButton.clicked.connect(self.save_settings)

        self.initial_settings = json.loads(
            json.dumps(default_settings), parse_float=str
        )

    def save_settings(self):
        """
        Save the settings the user just entered
        """

        # Gather the new settings
        settings_data = {}
        settings_data["overwrite"] = []
        settings_data["overwrite"] = {
            "keithley_source_address": self.keithley_source_address_lineEdit.text(),
            "keithley_multimeter_address": self.keithley_multimeter_address_lineEdit.text(),
            "arduino_com_address": self.arduino_com_address_lineEdit.text(),
            "motor_number": self.motor_number_lineEdit.text(),
            "motor_speed": self.motor_speed_spinBox.value(),
            "motor_offset": self.motor_offset_lineEdit.text(),
            # "spectrum_integration_time": self.spectrum_integration_time_lineEdit.text(),
            "spectrometer_non_linearity_correction": bool(
                str(self.non_linearity_correction_toggleSwitch.isChecked())
            ),
            # "photodiode_cutoff": self.photodiode_cutoff_lineEdit.text(),
            "photodiode_saturation": self.photodiode_saturation_lineEdit.text(),
            "oled_on_time": self.oled_on_time_lineEdit.text(),
            "multimeter_latency": self.multimeter_latency_lineEdit.text(),
            # "photodiode_area": self.photodiode_area_lineEdit.text(),
            # "photodiode_peak_response": self.photodiode_peak_response_lineEdit.text(),
            # "amplifier_resistance": self.amplifier_resistance_lineEdit.text(),
            # "oled_area": self.oled_area_lineEdit.text(),
            # "distance_photodiode_oled": self.distance_photodiode_oled_lineEdit.text(),
            "default_saving_path": self.default_saving_path_lineEdit.text(),
            "auto_test_minimum_voltage": self.auto_test_minimum_voltage_lineEdit.text(),
            "auto_test_maximum_voltage": self.auto_test_maximum_voltage_lineEdit.text(),
            "pre_bias_voltage": self.auto_test_prebias_voltage_lineEdit.text(),
        }

        # Load the default parameter settings
        default_settings = cf.read_global_settings(default=True)

        # Add the default parameters to the new settings json
        settings_data["default"] = []
        settings_data["default"] = default_settings

        # Save the entire thing again to the settings.json file
        with open(
            os.path.join(Path(__file__).parent.parent, "usr", "global_settings.json"),
            "w",
        ) as json_file:
            json.dump(settings_data, json_file, indent=4)

        cf.log_message("Settings saved")

        # Close window on accepting
        self.accept()

        reload_window_comparison = {
            k: settings_data["overwrite"][k]
            for k in self.initial_settings
            if k in settings_data["overwrite"]
            and self.initial_settings[k] != settings_data["overwrite"][k]
        }
        # If any of the parameters that require a reinitialisation has been changed, then do one
        if any(
            key in reload_window_comparison.keys()
            for key in [
                "keithley_source_address",
                "keithley_multimeter_address",
                "arduino_com_addres",
                "motor_number",
            ]
        ):
            # Before closing the window, reinstanciate the devices with the new
            # parameters
            loading_window = LoadingWindow(self.parent)

            # Execute loading dialog
            loading_window.exec()
        else:
            # Otherwise just do the necessary tweaks to the paramters
            if self.parent.sw_top_emitting_toggleSwitch.isChecked():
                offset_angle = float(settings_data["overwrite"]["motor_offset"]) + 180
            else:
                offset_angle = float(settings_data["overwrite"]["motor_offset"])

            self.parent.motor.change_offset_angle(offset_angle, relative=False)
            self.parent.spectrometer.non_linearity_correction = bool(
                settings_data["overwrite"]["spectrometer_non_linearity_correction"]
            )
            self.parent.motor.change_velocity(
                float(settings_data["overwrite"]["motor_speed"])
            )

    def load_defaults(self):
        """
        Load default settings (in case the user messed up the own settings)
        """

        # Read default settings
        default_settings = cf.read_global_settings(default=True)

        self.keithley_source_address_lineEdit.setText(
            str(default_settings["keithley_source_address"])
        )
        self.keithley_multimeter_address_lineEdit.setText(
            str(default_settings["keithley_multimeter_address"])
        )
        self.arduino_com_address_lineEdit.setText(
            str(default_settings["arduino_com_address"])
        )
        self.motor_number_lineEdit.setText(str(default_settings["motor_number"]))
        self.motor_speed_spinBox.setValue(float(default_settings["motor_speed"]))
        self.motor_offset_lineEdit.setText(str(default_settings["motor_offset"]))
        # self.spectrum_integration_time_lineEdit.setText(
        # str(default_settings["spectrum_integration_time"])
        # )

        self.non_linearity_correction_toggleSwitch.setChecked(
            bool(default_settings["spectrometer_non_linearity_correction"])
        )
        # self.photodiode_cutoff_lineEdit.setText(
        # str(default_settings["photodiode_cutoff"])
        # )
        self.photodiode_saturation_lineEdit.setText(
            str(default_settings["photodiode_saturation"])
        )
        self.oled_on_time_lineEdit.setText(str(default_settings["oled_on_time"]))
        self.multimeter_latency_lineEdit.setText(
            str(default_settings["multimeter_latency"])
        )
        # self.photodiode_area_lineEdit.setText(default_settings["photodiode_area"])
        # self.photodiode_peak_response_lineEdit.setText(
        #     default_settings["photodiode_peak_response"]
        # )
        # self.amplifier_resistance_lineEdit.setText(
        #     default_settings["amplifier_resistance"]
        # )
        # self.oled_area_lineEdit.setText(default_settings["oled_area"])
        # self.distance_photodiode_oled_lineEdit.setText(
        #     default_settings["distance_photodiode_oled"]
        # )
        self.default_saving_path_lineEdit.setText(
            default_settings["default_saving_path"]
        )
        self.auto_test_minimum_voltage_lineEdit.setText(
            str(default_settings["auto_test_minimum_voltage"])
        )
        self.auto_test_maximum_voltage_lineEdit.setText(
            str(default_settings["auto_test_maximum_voltage"])
        )
        self.auto_test_prebias_voltage_lineEdit.setText(
            str(default_settings["pre_bias_voltage"])
        )
