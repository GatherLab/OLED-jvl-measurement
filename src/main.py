from UI_main_window import Ui_MainWindow
from settings import Settings

from autotube_measurement import AutotubeMeasurement
from current_tester import CurrentTester
from spectrum_measurement import SpectrumMeasurement
from goniometer_measurement import GoniometerMeasurement
from loading_window import LoadingWindow

from tests.tests import MockThorlabMotor
from hardware import (
    ArduinoUno,
    OceanSpectrometer,
    ThorlabMotor,
    KeithleyMultimeter,
    KeithleySource,
)

import core_functions as cf
import pyvisa

from PySide2 import QtCore, QtGui, QtWidgets

import time
import os
import json
import sys
import functools
from datetime import date
import logging
from logging.handlers import RotatingFileHandler

import matplotlib.pylab as plt
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
        try:
            global_settings = cf.read_global_settings()
            ThorlabMotor(
                global_settings["motor_number"], global_settings["motor_offset"]
            )
        except:
            cf.log_message(
                "Motor can probably not be initialised. Reconnect the motor or change the serial number in the global settings."
            )

        # -------------------------------------------------------------------- #
        # -------------------------- Hardware Setup -------------------------- #
        # -------------------------------------------------------------------- #

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
        self.sw_activate_local_mode_pushButton.clicked.connect(self.activate_local_mode)
        self.sw_browse_pushButton.clicked.connect(self.browse_folder)

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

        # -------------------------------------------------------------------- #
        # ---------------------- Autotube Measurement  ----------------------- #
        # -------------------------------------------------------------------- #

        # Link actions to buttons
        self.aw_start_measurement_pushButton.clicked.connect(
            self.start_autotube_measurement
        )

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

        # -------------------------------------------------------------------- #
        # --------------------- Goniometer Measurement  ---------------------- #
        # -------------------------------------------------------------------- #
        self.gw_start_measurement_pushButton.clicked.connect(
            self.start_goniometer_measurement
        )

        self.gw_move_pushButton.clicked.connect(self.move_motor)

        self.gw_el_or_pl_toggleSwitch.clicked.connect(self.disable_el_options)

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
        self.gw_offset_angle_spinBox.setMaximum(180)
        self.gw_offset_angle_spinBox.setMinimum(-179)
        self.gw_offset_angle_spinBox.setValue(motor_position)
        self.gw_minimum_angle_spinBox.setMaximum(180)
        self.gw_minimum_angle_spinBox.setMinimum(-179)
        self.gw_minimum_angle_spinBox.setValue(0)
        self.gw_maximum_angle_spinBox.setMaximum(180)
        self.gw_maximum_angle_spinBox.setMinimum(-179)
        self.gw_maximum_angle_spinBox.setValue(90)
        self.gw_step_angle_spinBox.setMaximum(360)
        self.gw_step_angle_spinBox.setValue(1)
        self.gw_integration_time_spinBox.setMaximum(10000)
        self.gw_integration_time_spinBox.setMinimum(0)
        self.gw_integration_time_spinBox.setValue(300)
        # self.gw_homing_time_spinBox.setValue(30)
        # self.gw_moving_time_spinBox.setValue(1)
        self.gw_pulse_duration_spinBox.setValue(2)
        self.gw_vc_value_spinBox.setValue(5)
        self.gw_vc_compliance_spinBox.setValue(1.05)

        # Set standard parameters for Spectral Measurement
        self.specw_voltage_spinBox.setMinimum(-5.0)
        self.specw_voltage_spinBox.setMaximum(50.0)
        self.specw_voltage_spinBox.setSingleStep(0.1)
        self.specw_voltage_spinBox.setValue(0)

        # Set standard parameters for Spectral Measurement
        self.sw_ct_voltage_spinBox.setMinimum(-5.0)
        self.sw_ct_voltage_spinBox.setMaximum(50.0)
        self.sw_ct_voltage_spinBox.setSingleStep(0.1)
        self.sw_ct_voltage_spinBox.setValue(0)

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
        This might become important in the future. The best idea is probably
        to just kill all unused threads when we change the tab.
        """

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

    def activate_local_mode(self):
        """
        Function to reset the devices and toggle local mode to be able to
        activate pixel. I am not really sure if that is how to terminate a qthread correctly but it works.
        https://stackoverflow.com/questions/17045368/qthread-emits-finished-signal-but-isrunning-returns-true-and-isfinished-re
        """
        # Reset the keithley by reseting it as voltage source
        self.keithley_source.as_voltage_source(1.05)
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
        self.keithley_source.activate_output()

    @QtCore.Slot(float)
    def update_ammeter(self, current_reading):
        """
        Function that is continuously evoked when the current is updated by
        current_tester thread.
        """
        self.sw_current_lcdNumber.display(current_reading)

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

        # Activate output and set voltage
        self.current_tester.keithley_source.activate_output()
        self.current_tester.keithley_source.set_voltage(voltage)

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

    def prebias_pixels(self):
        """
        Prebias all pixels (e.g. at -2 V)
        """

        # Update statusbar
        cf.log_message("Prebiasing pixels started")

        # This should be in the global settings later on (probably not
        # necessary to change every time but sometimes)
        pre_bias_voltage = -2  # in V
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
        Automatic testing of all pixels. The first very simple idea is as follows:
            - The voltage for one pixel is slowly increased (maybe steps of
            0.2) only until a certain current is reached. As soon as it is
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
        voltage_range = np.linspace(2, 7, 26)
        biasing_time = 0.05

        # Unselect all pixels first (in case some have been selected before)
        self.unselect_all_pixels()

        # Turn off the voltage (if that was not already done)
        self.keithley_source.deactivate_output()

        # Go over all pixels
        working_pixels = []

        for pixel in range(len(self.sw_pushbutton_array)):
            # Close all relays
            self.arduino_uno.trigger_relay(0)

            # Set push button to checked and open relay of the pixel
            self.sw_pushbutton_array[pixel].setChecked(True)
            self.specw_pushbutton_array[pixel].setChecked(True)
            self.arduino_uno.trigger_relay(pixel + 1)

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

                if current >= 0.02 and current <= 5:
                    working_pixels.append(pixel + 1)
                    break

            # Deactivate the pixel again
            self.sw_pushbutton_array[pixel].setChecked(False)
            self.specw_pushbutton_array[pixel].setChecked(False)
            self.arduino_uno.trigger_relay(pixel + 1)

            # Turn off the voltage
            self.keithley_source.set_voltage(0)
            self.keithley_source.deactivate_output()
            self.sw_ct_voltage_spinBox.setValue(0)

        # Now activate all pixels that do work
        for pixel in working_pixels:
            self.sw_pushbutton_array[pixel - 1].setChecked(True)
            self.specw_pushbutton_array[pixel - 1].setChecked(True)
            self.toggle_pixel(pixel, "sw")
            pixel += 1

        # Set voltage to prebias voltage
        self.keithley_source.activate_output()

        # Update statusbar
        cf.log_message("Finished auto testing pixels")

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
            "check_bad_contacts": self.aw_bad_contacts_toggleSwitch.isChecked(),
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
        self.aw_ax.cla()
        self.aw_ax2.cla()

        # Plot current
        self.aw_ax.plot(
            voltage,
            current,
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

        self.aw_ax.grid(True)
        self.aw_ax.set_xlabel("Voltage (V)", fontsize=14)
        self.aw_ax.set_ylabel(
            "Current (mA)", color=(68 / 255, 188 / 255, 65 / 255), fontsize=14
        )
        self.aw_ax2.set_ylabel(
            "Photodiode Voltage (V)",
            color=(85 / 255, 170 / 255, 255 / 255),
            fontsize=14,
        )

        self.aw_fig.draw()

        # Update statusbar
        cf.log_message("Autotube measurement plotted")

    def start_autotube_measurement(self):
        """
        Function that executes the actual measurement (the logic of which is
        stored in autotube_measurement.py). Iteration over the selected
        pixels as well as a call for the plotting happens here.
        """

        # Save read setup parameters
        setup_parameters = self.safe_read_setup_parameters()

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
            selected_pixels,
            False,
            self,
        )

        # Start thread to run measurement
        self.autotube_measurement.start()

    # -------------------------------------------------------------------- #
    # ---------------------- Spectrum Measurement  ----------------------- #
    # -------------------------------------------------------------------- #
    def read_spectrum_parameters(self):
        """
        Function to read out the current fields entered in the spectrum tab
        """
        spectrum_parameters = {
            "test_voltage": self.specw_voltage_spinBox.value(),
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
        del self.specw_ax.lines[0]

        # Plot current
        self.specw_ax.plot(
            wavelength,
            intensity,
            color=(68 / 255, 188 / 255, 65 / 255),
            marker="o",
        )

        self.specw_fig.draw()

    # -------------------------------------------------------------------- #
    # --------------------- Goniometer Measurement  ---------------------- #
    # -------------------------------------------------------------------- #
    def read_goniometer_parameters(self):
        """
        Function to read out the current fields entered in the goniometer tab
        """
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
            "pulse_duration": self.gw_pulse_duration_spinBox.value(),
            "voltage_or_current": self.gw_voltage_or_current_toggleSwitch.isChecked(),
            "voltage_scan": self.gw_voltage_scan_toggleSwitch.isChecked(),
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
        # Update progress bar
        # progress += 1
        # self.progressBar.setProperty(
        # "value", int(progress / len(selected_pixels) * 100)
        # )

        # Now put the dataframe together again
        spectrum = pd.DataFrame(spec, columns=column_names)

        # Clear axis
        self.gw_ax.cla()

        # first subtract the background from all columns but the wavelength
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

        # temp = (
        # spectrum.transpose()
        # .sub(spectrum["background"])
        # .transpose()
        # .set_index("wavelength")
        # .drop(["background"], axis=1)
        # )
        # self.gw_animation.move(float(spectrum.columns[-1][:-1]))

        # spectrum.drop(["background"], axis=1)
        # spectrum.set_index("wavelength")
        self.gw_ax.set_xlabel("Angle (°)")
        self.gw_ax.set_ylabel("Wavelength (nm)")

        # Plot current data
        # This is the best way I could come up with so far. There must be a better one, however.
        x = temp.index.values.tolist()
        y = list(map(float, temp.columns.values.tolist()))

        # if (max(x) - min(x)) / len(x) == 0:
        #     x_step = 1
        # else:
        #      _step = (max(x) - min(x)) / len(x)

        # if (max(y) - min(y)) / len(y) == 0:
        #      _step = 1
        #     y_max = max(y) + 1
        # else:
        #     y_step = (max(y) - min(y)) / len(y)
        #     y_max = max(y)

        # X, Y = np.mgrid[
        #     min(x) : max(x) : x_step,
        #      in(y) : y_max : y_step,
        # ]

        X, Y = np.meshgrid(x, y)

        self.gw_ax.pcolormesh(Y, X, temp.to_numpy().T, shading="auto")
        # self.gw_fig.figure.colorbar(im, ax=self.gw_ax)

        # Now set the labels (not correct by default)
        # self.gw_ax.yaxis.set_major_locator(plt.MaxNLocator(5))
        # self.gw_ax.xaxis.set_major_locator(plt.MaxNLocator(5))

        # self.gw_ax.set_yticks(np.linspace(np.min(temp.index), np.max(temp.index), 5))
        # self.gw_ax.set_xticks(np.arange(0.5, len(temp.index), 1))

        # self.gw_ax.set_yticks(np.arange(0.5, len(temp.index), 1))
        # self.gw_ax.set_xticks(np.arange(0.5, len(temp.columns), 1))
        # self.gw_ax.set_xticklabels(xlabels, minor=False)
        # self.gw_ax.set_yticklabels(ylabels, minor=False)

        self.gw_fig.draw()

        # Update statusbar
        cf.log_message("Goniometer Measurement Plotted")

    def move_motor(self):
        """
        Function to do a bare movement of the motor without any measurement.
        """
        # # Read the global settings to initialise the motor
        # global_settings = cf.read_global_settings()

        # Read the angle from the spinBox
        angle = self.gw_offset_angle_spinBox.value()

        cf.log_message("Motor is moving")

        # Move the motor and change the animation
        self.motor.move_to(angle)

        # I decided to read the motor position instead of doing a virtual animation. The animation shall always show the true motor position (if the hardware allows that). The
        motor_position = self.motor.read_position()
        self.gw_animation.move(motor_position)
        app.processEvents()
        time.sleep(0.05)

        while not math.isclose(angle, motor_position, abs_tol=0.01):
            motor_position = self.motor.read_position()
            self.gw_animation.move(motor_position)
            app.processEvents()
            time.sleep(0.05)

        # Update animation once more since the position might be 0.9 at this
        # point (int comparison in the above while loop)
        self.gw_animation.move(motor_position)
        app.processEvents()

        cf.log_message("Motor moved to " + str(angle) + " °")

    def disable_el_options(self):
        """
        Function to disable all options that are only needed for el in case
        the pl switch was toggled.
        """
        # If it is checked, disable buttons. Else enable them
        if self.gw_el_or_pl_toggleSwitch.isChecked():
            # Set the two other toggle switches to False
            self.gw_voltage_scan_toggleSwitch.setChecked(False)
            self.gw_voltage_or_current_toggleSwitch.setChecked(False)

            # Disable all non-relevant options
            self.gw_voltage_scan_toggleSwitch.setEnabled(False)
            self.gw_voltage_or_current_toggleSwitch.setEnabled(False)
            self.gw_pulse_duration_spinBox.setEnabled(False)
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
            self.gw_voltage_scan_toggleSwitch.setEnabled(True)
            self.gw_voltage_or_current_toggleSwitch.setEnabled(True)
            self.gw_pulse_duration_spinBox.setEnabled(True)
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

    @QtCore.Slot()
    def pause_goniometer_measurement(self):
        """
        Function to ask to turn the PL lamp on before continuing
        """
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText("You can now turn on the UV-lamp")
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
            cf.log_message("UV lamp was turned on")
        elif button == QtWidgets.QMessageBox.Cancel:
            self.goniometer_measurement.pause = "return"
            cf.log_message("PL measurement aborted before UV lamp was turned on")
            self.gw_start_measurement_pushButton.setChecked(False)

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

        # Kill motor savely
        try:
            # Move motor back go home position
            self.motor.move_to(45)

            # Instead of defining a moving time, just read the motor position and
            # only start the measurement when the motor is at the right position
            motor_position = self.motor.read_position()

            while not math.isclose(motor_position, 45, abs_tol=0.01):
                motor_position = self.motor.read_position()
                self.update_animation.emit(motor_position)
                time.sleep(0.05)

            # Update animation once more since the position might be 0.9 at this
            # point (int comparison in the above while loop)
            self.update_animation.emit(motor_position)
            self.motor.clean_up()

        except Exception as e:
            cf.log_message("Motor could not be turned off savely")
            cf.log_message(e)

        # Kill connection to spectrometer savely
        try:
            self.spectrometer.close_connection()
        except Exception as e:
            cf.log_message("Spectrometer could not be turned off savely")
            cf.log_message(e)

        # Kill connection to Keithleys
        try:
            pyvisa.ResourceManager().close()
        except Exception as e:
            cf.log_message("Connection to Keithleys could not be closed savely")
            cf.log_message(e)

        # if can_exit:
        event.accept()  # let the window close
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

    # myappid = u"mycompan.myproduct.subproduct.version"  # arbitrary string
    # ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app_icon = QtGui.QIcon()
    app_icon.addFile("./icons/program_icon.png", QtCore.QSize(256, 256))
    app.setWindowIcon(app_icon)

    ui.show()
    sys.exit(app.exec_())
