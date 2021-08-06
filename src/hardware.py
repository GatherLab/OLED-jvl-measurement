import pyvisa  # Keithley Module
import serial  # Arduino Module
import seabreeze

seabreeze.use("pyseabreeze")
import seabreeze.spectrometers as sb  # MayaLSL Modules for Ocean Spectrometer

import core_functions as cf

import thorlabs_apt as apt  # thorlabs apt for thorlabs motor

import sys
import time
import logging
import re
import numpy as np

from PySide2 import QtCore, QtGui, QtWidgets


class ArduinoUno:
    """
    Class that manages all functionality of our arduino uno
    """

    def __init__(self, com_address):
        # Define a mutex
        self.mutex = QtCore.QMutex(QtCore.QMutex.Recursive)

        # Check for devices on the pc
        rm = pyvisa.ResourceManager()
        # The actual addresses for the Keithleys can be accessed via rm.list_resources()
        visa_resources = rm.list_resources()

        # Open COM port to Arduino
        if com_address not in visa_resources:
            cf.log_message(
                "The Arduino Uno seems to be missing. Try to reconnect to computer."
            )
            # self.queue.put(
            # "Arduino Uno seems to be missing."
            # + "\nPlease connect Arduino Uno to computer and try again."
            # )
            sys.exit()

        # Instead of letting the user explicitly define the COM port after he
        # already defined the com_address, search for the number in the
        # com_address to construct the right string
        uno_port = "COM" + re.findall(r"\d+", com_address)[0]

        # assign name to Arduino and assign short timeout to be able to do things fast
        self.uno = serial.Serial(uno_port, timeout=0.01)

        # Try to open the serial connection
        try:
            self.init_serial_connection()
        except serial.SerialException:
            # If the serial connection was already established, close it again and open it again
            try:
                self.uno.close()
                self.init_serial_connection()
            except IOError:
                cf.log_message(
                    "COM port to Arduino Uno already open. Reconnect arduino manually and try again."
                )
                # self.queue.put(
                # "COM2 port to Arduino Uno already open."
                # + "\nTry 'uno.close()' in your console or restarting IPython."
                # )
                sys.exit()

        # cf.log_message("Arduino successfully initiated")

    def init_serial_connection(self, wait=1):
        """
        Private function
        Initialise serial connection to com.

        com: func
            specify COM port. Needs to be opened prior to calling this function.
            e.g.:
                > uno = serial.Serial(2, timeout=0.2)
                > uno_init(com=uno)
        wait: flt
            time in seconds to wait before collecting initialisation message.
        """

        self.mutex.lock()

        # Open serial port
        try:
            self.uno.open()
        except serial.SerialException:
            # If port was already open, we do not have to open it obviously.
            cf.log_message("Arduino port was already open")

        # Wait for a defined period of time
        time.sleep(wait)

        # Read serial port result
        cf.log_message(
            "Arduino serial port successfully initialised with "
            + str(self.uno.readall())
        )
        # self.queue.put(com.readall())
        self.serial_connection_open = True
        self.mutex.unlock()

    def close_serial_connection(self):
        """
        Close connection to arduino
        """
        self.mutex.lock()
        self.uno.close()
        self.serial_connection_open = False
        self.mutex.unlock()

    def trigger_relay(self, relay):
        """
        Open or close a relay via COM on an Arduino with a 8-Relays shield.

        relay: int
            If relay == [1-8], the according relay opens or closes
            If relay == 0, all relays close
            If relay == 9, all relays open
        """
        self.mutex.lock()
        com = self.uno

        if self.serial_connection_open == False:
            self.init_serial_connection()

        # If the number is in the range [0, 9] the command is correct
        if relay not in np.arange(0, 10, 1):
            cf.log_message("Unknown arduino serial communication command")
        else:
            try:
                com.write(str.encode(str(relay)))
            except serial.SerialException:
                cf.log_message(
                    "Serial connection not established. Please make sure to do so before attempting to trigger a relay."
                )

        cf.log_message(com.readall())
        self.mutex.unlock()

    def close(self):
        """
        Function that is called before program is closed to make sure that
        all relays are closed
        """
        self.mutex.lock()
        self.trigger_relay(0)
        time.sleep(1)
        self.close_serial_connection()
        self.mutex.unlock()


