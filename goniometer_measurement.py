# -*- coding: utf-8 -*-

from PySide2 import QtCore

from hardware import (
    ArduinoUno,
    KeithleySource,
    KeithleyMultimeter,
    OceanSpectrometer,
    ThorlabMotor,
)
from tests.tests import (
    MockArduinoUno,
    MockKeithleySource,
    MockKeithleyMultimeter,
    MockOceanSpectrometer,
)
from autotube_measurement import AutotubeMeasurement

import time
import numpy as np
import pandas as pd


class GoniometerMeasurement(QtCore.QThread):
    """
    Thread class to do the goniometer measurement
    """

    def __init__(
        self,
        keithley_source_address,
        keithley_multimeter_address,
        com2_address,
        integration_time,
        motor_number,
        goniometer_measurement_parameters,
        autotube_measurement_parameters,
        pixel,
        photodiode_gain,
        parent=None,
    ):
        super(GoniometerMeasurement, self).__init__()

        # Initialise hardware
        self.uno = MockArduinoUno(com2_address)
        self.keithley_source = MockKeithleySource(
            keithley_source_address, autotube_measurement_parameters["scan_compliance"]
        )
        self.keithley_multimeter = MockKeithleyMultimeter(keithley_multimeter_address)
        self.spectrometer = MockOceanSpectrometer(integration_time)
        self.motor = ThorlabMotor(motor_number)

        # Initialise member variables
        self.goniometer_measurement_parameters = goniometer_measurement_parameters
        self.autotube_measurement_parameters = autotube_measurement_parameters

        self.keithley_source_address = keithley_source_address
        self.keithley_multimeter_address = keithley_multimeter_address
        self.com2_address = com2_address
        self.photodiode_gain = photodiode_gain
        self.pixel = pixel

    def run(self):
        """
        Function that runs when the thread is started. It contains the
        measurement routine that is triggered when the measure button is
        pressed
        """
        # while True:

        # "INITIALIZING SETTINGS"
        # defaults = {}
        # settings = {}
        # parameters = []
        # "SETTING DEFAULT PARAMETERS"
        # defaults[0] = "test"  # sample
        # defaults[1] = 318  # offset_angle
        # defaults[2] = 1  # step_angle
        # defaults[3] = 300000  # integrationtime in microseconds
        # defaults[4] = 20.0  # homing_time
        # defaults[5] = 0.2  # moving_time
        # defaults[6] = 0.2  # pulse_duration in s
        # defaults[7] = "F"  # ang_range
        # defaults[8] = "N"  # scan_status
        # defaults[9] = -2.0  # min_voltage
        # defaults[10] = 2.0  # change_voltage
        # defaults[11] = 4.0  # max_voltage
        # defaults[12] = 0.1  # min_step_voltage
        # defaults[13] = 1.0  # max_step_voltage
        # defaults[14] = 0.10  # scan_compliance
        # defaults[15] = "Current"  # source
        # defaults[16] = 0.001  # goniometer_value in A for current
        # defaults[17] = 5  # goniometer_compliance in V for voltage

        # "GETTING PARAMETERS FROM GUI, IF BLANK SETTING AS DEFAULT"
        # for x in range(0, 18, 1):
        # if not param[x]:
        # parameters.append(defaults[x])
        # else:
        # settings[x] = param[x]
        # parameters.append(settings[x])
        # if parameters[7] == "F":
        # self.min_angle = float(parameters[1]) - 90
        # self.max_angle = float(parameters[1]) + 90
        # elif parameters[7] == "HL":
        # self.min_angle = float(parameters[1])
        # self.max_angle = float(parameters[1]) + 90
        # elif parameters[7] == "HR":
        # self.min_angle = float(parameters[1]) - 90
        # self.max_angle = float(parameters[1])
        # else:
        # self.queue.put("Invalid input.")
        #
        # "SETTING PARAMTERS"
        # self.sample = parameters[0]
        # self.offset_angle = float(parameters[1])
        # self.step_angle = float(parameters[2])
        # self.integrationtime = float(parameters[3])
        # self.homing_time = float(parameters[4])
        # self.moving_time = float(parameters[5])
        # self.pulse_duration = float(parameters[6])
        # self.ang_range = parameters[7]
        # self.scan_status = parameters[8]
        # self.min_voltage = float(parameters[9])
        # self.change_voltage = float(parameters[10])
        # self.max_voltage = float(parameters[11])
        # self.min_step_voltage = float(parameters[12])
        # self.max_step_voltage = float(parameters[13])
        # self.scan_compliance = float(parameters[14])
        # self.source = parameters[15]
        # self.goniometer_value = float(parameters[16])
        # self.goniometer_compliance = float(parameters[17])

        # "SETTING DIRECTORY DETAILS"
        # now = dt.datetime.now()
        # datetime = str(
        #     now.strftime("%Y-%m-%d %H:%M")
        #     .replace(" ", "")
        #     .replace(":", "")
        #     .replace("-", "")
        # )
        # self.queue.put(
        #     "Measurement code : "
        #     + self.sample
        #     + datetime
        #     + "  (OLED device code followed by the datetime of measurement)."
        # )
        # # Set directories for recorded data.
        # directory = os.path.abspath(
        #     os.path.join(
        #         os.path.dirname(__file__), "data", self.sample, datetime, "raw"
        #     )
        # )  # Folder to separate raw and processed data
        # if os.path.isdir(directory):
        #     pass
        # else:
        #     os.makedirs(directory)

        # "SETTING FILE DETAILS"
        # # Filename Parameters
        # keithleyfilepath = os.path.join(directory, "keithleydata")
        # mayafilepath = os.path.join(directory, "spectrumdata")
        # if os.path.isdir(keithleyfilepath):
        #     pass
        # else:
        #     os.makedirs(keithleyfilepath)
        # if os.path.isdir(mayafilepath):
        #     pass
        # else:
        #     os.makedirs(mayafilepath)

        # keithleyfilename = (  # for filenames have foldername and filename
        #     "keithleyPDvoltages.txt"
        # )
        # keithleyfilename = os.path.abspath(
        #     os.path.join(keithleyfilepath, keithleyfilename)
        # )  # amended with full path

        # "INITIALIZING HARDWARE"
        # # Keithley Finding Device
        # rm = visa.ResourceManager()
        # keith = rm.open_resource(u"USB0::0x05E6::0x2450::04102170::INSTR")
        # keithmulti = rm.open_resource(u"USB0::0x05E6::0x2100::8003430::INSTR")
        # self.queue.put("\nKeithley Multimeter : " + str(keithmulti.query("*IDN?")))
        # self.queue.put("\nKeithley Sourcemeter : " + str(keith.query("*IDN?")))

        # self.queue.put("\nOceanOptics : " + str(DEVICES.MAYA_devices[0]))
        # DEVICES.spec.integration_time_micros(self.integrationtime)

        # Write operational parameters to Sourcemeter (Voltage to OLED)
        # keith.write("*rst")  # reset instrument
        # keith.write("Source:Function Volt")  # set voltage as source
        # keith.write('Sense:Function "Current"')  # choose current for measuring
        # keith.write(
        #     "Source:Volt:ILimit " + str(self.scan_compliance)
        # )  # set compliance
        # keith.write("Source:Volt:READ:BACK ON")  # reads back the set voltage
        # keith.write(
        #     "Current:NPLCycles 1"
        # )  # sets the read-out speed and accuracy (0.01 fastest, 10 slowest but highest accuracy)
        # keith.write("Current:AZero OFF")  # turn off autozero
        # keith.write("Source:Volt:Delay:AUTO OFF")  # turn off autodelay

        # Write operational parameters to Multimeter (Voltage from Photodiode)
        # keithmulti.write("*rst")  # reset instrument
        # keithmulti.write("SENSe:VOLTage:DC:RANGe 10")  # sets the voltage range
        # keithmulti.query("VOLTage:DC:RESolution?")  # sets the voltage resolution
        # keithmulti.write(
        #     "VOLTage:NPLCycles 1"
        # )  # sets the read-out speed and accuracy (0.01 fastest, 10 slowest but highest accuracy)
        # keithmulti.write(
        #     "TRIGer:SOURce BUS"
        # )  # sets the trigger to activate immediately after 'idle' -> 'wait-for-trigger'
        # keithmulti.write(
        #     "TRIGer:DELay 0"
        # )  # sets the trigger to activate immediately after 'idle' -> 'wait-for-trigger'

        # -------------------------------------------------------------------- #
        # ----------------------- Autotube Measurement ----------------------- #
        # -------------------------------------------------------------------- #
        # Move to initial motor position
        self.motor.move_to(self.max_angle)
        time.sleep(self.homing_time)

        # "#####################################################################"
        # "#####TAKING MEASUREMENTS FROM THE THORLABS PDA100A2 PHOTODIODE#####"
        # "#####################################################################"
        # Only do a complete JVL scan if this was selected in the GUI
        # Use the existent class autotube_measurement class for this instead of copying code
        if self.measurement_parameters["voltage_scan"]:

            # To make this work these parameters obviously have to be set in the init section
            jvl_measurement = AutotubeMeasurement(
                self.keithley_source_address,
                self.keithley_multimeter_address,
                self.com2_address,
                self.photodiode_gain,
                self.autotube_measurement_parameters,
                self.pixel,
                self.file_path,
            )

            # Do the actual measurement
            jvl_measurement.measure()

            # We have to decide how the saving of this data should work, though
            # but my current plan is to take the file path and add a folder to
            # it and otherwise save the data as before
            jvl_measurement.save_data()

        # self.queue.put("\n\nPHOTODIODE READINGS")
        # "IMPLEMENTATION"
        # generate empty lists for later data collection
        # Define voltage steps
        # Voltage points for low OLED voltage
        # low_vlt = np.arange(
        # self.min_voltage, self.change_voltage, self.max_step_voltage
        # )  # Voltage points for low OLED voltage
        # high_vlt = np.arange(
        # self.change_voltage, self.max_voltage + 0.1, self.min_step_voltage
        # )  # Voltage points for high OLED voltage
        # OLEDvlt = []
        # OLEDcrt = []
        # PDvlt = []
        # "SCANNING VOLTAGES"
        # Optional scanning voltage readings, runs readings if Y, anything else and this section is skipped
        # if self.scan_status == str("Y"):

        #     keithmulti.write(
        #         "INITiate"
        #     )  # Initiating 'wait_for_trigger' mode for Multimeter
        #     keith.write(
        #         'Trace:Make "OLEDbuffer", ' + str(max(len(low_vlt) + len(high_vlt), 10))
        #     )  # Buffer for Sourcemeter
        #     keith.write('Trace:Clear "OLEDbuffer"')  # Keithley empties the buffer
        #     background_diodevoltage = float(
        #         keithmulti.query("MEASure:VOLTage:DC?")
        #     )  # Take PD voltage reading from Multimeter for background
        #     self.queue.put(
        #         "Background Photodiode Voltage :" + str(background_diodevoltage) + " V"
        #     )
        #     self.queue.put("\nSaving output to: " + "keithleyPDvoltages.txt")
        #     keith.write("Output ON")
        #     # Low Voltage Readings
        #     for voltage in low_vlt:
        #         self.queue.put("\nOLED Voltage : " + str(voltage) + " V")
        #         keith.write(
        #             "Source:Volt " + str(voltage)
        #         )  # Set voltage to source_value

        #         diodevoltage = float(
        #             keithmulti.query("MEASure:VOLTage:DC?")
        #         )  # Take PD voltage reading from Multimeter
        #         oledcurrent = float(
        #             keith.query('Read? "OLEDbuffer"')[:-1]
        #         )  # Take OLED current reading from Sourcemeter
        #         self.queue.put("OLED Current : " + str(oledcurrent * 1e3) + " mA")
        #         self.queue.put(
        #             "Photodiode Voltage :"
        #             + str(diodevoltage - background_diodevoltage)
        #             + " V"
        #         )
        #         PDvlt.append(diodevoltage - background_diodevoltage)
        #         OLEDcrt.append(oledcurrent)
        #         OLEDvlt.append(voltage)

        #     # High Voltage Readings
        #     for voltage in high_vlt:
        #         self.queue.put("\nOLED Voltage : " + str(voltage) + " V")
        #         keith.write(
        #             "Source:Volt " + str(voltage)
        #         )  # Set voltage to source_value

        #         diodevoltage = float(
        #             keithmulti.query("MEASure:VOLTage:DC?")
        #         )  # Take PD voltage reading from Multimeter
        #         oledcurrent = float(
        #             keith.query('Read? "OLEDbuffer"')[:-1]
        #         )  # Take OLED current reading from Sourcemeter
        #         self.queue.put("OLED Current : " + str(oledcurrent * 1e3) + " mA")
        #         self.queue.put(
        #             "Photodiode Voltage :"
        #             + str(diodevoltage - background_diodevoltage)
        #             + " V"
        #         )
        #         PDvlt.append(diodevoltage - background_diodevoltage)
        #         OLEDcrt.append(oledcurrent)
        #         OLEDvlt.append(voltage)
        #         self.scan_status = "N"

        #     keith.write("Output OFF")
        #     OLEDvolt = np.array(OLEDvlt)  # Creates voltage array
        #     OLEDcurrent = (
        #         np.array(OLEDcrt) * 1e3
        #     )  # Creates current array; NOTE: current in mA !!!
        #     PDvoltage = np.array(PDvlt)
        #     photodiodedata = np.stack((OLEDvolt, OLEDcurrent, PDvoltage))
        #     np.savetxt(
        #         keithleyfilename,
        #         photodiodedata.T,
        #         fmt="%.4f %.4e %.6f",
        #         header="\n".join(header_lines),
        #         delimiter="\t",
        #         comments="",
        #     )

        # "SPECIFIC READING AT CERTAIN CURRENT"

        # # Write operational parameters to Sourcemeter (Current to OLED)
        # keith.write("Source:Function Current")  # set current as source
        # keith.write(
        #     "Source:Current " + str(self.goniometer_value)
        # )  # set current to source_value
        # keith.write('Sense:Function "Volt"')  # choose voltage for measuring
        # keith.write(
        #     "Source:Current:VLimit " + str(self.goniometer_compliance)
        # )  # set voltage compliance to compliance
        # keith.write(
        #     "Source:Current:READ:BACK OFF"
        # )  # record preset source value instead of measuring it anew. NO CURRENT IS MEASURED!!! (Costs approx. 1.5 ms)
        # keith.write("Volt:AZero OFF")  # turn off autozero
        # keith.write("Source:Current:Delay:AUTO OFF")  # turn off autodelay
        # keith.write("Output ON")  # Turn power on

        # -------------------------------------------------------------------- #
        # ------------------------ Specifics of the PD ----------------------- #
        # -------------------------------------------------------------------- #

        # Take PD voltage reading from Multimeter for background
        background_diodevoltage = self.keithley_multimeter.measure_voltage()

        # Now use the keithley as current source
        self.keithley_source.as_current_source(self.voltage_compliance)
        self.keithley_source.set_current(self.current)
        self.keithley_source.activate_output()

        # Take PD voltage reading from Multimeter
        specificPDvoltage = self.keithley_multimeter.measure_voltage()
        # Background Subtracted
        specificPDvoltage = specificPDvoltage - background_diodevoltage
        # Take OLED current reading from Sourcemeter
        specificOLEDcurrent = self.keithley_source.read_current()
        # Take OLED voltage reading from Sourcemeter
        specificOLEDvoltage = self.keithley_source.read_voltage()
        # Deactivate output
        self.keithley_source.deactivate_output()

        # self.queue.put("\n\nSaving output to: " + "specifickeithleyPDvoltages.txt")
        # self.queue.put("\nPhotodiode Voltage :" + str(specificPDvoltage) + " V")
        # self.queue.put("OLED Voltage : " + str(specificOLEDvoltage) + " V")
        # self.queue.put("OLED Current : " + str(specificOLEDcurrent * 1e3) + " mA")

        specificphotodiodedata = np.stack(
            (
                np.array(specificOLEDvoltage),
                np.array(specificOLEDcurrent),
                np.array(specificPDvoltage),
            )
        )
        specifickeithleyfilename = (  # for filenames have foldername and filename
            "specifickeithleyPDvoltages.txt"
        )
        # amended with full path
        specifickeithleyfilename = os.path.abspath(
            os.path.join(keithleyfilepath, specifickeithleyfilename)
        )
        np.savetxt(
            specifickeithleyfilename,
            specificphotodiodedata,
            fmt="%.4f",
            header="\n".join(header_lines),
            delimiter="\t",
            comments="",
        )

        # "#####################################################################"
        # "####TAKING MEASUREMENTS FROM THE OCEANOPTICS MAYALSL SPECTROMETER####"
        # "#####################################################################"

        # self.queue.put("\n\nSPECTROMETER READINGS")

        # "SETTING PARAMETERS"
        # # Keithley OLED Current Parameters
        # warning_message = False
        # if self.source == "Current":
        #     sense = "Volt"
        # else:
        #     sense = "Current"

        # if warning_message is True:
        #     self.queue.put("\nWARNING:\n")
        #     if self.source == "Current":
        #         self.queue.put(
        #             "You are about to set "
        #             + str(self.source)
        #             + " as source with "
        #             + str(self.goniometer_value * 1e3)
        #             + " mA."
        #         )
        #         self.queue.put(
        #             "Your "
        #             + sense
        #             + " Compliance is "
        #             + str(self.goniometer_compliance)
        #             + " V.\n"
        #         )
        #     else:
        #         self.queue.put(
        #             "You are about to set "
        #             + str(self.source)
        #             + " as source with "
        #             + str(self.goniometer_value)
        #             + " V."
        #         )
        #         self.queue.put(
        #             "Your "
        #             + sense
        #             + " Compliance is "
        #             + str(self.goniometer_compliance * 1e3)
        #             + " mA.\n"
        #         )
        #     while True:
        #         i = input(
        #             "If this looks right, press Enter to continue. Else press 'q'"
        #             " to quit."
        #         )
        #         if i == "q":
        #             sys.exit("User exit. Check your operational parameters.")
        #         else:
        #             break

        # # Printing source and compliance
        # if self.source == "Current":
        #     self.queue.put(
        #         "\nsource current: " + str(self.goniometer_value * 1e3) + " mA"
        #     )
        #     self.queue.put(
        #         "voltage compliance: " + str(self.goniometer_compliance) + " V"
        #     )
        # else:
        #     self.queue.put("\nsource voltage: " + str(self.goniometer_value) + " V")
        #     self.queue.put(
        #         "current compliance: " + str(self.goniometer_compliance * 1e3) + " mA"
        #     )

        # self.queue.put("approx pulse length: " + str(self.pulse_duration) + " s")
        # self.queue.put(
        #     "Saving output to: " + "keithleyOLEDvoltages.txt" + " and Angle_.txt"
        # ),

        # self.queue.put("\n\nSource: " + str(keith.query("Source:Function?")))
        # self.queue.put("Sense: " + str(keith.query("Sense:Voltage:Unit?")))

        # "SETTING FILE DETAILS"
        # # Filename Parameters
        # keithleyfilename = "keithleyOLEDvoltages.txt"  # changing keithley filename
        # keithleyfilename = os.path.abspath(
        #     os.path.join(keithleyfilepath, keithleyfilename)
        # )  # amended with full path
        # mayafilename = "Background.txt"  # setting mayalsl filename for dark reading
        # mayafilename = os.path.abspath(os.path.join(mayafilepath, mayafilename))

        # "IMPLEMENTATION"
        # # Generate empty lists for current/voltage and wavelength/intensity data collection
        # vlt = []  # Voltages
        # crt = []  # Currents
        # ang = []  # Angles
        # wvl = []  # Wavelengths
        # inte = []  # Intensities
        # spect = []  # Spectrums

        # -------------------------------------------------------------------- #
        # ------------------- Measure background spectrum  ------------------- #
        # -------------------------------------------------------------------- #

        # Take a background calibration spectrum (without illumination?)
        background = self.spectrometer.measure()
        file_name = "background"
        self.save_spectrum(background, file_name)
        # np.savetxt(
        # mayafilename,
        # spectrum.T,
        # fmt="%.4f %.0f",
        # delimiter="\t",
        # header="\n".join(header_lines3),
        # comments="",
        # )

        # -------------------------------------------------------------------- #
        # ----------------- Actual Goniometer Measurement  ------------------- #
        # -------------------------------------------------------------------- #
        self.keithley_source.init_buffer("pulsebuffer", 1000)

        self.motor.move_to(self.goniometer_measurement_parameters["min_angle"])
        time.sleep(self.goniometer_measurement_parameters["homing_time"])

        # Keithley write operational parameters to SMU
        # keith.write("*rst")  # reset instrument
        if self.goniometer_measurement_parameters["constant_current"]:
            self.keithley_source.as_current_source(
                self.current, self.voltage_compliance
            )
            self.keithley_source.set_current(self.current)
        else:
            self.keithley_source.as_voltage_source(self.current_compliance)
            self.keithley_source.set_voltage(self.voltage)

        # Since the data shall be plotted after each measurement (it could also
        # be done while measuring but I think there is not much benefit and the
        # programming is uglier), only one pixel is scanned at a time
        df_data = pd.DataFrame(columns=["angle", "voltage", "current"])

        # I have no idea what this is
        processing_time = 0.5  # Initial processing time in seconds

        # Move motor by given increment while giving current to OLED and reading spectrum
        i = 0
        for angle in np.arange(self.min_angle, self.max_angle + 1, self.step_angle):
            # Move motor to desired position
            self.motor.move_to(angle)
            # Sleep to give the motor enough time to move (is there no smarter way?)
            time.sleep(self.goniometer_measurement_parameters["moving_time"])

            # When the OLED is rotated to the right position activate its output
            self.keithley_source.activate_output()

            # Not sure why the system shoudl sleep now
            time.sleep(
                self.goniometer_measurement_parameters["pulse_duration"]
                - processing_time
            )

            # Measure the time that elapses
            start_process = time.perf_counter()

            # Append data
            self.df_data.loc[i, "angle"] = angle

            # Depending on the measurement mode set the parameters
            # I think this should in principle be constant but could change due
            # to degradation or something like that
            if self.goniometer_measurement_parameters["current_or_voltage"]:
                self.df_data.loc[i, "current"] = self.goniometer_measurement_parameters[
                    "current_or_voltage"
                ]
                self.df_data.loc[i, "voltage"] = self.keithley_source.read_voltage()
                # line13 = "Source Current:		" + str(self.goniometer_value * 1e3) + " mA"
                # line14 = "Source Voltage:      " + str(temp_buffer) + " V"
            else:
                self.df_data.lov[i, "current"] = self.keithley_source.read_current()
                self.df_data.loc[i, "voltage"] = self.goniometer_measurement_parameters[
                    "current_or_voltage"
                ]
                # line13 = "Source Voltage:		" + str(self.goniometer_value) + " V"
                # line14 = "Source Current:      " + str(temp_buffer * 1e3) + " mA"
            # header_lines3.append(line13)
            # header_lines3.append(line14)
            # Take spectrometer readings
            # wavelength = DEVICES.spec.wavelengths()  # creates a list of wavelengths
            # intensity = DEVICES.spec.intensities()  # creates a list of intensities

            # Measure the spectrum
            df_data_spectrum = pd.DataFrame(columns=["wavelength", "intensity"])
            (
                df_data_spectrum.wavelength,
                df_data_spectrum.intensity,
            )

            # Save the spectrum
            file_name = "spectrum"
            self.save_spectrum(df_data_spectrum, file_name)
            # = (
            # DEVICES.spec.spectrum()
            # )  # this gives a pre-stacked array of wavelengths and intensities
            # wvl.append(
            #     wavelength
            # )  # adding to a master list (may not be necessary with txt file outputs)
            # inte.append(
            #     intensity
            # )  # adding to a master list (may not be necessary with txt file outputs)
            # spect.append(
            #     spectrum
            # )  # adding to a master list (may not be necessary with txt file outputs)

            # "DISPLAYING SPECTRUM AS A PLOT"
            # self.queue.put([wavelength, intensity])

            # --------------- To Do ---------------------
            # Do some plotting by calling the main program
            # --------------- To Do ---------------------

            # Turn output off
            self.keithley_source.deactivate_output()

            # keith.write("Output OFF")  # Turn current off

            # Calculate the processing time (time it took to take the measurement)
            # I really don't know why we need this
            end_process = time.perf_counter()
            processing_time = end_process - start_process
            # self.queue.put("\nProcessing time :  " + str(processing_time))

            # if self.ang_range == "F":
            # self.queue.put("\nAngle : " + str(angle + 90 - self.offset_angle))
            # ang.append(angle + 90 - self.offset_angle)
            # elif self.ang_range == "HL":
            # self.queue.put("\nAngle : " + str(angle - self.offset_angle))
            # ang.append(angle - self.offset_angle)
            # elif self.ang_range == "HR":
            # self.queue.put("\nAngle : " + str(self.offset_angle - angle))
            # ang.append(self.offset_angle - angle)

            i += 1

        # pulse_data = np.stack((ang, vlt, crt))

        self.save_data(df_data)

        # self.queue.put("\n\nMEASUREMENT COMPLETE")

    def save_data(self, data):
        """
        Function that saves the angle, voltage and current for the measurement
        """
        # Header Parameters
        line01 = "Measurement code : " + self.sample + datetime
        line02 = 'Measurement programme :	"GatherLab Goniometer Measurement System".py'
        linex = "Credits :	Gather Lab, University of St Andrews, 2018"
        linexx = "Integration Time:  " + str(self.integrationtime) + "micro s"
        line03 = "Pulse duration :		" + str(self.pulse_duration) + " s"
        line04 = "Step time between voltages :		" + str(self.moving_time) + " s"
        if self.source == "Current":
            line05 = "Source Current:		" + str(self.goniometer_value * 1e3) + " mA"
            line06 = "Voltage Compliance:	" + str(self.goniometer_compliance) + " V"
        else:
            line05 = "Source Voltage:		" + str(self.goniometer_value) + " V"
            line06 = (
                "Current Compliance:	" + str(self.goniometer_compliance * 1e3) + " mA"
            )
        line07 = "### Measurement data ###"
        line08 = "OLEDVoltage	OLEDCurrent Photodiode Voltage"
        line09 = "V	              mA               V"
        line10 = "Angle    OLEDVoltage   	OLEDCurrent"
        line11 = "Degrees 	  V       	 A"
        line12 = "Wavelength   Intensity"
        line13 = "nm             -"

        header_lines = [
            line01,
            line02,
            linex,
            linexx,
            line03,
            line04,
            line05,
            line06,
            line07,
            line08,
            line09,
        ]  # PD Voltages
        header_lines2 = [
            line01,
            line02,
            linex,
            linexx,
            line03,
            line04,
            line05,
            line06,
            line07,
            line10,
            line11,
        ]  # OLED Voltages
        header_lines3 = [
            line01,
            line02,
            linex,
            linexx,
            line03,
            line04,
            line05,
            line06,
            line07,
            line12,
            line13,
        ]  # Spectrum Data

        # "PULSE OUTPUT FILE"
        # Writing the file for Keithley
        if self.source == "Current":
            np.savetxt(
                keithleyfilename,
                pulse_data.T,
                fmt="%.0f %.4f %.3e",
                delimiter="\t",
                header="\n".join(header_lines2),
                comments="",
            )
        else:
            np.savetxt(
                keithleyfilename,
                pulse_data.T,
                fmt="%.0f %.4f %.3e",
                delimiter="\t",
                header="\n".join(header_lines2),
                comments="",
            )

    def save_spectrum(self, data, file_name):
        """
        Function that shall the save the measured spectrum
        """
        "SPECTRUM OUTPUT FILE"

        mayafilename = os.path.abspath(os.path.join(mayafilepath, mayafilename))
        np.savetxt(
            mayafilename,
            spectrum.T,
            fmt="%.3f %.0f",
            delimiter="\t",
            header="\n".join(header_lines3),
            comments="",
        )
