# -*- coding: utf-8 -*-

import pyvisa  # Keithley Module
import serial  # Arduino Module

# The following modules are probably not necessary but maintained for the time
# being because they were used in the old code
import threading

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
        measurement_parameters,
        pixel,
    ):
        """
        Initialise class. Measurement parameters are handed over from the GUI
        """
        threading.Thread.__init__(self)

        # Now set the input parameters as parameters of the datastructure
        self.keithley_source_address = keithley_source_address
        self.keithley_multimeter_address = keithley_multimeter_address
        self.measurement_parameters = measurement_parameters
        self.pixel = pixel

    def uno_init(self, com, wait=2, open=False):
        """
        Initialise serial connection to com.

        com: func
            specify COM port. Needs to be opened prior to calling this function.
            e.g.:
                > uno = serial.Serial(2, timeout=0.2)
                > uno_init(com=uno)
        wait: flt
            time in seconds to wait before collecting initialisation message.
        """
        if open is True:
            com.open()
        time.sleep(wait)
        com.readall()
        # self.queue.put(com.readall())

    def uno_open_relay(self, com, relay, state=0, close=False, mute=False):
        """
        Open or close a relay via COM3 on an Arduino with a 4-Relays shield.

        com: func
            specify COM port. Needs to be opened prior to calling this function.
            e.g.:
                > uno = serial.Serial(2, timeout=0.2)
                > uno_open_relay(com=uno, relay=1, state=1, close=False)
        relay: int [1, 2, 3, 4, 5]
            If relay == [1-4], the according relay opens.
            If relay  == 5, all relays open.
        state: int [0, 1]
            If state == 0, all relays close.
            If state == 1, the accompanying relay opens.
        """

        # This can be done in a nicer way but let's leave it for the time being
        # not to mess around with everything too much
        if state == 0:
            com.write("0")
        else:
            if int(relay) >= 1 and int(relay) <= 9:
                com.write(str(relay))
            else:
                raise ValueError("The called self.pixel does not exist.")

        if mute is False:
            com.readall()
            # self.queue.put(com.readall())  # reads all there is
        if close is True:
            com.close()  # close COM port -> better done outside of definition env

    def set_gain(self, gain):
        """
        Set photodiode cutoff voltage according to gain of photodiode.

        gain: int (0, 10, 20, 30, 40, 50, 60, 70)
            Gain of photodiode which was used to measure the luminance.

        returns:
            PDcutoff: float
                cutoff voltage of photodiode below which only noise is expected.
        """

        # Also this can be done more efficiently but again lets leave it like
        # that, make it work for now and then come back at a later point
        if gain == 0:
            PDcutoff = 1e-6  # V
        elif gain == 10:
            PDcutoff = 3e-6  # V
        elif gain == 20:
            PDcutoff = 5e-6  # V
        elif gain == 30:
            PDcutoff = 1e-5  # V
        elif gain == 40:
            PDcutoff = 3e-5  # V
        elif gain == 50:
            PDcutoff = 1e-4  # V
        elif gain == 60:
            PDcutoff = 3e-4  # V
        elif gain == 70:
            PDcutoff = 2e-3  # V
        else:
            raise ValueError("Not a valid gain entered.")
            # self.queue.put(
            # "Error: Not a valid gain."
            # + "\nThe Thorlabs PDA100A-EC supports the following gains:"
            # + "\n0 dB, 10 dB, 20 dB, 30 dB, 40 dB, 50 dB, 60 dB, 70 dB"
            # + "\nCheck photodiode gain in your data header."
            # )
        return PDcutoff

    def init_devices(self, keithley_source_address, keithley_multimeter_address):
        """
        Initialise Hardware. This function must be improved later as well.
        For the time being it is probably alright.
        """
        # Keithley Finding Device
        rm = pyvisa.ResourceManager()
        # The actual addresses for the Keithleys can be accessed via rm.list_resources()
        visa_resources = rm.list_resources()

        # Check if Keithleys are present:
        if (keithley_source_address not in visa_resources) and (
            keithley_multimeter_address not in visa_resources
        ):
            raise LookupError(
                "Both SourceMeter and Multimeter seem to be absend or switched off."
            )
            # self.queue.put(
            # "\nBoth the SourceMeter and the MultiMeter seem to be absent or"
            # " switched off."
            # + "\nPlease connect both Keithleys to the computer and try again."
            # )
        elif keithley_source_address not in visa_resources:
            raise LookupError("The SourceMeter seems to be absent or switched off.")
            # self.queue.put(
            # "\nThe Keithley SourceMeter seems to be absent or switched off."
            # + "\nPlease connect the SourceMeter to the computer and try again."
            # )
        elif keithley_multimeter_address not in visa_resources:
            raise LookupError("The Multimeter seems to be absent or switched off.")
            # self.queue.put(
            # "\nThe Keithley MultiMeter seems to be absent or switched off."
            # + "\nPlease connect the MultiMeter to the computer and try again."
            # )
        keith = rm.open_resource(keithley_source_address)
        keithmulti = rm.open_resource(keithley_multimeter_address)

        # self.queue.put("\nKeithley Multimeter : ", keithmulti.query("*IDN?"))
        # self.queue.put("\nKeithley Sourcemeter : ", keith.query("*IDN?"))

        # Open COM port to Arduino (usually COM3):
        com3_address = u"ASRL3::INSTR"
        if com3_address not in visa_resources:
            raise LookupError(
                "The Arduino Uno seems to be missing. Try to reconnect to computer."
            )
            # self.queue.put(
            # "Arduino Uno seems to be missing."
            # + "\nPlease connect Arduino Uno to computer and try again."
            # )
            sys.exit()
        # assign name to Arduino with a timeout of 200 ms
        uno = serial.Serial(None, timeout=0.2)
        uno.port = "COM3"  # assign COM3
        try:  # try to open COM3 port
            self.uno_init(com=uno, wait=2, open=True)
        except serial.SerialException:
            try:  # try to catch exception
                uno.close()
                self.uno_init(com=uno, wait=2, open=True)
            except IOError:
                raise LookupError(
                    "COM3 port to Arduino Uno already open. Restart Python."
                )
                # self.queue.put(
                # "COM3 port to Arduino Uno already open."
                # + "\nTry 'uno.close()' in your console or restarting IPython."
                # )
                sys.exit()

        return keith, keithmulti, uno

    def measure(self, keith, keithmulti, uno):
        """
        Function that does the actual measurement. I am not sure yet, if I
        want to do the data saving part in this class as well, definitely not
        in this function. For the time being it might be better to just
        return a pandas dataframe as a result. Also I am not sure yet where I
        am going to save the header parameters but definitely this is not
        done in this function!
        """

        # Measure using Thorlabs PDA100A2 photodiode

        # Setup Source Meter
        # Write operational parameters to Sourcemeter (Voltage to OLED)
        keith.write("*rst")  # reset instrument
        keith.write("Source:Function Volt")  # set voltage as source
        keith.write('Sense:Function "Current"')  # choose current for measuring
        keith.write(
            "Source:Volt:ILimit " + str(self.measurement_parameters.compliance)
        )  # set compliance
        keith.write("Source:Volt:READ:BACK ON")  # reads back the set voltage
        # sets the read-out speed and accuracy (0.01 fastest, 10 slowest but highest accuracy)
        keith.write("Current:NPLCycles 1")
        keith.write("Current:AZero OFF")  # turn off autozero
        keith.write("Source:Volt:Delay:AUTO OFF")  # turn off autodelay

        "SETTING MULTIMETER"
        # Write operational parameters to Multimeter (Voltage from Photodiode)
        keithmulti.write("*rst")  # reset instrument
        keithmulti.write("SENSe:VOLTage:DC:RANGe 10")  # sets the voltage range
        # sets the voltage resolution
        keithmulti.query("VOLTage:DC:RESolution?")
        # sets the read-out speed and accuracy (0.01 fastest, 10 slowest but highest accuracy)
        keithmulti.write("VOLTage:NPLCycles 1")
        # sets the trigger to activate immediately after 'idle' -> 'wait-for-trigger'
        keithmulti.write("TRIGer:SOURce BUS")
        # sets the trigger to activate immediately after 'idle' -> 'wait-for-trigger'
        keithmulti.write("TRIGer:DELay 0")

        # self.queue.put("\n\nPHOTODIODE READINGS")

        "IMPLEMENTATION"
        # generate empty lists for later data collection
        low_vlt = np.arange(
            self.measurement_parameters.min_voltage,
            self.measurement_parameters.change_voltage,
            self.measurement_parameters.max_step_voltage,
        )  # Voltage points for low OLED voltage
        high_vlt = np.arange(
            self.measurement_parameters.change_voltage,
            self.measurement_parameters.max_voltage + 0.1,
            self.measurement_parameters.min_step_voltage,
        )  # Voltage points for high OLED voltage

        voltages_to_scan = np.append(low_vlt, high_vlt)

        # data = dict()
        "SCANNING VOLTAGES"
        # Optional scanning voltage readings, runs readings if Y, anything else and this section is skipped
        # for self.pixel in self.measurement_parameters.oled_self.pixels:
        # Create new arrays for each self.pixel measurement
        # OLEDvlt = []
        # OLEDcrt = []
        # PDvlt = []

        # Since the data shall be plotted after each measurement (it could also be done while measuring but I think there is not much benefit and the programming is uglier), only one self.pixel is scanned at a time
        df_data = pd.DataFrame(columns=["voltage", "current", "pd_voltage"])

        # Initiating 'wait_for_trigger' mode for Multimeter
        keithmulti.write("INITiate")

        # Buffer for Sourcemeter
        keith.write(
            'Trace:Make "OLEDbuffer", '
            + str(10 * max(len(low_vlt) + len(high_vlt), 10))
        )

        # Keithley empties the buffer
        keith.write('Trace:Clear "OLEDbuffer"')

        # Take PD voltage reading from Multimeter for background
        background_diodevoltage = float(keithmulti.query("MEASure:VOLTage:DC?"))
        # self.queue.put(
        #     "Background Photodiode Voltage :" + str(background_diodevoltage) + " V"
        # )
        # self.queue.put(
        #     "\nSaving output to: "
        #     + str(self.measurement_parameters.sample)
        #     + "D"
        #     + str(self.pixel)
        #     + ".txt"
        # )

        # Open activate on the selected self.pixel
        self.uno_open_relay(com=uno, relay=self.pixel, state=1, mute=False)

        # Activate output on Keithley
        keith.write("Output ON")

        # Low Voltage Readings
        i = 0
        for voltage in voltages_to_scan:
            # self.queue.put("\nOLED Voltage : " + str(voltage) + " V")
            # Set voltage to source_value
            keith.write("Source:Volt " + str(voltage))
            # Take PD voltage reading from Multimeter
            diode_voltage = float(keithmulti.query("MEASure:VOLTage:DC?"))
            # Take OLED current reading from Sourcemeter
            oledcurrent = float(keith.query('Read? "OLEDbuffer"')[:-1])

            "CHECK CURRENT AND VOLTAGES"
            # check if compliance is reached
            if abs(oledcurrent) >= self.measurement_parameters.compliance:
                keith.write("Output OFF")  # Turn power off
                # self.queue.put(" | compliance reached -> aborting")
                break
            # check for a bad contact
            elif self.measurement_parameters.check_bad_contact == "Y" and (
                voltage != 0
            ):
                if abs(oledcurrent) <= self.measurement_parameters.bad_contact:
                    keith.write("Output OFF")  # Turn power off
                    # self.queue.put(" | probably bad contact -> aborting")
                    break
            elif (
                self.measurement_parameters.check_pd_saturation == "Y"
            ):  # check for PD saturation
                if diode_voltage >= self.measurement_parameters.pd_saturation:
                    # self.queue.put(
                    # "Photodiode reaches saturation. You might want to adjust"
                    # " the gain."
                    # )
                    break

            # self.queue.put("OLED Current : " + str(oledcurrent * 1e3) + " mA")
            # self.queue.put(
            # "Photodiode Voltage :"
            # + str(diode_voltage - background_diodevoltage)
            # + " V"
            # )
            df_data.loc[i, "pd_voltage"] = diode_voltage - background_diodevoltage
            # Current should be in mA
            df_data.loc[i, "current"] = oledcurrent * 1e3
            df_data.loc[i, "voltage"] = voltage

        # Turn keithley off
        keith.write("Output OFF")

        # Turn off all relays again
        self.uno_open_relay(com=uno, relay=self.pixel, state=0)

        uno.close()  # close COM port

        # self.queue.put("\n\nMEASUREMENT COMPLETE")

        return df_data

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
        return