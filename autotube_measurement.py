# -*- coding: utf-8 -*-

import pyvisa  # Keithley Module
import serial  # Arduino Module

from PySide2 import QtCore

from hardware import ArduinoUno, KeithleySource, KeithleyMultimeter

# My suspicion about the queue module is that it is only there for logging. If
# that is really the case I would rather not use it to simplify things
import queue
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
        keithley_source_address,
        keithley_multimeter_address,
        com2_address,
        photodiode_gain,
        measurement_parameters,
        pixel,
        file_path,
    ):
        """
        Initialise class. Measurement parameters are handed over from the GUI
        """
        super(AutotubeMeasurement, self).__init__()

        # Initialise arduino and Keithley source and multimeter with the input addresses
        # self.uno = ArduinoUno(com2_address)
        # self.keithley_source = KeithleySource(
        #     keithley_source_address, measurement_parameters.compliance
        # )
        # self.keithley_multimeter = KeithleyMultimeter(keithley_multimeter_address)

        # Now set the input parameters as parameters of the datastructure
        self.measurement_parameters = measurement_parameters
        # self.PDcutoff = self.set_photodiode_gain(photodiode_gain)
        self.pixel = pixel

        # Since the data shall be plotted after each measurement (it could also
        # be done while measuring but I think there is not much benefit and the
        # programming is uglier), only one pixel is scanned at a time
        self.df_data = pd.DataFrame(columns=["voltage", "current", "pd_voltage"])

        self.file_path = file_path

    # For some reason this function is not used at all
    # def set_photodiode_gain(self, photodiode_gain):
    #     """
    #     Set photodiode cutoff voltage according to photodiode_gain of photodiode.

    #     photodiode_gain: int (0, 10, 20, 30, 40, 50, 60, 70)
    #         photodiode_gain of photodiode which was used to measure the luminance.

    #     returns:
    #         PDcutoff: float
    #             cutoff voltage of photodiode below which only noise is expected.
    #     """

    #     # Also this can be done more efficiently but aphotodiode_gain lets leave it like
    #     # that, make it work for now and then come back at a later point
    #     if photodiode_gain == 0:
    #         PDcutoff = 1e-6  # V
    #     elif photodiode_gain == 10:
    #         PDcutoff = 3e-6  # V
    #     elif photodiode_gain == 20:
    #         PDcutoff = 5e-6  # V
    #     elif photodiode_gain == 30:
    #         PDcutoff = 1e-5  # V
    #     elif photodiode_gain == 40:
    #         PDcutoff = 3e-5  # V
    #     elif photodiode_gain == 50:
    #         PDcutoff = 1e-4  # V
    #     elif photodiode_gain == 60:
    #         PDcutoff = 3e-4  # V
    #     elif photodiode_gain == 70:
    #         PDcutoff = 2e-3  # V
    #     else:
    #         raise ValueError("Not a valid photodiode_gain entered.")
    #         # self.queue.put(
    #         # "Error: Not a valid photodiode_gain."
    #         # + "\nThe Thorlabs PDA100A-EC supports the following photodiode_gains:"
    #         # + "\n0 dB, 10 dB, 20 dB, 30 dB, 40 dB, 50 dB, 60 dB, 70 dB"
    #         # + "\nCheck photodiode photodiode_gain in your data header."
    #         # )
    #     return PDcutoff

    def dummy_measure(self):
        self.df_data.voltage = np.array(
            [
                -2,
                -1,
                0,
                1,
                2,
                2.1,
                2.2,
                2.3,
                2.4,
                2.5,
                2.6,
                2.7,
                2.8,
                2.9,
                3,
                3.1,
                3.2,
                3.3,
                3.4,
                3.5,
                3.6,
                3.7,
                3.8,
                3.9,
                4,
                4.1,
                4.2,
                4.3,
                4.4,
                4.5,
                4.6,
                4.7,
                4.8,
                4.9,
                5,
                5.1,
                5.2,
                5.3,
                5.4,
                5.5,
                5.6,
                5.7,
                5.8,
                5.9,
                6,
                6.1,
                6.2,
                6.3,
                6.4,
                6.5,
                6.6,
                6.7,
                6.8,
                6.9,
                7,
                7.1,
                7.2,
                7.3,
                7.4,
                7.5,
                7.6,
                7.7,
                7.8,
                7.9,
                8,
                8.1,
                8.2,
                8.3,
                8.4,
                8.5,
                8.6,
                8.7,
                8.8,
                8.9,
                9,
                9.1,
                9.2,
                9.3,
                9.4,
                9.5,
                9.6,
                9.7,
                9.8,
                9.9,
                10,
            ]
        )
        self.df_data.current = np.array(
            [
                -0.0025634,
                -0.00073929,
                -3.8382e-07,
                0.00069859,
                0.0023444,
                0.0025943,
                0.0028066,
                0.0030633,
                0.0033521,
                0.0036661,
                0.0040481,
                0.0044954,
                0.0048432,
                0.0052769,
                0.0056609,
                0.006171,
                0.0067923,
                0.0074036,
                0.0081597,
                0.0088919,
                0.0097233,
                0.010581,
                0.011599,
                0.012985,
                0.014265,
                0.01579,
                0.017604,
                0.019672,
                0.021783,
                0.02421,
                0.027068,
                0.030444,
                0.033934,
                0.038022,
                0.042787,
                0.047902,
                0.054177,
                0.06081,
                0.068883,
                0.07755,
                0.087568,
                0.099012,
                0.11227,
                0.12676,
                0.14334,
                0.1621,
                0.18332,
                0.20722,
                0.23367,
                0.2634,
                0.29765,
                0.33625,
                0.3793,
                0.42735,
                0.48076,
                0.54053,
                0.60798,
                0.684,
                0.76757,
                0.86075,
                0.96499,
                1.0871,
                1.2192,
                1.3655,
                1.5329,
                1.7112,
                1.9114,
                2.1292,
                2.3756,
                2.6495,
                2.9514,
                3.289,
                3.6622,
                4.0761,
                4.536,
                5.0423,
                5.7103,
                6.329,
                7.0237,
                7.8016,
                8.6728,
                9.6452,
                11.215,
                12.414,
                13.782,
            ]
        )
        self.df_data.pd_voltage = np.array(
            [
                6e-06,
                -3.8e-05,
                -2e-06,
                -3.1e-05,
                -6.8e-05,
                -3e-05,
                -5.8e-05,
                -4.2e-05,
                -1.5e-05,
                -3e-06,
                -4.6e-05,
                8e-06,
                -6.2e-05,
                -3.8e-05,
                -0.000105,
                -4.1e-05,
                -8.7e-05,
                -1.7e-05,
                -8.7e-05,
                -0.0001,
                -6.9e-05,
                -7.9e-05,
                -5e-05,
                -2.8e-05,
                -8.9e-05,
                -7.8e-05,
                -1e-05,
                -9.4e-05,
                -7.8e-05,
                -7e-05,
                -4.9e-05,
                -5.9e-05,
                -8.9e-05,
                -9.4e-05,
                -0.000136,
                -7.9e-05,
                -6.2e-05,
                -7.7e-05,
                -9.1e-05,
                -6e-05,
                -6.4e-05,
                -3.6e-05,
                -8e-05,
                -1.7e-05,
                2.6e-05,
                -5.7e-05,
                -2.7e-05,
                0,
                3e-05,
                8.7e-05,
                9.3e-05,
                0.000174,
                0.000215,
                0.000241,
                -6e-05,
                2.5e-05,
                0.00017,
                0.000303,
                0.000437,
                0.000621,
                0.000813,
                0.001381,
                0.001734,
                0.002025,
                0.002408,
                0.002782,
                0.003241,
                0.003782,
                0.004342,
                0.004981,
                0.005663,
                0.006458,
                0.007436,
                0.008379,
                0.009543,
                0.010776,
                0.012442,
                0.013935,
                0.015675,
                0.017588,
                0.019682,
                0.022083,
                0.024367,
                0.028738,
                0.032014,
            ]
        )

    def measure(self):
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
            self.measurement_parameters.min_voltage,
            self.measurement_parameters.change_voltage,
            self.measurement_parameters.max_step_voltage,
        )
        # Voltage points for high OLED voltage
        high_vlt = np.arange(
            self.measurement_parameters.change_voltage,
            self.measurement_parameters.max_voltage + 0.1,
            self.measurement_parameters.min_step_voltage,
        )

        voltages_to_scan = np.append(low_vlt, high_vlt)

        self.keithley_source.init_buffer(low_vlt, high_vlt)

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
            if abs(oled_current) >= self.measurement_parameters.compliance:
                self.keithley_source.deactivate_output()
                raise Warning("Current compliance reached")
                break

            # check for a bad contact
            if self.measurement_parameters.check_bad_contact == True and (voltage != 0):
                if abs(oled_current) <= self.measurement_parameters.bad_contact:
                    self.keithley_source.deactivate_output()  # Turn power off
                    raise Warning(
                        "Pixel "
                        + self.pixel
                        + " probably has a bad contact. Measurement aborted."
                    )
                    break
            # check for PD saturation
            if self.measurement_parameters.check_pd_saturation == True:
                if diode_voltage >= self.measurement_parameters.pd_saturation:
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
            "Max voltage:   "
            + str(self.measurement_parameters["max_voltage"])
            + " V    "
            + "Change voltage:   "
            + str(self.measurement_parameters["changeover_voltage"])
            + " V    "
            + "Min voltage:   "
            + str(self.measurement_parameters["min_voltage"])
            + " V"
        )
        line04 = (
            "Step voltage at low voltages:   "
            + str(self.measurement_parameters["low_voltage_step"])
            + "V"
        )
        line05 = (
            "Step voltage at high voltages:   "
            + str(self.measurement_parameters["high_voltage_step"])
            + "V"
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
        with open(self.file_path, "a") as the_file:
            the_file.write("\n".join(header_lines))

        # Now write pandas dataframe to file
        self.df_data.to_csv(
            self.file_path, index=False, mode="a", header=False, sep="\t"
        )

        return

    def get_data(self):
        """
        Function to return the data that is stored in the class' file structure.
        """
        return self.df_data