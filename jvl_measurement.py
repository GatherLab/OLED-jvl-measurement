from UI_main_window import Ui_MainWindow
from UI_settings_window import Ui_Settings

from autotube_measurement import AutotubeMeasurement
from current_tester import CurrentTester
from spectrum_measurement import SpectrumMeasurement
from goniometer_measurement import GoniometerMeasurement

from tests.tests import MockThorlabMotor
from hardware import ThorlabMotor

from PySide2 import QtCore, QtGui, QtWidgets

import time
import os
import json
import functools
from datetime import date
import logging
from logging.handlers import RotatingFileHandler

import matplotlib.pylab as plt
import numpy as np
import pandas as pd

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

        # Update statusbar
        self.log_message("Initialising Program")
        self.tabWidget.currentChanged.connect(self.changed_tab_widget)

        # -------------------------------------------------------------------- #
        # ------------------------------ General ----------------------------- #
        # -------------------------------------------------------------------- #

        # Open the documentation in the browser (maybe in the future directly
        # open the readme file in the folder but currently this is so much
        # easier and prettier)
        self.actionDocumentation.triggered.connect(
            lambda: webbrowser.open(
                "https://github.com/GatherLab/OLED-jvl-measurement/blob/main/README.md"
            )
        )

        # Hide by default and only show if a process is running
        self.progressBar.hide()

        # -------------------------------------------------------------------- #
        # -------------------------- Current Tester -------------------------- #
        # -------------------------------------------------------------------- #

        # First init of current tester (should be activated when starting the
        # program)
        global_settings = self.read_global_settings()
        self.current_tester = CurrentTester(
            global_settings["arduino_com_address"],
            global_settings["keithley_source_address"],
            # global_settings["keithley_multimeter_address"],
            parent=self,
        )

        # Start thread
        self.current_tester.start()

        # Connect buttons
        self.sw_activate_local_mode_pushButton.clicked.connect(self.activate_local_mode)

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
            global_settings["arduino_com_address"],
            global_settings["keithley_source_address"],
            integration_time=300000,  # 300 ms
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
        self.gw_offset_angle_spinBox.setValue(0)
        self.gw_offset_angle_spinBox.setMaximum(180)
        self.gw_offset_angle_spinBox.setMinimum(-180)
        self.gw_minimum_angle_spinBox.setValue(0)
        self.gw_minimum_angle_spinBox.setMaximum(360)
        self.gw_minimum_angle_spinBox.setMinimum(-360)
        self.gw_maximum_angle_spinBox.setValue(180)
        self.gw_maximum_angle_spinBox.setMaximum(360)
        self.gw_maximum_angle_spinBox.setMinimum(-360)
        self.gw_step_angle_spinBox.setValue(1)
        self.gw_step_angle_spinBox.setMaximum(360)
        self.gw_integration_time_spinBox.setValue(300)
        self.gw_homing_time_spinBox.setValue(30)
        self.gw_moving_time_spinBox.setValue(1)
        self.gw_pulse_duration_spinBox.setValue(2)
        self.gw_vc_value_spinBox.setValue(5)
        self.gw_vc_compliance_spinBox.setValue(1.05)

        # Set standard parameters for Spectral Measurement
        self.specw_voltage_spinBox.setValue(0)
        self.specw_voltage_spinBox.setMinimum(-5.0)
        self.specw_voltage_spinBox.setMaximum(50.0)
        self.specw_voltage_spinBox.setSingleStep(0.1)

        # Set standard parameters for Spectral Measurement
        self.sw_ct_voltage_spinBox.setValue(0)
        self.sw_ct_voltage_spinBox.setMinimum(-5.0)
        self.sw_ct_voltage_spinBox.setMaximum(50.0)
        self.sw_ct_voltage_spinBox.setSingleStep(0.1)

        # Update statusbar
        self.log_message("Program ready")

    # -------------------------------------------------------------------- #
    # ------------------------- Global Functions ------------------------- #
    # -------------------------------------------------------------------- #
    @QtCore.Slot(str)
    def log_message(self, message):
        """
        Function that manages the logging, in the sense that everything is
        directly logged into statusbar and the log file at once instead of
        having to call multiple functions.
        """
        self.statusbar.showMessage(message, 10000000)
        logging.info(message)

    def changed_tab_widget(self):
        """
        Function that shall manage the threads that are running when we are
        on a certain tab. For instance the spectrum thread really only must
        run when the user is on the spectrum tab. Otherwise it can be paused.
        This might become important in the future. The best idea is probably
        to just kill all unused threads when we change the tab.
        """

        self.log_message(
            "Switched to tab widget no. " + str(self.tabWidget.currentIndex())
        )

        return

    def read_global_settings(self):
        """
        Read in global settings from file. The file can be changed using the
        settings window.
        """
        # Load from file to fill the lines
        with open("settings/global_settings.json") as json_file:
            data = json.load(json_file)
        try:
            settings = data["overwrite"]

            # Update statusbar
            self.log_message("Global Settings Read from File")
        except:
            settings = data["default"]

            # Update statusbar
            self.log_message("Default device parameters taken")

        return settings[0]

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

            self.log_message("Folder path or batchname not defined")
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

            self.log_message("Folder path not valid")
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
            "documentation": self.sw_documentation_textEdit.toPlainText(),
        }

        # Update statusbar
        self.log_message("Setup parameters read")

        return setup_parameters

    def activate_local_mode(self):
        """
        Function to reset the devices and toggle local mode to be able to
        activate pixel. I am not really sure if that is how to terminate a qthread correctly but it works.
        https://stackoverflow.com/questions/17045368/qthread-emits-finished-signal-but-isrunning-returns-true-and-isfinished-re
        """

        # Kill process and delete old current tester object
        self.current_tester.kill()
        del self.current_tester

        # Read in global settings and instanciate CurrentTester again
        global_settings = self.read_global_settings()
        self.current_tester = CurrentTester(
            global_settings["arduino_com_address"],
            global_settings["keithley_source_address"],
            # global_settings["keithley_multimeter_address"],
            parent=self,
        )

        # Start thread
        self.current_tester.start()

        # Update statusbar
        self.log_message("Current tester successfully reinstanciated")

    def toggle_pixel(self, pixel_number, tab):
        """
        Toggle pixel on or off by checking if the selected pixel was on
        already or not. This might require turning all pixels off first.
        """
        if tab == "sw":
            selected_pixels = self.read_setup_parameters()["selected_pixel"]
        elif tab == "specw":
            selected_pixels = self.read_spectrum_parameters()["selected_pixel"]

        if selected_pixels[pixel_number - 1]:
            # Turn pixel on
            self.current_tester.uno.open_relay(pixel_number, True)

            # Update statusbar
            self.log_message("Activated Pixel " + str(pixel_number))

            self.specw_pushbutton_array[pixel_number - 1].setChecked(True)
            self.sw_pushbutton_array[pixel_number - 1].setChecked(True)
        else:
            # Turn all pixels off first
            self.current_tester.uno.open_relay(pixel_number, False)

            # Get pixel numbers of those pixel that are True (activated)
            activated_pixels = [i + 1 for i, x in enumerate(selected_pixels) if x]

            for pixel in activated_pixels:
                self.current_tester.uno.open_relay(pixel, True)

            # Update statusbar
            self.log_message("Deactivated Pixel " + str(pixel_number))

            self.specw_pushbutton_array[pixel_number - 1].setChecked(False)
            self.sw_pushbutton_array[pixel_number - 1].setChecked(False)

            # print("Pixel " + str(pixel_number) + " turned off")

    @QtCore.Slot(float)
    def update_ammeter(self, current_reading):
        """
        Function that is continuously evoked when the current is updated by
        current_tester thread.
        """
        self.sw_current_lcdNumber.display(str(current_reading) + " A")

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
        self.log_message("Voltage Changed to " + str(round(voltage, 2)) + " V")

    def select_all_pixels(self):
        """
        Selects all pixels and applies the given voltage
        """

        # Toggle all buttons for the unselected pixels
        pixel = 1
        for push_button in self.sw_pushbutton_array:
            push_button.setChecked(True)
            self.toggle_pixel(pixel, "sw")
            pixel += 1

        # Update statusbar
        self.log_message("All pixels selected")

    def unselect_all_pixels(self):
        """
        Unselect all pixels
        """

        # Collectively turn off all pixels
        self.current_tester.uno.open_relay(1, False)

        # Uncheck all pixels
        for i in range(len(self.sw_pushbutton_array)):
            self.sw_pushbutton_array[i].setChecked(False)
            self.specw_pushbutton_array[i].setChecked(False)

        # Update statusbar
        self.log_message("All pixels unselected")

    def prebias_pixels(self):
        """
        Prebias all pixels (e.g. at -2 V)
        """

        # Update statusbar
        self.log_message("Prebiasing pixels started")

        # This should be in the global settings later on (probably not
        # necessary to change every time but sometimes)
        pre_bias_voltage = -2  # in V
        biasing_time = 0.5  # in s
        set_voltage = self.sw_ct_voltage_spinBox.value()

        # Unselect all pixels first (in case some have been selected before)
        self.unselect_all_pixels()

        # Set voltage to prebias voltage
        self.current_tester.keithley_source.set_voltage(pre_bias_voltage)
        self.sw_ct_voltage_spinBox.setValue(pre_bias_voltage)

        # Pre-bias all pixels automatically
        for pixel in range(len(self.sw_pushbutton_array)):
            # Close all relays
            self.current_tester.uno.open_relay(1, False)

            # Set push button to checked and open relay of the pixel
            self.sw_pushbutton_array[pixel].setChecked(True)
            self.specw_pushbutton_array[pixel].setChecked(True)
            self.current_tester.uno.open_relay(pixel + 1, True)

            # Turn on the voltage
            self.current_tester.keithley_source.activate_output()

            # Update GUI while being in a loop. It would be better to use
            # separate threads but for now this is the easiest way
            app.processEvents()

            # Bias for half a second
            time.sleep(biasing_time)

            # Deactivate the pixel again
            self.sw_pushbutton_array[pixel].setChecked(False)
            self.specw_pushbutton_array[pixel].setChecked(False)
            self.current_tester.uno.open_relay(pixel + 1, False)

            # Turn off the voltage
            self.current_tester.keithley_source.deactivate_output()

        # Set voltage to prebias voltage
        self.current_tester.keithley_source.activate_output()
        self.current_tester.keithley_source.set_voltage(set_voltage)
        self.sw_ct_voltage_spinBox.setValue(set_voltage)

        # Update statusbar
        self.log_message("Finished prebiasing")

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
        self.log_message("Auto testing pixels started")

        # Define voltage steps (in the future this could be settings in the
        # global settings as well)
        voltage_range = np.linspace(2, 7, 26)
        biasing_time = 0.05

        # Unselect all pixels first (in case some have been selected before)
        self.unselect_all_pixels()

        # Turn off the voltage (if that was not already done)
        self.current_tester.keithley_source.deactivate_output()

        # Go over all pixels
        working_pixels = []

        for pixel in range(len(self.sw_pushbutton_array)):
            # Close all relays
            self.current_tester.uno.open_relay(1, False)

            # Set push button to checked and open relay of the pixel
            self.sw_pushbutton_array[pixel].setChecked(True)
            self.specw_pushbutton_array[pixel].setChecked(True)
            self.current_tester.uno.open_relay(pixel + 1, True)

            for voltage in voltage_range:
                # Turn on the voltage at the value "voltage"
                self.current_tester.keithley_source.activate_output()
                self.current_tester.keithley_source.set_voltage(voltage)
                self.sw_ct_voltage_spinBox.setValue(voltage)

                # Update GUI while being in a loop. It would be better to use
                # separate threads but for now this is the easiest way
                app.processEvents()

                # Bias for a certain time
                time.sleep(biasing_time)

                # Now read the current
                current = self.current_tester.keithley_source.read_current()

                if current >= 0.02 and current <= 5:
                    working_pixels.append(pixel + 1)
                    break

            # Deactivate the pixel again
            self.sw_pushbutton_array[pixel].setChecked(False)
            self.specw_pushbutton_array[pixel].setChecked(False)
            self.current_tester.uno.open_relay(pixel + 1, False)

            # Turn off the voltage
            self.current_tester.keithley_source.set_voltage(0)
            self.current_tester.keithley_source.deactivate_output()
            self.sw_ct_voltage_spinBox.setValue(0)

        # Now activate all pixels that do work
        for pixel in working_pixels:
            self.sw_pushbutton_array[pixel - 1].setChecked(True)
            self.specw_pushbutton_array[pixel - 1].setChecked(True)
            self.toggle_pixel(pixel, "sw")
            pixel += 1

        # Set voltage to prebias voltage
        self.current_tester.keithley_source.activate_output()

        # Update statusbar
        self.log_message("Finished auto testing pixels")

    # -------------------------------------------------------------------- #
    # ---------------------- Autotube Measurement  ----------------------- #
    # -------------------------------------------------------------------- #

    def read_autotube_parameters(self):
        """
        Function to read out the current measurement parameters that are
        present when clicking the Start Measurement button
        """
        measurement_parameters = {
            "min_voltage": self.aw_min_voltage_spinBox.value(),
            "max_voltage": self.aw_max_voltage_spinBox.value(),
            "changeover_voltage": self.aw_changeover_voltage_spinBox.value(),
            "low_voltage_step": self.aw_low_voltage_step_spinBox.value(),
            "high_voltage_step": self.aw_high_voltage_step_spinBox.value(),
            "scan_compliance": self.aw_scan_compliance_spinBox.value(),
            "check_bad_contacts": self.aw_bad_contacts_toggleSwitch.isChecked(),
            "check_pd_saturation": self.aw_pd_saturation_toggleSwitch.isChecked(),
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
        self.log_message("Autotube paremeters read")

        return measurement_parameters, selected_pixels_numbers

    def plot_autotube_measurement(self, jvl_data):
        """
        Function to plot the results from the autotube measurement to the central graph.
        """
        # self.aw_fig.figure()

        # Clear axis
        self.aw_ax.cla()
        self.aw_ax2.cla()

        # Plot current
        self.aw_ax.plot(
            jvl_data.voltage.to_list(),
            jvl_data.current.to_list(),
            color=(68 / 255, 188 / 255, 65 / 255),
            marker="o",
        )
        # twin object for two different y-axis on the sample plot
        # make a plot with different y-axis using second axis object
        self.aw_ax2.plot(
            jvl_data.voltage.to_list(),
            jvl_data.pd_voltage.to_list(),
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
        self.log_message("Autotube measurement plotted")

    def start_autotube_measurement(self):
        """
        Function that executes the actual measurement (the logic of which is
        stored in autotube_measurement.py). Iteration over the selected
        pixels as well as a call for the plotting happens here.
        """

        # Save read setup parameters
        setup_parameters = self.safe_read_setup_parameters()

        # Update statusbar
        self.log_message("Autotube measurement started")

        measurement_parameters, selected_pixels = self.read_autotube_parameters()

        # Set progress bar to zero
        self.progressBar.show()
        self.progressBar.setProperty("value", 0)

        # Now read in the global settings from file
        global_settings = self.read_global_settings()

        # This shall create an instance of the AutotubeMeasurement class
        progress = 0
        for pixel in selected_pixels:
            file_path = (
                setup_parameters["folder_path"]
                + date.today().strftime("%Y-%m-%d_")
                + setup_parameters["batch_name"]
                + "_d"
                + str(setup_parameters["device_number"])
                + "_p"
                + str(pixel)
                + ".csv"
            )

            self.log_message("Running on Pixel " + str(pixel))

            # Instantiate our class
            measurement = AutotubeMeasurement(
                global_settings["keithley_source_address"],
                global_settings["keithley_multimeter_address"],
                global_settings["arduino_com_address"],
                measurement_parameters,
                pixel,
                file_path,
            )

            # Call measurement.run() to measure and save all the measured data into the class itself
            measurement.run()

            # Call measurement.save_data() to directly save the data to a file
            measurement.save_data()

            # Call measurement.get_data() that returns the actual data
            # so that we can feed it into plot_autotube_measurement
            self.plot_autotube_measurement(measurement.df_data)

            # Update progress bar
            progress += 1
            self.progressBar.setProperty(
                "value", int(progress / len(selected_pixels) * 100)
            )

            # Update GUI while being in a loop. It would be better to use
            # separate threads but for now this is the easiest way
            app.processEvents()

            # Wait a few seconds so that the user can have a look at the graph
            time.sleep(1)

        # Untoggle the pushbutton
        self.aw_start_measurement_pushButton.setChecked(False)

        # Update statusbar
        self.log_message("Autotube measurement finished")

        self.progressBar.hide()

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
        self.log_message("Spectrum parameters read")

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

            self.log_message("More or less than one pixel selected")
            raise UserWarning("Please select exactly one pixel!")

        # Store data in pd dataframe
        df_spectrum_data = pd.DataFrame(
            columns=["wavelength", "background", "intensity"]
        )

        # Get wavelength and intensity of spectrum under light conditions
        (
            df_spectrum_data["wavelength"],
            df_spectrum_data["intensity"],
        ) = self.spectrum_measurement.spectrometer.measure()

        # Turn off all pixels wait two seconds to ensure that there is no light left and measure again
        self.unselect_all_pixels()
        time.sleep(2)
        (
            wavelength,
            df_spectrum_data["background"],
        ) = self.spectrum_measurement.spectrometer.measure()

        # Save data

        file_path = (
            setup_parameters["folder_path"]
            + date.today().strftime("%Y-%m-%d_")
            + setup_parameters["batch_name"]
            + "_spectrum"
            + "_d"
            + str(setup_parameters["device_number"])
            + "_p"
            + str(selected_pixels[0])
            + ".csv"
        )

        # Define header line with voltage and integration time
        line01 = (
            "Voltage: "
            + str(self.specw_voltage_spinBox.value())
            + " V\t"
            + "Integration Time: "
            + str(self.spectrum_measurement.integration_time / 1000)
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

        # Write header lines to file
        with open(file_path, "a") as the_file:
            the_file.write("\n".join(header_lines))

        # Now write pandas dataframe to file
        df_spectrum_data.to_csv(
            file_path, index=False, mode="a", header=False, sep="\t"
        )

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
            "homing_time": self.gw_homing_time_spinBox.value(),
            "moving_time": self.gw_moving_time_spinBox.value(),
            "pulse_duration": self.gw_pulse_duration_spinBox.value(),
            "voltage_or_current": self.gw_voltage_or_current_toggleSwitch.isChecked(),
            "voltage_scan": self.gw_voltage_scan_toggleSwitch.isChecked(),
            "el_or_pl": self.gw_el_or_pl_toggleSwitch.isChecked(),
            "vc_value": self.gw_vc_value_spinBox.value(),
            "vc_compliance": self.gw_vc_compliance_spinBox.value(),
            "selected_pixels": [i + 1 for i, x in enumerate(pixels) if x],
        }

        # Update statusbar
        self.log_message("Goniometer parameters read")

        return goniometer_parameters

    def start_goniometer_measurement(self):
        """
        Function that starts the goniometer measurement. On the long run
        there should also be the option to interrupt the goniometer
        measurement when it is already running
        """

        # Read all relevant parameters
        setup_parameters = self.safe_read_setup_parameters()
        (
            autotube_measurement_parameters,
            selected_pixels,
        ) = self.read_autotube_parameters()
        goniometer_measurement_parameters = self.read_goniometer_parameters()
        global_settings = self.read_global_settings()

        # Check that only exactly one pixel is selected before measurement can
        # be started (this could be also done with the gui directly)
        if len(goniometer_measurement_parameters["selected_pixels"]) != 1:
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

            self.log_message("More or less than one pixel selected")
            raise UserWarning("Please select exactly one pixel")

            self.gw_start_measurement_pushButton.setChecked(False)
            return

        # Update statusbar
        self.log_message("Goniometer measurement started")

        # Set progress bar to zero
        self.progressBar.show()
        self.progressBar.setProperty("value", 0)

        # Instantiate our class it has to be a class variable otherwise it
        # would be destroyed as soon as this function terminates
        self.goniometer_measurement = GoniometerMeasurement(
            global_settings["keithley_source_address"],
            global_settings["keithley_multimeter_address"],
            global_settings["arduino_com_address"],
            global_settings["motor_number"],
            global_settings["motor_offset"],
            global_settings["spectrum_integration_time"],
            global_settings["photodiode_gain"],
            goniometer_measurement_parameters["selected_pixels"],
            setup_parameters["folder_path"],
            goniometer_measurement_parameters,
            autotube_measurement_parameters,
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
        self.log_message("Goniometer Measurement Plotted")

    def move_motor(self):
        """
        Function to do a bare movement of the motor without any measurement.
        """
        # Read the global settings to initialise the motor
        global_settings = self.read_global_settings()

        # Initialise motor (it might be better to do this less often)
        motor = MockThorlabMotor(
            global_settings["motor_number"], global_settings["motor_offset"]
        )

        # Read the angle from the spinBox
        angle = self.gw_offset_angle_spinBox.value()

        self.log_message("Motor is moving")

        # Move the motor and change the animation
        motor.move_to(angle)

        # I decided to read the motor position instead of doing a virtual animation. The animation shall always show the true motor position (if the hardware allows that). The
        motor_position = motor.read_position()
        self.gw_animation.move(motor_position)
        app.processEvents()
        time.sleep(0.05)

        while int(angle) != int(motor_position):
            motor_position = motor.read_position()
            self.gw_animation.move(motor_position)
            app.processEvents()
            print("Blub")
            time.sleep(0.05)

        self.log_message("Motor moved to " + str(angle) + " °")


# Logging
# Prepare file path etc. for logging
LOG_FILENAME = "./log.out"
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
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    # ui.setupUi(aMainWindow)
    ui.show()
    sys.exit(app.exec_())