class KeithleySource:
    """
    Class that manages all functionality of our Keithley voltage/current source
    """

    def __init__(self, keithley_source_address, current_compliance):
        """
        Initialise Hardware. This function must be improved later as well.
        For the time being it is probably alright.
        """
        # Define a mutex
        self.mutex = QtCore.QMutex(QtCore.QMutex.Recursive)

        # Keithley Finding Device
        rm = pyvisa.ResourceManager()
        # The actual addresses for the Keithleys can be accessed via rm.list_resources()
        visa_resources = rm.list_resources()

        # Check if keithley source is present at the given address
        if keithley_source_address not in visa_resources:
            cf.log_message("The SourceMeter seems to be absent or switched off.")
            raise IOError("The SourceMeter seems to be absent or switched off.")

        self.keith = rm.open_resource(keithley_source_address)

        # As a standard initialise the Keithley as a voltage source
        self.as_voltage_source(current_compliance)

        # Set voltage mode indicator
        self.mode = "voltage"

    def as_voltage_source(self, current_compliance):
        """
        Function that initalises the Keithley as a voltage source
        """
        self.mutex.lock()
        # Write operational parameters to Sourcemeter (Voltage to OLED)
        self.reset()
        # set voltage as source
        self.keith.write("Source:Function Volt")
        # choose current for measuring
        self.keith.write('Sense:Function "Current"')
        # set compliance
        self.keith.write("Source:Volt:ILimit " + str(current_compliance))
        # reads back the set voltage
        self.keith.write("Source:Volt:READ:BACK ON")
        # sets the read-out speed and accuracy (0.01 fastest, 10 slowest but highest accuracy)
        self.keith.write("Current:NPLCycles 1")
        self.keith.write("Current:AZero OFF")  # turn off autozero
        self.keith.write("Source:Volt:Delay:AUTO OFF")  # turn off autodelay

        # Set voltage mode indicator
        self.mode = "voltage"
        self.mutex.unlock()

    def as_current_source(self, voltage_compliance):
        """
        Initialise (or reinitialise) class as current source
        """
        self.mutex.lock()
        # Write operational parameters to Sourcemeter (Voltage to OLED)
        self.reset()
        # Write operational parameters to Sourcemeter (Current to OLED)
        self.keith.write("Source:Function Current")  # set current as source

        self.keith.write('Sense:Function "Volt"')  # choose voltage for measuring
        self.keith.write(
            "Source:Current:VLimit " + str(voltage_compliance)
        )  # set voltage compliance to compliance
        self.keith.write(
            "Source:Current:READ:BACK OFF"
        )  # record preset source value instead of measuring it anew. NO CURRENT IS MEASURED!!! (Costs approx. 1.5 ms)
        self.keith.write("Volt:AZero OFF")  # turn off autozero
        self.keith.write("Source:Current:Delay:AUTO OFF")  # turn off autodelay

        # Set current mode indicator
        self.mode = "current"
        self.mutex.unlock()

    def reset(self):
        """
        reset instrument
        """
        self.mutex.lock()
        self.keith.write("*rst")
        self.mutex.unlock()

    def init_buffer(self, buffer_name, buffer_length):
        """
        Initialise buffer of source meter
        """
        self.mutex.lock()
        # if the buffer already exists, delete it first to prevent the error
        # "parameter error TRACe:MAKE cannot use an existing reading buffer name keithley"
        # try:
        # self.keith.write('TRACe:DELete "' + buffer_name + '"')
        # except:
        # cf.log_message("Buffer " + buffer_name + " does not exist yet")
        self.keith.write(
            'Trace:Make "' + buffer_name + '", ' + str(max(buffer_length, 10))
        )

        # Keithley empties the buffer
        self.keith.write("Trace:Clear " + '"' + buffer_name + '"')
        self.buffer_name = buffer_name
        self.mutex.unlock()

    def empty_buffer(self, buffer_name):
        """
        Function that empties the Keithley's buffer for the next run
        """
        self.mutex.lock()
        self.keith.write("Trace:Clear " + '"' + buffer_name + '"')
        self.mutex.unlock()

    def activate_output(self):
        """
        Activate output
        """
        self.mutex.lock()
        self.keith.write("Output ON")
        self.mutex.unlock()

    def deactivate_output(self):
        """
        Turn power off
        """
        self.mutex.lock()
        self.keith.write("Output OFF")
        self.mutex.unlock()

    def read_current(self):
        """
        Read current on Keithley source meter
        """
        return float(self.keith.query("MEASure:CURRent:DC?"))

    def read_voltage(self):
        """
        Read voltage on Keithley source meter
        """
        return float(self.keith.query("MEASure:VOLTage:DC?"))

    def read_buffer(self, buffer_name):
        return float(self.keith.query('Read? "' + buffer_name + '"')[:-1])

    def set_voltage(self, voltage):
        """
        Set the voltage on the source meter (only in voltage mode)
        """

        self.mutex.lock()
        if self.mode == "voltage":
            self.keith.write("Source:Volt " + str(voltage))
        else:
            logging.warning(
                "You can not set the voltage of the Keithley source in current mode"
            )
        self.mutex.unlock()

    def set_current(self, current):
        """
        Set the current on the source meter (only in current mode)
        """
        self.mutex.lock()
        # set current to source_value
        if self.mode == "current":
            self.keith.write("Source:Current " + str(current))
        else:
            logging.warning(
                "You can not set the current of the Keithley source in voltage mode"
            )
        self.mutex.unlock()


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
            cf.log_message("The Multimeter seems to be absent or switched off.")
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
        self.keithmulti.write("SENSe:VOLTage:DC:RANGe 10")
        # sets the voltage resolution
        self.keithmulti.query("VOLTage:DC:RESolution?")
        # sets the read-out speed and accuracy (0.01 fastest, 10 slowest but highest accuracy)
        self.keithmulti.write("VOLTage:NPLCycles 1")
        # sets the trigger to activate immediately after 'idle' -> 'wait-for-trigger'
        self.keithmulti.write("TRIGer:SOURce BUS")
        # sets the trigger to activate immediately after 'idle' -> 'wait-for-trigger'
        self.keithmulti.write("TRIGer:DELay 0")
        # Activate wait for trigger mode
        self.keithmulti.write("INITiate")
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
            return float(self.keithmulti.query("MEASure:VOLTage:DC?"))
        else:
            return float(
                self.keithmulti.query("MEASure:VOLTage:DC? " + str(multimeter_range))
            )


