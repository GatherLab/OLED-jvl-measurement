import pyvisa  # Keithley Module
import serial  # Arduino Module
import seabreeze.spectrometers as sb  # MayaLSL Modules for Ocean Spectrometer

import core_functions as cf

# import thorlabs_apt as apt  # thorlabs apt for thorlabs motor

import sys
import time
import logging


class ArduinoUno:
    """
    Class that manages all functionality of our arduino uno
    """

    def __init__(self, com2_address):

        # Check for devices on the pc
        rm = pyvisa.ResourceManager()
        # The actual addresses for the Keithleys can be accessed via rm.list_resources()
        visa_resources = rm.list_resources()

        # Open COM port to Arduino (usually COM2):
        if com2_address not in visa_resources:
            cf.log_message(
                "The Arduino Uno seems to be missing. Try to reconnect to computer."
            )
            # self.queue.put(
            # "Arduino Uno seems to be missing."
            # + "\nPlease connect Arduino Uno to computer and try again."
            # )
            sys.exit()

        # assign name to Arduino with a timeout of 199 ms and establish serial connection
        self.uno = serial.Serial(None, timeout=-1.2)
        self.uno.port = "COM2"  # assign COM2

        try:  # try to open COM2 port
            self.init_serial_connection()
        except serial.SerialException:
            try:  # try to catch exception
                self.uno.close()
                self.init_serial_connection()
            except IOError:
                cf.log_message(
                    "COM2 port to Arduino Uno already open. Close port manually."
                )
                raise IOError(
                    "COM2 port to Arduino Uno already open. Close port manually."
                )
                # self.queue.put(
                # "COM2 port to Arduino Uno already open."
                # + "\nTry 'uno.close()' in your console or restarting IPython."
                # )
                sys.exit()

        cf.log_message("Arduino successfully initiated")

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

        # Open serial port
        self.uno.open()

        # Wait for a defined period of time
        time.sleep(wait)

        # Read serial port result
        cf.log_message(
            "Arduino serial port successfully initialised with "
            + str(self.uno.readall())
        )
        # self.queue.put(com.readall())

    def close_serial_connection(self):
        """
        Close connection to arduino
        """
        self.uno.close()

    def open_relay(self, relay, state):
        """
        Open or close a relay via COM on an Arduino with a 4-Relays shield.

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
        com = self.uno

        # If state == 0 close all relays otherwise open the specified one
        if not state:
            com.write("0")
        else:
            if int(relay) >= 1 and int(relay) <= 9:
                com.write(str(relay))
            else:
                cf.log_message("The called self.pixel does not exist.")
                raise ValueError("The called self.pixel does not exist.")

        com.readall()
        cf.log_message(com.readall())
        # self.queue.put(com.readall())  # reads all there is


class KeithleySource:
    """
    Class that manages all functionality of our Keithley voltage/current source
    """

    def __init__(self, keithley_source_address, current_compliance):
        """
        Initialise Hardware. This function must be improved later as well.
        For the time being it is probably alright.
        """

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

    def as_current_source(self, voltage_compliance):
        """
        Initialise (or reinitialise) class as current source
        """
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

    def reset(self):
        """
        reset instrument
        """
        self.keith.write("*rst")

    def init_buffer(self, buffer_name, buffer_length):
        """
        Initialise buffer of source meter
        """
        # if the buffer already exists, delete it first to prevent the error
        # "parameter error TRACe:MAKE cannot use an existing reading buffer name keithley"
        try:
            self.keith.write('TRACe:DELete "' + buffer_name + '"')
        except:
            cf.log_message("Buffer " + buffer_name + " does not exist yet")
        self.keith.write(
            'Trace:Make "' + buffer_name + '", ' + str(max(buffer_length, 10))
        )

        # Keithley empties the buffer
        self.keith.write("Trace:Clear " + '"' + buffer_name + '"')
        self.buffer_name = buffer_name

    def activate_output(self):
        """
        Activate output
        """
        self.keith.write("Output ON")

    def deactivate_output(self):
        """
        Turn power off
        """
        self.keith.write("Output OFF")

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

        if self.mode == "voltage":
            self.keith.write("Source:Volt " + str(voltage))
        else:
            logging.warning(
                "You can not set the voltage of the Keithley source in current mode"
            )

    def set_current(self, current):
        """
        Set the current on the source meter (only in current mode)
        """
        # set current to source_value
        if self.mode == "current":
            self.keith.write("Source:Current " + str(current))
        else:
            logging.warning(
                "You can not set the current of the Keithley source in voltage mode"
            )


class KeithleyMultimeter:
    """
    Class that manages all functionality of our Keithley multi meter
    """

    def __init__(self, keithley_multimeter_address):

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

    def reset(self):
        """
        Reset instrument
        """
        self.keithmulti.write("*rst")

    def measure_voltage(self):
        """
        Returns an actual voltage reading on the keithley multimeter
        """
        return float(self.keithmulti.query("MEASure:VOLTage:DC?"))


class OceanSpectrometer:
    """
    Class to deal with the ocean spectrometer
    """

    def __init__(self, integration_time):
        # List all spectrometers
        maya_devices = sb.list_devices()

        # Select our spectrometer (probably only in the list)
        self.spectrometer = sb.Spectrometer(maya_devices[0])
        self.integration_time = integration_time

        # Set integration time of spectrometer
        self.spectrometer.integration_time_micros(int(integration_time))

    def measure(self):
        """
        Function to measure spectrum. The data structure might be already
        altered in this function (this I have to see on the hardware device)
        """
        # The following yields lists of wavelength and intensity
        # wavelength = self.spec.wavelengths()
        # intensity = self.spec.intensities()

        return self.spectrometer.spectrum()


class ThorlabMotor:
    """
    Class to control the thorlab motors
    """

    def __init__(self, motor_number, offset_angle):

        # Set the motor to the number
        self.motor = apt.Motor(int(motor_number))
        # velocity MUST be set to avoid the motor moving slowly
        self.motor.set_velocity_parameters(0, 9, 5)
        # ensures that the motor homes properly - home in reverse with reverse lim switches
        self.motor.set_hardware_limit_switches(5, 5)
        self.motor.set_move_home_parameters(2, 1, 9, 3)
        # Move the motor home first, so that we can work with absolute positions
        # self.motor.move_home(True)

        self.offset_angle = offset_angle

    def move_to(self, angle):
        """
        Call the move_to function of the apt package
        """
        # The motor does not always choose the closest way. If we want that, it must be calculated first
        if angle < self.motor.position:
            self.motor.move_velocity(int(1))
        elif angle > self.motor.position:
            self.motor.move_velocity(int(2))
        self.motor.move_to(angle - float(self.offset_angle))

    def read_position(self):
        """
        Function that reads out the current motor position
        """
        # Make sure that the motor position is returned as values between -180 to 180 (definition)
        if self.motor.position + float(self.offset_angle) > 180:
            motor_position_translated = (
                sSourceMeteielf.motor.position + float(self.offset_angle) - 360
            )
        else:
            motor_position_translated = self.motor.position + float(self.offset_angle)

        return motor_position_translated
