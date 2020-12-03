# -*- coding: utf-8 -*-

import pyvisa  # Keithley Module
import serial  # Arduino Modul

from PySide2 import QtCore

from hardware import ArduinoUno, KeithleySource, KeithleyMultimeter
from tests.tests import MockArduinoUno, MockKeithleySource, MockKeithleyMultimeter


class GoniometerMeasurement(QtCore.QThread):
    """
    Thread class to do the goniometer measurement
    """

    def __init__(
        self,
        keithley_source_address,
        keithley_multimeter_address,
        com2_address,
        measurement_parameters,
        parent=None,
    ):
        super(GoniometerMeasurement, self).__init__()
        self.uno = MockArduinoUno(com2_address)
        self.keithley_source = MockKeithleySource(
            keithley_source_address, measurement_parameters["scan_compliance"]
        )
        self.keithley_multimeter = MockKeithleyMultimeter(keithley_multimeter_address)

    def testrunEL(self):
        while running == True:

            "INITIALIZING SETTINGS"
            defaults = {}
            settings = {}
            parameters = []
            "SETTING DEFAULT PARAMETERS"
            defaults[0] = "test"  # sample
            defaults[1] = 318  # offset_angle
            defaults[2] = 1  # step_angle
            defaults[3] = 300000  # integrationtime in microseconds
            defaults[4] = 20.0  # homing_time
            defaults[5] = 0.2  # moving_time
            defaults[6] = 0.2  # pulse_duration in s
            defaults[7] = "F"  # ang_range
            defaults[8] = "N"  # scan_status
            defaults[9] = -2.0  # min_voltage
            defaults[10] = 2.0  # change_voltage
            defaults[11] = 4.0  # max_voltage
            defaults[12] = 0.1  # min_step_voltage
            defaults[13] = 1.0  # max_step_voltage
            defaults[14] = 0.10  # scan_compliance
            defaults[15] = "Current"  # source
            defaults[16] = 0.001  # goniometer_value in A for current
            defaults[17] = 5  # goniometer_compliance in V for voltage

            "GETTING PARAMETERS FROM GUI, IF BLANK SETTING AS DEFAULT"
            for x in range(0, 18, 1):
                if not param[x]:
                    parameters.append(defaults[x])
                else:
                    settings[x] = param[x]
                    parameters.append(settings[x])
            if parameters[7] == "F":
                self.min_angle = float(parameters[1]) - 90
                self.max_angle = float(parameters[1]) + 90
            elif parameters[7] == "HL":
                self.min_angle = float(parameters[1])
                self.max_angle = float(parameters[1]) + 90
            elif parameters[7] == "HR":
                self.min_angle = float(parameters[1]) - 90
                self.max_angle = float(parameters[1])
            else:
                self.queue.put("Invalid input.")

            "SETTING PARAMTERS"
            self.sample = parameters[0]
            self.offset_angle = float(parameters[1])
            self.step_angle = float(parameters[2])
            self.integrationtime = float(parameters[3])
            self.homing_time = float(parameters[4])
            self.moving_time = float(parameters[5])
            self.pulse_duration = float(parameters[6])
            self.ang_range = parameters[7]
            self.scan_status = parameters[8]
            self.min_voltage = float(parameters[9])
            self.change_voltage = float(parameters[10])
            self.max_voltage = float(parameters[11])
            self.min_step_voltage = float(parameters[12])
            self.max_step_voltage = float(parameters[13])
            self.scan_compliance = float(parameters[14])
            self.source = parameters[15]
            self.goniometer_value = float(parameters[16])
            self.goniometer_compliance = float(parameters[17])

            "SETTING DIRECTORY DETAILS"
            now = dt.datetime.now()
            datetime = str(
                now.strftime("%Y-%m-%d %H:%M")
                .replace(" ", "")
                .replace(":", "")
                .replace("-", "")
            )
            self.queue.put(
                "Measurement code : "
                + self.sample
                + datetime
                + "  (OLED device code followed by the datetime of measurement)."
            )
            # Set directories for recorded data.
            directory = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__), "data", self.sample, datetime, "raw"
                )
            )  # Folder to separate raw and processed data
            if os.path.isdir(directory):
                pass
            else:
                os.makedirs(directory)

            "SETTING FILE DETAILS"
            # Filename Parameters
            keithleyfilepath = os.path.join(directory, "keithleydata")
            mayafilepath = os.path.join(directory, "spectrumdata")
            if os.path.isdir(keithleyfilepath):
                pass
            else:
                os.makedirs(keithleyfilepath)
            if os.path.isdir(mayafilepath):
                pass
            else:
                os.makedirs(mayafilepath)

            keithleyfilename = (  # for filenames have foldername and filename
                "keithleyPDvoltages.txt"
            )
            keithleyfilename = os.path.abspath(
                os.path.join(keithleyfilepath, keithleyfilename)
            )  # amended with full path

            # Header Parameters
            line01 = "Measurement code : " + self.sample + datetime
            line02 = (
                'Measurement programme :	"GatherLab Goniometer Measurement System".py'
            )
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
                    "Current Compliance:	"
                    + str(self.goniometer_compliance * 1e3)
                    + " mA"
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

            "INITIALIZING HARDWARE"
            # Keithley Finding Device
            rm = visa.ResourceManager()
            keith = rm.open_resource(u"USB0::0x05E6::0x2450::04102170::INSTR")
            keithmulti = rm.open_resource(u"USB0::0x05E6::0x2100::8003430::INSTR")
            self.queue.put("\nKeithley Multimeter : " + str(keithmulti.query("*IDN?")))
            self.queue.put("\nKeithley Sourcemeter : " + str(keith.query("*IDN?")))

            self.queue.put("\nOceanOptics : " + str(DEVICES.MAYA_devices[0]))
            # DEVICES.spec.integration_time_micros(self.integrationtime)

            # Write operational parameters to Sourcemeter (Voltage to OLED)
            keith.write("*rst")  # reset instrument
            keith.write("Source:Function Volt")  # set voltage as source
            keith.write('Sense:Function "Current"')  # choose current for measuring
            keith.write(
                "Source:Volt:ILimit " + str(self.scan_compliance)
            )  # set compliance
            keith.write("Source:Volt:READ:BACK ON")  # reads back the set voltage
            keith.write(
                "Current:NPLCycles 1"
            )  # sets the read-out speed and accuracy (0.01 fastest, 10 slowest but highest accuracy)
            keith.write("Current:AZero OFF")  # turn off autozero
            keith.write("Source:Volt:Delay:AUTO OFF")  # turn off autodelay

            # Write operational parameters to Multimeter (Voltage from Photodiode)
            keithmulti.write("*rst")  # reset instrument
            keithmulti.write("SENSe:VOLTage:DC:RANGe 10")  # sets the voltage range
            keithmulti.query("VOLTage:DC:RESolution?")  # sets the voltage resolution
            keithmulti.write(
                "VOLTage:NPLCycles 1"
            )  # sets the read-out speed and accuracy (0.01 fastest, 10 slowest but highest accuracy)
            keithmulti.write(
                "TRIGer:SOURce BUS"
            )  # sets the trigger to activate immediately after 'idle' -> 'wait-for-trigger'
            keithmulti.write(
                "TRIGer:DELay 0"
            )  # sets the trigger to activate immediately after 'idle' -> 'wait-for-trigger'

            "MOVING TO INITIAL POSITION"
            # DEVICES.ELmotor.move_to(self.max_angle)
            time.sleep(self.homing_time)

            "#####################################################################"
            "#####TAKING MEASUREMENTS FROM THE THORLABS PDA100A2 PHOTODIODE#####"
            "#####################################################################"

            self.queue.put("\n\nPHOTODIODE READINGS")
            "IMPLEMENTATION"
            # generate empty lists for later data collection
            low_vlt = np.arange(
                self.min_voltage, self.change_voltage, self.max_step_voltage
            )  # Voltage points for low OLED voltage
            high_vlt = np.arange(
                self.change_voltage, self.max_voltage + 0.1, self.min_step_voltage
            )  # Voltage points for high OLED voltage
            OLEDvlt = []
            OLEDcrt = []
            PDvlt = []
            "SCANNING VOLTAGES"
            # Optional scanning voltage readings, runs readings if Y, anything else and this section is skipped
            if self.scan_status == str("Y"):

                keithmulti.write(
                    "INITiate"
                )  # Initiating 'wait_for_trigger' mode for Multimeter
                keith.write(
                    'Trace:Make "OLEDbuffer", '
                    + str(max(len(low_vlt) + len(high_vlt), 10))
                )  # Buffer for Sourcemeter
                keith.write('Trace:Clear "OLEDbuffer"')  # Keithley empties the buffer
                background_diodevoltage = float(
                    keithmulti.query("MEASure:VOLTage:DC?")
                )  # Take PD voltage reading from Multimeter for background
                self.queue.put(
                    "Background Photodiode Voltage :"
                    + str(background_diodevoltage)
                    + " V"
                )
                self.queue.put("\nSaving output to: " + "keithleyPDvoltages.txt")
                keith.write("Output ON")
                # Low Voltage Readings
                for voltage in low_vlt:
                    self.queue.put("\nOLED Voltage : " + str(voltage) + " V")
                    keith.write(
                        "Source:Volt " + str(voltage)
                    )  # Set voltage to source_value

                    diodevoltage = float(
                        keithmulti.query("MEASure:VOLTage:DC?")
                    )  # Take PD voltage reading from Multimeter
                    oledcurrent = float(
                        keith.query('Read? "OLEDbuffer"')[:-1]
                    )  # Take OLED current reading from Sourcemeter
                    self.queue.put("OLED Current : " + str(oledcurrent * 1e3) + " mA")
                    self.queue.put(
                        "Photodiode Voltage :"
                        + str(diodevoltage - background_diodevoltage)
                        + " V"
                    )
                    PDvlt.append(diodevoltage - background_diodevoltage)
                    OLEDcrt.append(oledcurrent)
                    OLEDvlt.append(voltage)

                # High Voltage Readings
                for voltage in high_vlt:
                    self.queue.put("\nOLED Voltage : " + str(voltage) + " V")
                    keith.write(
                        "Source:Volt " + str(voltage)
                    )  # Set voltage to source_value

                    diodevoltage = float(
                        keithmulti.query("MEASure:VOLTage:DC?")
                    )  # Take PD voltage reading from Multimeter
                    oledcurrent = float(
                        keith.query('Read? "OLEDbuffer"')[:-1]
                    )  # Take OLED current reading from Sourcemeter
                    self.queue.put("OLED Current : " + str(oledcurrent * 1e3) + " mA")
                    self.queue.put(
                        "Photodiode Voltage :"
                        + str(diodevoltage - background_diodevoltage)
                        + " V"
                    )
                    PDvlt.append(diodevoltage - background_diodevoltage)
                    OLEDcrt.append(oledcurrent)
                    OLEDvlt.append(voltage)
                    self.scan_status = "N"

                keith.write("Output OFF")
                OLEDvolt = np.array(OLEDvlt)  # Creates voltage array
                OLEDcurrent = (
                    np.array(OLEDcrt) * 1e3
                )  # Creates current array; NOTE: current in mA !!!
                PDvoltage = np.array(PDvlt)
                photodiodedata = np.stack((OLEDvolt, OLEDcurrent, PDvoltage))
                np.savetxt(
                    keithleyfilename,
                    photodiodedata.T,
                    fmt="%.4f %.4e %.6f",
                    header="\n".join(header_lines),
                    delimiter="\t",
                    comments="",
                )

            "SPECIFIC READING AT CERTAIN CURRENT"

            # Write operational parameters to Sourcemeter (Current to OLED)
            keith.write("Source:Function Current")  # set current as source
            keith.write(
                "Source:Current " + str(self.goniometer_value)
            )  # set current to source_value
            keith.write('Sense:Function "Volt"')  # choose voltage for measuring
            keith.write(
                "Source:Current:VLimit " + str(self.goniometer_compliance)
            )  # set voltage compliance to compliance
            keith.write(
                "Source:Current:READ:BACK OFF"
            )  # record preset source value instead of measuring it anew. NO CURRENT IS MEASURED!!! (Costs approx. 1.5 ms)
            keith.write("Volt:AZero OFF")  # turn off autozero
            keith.write("Source:Current:Delay:AUTO OFF")  # turn off autodelay
            background_diodevoltage = float(
                keithmulti.query("MEASure:VOLTage:DC?")
            )  # Take PD voltage reading from Multimeter for background

            keith.write("Output ON")  # Turn power on
            specificPDvoltage = float(
                keithmulti.query("MEASure:VOLTage:DC?")
            )  # Take PD voltage reading from Multimeter
            specificPDvoltage = (
                specificPDvoltage - background_diodevoltage
            )  # Background Subtracted
            specificOLEDcurrent = float(
                keith.query("MEASure:CURRent:DC?")
            )  # Take OLED current reading from Sourcemeter
            specificOLEDvoltage = float(
                keith.query("MEASure:VOLTage:DC?")
            )  # Take OLED current reading from Sourcemeter
            keith.write("Output OFF")  # Turn power off

            self.queue.put("\n\nSaving output to: " + "specifickeithleyPDvoltages.txt")
            self.queue.put("\nPhotodiode Voltage :" + str(specificPDvoltage) + " V")
            self.queue.put("OLED Voltage : " + str(specificOLEDvoltage) + " V")
            self.queue.put("OLED Current : " + str(specificOLEDcurrent * 1e3) + " mA")

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
            specifickeithleyfilename = os.path.abspath(
                os.path.join(keithleyfilepath, specifickeithleyfilename)
            )  # amended with full path
            np.savetxt(
                specifickeithleyfilename,
                specificphotodiodedata,
                fmt="%.4f",
                header="\n".join(header_lines),
                delimiter="\t",
                comments="",
            )

            "#####################################################################"
            "####TAKING MEASUREMENTS FROM THE OCEANOPTICS MAYALSL SPECTROMETER####"
            "#####################################################################"

            self.queue.put("\n\nSPECTROMETER READINGS")

            "SETTING PARAMETERS"
            # Keithley OLED Current Parameters
            warning_message = False
            if self.source == "Current":
                sense = "Volt"
            else:
                sense = "Current"

            if warning_message is True:
                self.queue.put("\nWARNING:\n")
                if self.source == "Current":
                    self.queue.put(
                        "You are about to set "
                        + str(self.source)
                        + " as source with "
                        + str(self.goniometer_value * 1e3)
                        + " mA."
                    )
                    self.queue.put(
                        "Your "
                        + sense
                        + " Compliance is "
                        + str(self.goniometer_compliance)
                        + " V.\n"
                    )
                else:
                    self.queue.put(
                        "You are about to set "
                        + str(self.source)
                        + " as source with "
                        + str(self.goniometer_value)
                        + " V."
                    )
                    self.queue.put(
                        "Your "
                        + sense
                        + " Compliance is "
                        + str(self.goniometer_compliance * 1e3)
                        + " mA.\n"
                    )
                while True:
                    i = input(
                        "If this looks right, press Enter to continue. Else press 'q'"
                        " to quit."
                    )
                    if i == "q":
                        sys.exit("User exit. Check your operational parameters.")
                    else:
                        break

            # Printing source and compliance
            if self.source == "Current":
                self.queue.put(
                    "\nsource current: " + str(self.goniometer_value * 1e3) + " mA"
                )
                self.queue.put(
                    "voltage compliance: " + str(self.goniometer_compliance) + " V"
                )
            else:
                self.queue.put("\nsource voltage: " + str(self.goniometer_value) + " V")
                self.queue.put(
                    "current compliance: "
                    + str(self.goniometer_compliance * 1e3)
                    + " mA"
                )

            self.queue.put("approx pulse length: " + str(self.pulse_duration) + " s")
            self.queue.put(
                "Saving output to: " + "keithleyOLEDvoltages.txt" + " and Angle_.txt"
            ),

            # Keithley write operational parameters to SMU
            keith.write("*rst")  # reset instrument
            if self.source == "Current":
                keith.write("Source:Function Current")  # set current as source
                keith.write(
                    "Source:Current " + str(self.goniometer_value)
                )  # set current to source_value
                keith.write('Sense:Function "Volt"')  # choose voltage for measuring
                keith.write(
                    "Source:Current:VLimit " + str(self.goniometer_compliance)
                )  # set voltage compliance to compliance
                keith.write(
                    "Source:Current:READ:BACK OFF"
                )  # record preset source value instead of measuring it anew. NO CURRENT IS MEASURED!!! (Costs approx. 1.5 ms)
                keith.write("Volt:AZero OFF")  # turn off autozero
                keith.write("Source:Current:Delay:AUTO OFF")  # turn off autodelay
            else:
                keith.write("Source:Function Volt")  # set voltage as source
                keith.write(
                    "Source:Volt " + str(self.goniometer_value)
                )  # set voltage to source_value
                keith.write('Sense:Function "Current"')  # choose voltage for measuring
                keith.write(
                    "Source:Volt:ILimit " + str(self.goniometer_compliance)
                )  # set voltage
                keith.write(
                    "Source:Volt:READ:BACK OFF"
                )  # record preset source value instead of measuring it anew. NO VOLTAGE IS MEASURED!!! (Costs approx. 1.5 ms)
                keith.write(
                    "Current:NPLCycles 1"
                )  # set acquisition factor to acq_factor (effectively sets the acquisition time)
                keith.write("Current:AZero OFF")  # turn off autozero
                keith.write("Source:Volt:Delay:AUTO OFF")  # turn off autodelay

            self.queue.put("\n\nSource: " + str(keith.query("Source:Function?")))
            self.queue.put("Sense: " + str(keith.query("Sense:Voltage:Unit?")))

            "SETTING FILE DETAILS"
            # Filename Parameters
            keithleyfilename = "keithleyOLEDvoltages.txt"  # changing keithley filename
            keithleyfilename = os.path.abspath(
                os.path.join(keithleyfilepath, keithleyfilename)
            )  # amended with full path
            mayafilename = "Background.txt"  # setting mayalsl filename for dark reading
            mayafilename = os.path.abspath(os.path.join(mayafilepath, mayafilename))

            "IMPLEMENTATION"
            # Generate empty lists for current/voltage and wavelength/intensity data collection
            vlt = []  # Voltages
            crt = []  # Currents
            ang = []  # Angles
            wvl = []  # Wavelengths
            inte = []  # Intensities
            spect = []  # Spectrums

            buffer_length = 1000
            keith.write(
                'Trace:Make "pulsebuffer", ' + str(max(buffer_length, 10))
            )  # create buffer; buffer size must be between 10 and 11000020
            keith.write('Trace:Clear "pulsebuffer"')  # keithley empties the buffer

            # DEVICES.ELmotor.move_to(self.min_angle)
            time.sleep(self.homing_time)

            # Take calibration readings
            spectrum = (
                DEVICES.spec.spectrum()
            )  # this gives a pre-stacked array of wavelengths and intensities
            np.savetxt(
                mayafilename,
                spectrum.T,
                fmt="%.4f %.0f",
                delimiter="\t",
                header="\n".join(header_lines3),
                comments="",
            )
            processing_time = 0.5  # Initial processing time in seconds

            # Move motor by given increment while giving current to OLED and reading spectrum
            for angle in np.arange(self.min_angle, self.max_angle + 1, self.step_angle):

                # DEVICES.ELmotor.move_to(angle)
                time.sleep(self.moving_time)
                keith.write("Output ON")
                time.sleep(self.pulse_duration - processing_time)
                start_process = time.clock()
                temp_buffer = float(
                    keith.query('Read? "pulsebuffer"')[:-1]
                )  # take measurement from Keithley
                # Add Keithley readings to lists
                if self.source == "Current":
                    crt.append(self.goniometer_value)
                    vlt.append(temp_buffer)
                    line13 = (
                        "Source Current:		" + str(self.goniometer_value * 1e3) + " mA"
                    )
                    line14 = "Source Voltage:      " + str(temp_buffer) + " V"
                else:
                    crt.append(temp_buffer)
                    vlt.append(self.goniometer_value)
                    line13 = "Source Voltage:		" + str(self.goniometer_value) + " V"
                    line14 = "Source Current:      " + str(temp_buffer * 1e3) + " mA"
                header_lines3.append(line13)
                header_lines3.append(line14)
                # Take spectrometer readings
                wavelength = DEVICES.spec.wavelengths()  # creates a list of wavelengths
                intensity = DEVICES.spec.intensities()  # creates a list of intensities
                spectrum = (
                    DEVICES.spec.spectrum()
                )  # this gives a pre-stacked array of wavelengths and intensities
                wvl.append(
                    wavelength
                )  # adding to a master list (may not be necessary with txt file outputs)
                inte.append(
                    intensity
                )  # adding to a master list (may not be necessary with txt file outputs)
                spect.append(
                    spectrum
                )  # adding to a master list (may not be necessary with txt file outputs)

                "DISPLAYING SPECTRUM AS A PLOT"
                self.queue.put([wavelength, intensity])

                "SPECTRUM OUTPUT FILE"
                # Angle is written as 0 -> 180 rather than -90 -> 90
                if self.ang_range == "F":
                    mayafilename = (
                        "Angle" + str(angle + 90 - self.offset_angle).zfill(3) + ".txt"
                    )  # changing mayalsl filename for actual readings
                elif self.ang_range == "HL":
                    mayafilename = (
                        "Angle" + str(angle - self.offset_angle).zfill(3) + ".txt"
                    )  # changing mayalsl filename for actual readings
                elif self.ang_range == "HR":
                    mayafilename = (
                        "Angle" + str(self.offset_angle - angle).zfill(3) + ".txt"
                    )  # changing mayalsl filename for actual readings
                mayafilename = os.path.abspath(os.path.join(mayafilepath, mayafilename))
                np.savetxt(
                    mayafilename,
                    spectrum.T,
                    fmt="%.3f %.0f",
                    delimiter="\t",
                    header="\n".join(header_lines3),
                    comments="",
                )
                keith.write("Output OFF")  # Turn current off
                end_process = time.clock()
                processing_time = end_process - start_process
                self.queue.put("\nProcessing time :  " + str(processing_time))

                if self.ang_range == "F":
                    self.queue.put("\nAngle : " + str(angle + 90 - self.offset_angle))
                    ang.append(angle + 90 - self.offset_angle)
                elif self.ang_range == "HL":
                    self.queue.put("\nAngle : " + str(angle - self.offset_angle))
                    ang.append(angle - self.offset_angle)
                elif self.ang_range == "HR":
                    self.queue.put("\nAngle : " + str(self.offset_angle - angle))
                    ang.append(self.offset_angle - angle)

            pulse_data = np.stack((ang, vlt, crt))

            "PULSE OUTPUT FILE"
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

            self.queue.put("\n\nMEASUREMENT COMPLETE")
