import pyvisa  # Keithley Module
import serial  # Arduino Module
import seabreeze

seabreeze.use("pyseabreeze")
import seabreeze.spectrometers as sb  # MayaLSL Modules for Ocean Spectrometer


import thorlabs_apt as apt  # thorlabs apt for thorlabs motor

import sys
import time
import logging
import numpy as np

from PySide2 import QtCore, QtGui, QtWidgets


class KeithleyMultimeter:
    """
    Class that manages all functionality of our Keithley multi meter
    """

    def __init__(self, keithley_multimeter_address):
        # Define a mutex
        self.mutex = QtCore.QMutex(QtCore.QMutex.NonRecursive)

        # Keithley Finding Device
        rm = pyvisa.ResourceManager()
        # The actual addresses for the Keithleys can be accessed via rm.list_resources()
        visa_resources = rm.list_resources()

        if keithley_multimeter_address not in visa_resources:
            raise IOError("The Multimeter seems to be absent or switched off.")

        self.keithmulti = rm.open_resource(keithley_multimeter_address)

        # Write operational parameters to Multimeter (Voltage from Photodiode)
        # reset instrument
        self.reset()

    def reset(self):
        """
        Reset instrument
        """
        self.mutex.lock()
        self.keithmulti.write("*rst")

        # Write operational parameters to Multimeter (Voltage from Photodiode)
        # sets the voltage range
        self.keithmulti.write("SENSe:VOLTage:AC:RANGe 10")
        # sets the voltage resolution
        self.keithmulti.query("VOLTage:AC:RESolution?")
        # sets the read-out speed and accuracy (0.01 fastest, 10 slowest but highest accuracy)
        self.keithmulti.write("VOLTage:NPLCycles 1")
        # Activate wait for trigger mode
        self.keithmulti.write("INITiate")
        time.sleep(1)
        self.mutex.unlock()

    # def set_fixed_range(self, value):
    #     """
    #     Sets a fixed voltage range if the user selected so
    #     """
    #     # Turn off the auto range function of the multimeter
    #     self.keithmulti.write("SENSe:VOLTage:DC:RANGe:AUTO OFF")
    #     # Set the range of the multimeter to a fixed value
    #     self.keithmulti.write("CONF:VOLTage:DC:RANGe " + str(value))

    # def set_auto_range(self):
    #     """
    #     Sets automatic detection of the multimeter range
    #     """
    #     # Turn on the auto range function of the multimeter
    #     self.keithmulti.write("SENSe:VOLTage:DC:RANGe:AUTO ON")

    def measure_voltage(self, multimeter_range=0):
        """
        Returns an actual voltage reading on the keithley multimeter
        """
        if multimeter_range == 0:
            return float(self.keithmulti.query("MEASure:VOLTage:AC?"))
        else:
            return float(
                self.keithmulti.query("MEASure:VOLTage:AC? " + str(multimeter_range))
            )

    def trigger_mode(self):
        """
        Activate trigger mode to wait for a specific pulse
        """
        # Set the integration time to 1/3 ms
        self.keithmulti.write("SENSe:VOLTage:DC:NPLCycles 0.02")
        self.keithmulti.write("TRIGger:SOURce EXT")

        # Set number of samples before returning to idle state
        no_measurements_before_idle = 10
        self.keithmulti.write("TRIGger:COUNt " + str(no_measurements_before_idle))

        # Set delay time between trigger and measurement
        trigger_delay = 0
        self.keithmulti.write("TRIGger:DELay " + str(trigger_delay))

        self.keithmulti.write("INITiate")

        # time.sleep(no_measurements_before_idle * 1 / frequency)

        self.keithmulti.query("FETCH?")

        # self.keithmulti.query("READ?")

        # Set number of samples
        # no_samples = 1
        # self.keithmulti.write("SAMPle:COUNt " + str(no_samples))


multimeter = KeithleyMultimeter("USB0::0x05E6::0x2100::8011801::INSTR")

multimeter.trigger_mode()