class OceanSpectrometer:
    """
    Class to deal with the ocean spectrometer
    """

    def __init__(self, non_linearity_correction):
        # Define a mutex
        self.mutex = QtCore.QMutex(QtCore.QMutex.NonRecursive)
        # List all spectrometers
        maya_devices = sb.list_devices()

        # Select our spectrometer (probably only in the list)
        self.spectrometer = sb.Spectrometer(maya_devices[0])

        # Set integration time of spectrometer, doesn't really matter since it is changed in the software on the fly anyways
        self.set_integration_time_ms(300)

        # Check if one shall correct for non-linearity
        self.non_linearity_correction = non_linearity_correction

    def measure(self):
        """
        Function to measure spectrum. The data structure might be already
        altered in this function (this I have to see on the hardware device)
        """
        self.mutex.lock()
        # The following yields lists of wavelength and intensity
        # wavelength = self.spec.wavelengths()
        # intensity = self.spec.intensities()
        data = self.spectrometer.spectrum(
            correct_nonlinearity=self.non_linearity_correction
        )

        self.mutex.unlock()
        time.sleep(1)

        return data

    def set_integration_time_ms(self, integration_time):
        """
        Function that allows the user to set the integration time even after
        initialisation of the spectrometer
        """
        # Integration time is a string when it is read from the global settings
        # file. To make sure that it is converted correctly, convert it first
        # to a float, multiply by 1000 to convert to us and then convert to int
        # as required by the api
        self.mutex.lock()
        self.integration_time = int(float(integration_time) * 1000)
        self.spectrometer.integration_time_micros(self.integration_time)
        cf.log_message(
            "Spectrometer integration time set to " + str(integration_time) + " ms"
        )
        self.mutex.unlock()

    def close_connection(self):
        """
        Closes connection to spectrometer
        """

        self.mutex.lock()
        self.spectrometer.close()
        self.mutex.unlock()


