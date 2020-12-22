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
    MockThorlabMotor,
)
from autotube_measurement import AutotubeMeasurement

import time
import numpy as np
import pandas as pd


class GoniometerMeasurement(QtCore.QThread):
    """
    Thread class to do the goniometer measurement
    """

    update_goniometer_spectrum_signal = QtCore.Signal(list)

    def __init__(
        self,
        keithley_source_address,
        keithley_multimeter_address,
        com2_address,
        motor_number,
        motor_offset,
        integration_time,
        photodiode_gain,
        pixel,
        folder_path,
        goniometer_measurement_parameters,
        autotube_measurement_parameters,
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
        self.motor = MockThorlabMotor(motor_number, motor_offset)

        # Initialise member variables
        self.goniometer_measurement_parameters = goniometer_measurement_parameters
        self.autotube_measurement_parameters = autotube_measurement_parameters

        self.keithley_source_address = keithley_source_address
        self.keithley_multimeter_address = keithley_multimeter_address
        self.com2_address = com2_address
        self.photodiode_gain = photodiode_gain
        self.pixel = pixel
        self.folder_path = folder_path
        self.parent = parent

        # Connect signal to the updater from the parent class
        self.update_goniometer_spectrum_signal.connect(
            parent.update_goniometer_spectrum
        )

        # Declare the data structures that are used in the goniometer measurement
        self.iv_data = pd.DataFrame()
        self.spectrum_data = pd.DataFrame()
        self.specific_oled_voltage = 0
        self.specific_oled_current = 0
        self.specific_pd_voltage = 0

    def run(self):
        """
        Function that runs when the thread is started. It contains the
        measurement routine that is triggered when the measure button is
        pressed
        """

        # "INITIALIZING SETTINGS"
        # defaults = {}
        # settings = {}
        # parameters = []
        # "SETTING DEFAULT PARAMETERS"
        # defaults[0] = 'test' # sample
        # defaults[1] = 318 # offset_angle
        # defaults[2] = 1  # step_angle
        # defaults[3] = 300000 # integrationtime in microseconds
        # defaults[4] = 20.0 # homing_time
        # defaults[5] = 0.2 # moving_time
        # defaults[6] = 0.2  # pulse_duration in s
        # defaults[7] = 'F' # ang_range
        # defaults[8] = 'N' # scan_status
        # defaults[9] = -2.0  # min_voltage
        # defaults[10] = 2.0 # change_voltage
        # defaults[11] = 4.0  # max_voltage
        # defaults[12] = 0.1 # min_step_voltage
        # defaults[13] = 1.0 # max_step_voltage
        # defaults[14] = 0.10  # scan_compliance
        # defaults[15] = 'Current'  # source
        # defaults[16] = 0.001 # goniometer_value in A for current
        # defaults[17] = 5 # goniometer_compliance in V for voltage

        # "GETTING PARAMETERS FROM GUI, IF BLANK SETTING AS DEFAULT"
        # for x in range(0,18,1):
        # if not param[x]:
        # parameters.append(defaults[x])
        # else:
        # settings[x] = param[x]
        # parameters.append(settings[x])
        # if parameters[7] == 'F':
        # self.min_angle = float(parameters[1]) - 90
        # self.max_angle = float(parameters[1]) + 90
        # elif parameters[7] == 'HL':
        # self.min_angle = float(parameters[1])
        # self.max_angle = float(parameters[1]) + 90
        # elif parameters[7] == 'HR':
        # self.min_angle = float(parameters[1]) - 90
        # self.max_angle = float(parameters[1])
        # else:
        # self.queue.put('Invalid input.')
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
        # self.goniometer_value  = float(parameters[16])
        # self.goniometer_compliance = float(parameters[17])

        # "SETTING DIRECTORY DETAILS"
        # now = dt.datetime.now()
        # datetime = str(now.strftime("%Y-%m-%d %H:%M").replace(" ","").replace(":","").replace("-",""))
        # self.queue.put('Measurement code : ' + self.sample + datetime + '  (OLED device code followed by the datetime of measurement).')
        # # Set directories for recorded data.
        # directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', self.sample, datetime, 'raw')) # Folder to separate raw and processed data
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

        # # Write operational parameters to Sourcemeter (Voltage to OLED)
        # keith.write("*rst")  # reset instrument
        # keith.write("Source:Function Volt")  # set voltage as source
        # keith.write('Sense:Function "Current"')  # choose current for measuring
        # keith.write("Source:Volt:ILimit " + str(self.scan_compliance))  # set compliance
        # keith.write("Source:Volt:READ:BACK ON")  # reads back the set voltage
        # keith.write(
        #     "Current:NPLCycles 1"
        # )  # sets the read-out speed and accuracy (0.01 fastest, 10 slowest but highest accuracy)
        # keith.write("Current:AZero OFF")  # turn off autozero
        # keith.write("Source:Volt:Delay:AUTO OFF")  # turn off autodelay

        # # Write operational parameters to Multimeter (Voltage from Photodiode)
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

        # "MOVING TO INITIAL POSITION"
        # Move to initial position which is the offset position
        self.motor.move_to(0)
        self.parent.gw_animation.move(0)
        time.sleep(self.goniometer_measurement_parameters["homing_time"])

        # DEVICES.ELmotor.move_to(self.max_angle)
        # "#####################################################################"
        # "#####TAKING MEASUREMENTS FROM THE THORLABS PDA100A2 PHOTODIODE#####"
        # "#####################################################################"
        if self.goniometer_measurement_parameters["voltage_or_current"]:
            autotube_measurement = AutotubeMeasurement(
                self.keithley_source_address,
                self.keithley_multimeter_address,
                self.com2_address,
                self.photodiode_gain,
                self.autotube_measurement_parameters,
                self.pixel,
                self.folder_path,
            )
            autotube_measurement.measure()
            autotube_measurement.save_data()

        # self.queue.put("\n\nPHOTODIODE READINGS")
        # "IMPLEMENTATION"
        # # generate empty lists for later data collection
        # low_vlt = np.arange(
        #     self.min_voltage, self.change_voltage, self.max_step_voltage
        # )  # Voltage points for low OLED voltage
        # high_vlt = np.arange(
        #     self.change_voltage, self.max_voltage + 0.1, self.min_step_voltage
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

        # background_diodevoltage = float(
        #     keithmulti.query("MEASure:VOLTage:DC?")
        # )  # Take PD voltage reading from Multimeter for background

        # keith.write("Output ON")  # Turn power on

        # Take background voltage and measure specific current and voltage of photodiode and oled
        self.keithley_source.as_current_source(
            self.goniometer_measurement_parameters["vc_compliance"]
        )
        background_diode_voltage = self.keithley_multimeter.measure_voltage()
        self.keithley_source.activate_output()
        self.specific_pd_voltage = (
            self.keithley_multimeter.measure_voltage() - background_diode_voltage
        )
        self.specific_oled_current = self.keithley_source.read_current()
        self.specific_oled_voltage = self.keithley_source.read_voltage()
        self.keithley_source.deactivate_output()

        # specificPDvoltage = float(
        #     keithmulti.query("MEASure:VOLTage:DC?")
        # )  # Take PD voltage reading from Multimeter
        # specificPDvoltage = (
        #     specificPDvoltage - background_diodevoltage
        # )  # Background Subtracted
        # specificOLEDcurrent = float(
        #     keith.query("MEASure:CURRent:DC?")
        # )  # Take OLED current reading from Sourcemeter
        # specificOLEDvoltage = float(
        #     keith.query("MEASure:VOLTage:DC?")
        # )  # Take OLED current reading from Sourcemeter
        # keith.write("Output OFF")  # Turn power off
        # self.queue.put("\n\nSaving output to: " + "specifickeithleyPDvoltages.txt")
        # self.queue.put("\nPhotodiode Voltage :" + str(specificPDvoltage) + " V")
        # self.queue.put("OLED Voltage : " + str(specificOLEDvoltage) + " V")
        # self.queue.put("OLED Current : " + str(specificOLEDcurrent * 1e3) + " mA")

        # Here comes the real goniometer measurement

        # self.queue.put("\n\nSPECTROMETER READINGS")

        # "SETTING PARAMETERS"
        # Keithley OLED Current Parameters

        # Depending on if the user selected constant current or constant
        # voltage it is selected in the following what the Keithley source
        # should be
        if self.goniometer_measurement_parameters["voltage_or_current"]:
            self.keithley_source.as_voltage_source(
                self.goniometer_measurement_parameters["vc_compliance"]
            )
        else:
            self.keithley_source.as_current_source(
                self.goniometer_measurement_parameters["vc_compliance"]
            )

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
        #             "If this looks right, press Enter to continue. Else press 'q' to"
        #             " quit."
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

        # # Keithley write operational parameters to SMU
        # keith.write("*rst")  # reset instrument
        # if self.source == "Current":
        #     keith.write("Source:Function Current")  # set current as source
        #     keith.write(
        #         "Source:Current " + str(self.goniometer_value)
        #     )  # set current to source_value
        #     keith.write('Sense:Function "Volt"')  # choose voltage for measuring
        #     keith.write(
        #         "Source:Current:VLimit " + str(self.goniometer_compliance)
        #     )  # set voltage compliance to compliance
        #     keith.write(
        #         "Source:Current:READ:BACK OFF"
        #     )  # record preset source value instead of measuring it anew. NO CURRENT IS MEASURED!!! (Costs approx. 1.5 ms)
        #     keith.write("Volt:AZero OFF")  # turn off autozero
        #     keith.write("Source:Current:Delay:AUTO OFF")  # turn off autodelay
        # else:
        #     keith.write("Source:Function Volt")  # set voltage as source
        #     keith.write(
        #         "Source:Volt " + str(self.goniometer_value)
        #     )  # set voltage to source_value
        #     keith.write('Sense:Function "Current"')  # choose voltage for measuring
        #     keith.write(
        #         "Source:Volt:ILimit " + str(self.goniometer_compliance)
        #     )  # set voltage
        #     keith.write(
        #         "Source:Volt:READ:BACK OFF"
        #     )  # record preset source value instead of measuring it anew. NO VOLTAGE IS MEASURED!!! (Costs approx. 1.5 ms)
        #     keith.write(
        #         "Current:NPLCycles 1"
        #     )  # set acquisition factor to acq_factor (effectively sets the acquisition time)
        #     keith.write("Current:AZero OFF")  # turn off autozero
        #     keith.write("Source:Volt:Delay:AUTO OFF")  # turn off autodelay

        # self.queue.put("\n\nSource: " + str(keith.query("Source:Function?")))
        # self.queue.put("Sense: " + str(keith.query("Sense:Voltage:Unit?")))

        # "IMPLEMENTATION"
        # Generate empty lists for current/voltage and wavelength/intensity data collection
        # vlt = []  # Voltages
        # crt = []  # Currents
        # ang = []  # Angles
        # wvl = []  # Wavelengths
        # inte = []  # Intensities
        # spect = []  # Spectrums
        # buffer_length = 1000

        self.keithley_source.init_buffer("pulsebuffer", buffer_length=1000)

        # keith.write(
        #     'Trace:Make "pulsebuffer", ' + str(max(buffer_length, 10))
        # )  # create buffer; buffer size must be between 10 and 11000020
        # keith.write('Trace:Clear "pulsebuffer"')  # keithley empties the buffer

        self.motor.move_to(self.goniometer_measurement_parameters["minimum_angle"])
        self.parent.gw_animation.move(
            self.goniometer_measurement_parameters["minimum_angle"]
        )
        time.sleep(self.goniometer_measurement_parameters["homing_time"])

        # DEVICES.ELmotor.move_to(self.min_angle)
        # time.sleep(self.homing_time)
        # Take calibration readings
        calibration_spectrum = self.spectrometer.measure()
        self.spectrum_data["wavelength"] = calibration_spectrum[0]
        self.spectrum_data["background"] = calibration_spectrum[1]
        # spectrum = (
        #     DEVICES.spec.spectrum()
        # )  # this gives a pre-stacked array of wavelengths and intensities

        # Initial processing time in seconds
        # I am not quite sure why this is done and if there is no better way of doing it
        processing_time = 0.5

        # Empty list, stores the data as multiple dicts to later generate a pd dataframe
        rows_list = []

        # Move motor by given increment while giving current to OLED and reading spectrum
        for angle in np.arange(
            self.goniometer_measurement_parameters["minimum_angle"],
            self.goniometer_measurement_parameters["maximum_angle"] + 1,
            self.goniometer_measurement_parameters["step_angle"],
        ):

            self.motor.move_to(angle)
            self.parent.gw_animation.move(angle)
            time.sleep(self.goniometer_measurement_parameters["moving_time"])
            self.keithley_source.activate_output()
            # DEVICES.ELmotor.move_to(angle)
            # keith.write("Output ON")
            time.sleep(
                self.goniometer_measurement_parameters["pulse_duration"]
                - processing_time
            )

            start_process = time.process_time()
            temp_buffer = self.keithley_source.read_current()
            # iv_data[]
            # temp_buffer = float(
            #     keith.query('Read? "pulsebuffer"')[:-1]
            # )  # take measurement from Keithley
            # Add Keithley readings to lists

            # In the case of a voltage scan
            if self.goniometer_measurement_parameters["voltage_or_current"]:
                data_dict = {
                    "angle": angle,
                    "voltage": temp_buffer,
                    "current": self.goniometer_measurement_parameters["vc_value"],
                }
                # line13 = "Source Current:		" + str(self.goniometer_value * 1e3) + " mA"
                # line14 = "Source Voltage:      " + str(temp_buffer) + " V"
            else:
                data_dict = {
                    "angle": angle,
                    "voltage": self.goniometer_measurement_parameters["vc_value"],
                    "current": temp_buffer,
                }
                # crt.append(temp_buffer)
                # vlt.append(self.goniometer_value)
                # line13 = "Source Voltage:		" + str(self.goniometer_value) + " V"
                # line14 = "Source Current:      " + str(temp_buffer * 1e3) + " mA"

            rows_list.append(data_dict)

            # Now measure spectrum (wavelength and intensity)
            self.spectrum_data[str(angle) + "°"] = self.spectrometer.measure()[1]

            # Emit a signal to update the plot
            self.update_goniometer_spectrum_signal.emit(self.spectrum_data)

            # wavelength = DEVICES.spec.wavelengths()  # creates a list of wavelengths
            # intensity = DEVICES.spec.intensities()  # creates a list of intensities
            # spectrum = (
            # DEVICES.spec.spectrum()
            # )  # this gives a pre-stacked array of wavelengths and intensities
            # wvl.append(
            # wavelength
            # )  # adding to a master list (may not be necessary with txt file outputs)
            # inte.append(
            # intensity
            # )  # adding to a master list (may not be necessary with txt file outputs)
            # spect.append(
            # spectrum
            # )  # adding to a master list (may not be necessary with txt file outputs)
            # "DISPLAYING SPECTRUM AS A PLOT"
            # self.queue.put([wavelength, intensity])
            # "SPECTRUM OUTPUT FILE"
            # Angle is written as 0 -> 180 rather than -90 -> 90
            self.keithley_source.deactivate_output()
            # keith.write("Output OFF")  # Turn current off

            # Calculate the processing time it took
            end_process = time.process_time()
            processing_time = end_process - start_process

            # self.queue.put("\nProcessing time :  " + str(processing_time))
            # if self.ang_range == "F":
            #     self.queue.put("\nAngle : " + str(angle + 90 - self.offset_angle))
            #     ang.append(angle + 90 - self.offset_angle)
            # elif self.ang_range == "HL":
            #     self.queue.put("\nAngle : " + str(angle - self.offset_angle))
            #     ang.append(angle - self.offset_angle)
            # elif self.ang_range == "HR":
            #     self.queue.put("\nAngle : " + str(self.offset_angle - angle))
            #     ang.append(self.offset_angle - angle)

        self.iv_data = pd.DataFrame(rows_list)

        # pulse_data = np.stack((ang, vlt, crt))
        # "PULSE OUTPUT FILE"
        # Writing the file for Keithley
        # self.queue.put("\n\nMEASUREMENT COMPLETE")

    def save_iv_data(self):
        """
        Function to save the iv data that contains the data of current and
        voltage at each angle.
        """
        # Header Parameters
        line01 = (
            "Integration time:   "
            + str(self.goniometer_measurement_parameters["integration_time"])
            + " micro s    "
            + "Pulse duration:   "
            + str(self.goniometer_measurement_parameters["pulse_duration"])
            + " s    "
            + "Step time:   "
            + str(self.goniometer_measurement_parameters["moving_time"])
            + " 2"
        )
        if self.goniometer_measurement_parameters["voltage_or_current"]:
            line02 = (
                "Source Voltage:		"
                + str(self.goniometer_measurement_parameters["vc_value"])
                + " V"
                + "Current Compliance:	"
                + str(self.goniometer_measurement_parameters["vc_compliance"] * 1e3)
                + " mA"
            )
        else:
            line02 = (
                "Source Current:		"
                + str(self.goniometer_measurement_parameters["vc_value"] * 1e3)
                + " mA"
                + "Voltage Compliance:	"
                + str(self.goniometer_measurement_parameters["vc_compliance"])
                + " V"
            )

        # Save the specific oled and photodiode data
        line03 = "Specific oled and photodiode data"
        line04 = (
            "OLED voltage:     "
            + str(self.specific_oled_voltage)
            + " V"
            + "OLED current:        "
            + str(self.specific_oled_current)
            + " mA"
            + "PD voltage:      "
            + str(self.specific_pd_voltage)
            + " V"
        )
        line05 = "### Measurement data ###"
        line06 = "Angle\t OLED Voltage\t OLED Current"
        line07 = "°\t V\t mA\n"

        header_lines = [
            line01,
            line02,
            line03,
            line04,
            line05,
            line06,
            line07,
        ]

        # Write header lines to file
        with open(self.folder_path + "goniometer_iv_data.csv", "a") as the_file:
            the_file.write("\n".join(header_lines))

        # Now write pandas dataframe to file
        self.iv_data.to_csv(
            self.folder_path + "goniometer_iv_data.csv",
            index=False,
            mode="a",
            header=False,
            sep="\t",
        )

    def save_spectrum_data(self):
        """
        Function to save the spectrum data to a separate file
        """
        # Header Parameters
        line01 = (
            "Integration time:   "
            + str(self.goniometer_measurement_parameters["integration_time"])
            + " micro s    "
            + "Pulse duration:   "
            + str(self.goniometer_measurement_parameters["pulse_duration"])
            + " s    "
            + "Step time:   "
            + str(self.goniometer_measurement_parameters["moving_time"])
            + " 2"
        )
        if self.goniometer_measurement_parameters["voltage_or_current"]:
            line02 = (
                "Source Voltage:		"
                + str(self.goniometer_measurement_parameters["vc_value"])
                + " V"
                + "Current Compliance:	"
                + str(self.goniometer_measurement_parameters["vc_compliance"] * 1e3)
                + " mA"
            )
        else:
            line02 = (
                "Source Current:		"
                + str(self.goniometer_measurement_parameters["vc_value"] * 1e3)
                + " mA"
                + "Voltage Compliance:	"
                + str(self.goniometer_measurement_parameters["vc_compliance"])
                + " V"
            )

        # Save the specific oled and photodiode data
        line03 = "### Measurement data ###"

        header_lines = [
            line01,
            line02,
            line03,
        ]

        # Write header lines to file
        with open(self.folder_path + "goniometer_spectra.csv", "a") as the_file:
            the_file.write("\n".join(header_lines))

        # Now write pandas dataframe to file with header names
        self.spectrum_data.to_csv(
            self.folder_path + "goniometer_spectra.csv",
            index=False,
            mode="a",
            header=True,
            sep="\t",
        )
