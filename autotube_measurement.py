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

    def __init__(self, measurement_parameters):
        """
        Initialise class. Measurement parameters are handed over from the GUI
        """
        threading.Thread.__init__(self)

        keith_address = u"USB0::0x05E6::0x2450::04102170::INSTR"
        keithmulti_address = u"USB0::0x05E6::0x2100::8003430::INSTR"

        # Measurement parameters do not have to be initialised as class members
        # but can directly be passed to each function in the class (I think
        # that is sufficient for the moment). Preferred structure would be
        # probably a dictionary.

        # The testrunEL function is complete crap since it only initalises the
        # variables and then serves as a definition ground for other functions
        # --> Bad style

    # def testrunEL(self):

    # "INITIALIZING SETTINGS"
    # defaults = {}
    # settings = {}
    # parameters = []
    # self.oled_pixels = []
    # "SETTING DEFAULT PARAMETERS"
    # defaults[0] = 'test' # sample
    # defaults[1] = 'Y' # pixel 1
    # defaults[2] = 'Y' # pixel 2
    # defaults[3] = 'Y' # pixel 3
    # defaults[4] = 'Y' # pixel 4
    # defaults[5] = 'Y' # pixel 5
    # defaults[6] = 'Y' # pixel 6
    # defaults[7] = 'Y' # pixel 7
    # defaults[8] = 'Y' # pixel 8
    # defaults[9] = -2.0  # min_voltage
    # defaults[10] = 2.0 # change_voltage
    # defaults[11] = 5.0  # max_voltage
    # defaults[12] = 0.1 # min_step_voltage
    # defaults[13] = 1.0 # max_step_voltage
    # defaults[14] = 1.05  # compliance
    # defaults[15] = 'Y'  # check bad contact
    # defaults[16] = 1e-10 # bad contact threshold
    # defaults[17] = 'Y' # check photodiode saturation
    # defaults[18] = 10 # photodiode saturation voltage

    # "GETTING PARAMETERS FROM GUI, IF BLANK SETTING AS DEFAULT"
    # for x in range(0,19,1):
    # if not param_m[x]:
    # parameters.append(defaults[x])
    # else:
    # settings[x] = param_m[x]
    # parameters.append(settings[x])
    # else:
    # self.queue.put('Invalid input.')
    #
    # print parameters
    # for x in range(1,9,1):
    # if parameters[x] == 'Y':
    # self.oled_pixels.append(x)
    #
    # "SETTING PARAMTERS"
    # self.sample = parameters[0]
    # self.min_voltage = float(parameters[9])
    # self.change_voltage = float(parameters[10])
    # self.max_voltage = float(parameters[11])
    # self.min_step_voltage = float(parameters[12])
    # self.max_step_voltage = float(parameters[13])
    # self.compliance = float(parameters[14])
    # self.check_bad_contact = parameters[15]
    # self.bad_contact  = float(parameters[16])
    # self.check_pd_saturation = parameters[17]
    # self.pd_saturation = float(parameters[18])

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
                raise ValueError("The called pixel does not exist.")

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

    def init_devices(self, keith_address, keithmulti_address):
        """
        Initialise Hardware. This function must be improved later as well.
        For the time being it is probably alright.
        """
        # Keithley Finding Device
        rm = pyvisa.ResourceManager()
        # The actual addresses for the Keithleys can be accessed via rm.list_resources()
        visa_resources = rm.list_resources()

        # Check if Keithleys are present:
        if (keith_address not in visa_resources) and (
            keithmulti_address not in visa_resources
        ):
            raise LookupError(
                "Both SourceMeter and Multimeter seem to be absend or switched off."
            )
            # self.queue.put(
            # "\nBoth the SourceMeter and the MultiMeter seem to be absent or"
            # " switched off."
            # + "\nPlease connect both Keithleys to the computer and try again."
            # )
        elif keith_address not in visa_resources:
            raise LookupError("The SourceMeter seems to be absent or switched off.")
            # self.queue.put(
            # "\nThe Keithley SourceMeter seems to be absent or switched off."
            # + "\nPlease connect the SourceMeter to the computer and try again."
            # )
        elif keithmulti_address not in visa_resources:
            raise LookupError("The Multimeter seems to be absent or switched off.")
            # self.queue.put(
            # "\nThe Keithley MultiMeter seems to be absent or switched off."
            # + "\nPlease connect the MultiMeter to the computer and try again."
            # )
        keith = rm.open_resource(keith_address)
        keithmulti = rm.open_resource(keithmulti_address)

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

    def start_measurement(self, pixel, measurement_parameters, keith, keithmulti, uno):
        """
        Function that does the actual measurement. I am not sure yet, if I
        want to do the data saving part in this class as well, definitely not
        in this function. For the time being it might be better to just
        return a pandas dataframe as a result. Also I am not sure yet where I
        am going to save the header parameters but definitely this is not
        done in this function!
        """

        # Print header:
        # self.queue.put('\nCHECK YOUR MEASUREMENT PARAMETERS\n' +
        # '\n-> Measuring the following OLED pixels: ' + str(self.oled_pixels) +
        # '\n' +
        # '\n-> Start voltage: ' + str(self.min_voltage) + ' V' +
        # '\n-> Low voltage step size: ' + str(self.min_step_voltage) + ' V' +
        # '\n' +
        # '\n-> Switch voltage step size and delay time at: ' + str(self.change_voltage) + ' V' +
        # '\n' +
        # '\n-> High voltage step size: ' + str(self.max_step_voltage) + ' V' +
        # '\n-> Stop voltage: ' + str(self.max_voltage) + ' V' +
        # '\n' +
        # '\n-> Compliance Current: ' + str(self.compliance) + ' A' +
        # '\n' +
        # '\n-> Check for bad contact: ' + self.check_bad_contact +
        # '\n-> Threshold current for bad contact: ' + str(self.bad_contact) + ' A' +
        # '\n' +
        # '\n-> Check for photodiode saturation: ' + self.check_pd_saturation +
        # '\n-> Threshold voltage for phododiode saturation: ' + str(self.pd_saturation) + ' V' +
        # '\n\n')

        # "SETTING DIRECTORY DETAILS"
        # now = dt.datetime.now()
        # datetime = str(now.strftime("%Y-%m-%d %H:%M").replace(" ","").replace(":","").replace("-",""))
        # directory = {}
        # keithleyfilepath = {}
        # for pixel in self.oled_pixels:
        # directory[pixel] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', datetime, )) # Folder to separate raw and processed data
        # if os.path.isdir(directory[pixel]):
        # pass
        # else:
        # os.makedirs(directory[pixel])
        # keithleyfilepath[pixel] = os.path.join(directory[pixel], str(self.sample))
        # if os.path.isdir(keithleyfilepath[pixel]):
        # pass
        # else:
        # os.makedirs(keithleyfilepath[pixel])

        # "SETTING FILE AND DIRECTORY PARAMETERS"
        # Filename Parameters
        # now = dt.datetime.now()
        # datetime = str(now.strftime("%Y-%m-%d %H:%M").replace(" ","").replace(":","").replace("-",""))
        # directory = os.path.join(os.path.dirname(__file__), 'data', self.sample, datetime)  # setting data folder
        # keithleydata = str(self.sample)  # for filenames have foldername and filename
        # keithleydata = os.path.abspath(os.path.join(directory, keithleydata))  # amended with full path

        # Header Parameters
        # line01 = 'Measurement code : ' + self.sample + datetime
        # line02 = 'Measurement programme :	 autotube_LIV.py'
        # linex = 'Credits :	EA, CM, SH, University of St Andrews, 2018'
        # line03 = 'Max voltage:   ' + str(self.max_voltage) + ' V    ' + 'Change voltage:   ' + str(self.change_voltage) + ' V    ' +'Min voltage:   ' + str(self.min_voltage) + ' V'
        # line04 = 'Step voltage at low voltages:   ' + str(self.min_step_voltage)+ 'V'
        # line05 = 'Step voltage at high voltages:   ' + str(self.max_step_voltage)+ 'V'
        # line06 = 'Current Compliance:   ' + str(self.compliance) + ' A'
        # line07 = '### Measurement data ###'
        # line08 = 'OLEDVoltage	OLEDCurrent Photodiode Voltage'
        # line09 = 'V	              mA               V'
        #
        # header_lines = [line01, line02, linex, line03, line04, line05, line06, line07, line08, line09]

        "#####################################################################"
        "#####TAKING MEASUREMENTS FROM THE THORLABS PDA100A2 PHOTODIODE#####"
        "#####################################################################"

        "SETTING SOURCEMETER"
        # Write operational parameters to Sourcemeter (Voltage to OLED)
        keith.write("*rst")  # reset instrument
        keith.write("Source:Function Volt")  # set voltage as source
        keith.write('Sense:Function "Current"')  # choose current for measuring
        keith.write(
            "Source:Volt:ILimit " + str(measurement_parameters.compliance)
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
            measurement_parameters.min_voltage,
            measurement_parameters.change_voltage,
            measurement_parameters.max_step_voltage,
        )  # Voltage points for low OLED voltage
        high_vlt = np.arange(
            measurement_parameters.change_voltage,
            measurement_parameters.max_voltage + 0.1,
            measurement_parameters.min_step_voltage,
        )  # Voltage points for high OLED voltage

        voltages_to_scan = np.append(low_vlt, high_vlt)

        # data = dict()
        "SCANNING VOLTAGES"
        # Optional scanning voltage readings, runs readings if Y, anything else and this section is skipped
        # for pixel in measurement_parameters.oled_pixels:
        # Create new arrays for each pixel measurement
        # OLEDvlt = []
        # OLEDcrt = []
        # PDvlt = []

        # Since the data shall be plotted after each measurement (it could also be done while measuring but I think there is not much benefit and the programming is uglier), only one pixel is scanned at a time
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
        #     + str(measurement_parameters.sample)
        #     + "D"
        #     + str(pixel)
        #     + ".txt"
        # )

        # Open activate on the selected pixel
        self.uno_open_relay(com=uno, relay=pixel, state=1, mute=False)

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
            if abs(oledcurrent) >= measurement_parameters.compliance:
                keith.write("Output OFF")  # Turn power off
                # self.queue.put(" | compliance reached -> aborting")
                break
            # check for a bad contact
            elif measurement_parameters.check_bad_contact == "Y" and (voltage != 0):
                if abs(oledcurrent) <= measurement_parameters.bad_contact:
                    keith.write("Output OFF")  # Turn power off
                    # self.queue.put(" | probably bad contact -> aborting")
                    break
            elif (
                measurement_parameters.check_pd_saturation == "Y"
            ):  # check for PD saturation
                if diode_voltage >= measurement_parameters.pd_saturation:
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

        # I am not sure what is going on here. Currently I think we don't
        # need it (or at least could do it smarter) but maybe I don't
        # understand it good it enough.

        # # High Voltage Readings
        # for voltage in high_vlt:
        #     self.queue.put("\nOLED Voltage : " + str(voltage) + " V")
        #     # Set voltage to source_value
        #     keith.write("Source:Volt " + str(voltage))
        #     time.sleep(0.05)
        #     # Take PD voltage reading from Multimeter
        #     testvoltage = float(keithmulti.query("MEASure:VOLTage:DC?"))
        #     # Take OLED current reading from Sourcemeter
        #     testcurrent = float(keith.query('Read? "OLEDbuffer"')[:-1])
        #     # Take PD voltage reading from Multimeter
        #     testvoltage = float(keithmulti.query("MEASure:VOLTage:DC?"))
        #     # Take OLED current reading from Sourcemeter
        #     testcurrent = float(keith.query('Read? "OLEDbuffer"')[:-1])
        #     self.queue.put("Test OLED Current : " + str(testcurrent * 1e3) + " mA")
        #     self.queue.put(
        #         "Test Photodiode Voltage :"
        #         + str(testvoltage - background_diodevoltage)
        #         + " V"
        #     )
        #     time.sleep(0.05)
        #     # Take PD voltage reading from Multimeter
        #     testvoltage = float(keithmulti.query("MEASure:VOLTage:DC?"))
        #     # Take OLED current reading from Sourcemeter
        #     testcurrent = float(keith.query('Read? "OLEDbuffer"')[:-1])
        #     # Take PD voltage reading from Multimeter
        #     testvoltage = float(keithmulti.query("MEASure:VOLTage:DC?"))
        #     # Take OLED current reading from Sourcemeter
        #     testcurrent = float(keith.query('Read? "OLEDbuffer"')[:-1])
        #     self.queue.put("Test OLED Current : " + str(testcurrent * 1e3) + " mA")
        #     self.queue.put(
        #         "Test Photodiode Voltage :"
        #         + str(testvoltage - background_diodevoltage)
        #         + " V"
        #     )
        #     time.sleep(0.05)
        #     # Take PD voltage reading from Multimeter
        #     diode_voltage = float(keithmulti.query("MEASure:VOLTage:DC?"))
        #     # Take OLED current reading from Sourcemeter
        #     oledcurrent = float(keith.query('Read? "OLEDbuffer"')[:-1])
        #     # Take PD voltage reading from Multimeter
        #     diode_voltage = float(keithmulti.query("MEASure:VOLTage:DC?"))
        #     # Take OLED current reading from Sourcemeter
        #     oledcurrent = float(keith.query('Read? "OLEDbuffer"')[:-1])

        #     "CHECK CURRENT AND VOLTAGES"
        #     # check if compliance is reached
        #     if abs(oledcurrent) >= measurement_parameters.compliance:
        #         keith.write("Output OFF")  # Turn power off
        #         self.queue.put(" | compliance reached -> aborting")
        #         break
        #     # check for a bad contact
        #     elif measurement_parameters.check_bad_contact == "Y" and (voltage != 0):
        #         if abs(oledcurrent) <= measurement_parameters.bad_contact:
        #             keith.write("Output OFF")  # Turn power off
        #             self.queue.put(" | probably bad contact -> aborting")
        #             break
        #     elif (
        #         measurement_parameters.check_pd_saturation == "Y"
        #     ):  # check for PD saturation
        #         if diode_voltage >= measurement_parameters.pd_saturation:
        #             self.queue.put(
        #                 "Photodiode reaches saturation. You might want to adjust"
        #                 " the gain."
        #             )
        #             break

        #     self.queue.put("OLED Current : " + str(oledcurrent * 1e3) + " mA")
        #     self.queue.put(
        #         "Photodiode Voltage :"
        #         + str(diode_voltage - background_diodevoltage)
        #         + " V"
        #     )
        #     PDvlt.append(diode_voltage - background_diodevoltage)
        #     OLEDcrt.append(oledcurrent)
        #     OLEDvlt.append(voltage)

        # Turn keithley off
        keith.write("Output OFF")

        # Turn off all relays again
        self.uno_open_relay(com=uno, relay=pixel, state=0)

        # Instead of doing the terrible saving, for now we just add the
        # dataframe to a dictionary that can then later be saved properly
        # in another function or even class
        # data[str(pixel)] = df_data

        # OLEDvolt = np.array(OLEDvlt)  # Creates voltage array
        # Creates current array; NOTE: current in mA !!!
        # OLEDcurrent = np.array(OLEDcrt) * 1e3
        # PDvoltage = np.array(PDvlt)
        # photodiodedata = np.stack((OLEDvolt, OLEDcurrent, PDvoltage))
        # for filenames have foldername and filename
        # keithleyfilename = (
        # str(measurement_parameters.sample) + "D" + str(pixel) + ".txt"
        # )
        # keithleyfilename = os.path.abspath(
        # os.path.join(keithleyfilepath[pixel], keithleyfilename)
        # )  # amended with full path
        # np.savetxt(keithleyfilename, photodiodedata.T, fmt='%.4f %.4e %.6f', header='\n'.join(header_lines), delimiter='\t', comments='')
        # self.queue.put(
        # "Remember to check your PHOTODIODE GAIN and take forward spectrum for EQE"
        # " calculation\n"
        # )
        uno.close()  # close COM port

        # self.queue.put("\n\nMEASUREMENT COMPLETE")

        return df_data