class ThorlabMotor:
    """
    Class to control the thorlab motors
    """

    def __init__(self, motor_number, offset_angle):
        # Define a mutex
        self.mutex = QtCore.QMutex(QtCore.QMutex.NonRecursive)

        # First cleanup before we can work with things (otherwise there might be
        # an open connection somewhere)
        self.clean_up()
        time.sleep(5)

        # from stage.motor_ini.core import find_stages

        # s = list(find_stages())
        # Set the motor to the number
        self.motor = apt.Motor(int(motor_number))
        time.sleep(1)
        # velocity MUST be set to avoid the motor moving slowly
        self.motor.set_velocity_parameters(0, 9, 10)
        # ensures that the motor homes properly - home in reverse with reverse lim switches
        self.motor.set_hardware_limit_switches(5, 5)
        self.motor.set_move_home_parameters(2, 1, 10, 3)
        # Move the motor home first, so that we can work with absolute positions
        # self.motor.move_home(True)

        self.offset_angle = offset_angle

    def move_to(self, angle, blocking=False):
        """
        Call the move_to function of the apt package
        """
        self.mutex.lock()

        # It seems like the "move_velocity" function of the thorlabs library is
        # dead. Therefore, the following is a workaround that always moves to
        # zero first in these cases (since the motor always # takes the shortest
        # route but we don't want to allow for full rotations)
        # if np.logical_or(
        #     (
        #         self.motor.position >= 270 + self.offset_angle
        #         or self.motor.position <= 90 + self.offset_angle
        #     )
        #     and angle < 0,
        #     (
        #         self.motor.position < 270 + self.offset_angle
        #         or self.motor.position > 90 + self.offset_angle
        #     )
        #     and angle > 0,
        # ):
        #     self.motor.move_to(0 + self.offset_angle, blocking=True)

        # # The motor does not always choose the closest way. If we want that, it must be calculated first
        # dict_direction = {"clockwise": 1, "counterclockwise": 2}
        # direction = 1

        # if angle < self.motor.position:
        #     direction = dict_direction["clockwise"]
        #     # self.motor.move_velocity(int(1))
        # elif angle > self.motor.position:
        #     direction = dict_direction["counterclockwise"]
        #     # self.motor.move_velocity(int(2))

        # # Ideally the motor shouldn't turn completely around not to break the
        # # cable (turn around at 180°)
        # # The numbers here result from the motor reading of the motor between 0
        # # and 360 degrees whereas we have a 45° offset due to our current setup
        # if (self.motor.position >= 270 + self.offset_angle or self.motor.position <= 90 + self.offset_angle) and angle < 0:
        #     # self.motor.move_velocity(int(1))
        #     direction = dict_direction["clockwise"]
        # elif (self.motor.position < 270 + self.offset_angle or self.motor.position > 90 + self.offset_angle) and angle > 0:
        #     # self.motor.move_velocity(int(2))
        #     direction = dict_direction["counterclockwise"]

        # self.motor.move_velocity(int(direction))

        self.motor.move_to(angle - float(self.offset_angle), blocking)
        self.mutex.unlock()

    def read_position(self):
        """
        Function that reads out the current motor position
        """
        self.mutex.lock()
        # Make sure that the motor position is returned as values between -180 to 180 (definition)
        if self.motor.position + float(self.offset_angle) > 180:
            motor_position_translated = (
                self.motor.position + float(self.offset_angle) - 360
            )
        else:
            motor_position_translated = self.motor.position + float(self.offset_angle)

        self.mutex.unlock()
        return motor_position_translated

    def clean_up(self):
        """
        This solution is a little bit hacky but works. This is copied code
        from the thorlabs_api repo and enables controlled cleaning up of the
        connection to the motor when the program is closed.
        """
        self.mutex.lock()
        import ctypes
        import os
        from thorlabs_apt import _APTAPI

        if os.name != "nt":
            raise Exception(
                "Your operating system is not supported. "
                "Thorlabs' APT API only works on Windows."
            )
        lib = None
        filename = ctypes.util.find_library("APT")
        if filename is not None:
            lib = ctypes.windll.LoadLibrary(filename)
        else:
            filename = "%s/APT.dll" % os.path.dirname(__file__)
            lib = ctypes.windll.LoadLibrary(filename)
            if lib is None:
                filename = "%s/APT.dll" % os.path.dirname(sys.argv[0])
                lib = ctypes.windll.LoadLibrary(lib)
                if lib is None:
                    raise Exception("Could not find shared library APT.dll.")
        _APTAPI.set_ctypes_argtypes(lib)
        err_code = lib.APTInit()
        if err_code != 0:
            raise Exception("Thorlabs APT Initialization failed.")
        if lib.EnableEventDlg(False) != 0:
            raise Exception("Couldn't disable event dialog.")

        if lib is not None:
            lib.APTCleanUp()
            lib.APTInit()
        self.mutex.unlock()
