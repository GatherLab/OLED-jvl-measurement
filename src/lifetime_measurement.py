# -*- coding: utf-8 -*-

import pyvisa  # Keithley Module
import serial  # Arduino Module

from PySide2 import QtCore

from hardware import ArduinoUno, KeithleySource, KeithleyMultimeter
from tests.tests import MockArduinoUno, MockKeithleySource, MockKeithleyMultimeter

# My suspicion about the queue module is that it is only there for logging. If
# that is really the case I would rather not use it to simplify things
# import queue
import time
import datetime as dt
import sys
import core_functions as cf

import os

import pandas as pd
import numpy as np
import math


class LifetimeMeasurement(QtCore.QThread):
    """
    Class that contains all the relevant functions for a lifetime measurement
    """

    update_plot = QtCore.Signal(list, list)
    update_progress_bar = QtCore.Signal(str, float)
    # show_progress_bar = QtCore.Signal()
    hide_progress_bar = QtCore.Signal()
    reset_start_button = QtCore.Signal(bool)

    def __init__(
        self,
        keithley_source,
        keithley_multimeter,
        arduino,
        measurement_parameters,
        setup_parameters,
        selected_pixels,
        parent=None,
    ):
        """
        Initialise class. Measurement parameters are handed over from the GUI
        """
        super(LifetimeMeasurement, self).__init__()

        # Assign hardware and reset
        self.uno = arduino
        self.uno.init_serial_connection()
        self.keithley_source = keithley_source
        self.keithley_source.as_voltage_source(measurement_parameters["max_current"])
        self.keithley_multimeter = keithley_multimeter
        self.keithley_multimeter.reset()

        # Now set the input parameters as parameters of the datastructure
        self.measurement_parameters = measurement_parameters
        self.setup_parameters = setup_parameters
        # self.PDcutoff = self.set_photodiode_gain(photodiode_gain)
        self.selected_pixels = selected_pixels

        # Since the data shall be plotted after each measurement (it could also
        # be done while measuring but I think there is not much benefit and the
        # programming is uglier), only one pixel is scanned at a time
        self.df_data = pd.DataFrame(
            columns=["time", "pd_voltage", "oled_current", "oled_voltage"]
        )

        # Connect the signals
        self.update_plot.connect(parent.plot_lifetime_measurement)
        self.update_progress_bar.connect(parent.progressBar.setProperty)
        self.hide_progress_bar.connect(parent.progressBar.hide)
        # self.show_progress_bar.connect(parent.progressBar.show)
        self.reset_start_button.connect(
            parent.ltw_start_measurement_pushButton.setChecked
        )

        # Variable that stops the measurement
        self.stop = False

        self.parent = parent

    def run(self):
        """
        Function that does the actual measurement.
        """

        import pydevd

        pydevd.settrace(suspend=False)

        # To update progres bar
        progress = 0

        self.parent.unselect_all_pixels()

        self.update_progress_bar.emit("value", 0)

        # Set voltage
        self.keithley_source.set_voltage(self.measurement_parameters["voltage"])

        # Iterate over all selected pixels
        for pixel in self.selected_pixels:
            # self.keithley_source.empty_buffer("OLEDbuffer")

            cf.log_message("Running on Pixel " + str(pixel))

            # Take PD voltage reading from Multimeter for background
            background_diodevoltage = self.keithley_multimeter.measure_voltage()

            # Activate the relay of the selected pixel
            self.uno.trigger_relay(pixel)

            # Turn on the voltage
            self.keithley_source.activate_output()

            # Define starting time and elapsed time
            starting_time = time.time()

            i = 0
            while (
                time.time() - starting_time < self.measurement_parameters["on_time"] + 1
            ):
                beginning_time = time.time()

                # Take PD voltage reading from Multimeter
                # if self.measurement_parameters["fixed_multimeter_range"]:
                # diode_voltage = self.keithley_multimeter.measure_voltage(1)
                # else:
                # Take OLED current reading from Sourcemeter
                diode_voltage = self.keithley_multimeter.measure_voltage()
                oled_current = self.keithley_source.read_current()
                oled_voltage = self.keithley_source.read_voltage()

                # Check if PD saturation is reached
                if (
                    diode_voltage
                    >= self.measurement_parameters["photodiode_saturation"]
                ):
                    cf.log_message(
                        "Photodiode reached saturation. You might want to adjust the photodiode gain."
                    )

                    # Wait a second so that the user can read the message
                    time.sleep(1)
                    break

                if i == 0:
                    starting_time = time.time()

                # Current should be in mA
                self.df_data.loc[i, "time"] = time.time() - starting_time
                self.df_data.loc[i, "pd_voltage"] = (
                    diode_voltage - background_diodevoltage
                )

                self.df_data.loc[i, "oled_current"] = oled_current
                self.df_data.loc[i, "oled_voltage"] = oled_voltage
                self.update_plot.emit(
                    self.df_data.time.to_numpy(dtype=float),
                    self.df_data.pd_voltage.to_numpy(dtype=float),
                )

                # increment counter
                i += 1

                # Breaks out of the time loop
                if self.stop == True:
                    break

                # Sleep for the time of measurement interval
                if (
                    self.measurement_parameters["measurement_interval"]
                    - (time.time() - beginning_time)
                    > 0
                ):
                    time.sleep(
                        self.measurement_parameters["measurement_interval"]
                        - (time.time() - beginning_time)
                    )

            # If a bad contact was detected, jump this iteration (no saving etc.)
            # if bad_contact == True:
            #     continue

            # Turn keithley off
            self.keithley_source.deactivate_output()

            # Turn off all relays
            self.uno.trigger_relay(pixel)

            # Save data
            self.save_data(pixel)

            # Breaks the pixel loop so that only the output is deactivated etc.
            if self.stop == True:
                break

            # Update progress bar
            progress += 1

            self.update_progress_bar.emit(
                "value", int(progress / len(self.selected_pixels) * 100)
            )

            # Update GUI while being in a loop. It would be better to use
            # separate threads but for now this is the easiest way
            # app.processEvents()

            # Wait a few seconds so that the user can have a look at the graph
            time.sleep(1)

        # Breaks the pixel loop so that only the output is deactivated etc.
        if self.stop == True:
            cf.log_message("Lifetime measurement interrupted by user")
            self.hide_progress_bar.emit()
            return

        # Untoggle the pushbutton
        self.reset_start_button.emit(False)

        # Set keithley source back to initial value set in setup window
        # self.keithley_source.set_voltage(self.setup_parameters["test_voltage"])

        # Update statusbar
        cf.log_message("Lifetime measurement finished")

        # Hise progress bar
        self.hide_progress_bar.emit()

        # close COM port
        # self.uno.close_serial_connection()

    def save_data(self, pixel):
        """
        Function to save the measured data to file. This should probably be
        integrated into the LifetimeMeasurement class
        """
        # Define Header
        line01 = (
            "Voltage: "
            + str(self.measurement_parameters["voltage"])
            + " V\t"
            + "On Time: "
            + str(self.measurement_parameters["on_time"])
            + " s\t"
            + "Measurement Interval: "
            + str(self.measurement_parameters["measurement_interval"])
            + " s"
        )
        line02 = "### Measurement data ###"
        line03 = "Time\t Photodiode Voltage\t OLED Voltage\t OLED Current"
        line04 = "s\t V\t V\t A\n"

        header_lines = [
            line01,
            line02,
            line03,
            line04,
        ]

        # Write header lines to file
        file_path = (
            self.setup_parameters["folder_path"]
            + dt.date.today().strftime("%Y-%m-%d_")
            + self.setup_parameters["batch_name"]
            + "_d"
            + str(self.setup_parameters["device_number"])
            + "_p"
            + str(pixel)
            + "_lt"
            + ".csv"
        )

        # Format the dataframe for saving (no. of digits)
        self.df_data["time"] = self.df_data["time"].map(lambda x: "{0:.2f}".format(x))
        self.df_data["pd_voltage"] = self.df_data["pd_voltage"].map(
            lambda x: "{0:.7f}".format(x)
        )
        self.df_data["oled_voltage"] = self.df_data["pd_voltage"].map(
            lambda x: "{0:.4f}".format(x)
        )
        self.df_data["oled_current"] = self.df_data["pd_voltage"].map(
            lambda x: "{0:.4f}".format(x)
        )

        # Save file
        cf.save_file(self.df_data, file_path, header_lines)

        # with open(file_path, "a") as the_file:
        #     the_file.write("\n".join(header_lines))

        # # Now write pandas dataframe to file
        # self.df_data.to_csv(file_path, index=False, mode="a", header=False, sep="\t")

    # def get_data(self):
    #     """
    #     Function to return the data that is stored in the class' file structure.
    #     """
    #     return self.df_data
