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

import os

import pandas as pd
import numpy as np


class AutotubeMeasurement(QtCore.QThread):
    """
    Class that contains all the relevant functions for the autotube EL measurement task
    """

    def __init__(
        self,
        keithley_source,
        keithley_multimeter,
        uno,
        measurement_parameters,
        setup_parameters,
        pixel,
        devices_already_initialised,
    ):
        """
        Initialise class. Measurement parameters are handed over from the GUI
        """
        super(AutotubeMeasurement, self).__init__()

        # Initialise arduino and Keithley source and multimeter with the input addresses
        if devices_already_initialised:
            self.uno = uno
            self.keithley_source = keithley_source
            self.keithley_multimeter = keithley_multimeter
        else:
            self.uno = MockArduinoUno(uno)
            self.keithley_source = MockKeithleySource(
                keithley_source, measurement_parameters["scan_compliance"]
            )
            self.keithley_multimeter = MockKeithleyMultimeter(keithley_multimeter)

        # Now set the input parameters as parameters of the datastructure
        self.measurement_parameters = measurement_parameters
        self.setup_parameters = setup_parameters
        # self.PDcutoff = self.set_photodiode_gain(photodiode_gain)
        self.pixel = pixel

        # Since the data shall be plotted after each measurement (it could also
        # be done while measuring but I think there is not much benefit and the
        # programming is uglier), only one pixel is scanned at a time
        self.df_data = pd.DataFrame(columns=["voltage", "current", "pd_voltage"])

    def run(self):
        """
        Function that does the actual measurement. I am not sure yet, if I
        want to do the data saving part in this class as well, definitely not
        in this function. For the time being it might be better to just
        return a pandas dataframe as a result. Also I am not sure yet where I
        am going to save the header parameters but definitely this is not
        done in this function!
        """

        # Define voltage steps
        # Voltage points for low OLED voltage
        low_vlt = np.arange(
            self.measurement_parameters["min_voltage"],
            self.measurement_parameters["changeover_voltage"],
            self.measurement_parameters["low_voltage_step"],
        )
        # Voltage points for high OLED voltage
        high_vlt = np.arange(
            self.measurement_parameters["changeover_voltage"],
            self.measurement_parameters["max_voltage"] + 0.1,
            self.measurement_parameters["high_voltage_step"],
        )

        voltages_to_scan = np.append(low_vlt, high_vlt)

        self.keithley_source.init_buffer(
            "OLEDbuffer", 10 * len(low_vlt) + len(high_vlt)
        )

        # Take PD voltage reading from Multimeter for background
        background_diodevoltage = self.keithley_multimeter.measure_voltage()

        # Activate the relay of the selected pixel
        self.uno.open_relay(relay=self.pixel, state=1)

        # Turn on the voltage
        self.keithley_source.activate_output()

        # Low Voltage Readings
        i = 0
        for voltage in voltages_to_scan:
            # self.queue.put("\nOLED Voltage : " + str(voltage) + " V")
            # Set voltage to source_value
            self.keithley_source.set_voltage(str(voltage))

            # Take PD voltage reading from Multimeter
            diode_voltage = self.keithley_multimeter.measure_voltage()
            # Take OLED current reading from Sourcemeter
            oled_current = self.keithley_source.read_current()

            # check if compliance is reached
            if abs(oled_current) >= self.measurement_parameters["scan_compliance"]:
                self.keithley_source.deactivate_output()
                raise Warning("Current compliance reached")
                break

            # check for a bad contact
            if self.measurement_parameters["check_bad_contacts"] == True and (
                voltage != 0
            ):
                if abs(oled_current) <= self.measurement_parameters["bad_contact"]:
                    self.keithley_source.deactivate_output()  # Turn power off
                    raise Warning(
                        "Pixel "
                        + self.pixel
                        + " probably has a bad contact. Measurement aborted."
                    )
                    break
            # check for PD saturation
            if self.measurement_parameters["check_pd_saturation"] == True:
                if diode_voltage >= self.measurement_parameters["pd_saturation"]:
                    raise Warning(
                        "Photodiode reaches saturation. You might want to adjust the"
                        " photodiode gain"
                    )
                    break

            self.df_data.loc[i, "pd_voltage"] = diode_voltage - background_diodevoltage
            # Current should be in mA
            self.df_data.loc[i, "current"] = oled_current * 1e3
            self.df_data.loc[i, "voltage"] = voltage

            i += 1

        # Turn keithley off
        self.keithley_source.deactivate_output()

        # Turn off all relays
        self.uno.open_relay(relay=self.pixel, state=0)

        self.uno.close_serial_connection()  # close COM port

    def save_data(self):
        """
        Function to save the measured data to file. This should probably be
        integrated into the AutotubeMeasurement class
        """
        # Define Header
        line03 = (
            "Min voltage:   "
            + str(self.measurement_parameters["min_voltage"])
            + " V   "
            + "Max voltage:   "
            + str(self.measurement_parameters["max_voltage"])
            + " V    "
            + "Change voltage:   "
            + str(self.measurement_parameters["changeover_voltage"])
            + " V"
        )
        line04 = (
            "Step voltage at low voltages:   "
            + str(self.measurement_parameters["low_voltage_step"])
            + " V"
        )
        line05 = (
            "Step voltage at high voltages:   "
            + str(self.measurement_parameters["high_voltage_step"])
            + " V"
        )
        line06 = (
            "Current Compliance:   "
            + str(self.measurement_parameters["scan_compliance"])
            + " A"
        )
        line07 = "### Measurement data ###"
        line08 = "OLEDVoltage\t OLEDCurrent\t Photodiode Voltage"
        line09 = "V\t mA\t V\n"

        header_lines = [
            line03,
            line04,
            line05,
            line06,
            line07,
            line08,
            line09,
        ]

        # Write header lines to file
        file_path = (
            self.setup_parameters["folder_path"]
            + dt.date.today().strftime("%Y-%m-%d_")
            + self.setup_parameters["batch_name"]
            + "_d"
            + str(self.setup_parameters["device_number"])
            + "_p"
            + str(self.pixel)
            + "_jvl"
            + ".csv"
        )
        with open(file_path, "a") as the_file:
            the_file.write("\n".join(header_lines))

        # Now write pandas dataframe to file
        self.df_data.to_csv(file_path, index=False, mode="a", header=False, sep="\t")

    # def get_data(self):
    #     """
    #     Function to return the data that is stored in the class' file structure.
    #     """
    #     return self.df_data