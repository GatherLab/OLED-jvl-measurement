from UI_main_window import Ui_MainWindow
from settings import Settings

from autotube_measurement import AutotubeMeasurement
from current_tester import CurrentTester
from spectrum_measurement import SpectrumMeasurement
from lifetime_measurement import LifetimeMeasurement
from goniometer_measurement import GoniometerMeasurement
from loading_window import LoadingWindow

from tests.tests import MockThorlabMotor
from hardware import (
    ArduinoUno,
    OceanSpectrometer,
    ThorlabMotor,
    KeithleyMultimeter,
    KeithleySource,
    MotorMoveThread,
)

import core_functions as cf
import pyvisa

from PySide6 import QtCore, QtGui, QtWidgets

import time
import os
import json
import sys
import functools
from pathlib import Path
from datetime import date
import logging
from logging.handlers import RotatingFileHandler

import matplotlib.pylab as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
import math

import webbrowser


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """
    This class contains the logic of the program and is explicitly seperated
    from the UI classes. However, it is a child class of Ui_MainWindow.
    """

    def __init__(self):
        """
        Initialise instance
        """
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # For some odd reason this is necessary in the main thread already.
        # Otherwise the motor won't initialise and the program crash without an error...
        # try:
        #     global_settings = cf.read_global_settings()
        #     ThorlabMotor(
        #         global_settings["motor_number"], global_settings["motor_offset"]
        #     )
        # except:
        #     cf.log_message(
        #         "Motor can probably not be initialised. Reconnect the motor or change the serial number in the global settings."
        #     )

        # -------------------------------------------------------------------- #
        # -------------------------- Hardware Setup -------------------------- #
        # -------------------------------------------------------------------- #
        self.motor_run = MotorMoveThread(0, 0, False, self)

        # Execute initialisation thread
        loading_window = LoadingWindow(self)

        # Execute loading dialog
        loading_window.exec()

        # Update the graphics to the current motor position
        motor_position = self.motor.read_position()
        self.gw_animation.move(motor_position)

        # Read global settings first (what if they are not correct yet?)
        # global_settings = cf.read_global_settings()

        # -------------------------------------------------------------------- #
        # ------------------------------ General ----------------------------- #
        # -------------------------------------------------------------------- #

        # Update statusbar
        cf.log_message("Initialising Program")
        self.tabWidget.currentChanged.connect(self.changed_tab_widget)

        # Hide by default and only show if a process is running
        self.progressBar.hide()

        # -------------------------------------------------------------------- #
        # ------------------------- Default Values --------------------------- #
        # -------------------------------------------------------------------- #

        # Automatically overwrite the overwrite values with the defaults when
        # the program is started to ensure that defaults are defaults by default
        default_settings = cf.read_global_settings(default=True)
        settings_data = {}
        settings_data["overwrite"] = []
        settings_data["overwrite"] = default_settings
        settings_data["default"] = []
        settings_data["default"] = default_settings

        # Save the entire thing again to the settings.json file
        with open(
            os.path.join(Path(__file__).parent.parent, "usr", "global_settings.json"),
            "w",
        ) as json_file:
            json.dump(settings_data, json_file, indent=4)

        cf.log_message("Overwrite Settings set to Default")

        # -------------------------------------------------------------------- #
        # -------------------------- Current Tester -------------------------- #
        # -------------------------------------------------------------------- #

        # First init of current tester (should be activated when starting the
        # program)
        self.current_tester = CurrentTester(
            self.arduino_uno,
            self.keithley_source,
            parent=self,
        )

        # Start thread
        self.current_tester.start()

        # Connect buttons
        self.sw_reset_hardware_pushButton.clicked.connect(self.reset_hardware)
        self.sw_browse_pushButton.clicked.connect(self.browse_folder)

        # Connect toggle switches
        self.sw_top_emitting_toggleSwitch.clicked.connect(self.mirror_goniometer_angles)
        self.sw_nip_toggleSwitch.clicked.connect(self.reverse_all_voltages)

        # Connect sw pixel to toggle function
        self.sw_pixel1_pushButton.clicked.connect(
            functools.partial(self.toggle_pixel, 1, "sw")
        )
        self.sw_pixel2_pushButton.clicked.connect(
            functools.partial(self.toggle_pixel, 2, "sw")
        )
        self.sw_pixel3_pushButton.clicked.connect(
            functools.partial(self.toggle_pixel, 3, "sw")
        )
        self.sw_pixel4_pushButton.clicked.connect(
            functools.partial(self.toggle_pixel, 4, "sw")
        )
        self.sw_pixel5_pushButton.clicked.connect(
            functools.partial(self.toggle_pixel, 5, "sw")
        )
        self.sw_pixel6_pushButton.clicked.connect(
            functools.partial(self.toggle_pixel, 6, "sw")
        )
        self.sw_pixel7_pushButton.clicked.connect(
            functools.partial(self.toggle_pixel, 7, "sw")
        )
        self.sw_pixel8_pushButton.clicked.connect(
            functools.partial(self.toggle_pixel, 8, "sw")
        )

        # Define array that contains all pushbuttons (or pointer to it)
        # Only for easier handling of the current tester
        self.sw_pushbutton_array = [
            self.sw_pixel1_pushButton,
            self.sw_pixel2_pushButton,
            self.sw_pixel3_pushButton,
            self.sw_pixel4_pushButton,
            self.sw_pixel5_pushButton,
            self.sw_pixel6_pushButton,
            self.sw_pixel7_pushButton,
            self.sw_pixel8_pushButton,
        ]

        # Connect voltage combo box
        self.sw_ct_voltage_spinBox.valueChanged.connect(
            functools.partial(self.voltage_changed, "sw")
        )

        # Connect automatic functions
        self.sw_select_all_pushButton.clicked.connect(self.select_all_pixels)
        self.sw_unselect_all_push_button.clicked.connect(self.unselect_all_pixels)
        self.sw_prebias_pushButton.clicked.connect(self.prebias_pixels)
        self.sw_auto_test_pushButton.clicked.connect(self.autotest_pixels)

        # Assign shortcuts to the pushbuttons
        self.sw_pixel1_pushButton.setShortcut("1")
        self.sw_pixel2_pushButton.setShortcut("2")
        self.sw_pixel3_pushButton.setShortcut("3")
        self.sw_pixel4_pushButton.setShortcut("4")
        self.sw_pixel5_pushButton.setShortcut("5")
        self.sw_pixel6_pushButton.setShortcut("6")
        self.sw_pixel7_pushButton.setShortcut("7")
        self.sw_pixel8_pushButton.setShortcut("8")

        self.sw_select_all_pushButton.setShortcut("9")
        self.sw_unselect_all_push_button.setShortcut("0")

        # -------------------------------------------------------------------- #
        # ---------------------- Autotube Measurement  ----------------------- #
        # -------------------------------------------------------------------- #

        # Link actions to buttons
        self.aw_start_measurement_pushButton.clicked.connect(
            self.start_autotube_measurement
        )

        self.aw_pushbutton_array = [
            self.aw_pixel1_pushButton,
            self.aw_pixel2_pushButton,
            self.aw_pixel3_pushButton,
            self.aw_pixel4_pushButton,
            self.aw_pixel5_pushButton,
            self.aw_pixel6_pushButton,
            self.aw_pixel7_pushButton,
            self.aw_pixel8_pushButton,
        ]

        # Assign shortcuts to the pushbuttons
        self.aw_pixel1_pushButton.setShortcut("1")
        self.aw_pixel2_pushButton.setShortcut("2")
        self.aw_pixel3_pushButton.setShortcut("3")
        self.aw_pixel4_pushButton.setShortcut("4")
        self.aw_pixel5_pushButton.setShortcut("5")
        self.aw_pixel6_pushButton.setShortcut("6")
        self.aw_pixel7_pushButton.setShortcut("7")
        self.aw_pixel8_pushButton.setShortcut("8")

        # By default activate the auto position option
        self.aw_auto_measure_toggleSwitch.setChecked(True)

        # -------------------------------------------------------------------- #
        # ---------------------- Spectrum Measurement  ----------------------- #
        # -------------------------------------------------------------------- #

        self.spectrum_measurement = SpectrumMeasurement(
            self.arduino_uno,
            self.keithley_source,
            self.spectrometer,
            parent=self,
        )
        # Start thread
        self.spectrum_measurement.start()

        # Connect voltage change to function
        self.specw_voltage_spinBox.valueChanged.connect(
            functools.partial(self.voltage_changed, "specw")
        )
        self.specw_integration_time_spinBox.valueChanged.connect(
            self.integration_time_changed
        )

        # Connect specw pixel to toggle function
        self.specw_pixel1_pushButton.clicked.connect(
            functools.partial(self.toggle_pixel, 1, "specw")
        )
        self.specw_pixel2_pushButton.clicked.connect(
            functools.partial(self.toggle_pixel, 2, "specw")
        )
        self.specw_pixel3_pushButton.clicked.connect(
            functools.partial(self.toggle_pixel, 3, "specw")
        )
        self.specw_pixel4_pushButton.clicked.connect(
            functools.partial(self.toggle_pixel, 4, "specw")
        )
        self.specw_pixel5_pushButton.clicked.connect(
            functools.partial(self.toggle_pixel, 5, "specw")
        )
        self.specw_pixel6_pushButton.clicked.connect(
            functools.partial(self.toggle_pixel, 6, "specw")
        )
        self.specw_pixel7_pushButton.clicked.connect(
            functools.partial(self.toggle_pixel, 7, "specw")
        )
        self.specw_pixel8_pushButton.clicked.connect(
            functools.partial(self.toggle_pixel, 8, "specw")
        )

        # Define array that contains all pushbuttons (or pointer to it)
        # Only for easier handling of the current tester
        self.specw_pushbutton_array = [
            self.specw_pixel1_pushButton,
            self.specw_pixel2_pushButton,
            self.specw_pixel3_pushButton,
            self.specw_pixel4_pushButton,
            self.specw_pixel5_pushButton,
            self.specw_pixel6_pushButton,
            self.specw_pixel7_pushButton,
            self.specw_pixel8_pushButton,
        ]

        # Save spectrum button
        self.specw_save_spectrum_pushButton.clicked.connect(self.save_spectrum)

        # Assign shortcuts to the pushbuttons
        self.specw_pixel1_pushButton.setShortcut("1")
        self.specw_pixel2_pushButton.setShortcut("2")
        self.specw_pixel3_pushButton.setShortcut("3")
        self.specw_pixel4_pushButton.setShortcut("4")
        self.specw_pixel5_pushButton.setShortcut("5")
        self.specw_pixel6_pushButton.setShortcut("6")
        self.specw_pixel7_pushButton.setShortcut("7")
        self.specw_pixel8_pushButton.setShortcut("8")

        # -------------------------------------------------------------------- #
        # ---------------------- Lifetime Measurement  ----------------------- #
        # -------------------------------------------------------------------- #

        # Link actions to buttons
        self.ltw_start_measurement_pushButton.clicked.connect(
            self.start_lifetime_measurement
        )

        # Assign shortcuts to the pushbuttons
        self.ltw_pixel1_pushButton.setShortcut("1")
        self.ltw_pixel2_pushButton.setShortcut("2")
        self.ltw_pixel3_pushButton.setShortcut("3")
        self.ltw_pixel4_pushButton.setShortcut("4")
        self.ltw_pixel5_pushButton.setShortcut("5")
        self.ltw_pixel6_pushButton.setShortcut("6")
        self.ltw_pixel7_pushButton.setShortcut("7")
        self.ltw_pixel8_pushButton.setShortcut("8")

        self.ltw_voltage_or_current_toggleSwitch.clicked.connect(
            self.change_measurement_mode_ltw
        )

        # Set true by default
        self.ltw_voltage_or_current_toggleSwitch.setChecked(True)

        # All pixels mode
        self.ltw_all_pixel_mode_toggleSwitch.clicked.connect(
            self.disable_pixel_selection
        )

        # -------------------------------------------------------------------- #
        # --------------------- Goniometer Measurement  ---------------------- #
        # -------------------------------------------------------------------- #
        self.gw_start_measurement_pushButton.clicked.connect(
            self.start_goniometer_measurement
        )

        self.gw_move_pushButton.clicked.connect(self.move_motor)

        self.gw_el_or_pl_toggleSwitch.clicked.connect(self.disable_el_options)

        # Assign shortcuts to the pushbuttons
        self.gw_pixel1_pushButton.setShortcut("1")
        self.gw_pixel2_pushButton.setShortcut("2")
        self.gw_pixel3_pushButton.setShortcut("3")
        self.gw_pixel4_pushButton.setShortcut("4")
        self.gw_pixel5_pushButton.setShortcut("5")
        self.gw_pixel6_pushButton.setShortcut("6")
        self.gw_pixel7_pushButton.setShortcut("7")
        self.gw_pixel8_pushButton.setShortcut("8")

        self.gw_voltage_or_current_toggleSwitch.clicked.connect(
            self.change_measurement_mode
        )

        # Set true by default
        self.gw_voltage_or_current_toggleSwitch.setChecked(True)
        self.gw_background_every_step_toggleSwitch.setChecked(True)
        self.gw_degradation_check_toggleSwitch.setChecked(True)

        # self.motor_run = motormovethread(0, 45, self)

        # -------------------------------------------------------------------- #
        # --------------------------- Menubar -------------------------------- #
        # -------------------------------------------------------------------- #
        self.actionOptions.triggered.connect(self.show_settings)

        # Open the documentation in the browser (maybe in the future directly
        # open the readme file in the folder but currently this is so much
        # easier and prettier)
        self.actionDocumentation.triggered.connect(
            lambda: webbrowser.open(
                "https://github.com/GatherLab/OLED-jvl-measurement/blob/main/README.md"
            )
        )

        self.actionOpen_Log.triggered.connect(lambda: self.open_file("log.out"))

        # -------------------------------------------------------------------- #
        # --------------------- Set Standard Parameters ---------------------- #
        # -------------------------------------------------------------------- #

        # Set standard parameters for autotube measurement
        self.aw_min_voltage_spinBox.setMinimum(-200)
        self.aw_min_voltage_spinBox.setValue(-2)
        self.aw_max_voltage_spinBox.setMaximum(200)
        self.aw_max_voltage_spinBox.setValue(4)
        self.aw_changeover_voltage_spinBox.setSingleStep(0.1)
        self.aw_changeover_voltage_spinBox.setValue(2)
        self.aw_low_voltage_step_spinBox.setSingleStep(0.1)
        self.aw_low_voltage_step_spinBox.setValue(0.5)
        self.aw_high_voltage_step_spinBox.setSingleStep(0.1)
        self.aw_high_voltage_step_spinBox.setValue(0.1)
        self.aw_scan_compliance_spinBox.setMaximum(1.05)
        self.aw_scan_compliance_spinBox.setSingleStep(0.05)
        self.aw_scan_compliance_spinBox.setMinimum(0)
        self.aw_scan_compliance_spinBox.setMaximum(1050)
        self.aw_scan_compliance_spinBox.setValue(1050)

        # Set standard parameters for Goniometer
        self.gw_offset_angle_spinBox.setMaximum(180)
        self.gw_offset_angle_spinBox.setMinimum(-179)
        self.gw_offset_angle_spinBox.setValue(motor_position)
        self.gw_minimum_angle_spinBox.setMaximum(180)
        self.gw_minimum_angle_spinBox.setMinimum(-179)
        self.gw_minimum_angle_spinBox.setValue(-90)
        self.gw_maximum_angle_spinBox.setMaximum(180)
        self.gw_maximum_angle_spinBox.setMinimum(-179)
        self.gw_maximum_angle_spinBox.setValue(90)
        self.gw_step_angle_spinBox.setMaximum(360)
        self.gw_step_angle_spinBox.setValue(3)
        self.gw_integration_time_spinBox.setMaximum(10000)
        self.gw_integration_time_spinBox.setMinimum(0)
        self.gw_integration_time_spinBox.setValue(300)
        # self.gw_homing_time_spinBox.setValue(30)
        # self.gw_moving_time_spinBox.setValue(1)
        # self.gw_oled_on_time_spinBox.setValue(2)
        self.gw_vc_value_spinBox.setValue(3.5)
        self.gw_vc_value_spinBox.setMinimum(0)
        self.gw_vc_value_spinBox.setMaximum(1050)
        self.gw_vc_compliance_spinBox.setMinimum(0)
        self.gw_vc_compliance_spinBox.setMaximum(1050)
        self.gw_vc_compliance_spinBox.setValue(5)

        # Set standard parameters for Spectral Measurement
        self.specw_voltage_spinBox.setMinimum(-200.0)
        self.specw_voltage_spinBox.setMaximum(200.0)
        self.specw_voltage_spinBox.setSingleStep(0.1)
        self.specw_voltage_spinBox.setValue(0)
        self.specw_voltage_spinBox.setKeyboardTracking(False)

        self.specw_integration_time_spinBox.setMinimum(8)
        self.specw_integration_time_spinBox.setMaximum(10000)
        self.specw_integration_time_spinBox.setSingleStep(50)
        self.specw_integration_time_spinBox.setValue(100)
        self.specw_integration_time_spinBox.setKeyboardTracking(False)

        # Set standard parameters for Current Tester Measurement
        self.sw_ct_voltage_spinBox.setMinimum(-200.0)
        self.sw_ct_voltage_spinBox.setMaximum(200.0)
        self.sw_ct_voltage_spinBox.setSingleStep(0.1)
        self.sw_ct_voltage_spinBox.setValue(0)
        self.sw_ct_voltage_spinBox.setKeyboardTracking(False)

        # Set standard parameters for lifetime measurement
        self.ltw_voltage_spinBox.setMinimum(0.1)
        self.ltw_voltage_spinBox.setMaximum(10)
        self.ltw_voltage_spinBox.setValue(3.5)
        self.ltw_max_current_spinBox.setMinimum(0.1)
        self.ltw_max_current_spinBox.setMaximum(1050)
        self.ltw_max_current_spinBox.setValue(10)
        self.ltw_on_time_spinBox.setMinimum(1)
        self.ltw_on_time_spinBox.setMaximum(10000)
        self.ltw_on_time_spinBox.setValue(120)
        self.ltw_measurement_interval_spinBox.setMinimum(1)
        self.ltw_measurement_interval_spinBox.setMaximum(10000)
        self.ltw_measurement_interval_spinBox.setValue(10)

        # Update statusbar
        cf.log_message("Program ready")

    # -------------------------------------------------------------------- #
    # ------------------------- Global Functions ------------------------- #
    # -------------------------------------------------------------------- #
    def browse_folder(self):
        """
        Open file dialog to browse through directories
        """
        global_variables = cf.read_global_settings()

        self.global_path = QtWidgets.QFileDialog.getExistingDirectory(
            QtWidgets.QFileDialog(),
            "Select a Folder",
            global_variables["default_saving_path"],
            QtWidgets.QFileDialog.ShowDirsOnly,
        )
        print(self.global_path)
        # file_dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)

        # if file_dialog1.exec():
        #     # Set global path to selected path
        #     self.global_path = file_dialog1.selectedFiles()

        #     # Set the according line edit
        self.sw_folder_path_lineEdit.setText(self.global_path + "/")

    def show_settings(self):
        """
        Shows the settings
        """
        self.settings_window = Settings(self)
        # ui = Ui_Settings()
        # ui.setupUi(self.settings_window, parent=self)

        p = (
            self.frameGeometry().center()
            - QtCore.QRect(QtCore.QPoint(), self.settings_window.sizeHint()).center()
        )

        self.settings_window.move(p)

        # self.settings_window.show()

        result = self.settings_window.exec()

    @QtCore.Slot(ArduinoUno)
    def init_arduino(self, arduino_object):
        """
        Receives an arduino object from the init thread
        """
        self.arduino_uno = arduino_object

    @QtCore.Slot(ThorlabMotor)
    def init_motor(self, motor_object):
        """
        Receives an arduino object from the init thread
        """
        self.motor = motor_object

    @QtCore.Slot(KeithleySource)
    def init_source(self, source_object):
        """
        Receives an arduino object from the init thread
        """
        self.keithley_source = source_object

    @QtCore.Slot(KeithleyMultimeter)
    def init_multimeter(self, multimeter_object):
        """
        Receives an arduino object from the init thread
        """
        self.keithley_multimeter = multimeter_object

    @QtCore.Slot(OceanSpectrometer)
    def init_spectrometer(self, spectrometer_object):
        """
        Receives an arduino object from the init thread
        """
        self.spectrometer = spectrometer_object

    def open_file(self, path):
        """
        Opens a file on the machine with the standard program
        https://stackoverflow.com/questions/6045679/open-file-with-pyqt
        """
        if sys.platform.startswith("linux"):
            subprocess.call(["xdg-open", path])
        else:
            os.startfile(path)

    # @QtCore.Slot(str)
    # def cf.log_message(self, message):
    #     """
    #     Function that manages the logging, in the sense that everything is
    #     directly logged into statusbar and the log file at once as well as
    #     printed to the console instead of having to call multiple functions.
    #     """
    #     self.statusbar.showMessage(message, 10000000)
    #     logging.info(message)
    #     print(message)

    def changed_tab_widget(self):
        """
        Function that shall manage the threads that are running when we are
        on a certain tab. For instance the spectrum thread really only must
        run when the user is on the spectrum tab. Otherwise it can be paused.
        This might become important in the future.
        """

        if self.tabWidget.currentIndex() == 0:
            self.spectrum_measurement.pause = True
            self.current_tester.pause = False
        if self.tabWidget.currentIndex() == 1:
            self.spectrum_measurement.pause = True
            self.current_tester.pause = True
        if self.tabWidget.currentIndex() == 2:
            self.spectrum_measurement.pause = False
            self.current_tester.pause = False
        if self.tabWidget.currentIndex() == 3:
            self.spectrum_measurement.pause = True
            self.current_tester.pause = True

        cf.log_message(
            "Switched to tab widget no. " + str(self.tabWidget.currentIndex())
        )

        return

    # def read_global_settings(self):
    #     """
    #     Read in global settings from file. The file can be changed using the
    #     settings window.
    #     """
    #     # Load from file to fill the lines
    #     with open("settings/global_settings.json") as json_file:
    #         data = json.load(json_file)
    #     try:
    #         settings = data["overwrite"]

    #         # Update statusbar
    #         cf.log_message("Global Settings Read from File")
    #     except:
    #         settings = data["default"]

    #         # Update statusbar
    #         cf.log_message("Default device parameters taken")

    #     return settings[0]

    def safe_read_setup_parameters(self):
        """
        Read setup parameters and if any important field is missing, return a qmessagebox
        """

        # Read out measurement and setup parameters from GUI
        setup_parameters = self.read_setup_parameters()

        # Check if folder path exists
        if (
            setup_parameters["folder_path"] == ""
            or setup_parameters["batch_name"] == ""
        ):
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText("Please set folder path and batch name first!")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.setStyleSheet(
                "background-color: rgb(44, 49, 60);\n"
                "color: rgb(255, 255, 255);\n"
                'font: 63 bold 10pt "Segoe UI";\n'
                ""
            )
            msgBox.exec()

            self.aw_start_measurement_pushButton.setChecked(False)
            self.gw_start_measurement_pushButton.setChecked(False)

            cf.log_message("Folder path or batchname not defined")
            raise UserWarning("Please set folder path and batchname first!")

        # Now check if the folder path ends on a / otherwise try to add it
        if not setup_parameters["folder_path"][-1] == "/":
            setup_parameters["folder_path"] = setup_parameters["folder_path"] + "/"
            self.sw_folder_path_lineEdit.setText(setup_parameters["folder_path"])

        # Now check if the read out path is a valid path
        if not os.path.isdir(setup_parameters["folder_path"]):
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText("Please enter a valid folder path")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.setStyleSheet(
                "background-color: rgb(44, 49, 60);\n"
                "color: rgb(255, 255, 255);\n"
                'font: 63 bold 10pt "Segoe UI";\n'
                ""
            )
            msgBox.exec()

            self.aw_start_measurement_pushButton.setChecked(False)

            cf.log_message("Folder path not valid")
            raise UserWarning("Please enter a valid folder path!")

        return setup_parameters

    def make_format(self, current, other):
        """
        function to allow display of both coordinates for figures with two axis
        """

        # current and other are axes
        def format_coord(x, y):
            # x, y are data coordinates
            # convert to display coords
            display_coord = current.transData.transform((x, y))
            inv = other.transData.inverted()
            # convert back to data coords with respect to ax
            ax_coord = inv.transform(display_coord)
            coords = [ax_coord, (x, y)]
            return "Left: {:<40}    Right: {:<}".format(
                *["({:.3f}, {:.3f})".format(x, y) for x, y in coords]
            )

        return format_coord

    # -------------------------------------------------------------------- #
    # -------------------------- Current Tester -------------------------- #
    # -------------------------------------------------------------------- #
    def read_setup_parameters(self):
        """
        Function to read out the current fields entered in the setup tab
        """
        setup_parameters = {
            "folder_path": self.sw_folder_path_lineEdit.text(),
            "batch_name": self.sw_batch_name_lineEdit.text(),
            "device_number": self.sw_device_number_spinBox.value(),
            "test_voltage": self.sw_ct_voltage_spinBox.value(),
            "top_emitting": self.sw_top_emitting_toggleSwitch.isChecked(),
            "nip": self.sw_nip_toggleSwitch.isChecked(),
            "selected_pixel": [
                self.sw_pixel1_pushButton.isChecked(),
                self.sw_pixel2_pushButton.isChecked(),
                self.sw_pixel3_pushButton.isChecked(),
                self.sw_pixel4_pushButton.isChecked(),
                self.sw_pixel5_pushButton.isChecked(),
                self.sw_pixel6_pushButton.isChecked(),
                self.sw_pixel7_pushButton.isChecked(),
                self.sw_pixel8_pushButton.isChecked(),
            ],
        }

        # Update statusbar
        cf.log_message("Setup parameters read")

        return setup_parameters

    def reset_hardware(self):
        """
        Function to reset the devices and toggle local mode to be able to
        activate pixel. I am not really sure if that is how to terminate a qthread correctly but it works.
        https://stackoverflow.com/questions/17045368/qthread-emits-finished-signal-but-isrunning-returns-true-and-isfinished-re
        """
        # Reset the keithley by reseting it as voltage source
        self.keithley_source.as_voltage_source(1050)
        self.keithley_multimeter.reset()
        self.arduino_uno.init_serial_connection()

        # # Kill process and delete old current tester object
        # self.current_tester.kill()
        # time.sleep(1)
        # del self.current_tester

        # # Read in global settings and instanciate CurrentTester again
        # self.current_tester = CurrentTester(
        #     self.arduino_uno,
        #     self.keithley_source,
        #     parent=self,
        # )

        # # Start thread
        # self.current_tester.start()

        # # Update statusbar
        # cf.log_message("Current tester successfully reinstanciated")

    def toggle_pixel(self, pixel_number, tab):
        """
        Toggles the pixel and changes the state of the pushbuttons
        """
        if tab == "sw":
            selected_pixels = self.read_setup_parameters()["selected_pixel"]
        elif tab == "specw":
            selected_pixels = self.read_spectrum_parameters()["selected_pixel"]

        # Set keithley source to the value of the change voltage field
        self.keithley_source.set_voltage(self.sw_ct_voltage_spinBox.value())

        # Turn pixel on
        self.current_tester.uno.trigger_relay(pixel_number)

        if selected_pixels[pixel_number - 1]:
            # Update statusbar
            cf.log_message("Activated Pixel " + str(pixel_number))

            self.specw_pushbutton_array[pixel_number - 1].setChecked(True)
            self.sw_pushbutton_array[pixel_number - 1].setChecked(True)
        else:
            # Update statusbar
            cf.log_message("Deactivated Pixel " + str(pixel_number))

            self.specw_pushbutton_array[pixel_number - 1].setChecked(False)
            self.sw_pushbutton_array[pixel_number - 1].setChecked(False)

            # print("Pixel " + str(pixel_number) + " turned off")

        # Read the voltage value to decide if the output should be turned on or not
        voltage = self.sw_ct_voltage_spinBox.value()

        if math.isclose(float(voltage), 0):
            self.keithley_source.deactivate_output()
        else:
            self.keithley_source.activate_output()

    @QtCore.Slot(float)
    def update_ammeter(self, current_reading):
        """
        Function that is continuously evoked when the current is updated by
        current_tester thread.
        """
        # This has to be checked again not sure if the conversion is correct
        self.sw_current_lcdNumber.display(round(current_reading * 1e3, 4))

    def voltage_changed(self, tab, voltage):
        """
        Function that changes the real voltage when the voltage was changed
        in the UI
        """
        # Read in voltage from spinBox of the according tab and change the
        # value of the other one
        if tab == "sw":
            voltage = self.sw_ct_voltage_spinBox.value()

            # Block triggering of a signal so that this function is not called twice
            self.specw_voltage_spinBox.blockSignals(True)
            self.specw_voltage_spinBox.setValue(voltage)
            self.specw_voltage_spinBox.blockSignals(False)

        elif tab == "specw":
            voltage = self.specw_voltage_spinBox.value()

            # Block triggering of a signal so that this function is not called twice
            self.sw_ct_voltage_spinBox.blockSignals(True)
            self.sw_ct_voltage_spinBox.setValue(voltage)
            self.sw_ct_voltage_spinBox.blockSignals(False)

        # Set voltage
        self.current_tester.keithley_source.set_voltage(voltage)

        # If the voltage is set to zero, deactivate the output otherwise, activate it
        if math.isclose(float(voltage), 0):
            self.keithley_source.deactivate_output()
        else:
            self.current_tester.keithley_source.activate_output()

        # Update statusbar
        cf.log_message("Voltage Changed to " + str(round(voltage, 2)) + " V")

    def select_all_pixels(self):
        """
        Selects all pixels and applies the given voltage
        """

        # Toggle all buttons for the unselected pixels
        self.current_tester.uno.trigger_relay(9)

        for i in range(len(self.sw_pushbutton_array)):
            self.sw_pushbutton_array[i].setChecked(True)
            self.specw_pushbutton_array[i].setChecked(True)

        # Update statusbar
        cf.log_message("All pixels selected")

    def unselect_all_pixels(self):
        """
        Unselect all pixels
        """

        # Collectively turn off all pixels
        self.current_tester.uno.trigger_relay(0)

        # Uncheck all pixels
        for i in range(len(self.sw_pushbutton_array)):
            self.sw_pushbutton_array[i].setChecked(False)
            self.specw_pushbutton_array[i].setChecked(False)

        # Update statusbar
        cf.log_message("All pixels unselected")

    def update_app(self):
        """
        Helper function to call update function from other class
        """
        app.processEvents()

    def prebias_pixels(self):
        """
        Prebias all pixels (e.g. at -2 V)
        """

        # Update statusbar
        cf.log_message("Prebiasing pixels started")

        # This should be in the global settings later on (probably not
        # necessary to change every time but sometimes)
        pre_bias_voltage = cf.read_global_settings()["pre_bias_voltage"]
        biasing_time = 0.5  # in s
        set_voltage = self.sw_ct_voltage_spinBox.value()

        # Unselect all pixels first (in case some have been selected before)
        self.unselect_all_pixels()

        # Set voltage to prebias voltage
        self.keithley_source.set_voltage(pre_bias_voltage)
        self.sw_ct_voltage_spinBox.setValue(pre_bias_voltage)

        # Pre-bias all pixels automatically
        for pixel in range(len(self.sw_pushbutton_array)):
            # Close all relays
            self.arduino_uno.trigger_relay(0)

            # Set push button to checked and open relay of the pixel
            self.sw_pushbutton_array[pixel].setChecked(True)
            self.specw_pushbutton_array[pixel].setChecked(True)
            self.arduino_uno.trigger_relay(pixel + 1)

            # Turn on the voltage
            self.keithley_source.activate_output()

            # Update GUI while being in a loop. It would be better to use
            # separate threads but for now this is the easiest way
            app.processEvents()

            # Bias for half a second
            time.sleep(biasing_time)

            # Deactivate the pixel again
            self.sw_pushbutton_array[pixel].setChecked(False)
            self.specw_pushbutton_array[pixel].setChecked(False)
            self.arduino_uno.trigger_relay(pixel + 1)

            # Turn off the voltage
            self.keithley_source.deactivate_output()

        # Set voltage to prebias voltage
        self.keithley_source.activate_output()
        self.keithley_source.set_voltage(set_voltage)
        self.sw_ct_voltage_spinBox.setValue(set_voltage)

        # Update statusbar
        cf.log_message("Finished prebiasing")

    def autotest_pixels(self):
        """
        Automatic testing of all pixels. The first very simple idea is as following:
            - The voltage for one pixel is slowly increased (maybe steps of
            0.5) only until a certain current is reached. As soon as it is
            reached, the pixel is marked as a working pixel
            - If the current is too high for a low voltage (the threshold has
            to be defined carefully), the pixel is thrown out and not marked
            as working, since it is shorted
            - All working pixels are in the end activated and the voltage is set back to zero. The user can then test if they work by checking them manually or just by increasing the voltage with all these pixels selected.
        """

        # Update statusbar
        cf.log_message("Auto testing pixels started")

        # Define voltage steps (in the future this could be settings in the
        # global settings as well)
        global_settings = cf.read_global_settings()
        voltage_range = np.linspace(
            global_settings["auto_test_minimum_voltage"],
            global_settings["auto_test_maximum_voltage"],
            5,
            endpoint=True,
        )
        # voltage_range = np.linspace(2, 4, 26)
        biasing_time = 0.05

        # Reset Keithley multimeter
        self.keithley_multimeter.reset()

        # Unselect all pixels first (in case some have been selected before)
        self.unselect_all_pixels()

        # Turn off the voltage (if that was not already done)
        self.keithley_source.deactivate_output()

        # Go over all pixels
        working_pixels = []

        # Close all relays
        self.arduino_uno.trigger_relay(0)

        for pixel in range(len(self.sw_pushbutton_array)):

            # Set push button to checked and open relay of the pixel
            self.sw_pushbutton_array[pixel].setChecked(True)
            self.specw_pushbutton_array[pixel].setChecked(True)
            self.aw_pushbutton_array[pixel].setChecked(True)
            self.arduino_uno.trigger_relay(pixel + 1)

            # Measure baseline pd_voltage to compare value with
            pd_voltage_baseline = self.keithley_multimeter.measure_voltage()

            for voltage in voltage_range:
                # Turn on the voltage at the value "voltage"
                self.keithley_source.activate_output()
                self.keithley_source.set_voltage(voltage)
                self.sw_ct_voltage_spinBox.setValue(voltage)

                # Update GUI while being in a loop. It would be better to use
                # separate threads but for now this is the easiest way
                app.processEvents()

                # Bias for a certain time
                time.sleep(biasing_time)

                # Now read the current
                current = self.keithley_source.read_current()
                print(current)

                # A pixel is an open-circuit when the measured current is terribly low
                if voltage > voltage_range[0]:
                    if current < 1e-8:
                        break

                pd_voltage = self.keithley_multimeter.measure_voltage()
                print(pd_voltage)

                # A pixel is only working when it shows a high enough change in
                # PD voltage compared to the measured value before
                if pd_voltage - pd_voltage_baseline >= 0.001:
                    working_pixels.append(pixel + 1)
                    break
                else:
                    pd_voltage_baseline = pd_voltage

            # Deactivate the pixel again
            self.sw_pushbutton_array[pixel].setChecked(False)
            self.specw_pushbutton_array[pixel].setChecked(False)
            self.aw_pushbutton_array[pixel].setChecked(False)
            self.arduino_uno.trigger_relay(pixel + 1)

            # Turn off the voltage
            self.keithley_source.set_voltage(0)
            self.keithley_source.deactivate_output()
            self.sw_ct_voltage_spinBox.setValue(0)

        # Now activate all pixels that do work
        for pixel in working_pixels:
            self.sw_pushbutton_array[pixel - 1].setChecked(True)
            self.specw_pushbutton_array[pixel - 1].setChecked(True)
            self.aw_pushbutton_array[pixel - 1].setChecked(True)

            self.toggle_pixel(pixel, "sw")
            pixel += 1

        # Deactivate output again (since pixels were triggered)
        self.keithley_source.deactivate_output()

        # Update statusbar
        cf.log_message("Finished auto testing pixels")

    def mirror_goniometer_angles(self):
        """
        Function to mirror the goniometer angles for top emitting OLEDs
        """
        if self.sw_top_emitting_toggleSwitch.isChecked():
            self.motor.change_offset_angle(180)
            self.motor.top_emitting_reverse_angles = -1
            self.progressBar.show()
            self.gw_animation.reverse_angles(True)
            self.motor.move_to(0)
            # # Wait until the motor move is finished
            # while not self.motor_run.isFinished():
            #     time.sleep(0.1)
            # self.progressBar.hide()
            cf.log_message(
                "Motor offset angle increased by 180° and motor is moving to new zero position to account for top emitting device."
            )
        else:
            self.motor.change_offset_angle(-180)
            self.motor.top_emitting_reverse_angles = 1
            self.progressBar.show()
            self.gw_animation.reverse_angles(False)
            self.motor.move_to(0)
            # # Wait until the motor move is finished
            # while not self.motor_run.isFinished():
            #     time.sleep(0.1)
            # self.progressBar.hide()
            cf.log_message(
                "Motor offset angle set back to original value and motor is moving to new zero position to account for bottom emitting device."
            )

    def reverse_all_voltages(self):
        """
        Reverse all voltages to prevent the user from needing to swap the cables
        of the source. However, keep the readings and entires positive.
        """
        if self.sw_nip_toggleSwitch.isChecked():
            self.keithley_source.reverse = -1
            cf.log_message("All voltages are reversed")
        else:
            self.keithley_source.reverse = 1
            cf.log_message("Voltages are not reversed")

    # -------------------------------------------------------------------- #
    # ---------------------- Autotube Measurement  ----------------------- #
    # -------------------------------------------------------------------- #

    def read_autotube_parameters(self):
        """
        Function to read out the current measurement parameters that are
        present when clicking the Start Measurement button
        """
        global_parameters = cf.read_global_settings()
        measurement_parameters = {
            "min_voltage": self.aw_min_voltage_spinBox.value(),
            "max_voltage": self.aw_max_voltage_spinBox.value(),
            "changeover_voltage": self.aw_changeover_voltage_spinBox.value(),
            "low_voltage_step": self.aw_low_voltage_step_spinBox.value(),
            "high_voltage_step": self.aw_high_voltage_step_spinBox.value(),
            "scan_compliance": self.aw_scan_compliance_spinBox.value(),
            "auto_spectrum": self.aw_auto_measure_toggleSwitch.isChecked(),
            # "check_bad_contacts": self.aw_bad_contacts_toggleSwitch.isChecked(),
            # "fixed_multimeter_range": self.aw_set_fixed_multimeter_range_toggleSwitch.isChecked(),
            "photodiode_saturation": float(global_parameters["photodiode_saturation"]),
            # "check_pd_saturation": self.aw_pd_saturation_toggleSwitch.isChecked(),
        }

        # Boolean list for selected pixels
        selected_pixels = [
            self.aw_pixel1_pushButton.isChecked(),
            self.aw_pixel2_pushButton.isChecked(),
            self.aw_pixel3_pushButton.isChecked(),
            self.aw_pixel4_pushButton.isChecked(),
            self.aw_pixel5_pushButton.isChecked(),
            self.aw_pixel6_pushButton.isChecked(),
            self.aw_pixel7_pushButton.isChecked(),
            self.aw_pixel8_pushButton.isChecked(),
        ]

        # Return only the pixel numbers of the selected pixels
        selected_pixels_numbers = [i + 1 for i, x in enumerate(selected_pixels) if x]

        # Update statusbar
        cf.log_message("Autotube paremeters read")

        return measurement_parameters, selected_pixels_numbers

    @QtCore.Slot(list, list, list)
    def plot_autotube_measurement(self, voltage, current, pd_voltage):
        """
        Function to plot the results from the autotube measurement to the central graph.
        """
        # self.aw_fig.figure()

        # Clear axis
        # try:
        #     del self.aw_ax.lines
        #     del self.aw_ax2.lines
        # except AttributeError:
        #     print("Start Plotting")
        ax1_scale = self.aw_ax.get_yaxis().get_scale()
        ax2_scale = self.aw_ax2.get_yaxis().get_scale()

        self.aw_ax.cla()
        self.aw_ax2.cla()

        # Plot current
        self.aw_ax.plot(
            voltage,
            np.abs(current),
            color=(68 / 255, 188 / 255, 65 / 255),
            marker="o",
        )
        # twin object for two different y-axis on the sample plot
        # make a plot with different y-axis using second axis object
        self.aw_ax2.plot(
            voltage,
            pd_voltage,
            color=(85 / 255, 170 / 255, 255 / 255),
            marker="o",
        )
        self.aw_ax2.format_coord = self.make_format(self.aw_ax, self.aw_ax2)

        self.aw_ax.grid(True)
        self.aw_ax.set_xlabel("Voltage (V)", fontsize=14)
        self.aw_ax.set_ylabel(
            "Abs. Current (mA)", color=(68 / 255, 188 / 255, 65 / 255), fontsize=14
        )
        self.aw_ax2.set_ylabel(
            "Photodiode Voltage (V)",
            color=(85 / 255, 170 / 255, 255 / 255),
            fontsize=14,
        )

        # If the axis was previously a log, keep it as a log
        self.aw_ax.set_yscale(ax1_scale)
        self.aw_ax2.set_yscale(ax2_scale)

        self.aw_fig.draw()

        # Update statusbar
        cf.log_message("Autotube measurement plotted")

    def start_autotube_measurement(self):
        """
        Function that executes the actual measurement (the logic of which is
        stored in autotube_measurement.py). Iteration over the selected
        pixels as well as a call for the plotting happens here.
        """
        # If the measurement was already started and the button is clicked
        # again, stop the measurement
        if not self.aw_start_measurement_pushButton.isChecked():
            self.autotube_measurement.stop = True
            return

        # Save read setup parameters
        setup_parameters = self.safe_read_setup_parameters()

        # Read global parameters
        global_settings = cf.read_global_settings()

        # Update statusbar
        cf.log_message("Autotube measurement started")

        measurement_parameters, selected_pixels = self.read_autotube_parameters()

        # Set progress bar to zero
        self.progressBar.show()
        self.progressBar.setProperty("value", 0)

        # Now read in the global settings from file
        # global_settings = cf.read_global_settings()

        # Instantiate our class
        self.autotube_measurement = AutotubeMeasurement(
            self.keithley_source,
            self.keithley_multimeter,
            self.arduino_uno,
            measurement_parameters,
            setup_parameters,
            global_settings["multimeter_latency"],
            selected_pixels,
            global_settings["photodiode_position"],
            self,
        )

        # Start thread to run measurement
        self.autotube_measurement.start()

    # -------------------------------------------------------------------- #
    # ---------------------- Spectrum Measurement  ----------------------- #
    # -------------------------------------------------------------------- #
    def integration_time_changed(self):
        """
        Function that changes the real voltage when the voltage was changed
        in the UI
        """
        # Read in integration time from spinBox
        integration_time = self.specw_integration_time_spinBox.value()

        # Set integration_time
        self.spectrometer.set_integration_time_ms(integration_time)

    def read_spectrum_parameters(self):
        """
        Function to read out the current fields entered in the spectrum tab
        """
        spectrum_parameters = {
            "test_voltage": self.specw_voltage_spinBox.value(),
            "integration_time": self.specw_integration_time_spinBox.value(),
            "selected_pixel": [
                self.specw_pixel1_pushButton.isChecked(),
                self.specw_pixel2_pushButton.isChecked(),
                self.specw_pixel3_pushButton.isChecked(),
                self.specw_pixel4_pushButton.isChecked(),
                self.specw_pixel5_pushButton.isChecked(),
                self.specw_pixel6_pushButton.isChecked(),
                self.specw_pixel7_pushButton.isChecked(),
                self.specw_pixel8_pushButton.isChecked(),
            ],
        }

        # Update statusbar
        cf.log_message("Spectrum parameters read")

        return spectrum_parameters

    def save_spectrum(self):
        """
        Function that saves the spectrum (probably by doing another
        measurement and shortly turning on the OLED for a background
        measurement and then saving this into a single file)
        """

        # Load in setup parameters and make sure that the parameters make sense
        global_settings = cf.read_global_settings()
        setup_parameters = self.safe_read_setup_parameters()
        spectrum_parameters = self.read_spectrum_parameters()

        # Return only the pixel numbers of the selected pixels
        selected_pixels = [
            i + 1 for i, x in enumerate(spectrum_parameters["selected_pixel"]) if x
        ]

        # Ensure that only one pixel is selected (anything else does not really
        # make sense)
        if np.size(selected_pixels) == 0 or np.size(selected_pixels) > 1:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText("Please select exactly one pixel!")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.setStyleSheet(
                "background-color: rgb(44, 49, 60);\n"
                "color: rgb(255, 255, 255);\n"
                'font: 63 bold 10pt "Segoe UI";\n'
                ""
            )
            msgBox.exec()

            cf.log_message("More or less than one pixel selected")
            raise UserWarning("Please select exactly one pixel!")

        self.progressBar.show()

        # Store data in pd dataframe
        df_spectrum_data = pd.DataFrame(
            columns=["wavelength", "background", "intensity"]
        )

        # Get wavelength and intensity of spectrum under light conditions
        (
            df_spectrum_data["wavelength"],
            df_spectrum_data["intensity"],
        ) = self.spectrometer.measure()

        self.progressBar.setProperty("value", 50)

        # Turn off all pixels wait two seconds to ensure that there is no light left and measure again
        self.unselect_all_pixels()
        time.sleep(2)
        (
            wavelength,
            df_spectrum_data["background"],
        ) = self.spectrometer.measure()

        # Save data
        file_path = (
            setup_parameters["folder_path"]
            + date.today().strftime("%Y-%m-%d_")
            + setup_parameters["batch_name"]
            + "_d"
            + str(setup_parameters["device_number"])
            + "_p"
            + str(selected_pixels[0])
            + "_spec"
            + ".csv"
        )

        # Define header line with voltage and integration time
        line01 = (
            "Voltage: "
            + str(self.specw_voltage_spinBox.value())
            + " V\t"
            + "Integration Time: "
            + str(self.spectrum_measurement.spectrometer.integration_time)
            + " ms"
            + "Non-linearity Correction: "
            + str(bool(global_settings["spectrometer_non_linearity_correction"]))
        )

        line02 = "### Measurement data ###"
        line03 = "Wavelength\t Background\t Intensity"
        line04 = "nm\t counts\t counts\n"
        header_lines = [
            line01,
            line02,
            line03,
            line04,
        ]

        # Format the dataframe for saving (no. of digits)
        df_spectrum_data["wavelength"] = df_spectrum_data["wavelength"].map(
            lambda x: "{0:.2f}".format(x)
        )
        df_spectrum_data["background"] = df_spectrum_data["background"].map(
            lambda x: "{0:.1f}".format(x)
        )
        df_spectrum_data["intensity"] = df_spectrum_data["intensity"].map(
            lambda x: "{0:.1f}".format(x)
        )

        cf.save_file(df_spectrum_data, file_path, header_lines)

        # # Write header lines to file
        # with open(file_path, "a") as the_file:
        #     the_file.write("\n".join(header_lines))

        # # Now write pandas dataframe to file
        # df_spectrum_data.to_csv(
        #     file_path, index=False, mode="a", header=False, sep="\t"
        # )

        self.progressBar.setProperty("value", 100)
        time.sleep(0.5)
        self.progressBar.hide()

    @QtCore.Slot(list, list)
    def update_spectrum(self, wavelength, intensity):
        """
        Function that is continuously evoked when the spectrum is updated by
        the other thread
        """
        # Clear plot
        # self.specw_ax.cla()
        if self.specw_ax.lines:
            self.specw_ax.lines[0].remove()

        # Plot current
        self.specw_ax.plot(
            wavelength,
            intensity,
            color=(68 / 255, 188 / 255, 65 / 255),
            marker="o",
        )

        self.specw_fig.draw()

    # -------------------------------------------------------------------- #
    # ---------------------- Lifetime Measurement  ----------------------- #
    # -------------------------------------------------------------------- #

    def read_lifetime_parameters(self):
        """
        Function to read out the current measurement parameters that are
        present when clicking the Start Measurement button
        """
        global_parameters = cf.read_global_settings()
        measurement_parameters = {
            "current_mode": self.ltw_voltage_or_current_toggleSwitch.isChecked(),
            "voltage": self.ltw_voltage_spinBox.value(),
            "max_current": self.ltw_max_current_spinBox.value(),
            "on_time": self.ltw_on_time_spinBox.value(),
            "measurement_interval": self.ltw_measurement_interval_spinBox.value(),
            "all_pixel_mode": self.ltw_all_pixel_mode_toggleSwitch.isChecked(),
            # "check_bad_contacts": self.aw_bad_contacts_toggleSwitch.isChecked(),
            # "fixed_multimeter_range": self.aw_set_fixed_multimeter_range_toggleSwitch.isChecked(),
            "photodiode_saturation": float(global_parameters["photodiode_saturation"]),
            # "check_pd_saturation": self.aw_pd_saturation_toggleSwitch.isChecked(),
        }

        # Boolean list for selected pixels
        selected_pixels = [
            self.ltw_pixel1_pushButton.isChecked(),
            self.ltw_pixel2_pushButton.isChecked(),
            self.ltw_pixel3_pushButton.isChecked(),
            self.ltw_pixel4_pushButton.isChecked(),
            self.ltw_pixel5_pushButton.isChecked(),
            self.ltw_pixel6_pushButton.isChecked(),
            self.ltw_pixel7_pushButton.isChecked(),
            self.ltw_pixel8_pushButton.isChecked(),
        ]

        # Return only the pixel numbers of the selected pixels
        selected_pixels_numbers = [i + 1 for i, x in enumerate(selected_pixels) if x]

        # Update statusbar
        cf.log_message("Lifetime parameters read")

        return measurement_parameters, selected_pixels_numbers

    @QtCore.Slot(list, list, list, bool)
    def plot_lifetime_measurement(
        self, time, pd_voltage, current_or_voltage, current_mode
    ):
        """
        Function to plot the results from the lifetime measurement to the central graph.
        """
        # self.aw_fig.figure()

        # Clear axis
        # try:
        #     del self.aw_ax.lines
        #     del self.aw_ax2.lines
        # except AttributeError:
        #     print("Start Plotting")
        ax1_scale = self.ltw_ax.get_yaxis().get_scale()
        ax2_scale = self.ltw_ax2.get_yaxis().get_scale()

        self.ltw_ax.cla()
        self.ltw_ax2.cla()

        # Plot current
        self.ltw_ax.plot(
            time,
            np.abs(pd_voltage),
            color=(68 / 255, 188 / 255, 65 / 255),
            marker="o",
        )
        # twin object for two different y-axis on the sample plot
        # make a plot with different y-axis using second axis object
        self.ltw_ax2.plot(
            time,
            current_or_voltage,
            color=(85 / 255, 170 / 255, 255 / 255),
            marker="o",
        )
        self.ltw_ax2.format_coord = self.make_format(self.ltw_ax, self.ltw_ax2)

        self.ltw_ax.grid(True)
        self.ltw_ax.set_xlabel("Time (s)", fontsize=14)
        self.ltw_ax.set_ylabel("Photodiode Voltage (V)", fontsize=14)

        if current_mode:
            self.ltw_ax2.set_ylabel(
                "Voltage (V)",
                color=(85 / 255, 170 / 255, 255 / 255),
                fontsize=14,
            )
        else:
            self.ltw_ax2.set_ylabel(
                "Current (A)",
                color=(85 / 255, 170 / 255, 255 / 255),
                fontsize=14,
            )

        # If the axis was previously a log, keep it as a log
        self.ltw_ax.set_yscale(ax1_scale)
        self.ltw_ax2.set_yscale(ax2_scale)

        self.ltw_fig.draw()

        # Update statusbar
        cf.log_message("Lifetime measurement plotted")

    def start_lifetime_measurement(self):
        """
        Function that executes the actual measurement (the logic of which is
        stored in lifetime_measurement.py). Iteration over the selected
        pixels as well as a call for the plotting happens here.
        """
        # If the measurement was already started and the button is clicked
        # again, stop the measurement
        if not self.ltw_start_measurement_pushButton.isChecked():
            self.lifetime_measurement.stop = True
            return

        # Save read setup parameters
        setup_parameters = self.safe_read_setup_parameters()

        # Read global parameters
        global_settings = cf.read_global_settings()

        # Update statusbar
        cf.log_message("Lifetime measurement started")

        measurement_parameters, selected_pixels = self.read_lifetime_parameters()

        # Set progress bar to zero
        self.progressBar.show()
        self.progressBar.setProperty("value", 0)

        # Now read in the global settings from file
        # global_settings = cf.read_global_settings()

        # Instantiate our class
        self.lifetime_measurement = LifetimeMeasurement(
            self.keithley_source,
            self.keithley_multimeter,
            self.arduino_uno,
            measurement_parameters,
            setup_parameters,
            selected_pixels,
            self,
        )

        # Start thread to run measurement
        self.lifetime_measurement.start()

    def disable_pixel_selection(self):
        """
        Function to disable all options that are only needed for el in case
        the pl switch was toggled.
        """
        # If it is checked, disable buttons. Else enable them
        if self.ltw_all_pixel_mode_toggleSwitch.isChecked():
            self.ltw_pixel1_pushButton.setEnabled(False)
            self.ltw_pixel2_pushButton.setEnabled(False)
            self.ltw_pixel3_pushButton.setEnabled(False)
            self.ltw_pixel4_pushButton.setEnabled(False)
            self.ltw_pixel5_pushButton.setEnabled(False)
            self.ltw_pixel6_pushButton.setEnabled(False)
            self.ltw_pixel7_pushButton.setEnabled(False)
            self.ltw_pixel8_pushButton.setEnabled(False)

            self.ltw_pixel1_pushButton.setChecked(True)
            self.ltw_pixel2_pushButton.setChecked(True)
            self.ltw_pixel3_pushButton.setChecked(True)
            self.ltw_pixel4_pushButton.setChecked(True)
            self.ltw_pixel5_pushButton.setChecked(True)
            self.ltw_pixel6_pushButton.setChecked(True)
            self.ltw_pixel7_pushButton.setChecked(True)
            self.ltw_pixel8_pushButton.setChecked(True)

        else:
            # Enable all options that are only relevant for EL measurements
            self.ltw_pixel1_pushButton.setEnabled(True)
            self.ltw_pixel2_pushButton.setEnabled(True)
            self.ltw_pixel3_pushButton.setEnabled(True)
            self.ltw_pixel4_pushButton.setEnabled(True)
            self.ltw_pixel5_pushButton.setEnabled(True)
            self.ltw_pixel6_pushButton.setEnabled(True)
            self.ltw_pixel7_pushButton.setEnabled(True)
            self.ltw_pixel8_pushButton.setEnabled(True)

    # -------------------------------------------------------------------- #
    # --------------------- Goniometer Measurement  ---------------------- #
    # -------------------------------------------------------------------- #
    def read_goniometer_parameters(self):
        """
        Function to read out the current fields entered in the goniometer tab
        """

        global_parameters = cf.read_global_settings()
        pixels = [
            self.gw_pixel1_pushButton.isChecked(),
            self.gw_pixel2_pushButton.isChecked(),
            self.gw_pixel3_pushButton.isChecked(),
            self.gw_pixel4_pushButton.isChecked(),
            self.gw_pixel5_pushButton.isChecked(),
            self.gw_pixel6_pushButton.isChecked(),
            self.gw_pixel7_pushButton.isChecked(),
            self.gw_pixel8_pushButton.isChecked(),
        ]

        goniometer_parameters = {
            "minimum_angle": self.gw_minimum_angle_spinBox.value(),
            "maximum_angle": self.gw_maximum_angle_spinBox.value(),
            "step_angle": self.gw_step_angle_spinBox.value(),
            "integration_time": self.gw_integration_time_spinBox.value(),
            # "homing_time": self.gw_homing_time_spinBox.value(),
            # "moving_time": self.gw_moving_time_spinBox.value(),
            "oled_on_time": global_parameters["oled_on_time"],
            "voltage_or_current": self.gw_voltage_or_current_toggleSwitch.isChecked(),
            "background_every_step": self.gw_background_every_step_toggleSwitch.isChecked(),
            "degradation_check": self.gw_degradation_check_toggleSwitch.isChecked(),
            "el_or_pl": self.gw_el_or_pl_toggleSwitch.isChecked(),
            "vc_value": self.gw_vc_value_spinBox.value(),
            "vc_compliance": self.gw_vc_compliance_spinBox.value(),
            "selected_pixels": [i + 1 for i, x in enumerate(pixels) if x],
        }

        # Update statusbar
        cf.log_message("Goniometer parameters read")

        return goniometer_parameters

    def start_goniometer_measurement(self):
        """
        Function that starts the goniometer measurement. On the long run
        there should also be the option to interrupt the goniometer
        measurement when it is already running
        """
        # If the measurement is already running and the button is pressed,
        # abort the measurement
        if not self.gw_start_measurement_pushButton.isChecked():
            self.goniometer_measurement.pause = "return"
            return

        # Read all relevant parameters
        setup_parameters = self.safe_read_setup_parameters()
        (
            autotube_measurement_parameters,
            selected_pixels,
        ) = self.read_autotube_parameters()
        goniometer_measurement_parameters = self.read_goniometer_parameters()
        # global_settings = cf.read_global_settings()

        # Check that only exactly one pixel is selected before measurement can
        # be started (this could be also done with the gui directly). Also if
        # pl was selected the selected pixels do not matter
        if (not goniometer_measurement_parameters["el_or_pl"]) and len(
            goniometer_measurement_parameters["selected_pixels"]
        ) != 1:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText("Please select exactly one pixel")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.setStyleSheet(
                "background-color: rgb(44, 49, 60);\n"
                "color: rgb(255, 255, 255);\n"
                'font: 63 bold 10pt "Segoe UI";\n'
                ""
            )
            msgBox.exec()

            self.gw_start_measurement_pushButton.setChecked(False)
            cf.log_message("More or less than one pixel selected")
            raise UserWarning("Please select exactly one pixel")

            return

        # Update statusbar
        cf.log_message("Goniometer measurement started")

        # Set progress bar to zero
        self.progressBar.show()
        self.progressBar.setProperty("value", 0)

        # Instantiate our class it has to be a class variable otherwise it
        # would be destroyed as soon as this function terminates
        self.goniometer_measurement = GoniometerMeasurement(
            self.keithley_source,
            self.keithley_multimeter,
            self.arduino_uno,
            self.motor,
            self.spectrometer,
            goniometer_measurement_parameters["selected_pixels"],
            goniometer_measurement_parameters,
            autotube_measurement_parameters,
            setup_parameters,
            self,
        )

        # Call measurement.start() to measure and save all the measured data into the class itself
        # measurement.run()
        self.goniometer_measurement.start()

        # Call measurement.save_data() to directly save the data to a file
        # measurement.save_iv_data()
        # measurement.save_spectrum_data()

        # Update GUI while being in a loop. It would be better to use
        # separate threads but for now this is the easiest way
        # app.processEvents()

        # Untoggle the pushbutton
        # self.gw_start_measurement_pushButton.setChecked(False)

    @QtCore.Slot(list, list)
    def update_goniometer_spectrum(self, column_names, spec):
        """
        Function that updates the goniometer measured spectrum as well as the status and progress bar
        """
        # Now put the dataframe together again
        spectrum = pd.DataFrame(spec, columns=column_names)

        # Check if this is the first time in this run that the graph is
        # plotted. This is the case, when the dataframe only has three columns
        # (wavelength, background, minimum angle intensity)
        if spectrum.shape[1] == 3:
            self.gw_fig.figure.clf()
            self.gw_ax1, self.gw_ax2 = self.gw_fig.figure.subplots(1, 2)
        else:
            self.gw_ax1.cla()
            self.gw_ax2.cla()

        # Check if there are multiple background spectra
        background_columns = [col for col in spectrum.columns if "bg" in col]

        if len(background_columns) == 0:
            # Case 1: Only one background spectrum
            temp = (
                spectrum.drop(["wavelength"], axis=1)
                .transpose()
                .sub(spectrum["background"])
                .transpose()
            )

            # Now add the wavelength to the dataframe again
            temp["wavelength"] = spectrum["wavelength"]

            # And set the wavelength as index of the dataframe and drop the background instead now
            temp = temp.set_index("wavelength").drop(["background"], axis=1)
        else:
            # Case 2: Multiple background spectra
            temp = spectrum.copy()

            for i in range(0, len(background_columns)):
                background_col = background_columns[i]
                intensity_col = spectrum.columns[
                    spectrum.columns.get_loc(background_col) + 1
                ]

                # Subtract the background spectrum from the corresponding intensity data
                temp[intensity_col] = temp[intensity_col] - temp[background_col]

            # Drop all background columns
            temp = temp.drop(background_columns, axis=1)

            # Set the wavelength as index of the dataframe
            temp = temp.set_index("wavelength")

        # Plot current data
        # This is the best way I could come up with so far. There must be a better one, however.
        x = temp.index.values.tolist()
        y = list(map(float, temp.columns.values.tolist()))

        X, Y = np.meshgrid(x, y)

        self.gw_ax1.set_xlabel("Angle (°)")
        self.gw_ax1.set_ylabel("Wavelength (nm)")

        self.gw_ax1.pcolormesh(Y, X, temp.to_numpy().T, shading="auto")

        # Calculate the maximum for each angle
        max_intensity_for_each_angle = temp.max(axis=0).to_list()
        angles = temp.max(axis=0).index.to_numpy(dtype=float)

        self.gw_ax2.set_xlabel("Angle (°)")
        self.gw_ax2.set_ylabel("Maximum Intensity (counts)")
        self.gw_ax2.grid(True)

        self.gw_ax2.plot(
            angles,
            max_intensity_for_each_angle,
            color=(85 / 255, 170 / 255, 255 / 255),
            marker="o",
        )

        # Draw the new figure
        self.gw_fig.draw()
        time.sleep(0.1)

        # Update statusbar
        cf.log_message("Goniometer Measurement Plotted")

    @QtCore.Slot(list, list)
    def update_goniometer_simple_spectrum(self, spectrum, labels):
        """
        Function that does simple plotting of a 1D spectrum at the beginning
        and in the end
        """
        # Clear the figure and create one with single graph
        self.gw_fig.figure.clf()
        self.gw_ax1 = self.gw_fig.figure.subplots()

        # Depending on the size of the input array, plot several graphs
        for i in range(np.shape(spectrum)[0] - 1):
            self.gw_ax1.set_xlabel("Wavelength (nm)")
            self.gw_ax1.set_ylabel("Intensity (counts)")
            self.gw_ax1.grid(True)

            self.gw_ax1.plot(spectrum[0], spectrum[i + 1], label=labels[i])

        # Show a legend
        self.gw_ax1.legend()

        # Draw the new figure
        self.gw_fig.draw()
        time.sleep(0.1)

        # Update statusbar
        cf.log_message("Spectrum plotted")

    def move_motor(self):
        """
        Function to do a bare movement of the motor without any measurement.
        """
        # # Read the global settings to initialise the motor
        # global_settings = cf.read_global_settings()

        # Read the angle from the spinBox
        angle = self.gw_offset_angle_spinBox.value()

        self.progressBar.show()
        self.motor.move_to(angle)

    def disable_el_options(self):
        """
        Function to disable all options that are only needed for el in case
        the pl switch was toggled.
        """
        # If it is checked, disable buttons. Else enable them
        if self.gw_el_or_pl_toggleSwitch.isChecked():
            # Set the two other toggle switches to False
            self.gw_background_every_step_toggleSwitch.setChecked(False)
            self.gw_voltage_or_current_toggleSwitch.setChecked(False)

            # Disable all non-relevant options
            self.gw_background_every_step_toggleSwitch.setEnabled(False)
            self.gw_voltage_or_current_toggleSwitch.setEnabled(False)
            # self.gw_oled_on_time_spinBox.setEnabled(False)
            self.gw_vc_value_spinBox.setEnabled(False)
            self.gw_vc_compliance_spinBox.setEnabled(False)

            self.gw_pixel1_pushButton.setEnabled(False)
            self.gw_pixel2_pushButton.setEnabled(False)
            self.gw_pixel3_pushButton.setEnabled(False)
            self.gw_pixel4_pushButton.setEnabled(False)
            self.gw_pixel5_pushButton.setEnabled(False)
            self.gw_pixel6_pushButton.setEnabled(False)
            self.gw_pixel7_pushButton.setEnabled(False)
            self.gw_pixel8_pushButton.setEnabled(False)

        else:
            # Enable all options that are only relevant for EL measurements
            self.gw_background_every_step_toggleSwitch.setEnabled(True)
            self.gw_voltage_or_current_toggleSwitch.setEnabled(True)
            # self.gw_oled_on_time_spinBox.setEnabled(True)
            self.gw_vc_value_spinBox.setEnabled(True)
            self.gw_vc_compliance_spinBox.setEnabled(True)

            self.gw_pixel1_pushButton.setEnabled(True)
            self.gw_pixel2_pushButton.setEnabled(True)
            self.gw_pixel3_pushButton.setEnabled(True)
            self.gw_pixel4_pushButton.setEnabled(True)
            self.gw_pixel5_pushButton.setEnabled(True)
            self.gw_pixel6_pushButton.setEnabled(True)
            self.gw_pixel7_pushButton.setEnabled(True)
            self.gw_pixel8_pushButton.setEnabled(True)

    @QtCore.Slot(str)
    def pause_goniometer_measurement(self, status):
        """
        Function to ask to turn the PL lamp on before continuing
        """
        msgBox = QtWidgets.QMessageBox()
        # Now check which message to display (turn on or off the lamp)
        if status == "on":
            msgBox.setText("You can now turn on the UV-lamp")
        elif status == "off":
            msgBox.setText("You can now turn off the UV-lamp")

        msgBox.setStandardButtons(
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel
        )
        msgBox.setStyleSheet(
            "QWidget {\n"
            "            background-color: rgb(44, 49, 60);\n"
            "            color: rgb(255, 255, 255);\n"
            '            font: 63 10pt "Segoe UI";\n'
            "}\n"
            "QPushButton {\n"
            "            border: 2px solid rgb(52, 59, 72);\n"
            "            border-radius: 5px;\n"
            "            background-color: rgb(52, 59, 72);\n"
            "}\n"
            "QPushButton:hover {\n"
            "            background-color: rgb(57, 65, 80);\n"
            "            border: 2px solid rgb(61, 70, 86);\n"
            "}\n"
            "QPushButton:pressed {\n"
            "            background-color: rgb(35, 40, 49);\n"
            "            border: 2px solid rgb(43, 50, 61);\n"
            "}\n"
            "QPushButton:checked {\n"
            "            background-color: rgb(35, 40, 49);\n"
            "            border: 2px solid rgb(85, 170, 255);\n"
            "}"
        )
        button = msgBox.exec()

        if button == QtWidgets.QMessageBox.Ok:
            self.goniometer_measurement.pause = "break"
        elif button == QtWidgets.QMessageBox.Cancel:
            self.goniometer_measurement.pause = "return"
            self.gw_start_measurement_pushButton.setChecked(False)

    def change_measurement_mode(self):
        """
        Function that does some visual changes if the user selects current or
        voltage mode in AR measurements.
        """
        if self.gw_voltage_or_current_toggleSwitch.isChecked():
            # Current mode
            # Set compliance to 5V
            self.gw_vc_compliance_spinBox.setValue(5)
            self.gw_vc_compliance_label.setText("Max. Voltage (V)")
            self.gw_vc_value_label.setText("Applied Current (mA)")

        else:
            # Voltage mode
            # Set compliance to 1.05 A
            self.gw_vc_compliance_spinBox.setValue(1050)
            self.gw_vc_compliance_label.setText("Max. Current (mA)")
            self.gw_vc_value_label.setText("Applied Voltage (V)")

    def change_measurement_mode_ltw(self):
        """
        Function that does some visual changes if the user selects current or
        voltage mode in AR measurements.
        """
        if self.ltw_voltage_or_current_toggleSwitch.isChecked():
            # Current mode
            # Set compliance to 5V
            self.ltw_voltage_spinBox.setValue(5)
            self.ltw_voltage_label.setText("Max. Voltage (V)")
            self.ltw_max_current_label.setText("Applied Current (mA)")

        else:
            # Voltage mode
            # Set compliance to 1.05 A
            self.ltw_max_current_spinBox.setValue(1050)
            self.ltw_max_current_label.setText("Max. Current (mA)")
            self.ltw_voltage_label.setText("Applied Voltage (V)")

    def closeEvent(self, event):
        """
        Function that shall allow for save closing of the program
        """

        cf.log_message("Program closed")

        # Kill spectrometer thread
        try:
            self.spectrum_measurement.kill()
        except Exception as e:
            cf.log_message("Spectrometer thread could not be killed")
            cf.log_message(e)

        # Kill keithley thread savely
        try:
            self.current_tester.kill()
        except Exception as e:
            cf.log_message("Keithley thread could not be killed")
            cf.log_message(e)

        # Kill arduino connection
        try:
            self.arduino_uno.close()
        except Exception as e:
            cf.log_message("Arduino connection could not be savely killed")
            cf.log_message(e)

        # Kill connection to spectrometer savely
        try:
            self.spectrometer.close_connection()
        except Exception as e:
            cf.log_message("Spectrometer could not be turned off savely")
            cf.log_message(e)

        # Turn off all outputs etc of Keithley source
        try:
            self.keithley_source.deactivate_output()
        except Exception as e:
            cf.log_message("Keithley source output could not be deactivated")
            cf.log_message(e)

        # Kill connection to Keithleys
        try:
            pyvisa.ResourceManager().close()
        except Exception as e:
            cf.log_message("Connection to Keithleys could not be closed savely")
            cf.log_message(e)

        # Kill motor savely
        try:
            self.progressBar.show()
            # Move motor back go home position
            global_settings = cf.read_global_settings()
            self.motor.change_velocity(20)
            self.motor.top_emitting_reverse_angles = 1
            self.motor.change_offset_angle(
                global_settings["motor_offset"], relative=False
            )
            self.motor.move_to(global_settings["motor_offset"])

            # Wait until the motor move is finished
            while not self.motor_run.isFinished():
                time.sleep(0.1)

            self.progressBar.hide()
            self.motor.clean_up()

        except Exception as e:
            cf.log_message("Motor could not be turned off savely")
            cf.log_message(e)

        # if can_exit:
        event.accept()  # let the window close
        self.close()
        # else:
        #     event.ignore()


# Logging
# Prepare file path etc. for logging
LOG_FILENAME = "./usr/log.out"
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format=(
        "%(asctime)s - [%(levelname)s] -"
        " (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
    ),
    datefmt="%m/%d/%Y %I:%M:%S %p",
)

# Activate log_rotate to rotate log files after it reached 1 MB size ()
handler = RotatingFileHandler(LOG_FILENAME, maxBytes=1000000)
logging.getLogger("Rotating Log").addHandler(handler)


# ---------------------------------------------------------------------------- #
# -------------------- This is to execute the program ------------------------ #
# ---------------------------------------------------------------------------- #
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()

    # Icon (see https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105)
    import ctypes

    if not sys.platform.startswith("linux"):
        myappid = "mycompan.myproduct.subproduct.version"  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app_icon = QtGui.QIcon()
    app_icon.addFile("./icons/program_icon.png", QtCore.QSize(256, 256))
    app.setWindowIcon(app_icon)

    ui.show()
    sys.exit(app.exec())
