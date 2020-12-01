# -*- coding: utf-8 -*-

import pyvisa  # Keithley Module
import serial  # Arduino Module

# The following modules are probably not necessary but maintained for the time
# being because they were used in the old code
import threading

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


class AutotubeMeasurement(threading.Thread):
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
    ):
        """
        Initialise class. Measurement parameters are handed over from the GUI
        """
        threading.Thread.__init__(self)

        # Initialise arduino and Keithley source and multimeter with the input addresses
        self.uno = ArduinoUno(com2_address)
        self.keithley_source = KeithleySource(
            keithley_source_address, measurement_parameters.compliance
        )
        self.keithley_multimeter = KeithleyMultimeter(keithley_multimeter_address)

        # Now set the input parameters as parameters of the datastructure
        self.measurement_parameters = measurement_parameters
        # self.PDcutoff = self.set_photodiode_gain(photodiode_gain)
        self.pixel = pixel

        # Since the data shall be plotted after each measurement (it could also
        # be done while measuring but I think there is not much benefit and the
        # programming is uglier), only one pixel is scanned at a time
        self.df_data = pd.DataFrame(columns=["voltage", "current", "pd_voltage"])

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
        return

    def get_data(self):
        """
        Function to return the data that is stored in the class' file structure.
        """
        return self.df_data