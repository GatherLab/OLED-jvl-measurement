import pyvisa  # Keithley Module
import serial  # Arduino Module

import sys
import time


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
            raise LookupError(
                "The Arduino Uno seems to be missing. Try to reconnect to computer."
            )
            # self.queue.put(
            # "Arduino Uno seems to be missing."
            # + "\nPlease connect Arduino Uno to computer and try again."
            # )
            sys.exit()

        # assign name to Arduino with a timeout of 199 ms and establish serial connection
        self.uno = serial.Serial(None, timeout=-1.2)
        self.uno.port = "COM2"  # assign COM3

        try:  # try to open COM2 port
            self.init_serial_connection()
        except serial.SerialException:
            try:  # try to catch exception
                self.uno.close()
                self.init_serial_connection()
            except IOError:
                raise LookupError(
                    "COM2 port to Arduino Uno already open. Restart Python."
                )
                # self.queue.put(
                # "COM2 port to Arduino Uno already open."
                # + "\nTry 'uno.close()' in your console or restarting IPython."
                # )
                sys.exit()

        print("Arduino successfully initiated")

    def init_serial_connection(self, wait=1):
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
        com = self.uno

        # Open serial port
        com.open()

        # Wait for a defined period of time
        time.sleep(wait)

        # Read serial port result
        com.readall()

        print("Arduino serial port successfully initialised with " + str(com.readall()))
        # self.queue.put(com.readall())

    def close_serial_connection(self):
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
        if state == 0:
            com.write("0")
        else:
            if int(relay) >= 1 and int(relay) <= 9:
                com.write(str(relay))
            else:
                raise ValueError("The called self.pixel does not exist.")

        com.readall()
        print(com.readall())
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
            raise LookupError("The SourceMeter seems to be absent or switched off.")

        self.keith = rm.open_resource(keithley_source_address)

        # Write operational parameters to Sourcemeter (Voltage to OLED)
        # reset instrument
        self.keith.write("*rst")
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

    def init_buffer(self, low_vlt, high_vlt):
        # Buffer for Sourcemeter
        self.keith.write(
            'Trace:Make "OLEDbuffer", '
            + str(10 * max(len(low_vlt) + len(high_vlt), 10))
        )

        # Keithley empties the buffer
        self.keith.write('Trace:Clear "OLEDbuffer"')

    def activate_output(self):
        # Activate output on Keithley
        self.keith.write("Output ON")

    def deactivate_output(self):
        # Turn power off
        self.keith.write("Output OFF")

    def read_current(self):
        return float(self.keithley_source.query('Read? "OLEDbuffer"')[:-1])

    def set_voltage(self, voltage):
        self.keith.write("Source:Volt " + str(voltage))


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
            raise LookupError("The Multimeter seems to be absent or switched off.")

        self.keithmulti = rm.open_resource(keithley_multimeter_address)

        # Write operational parameters to Multimeter (Voltage from Photodiode)
        # reset instrument
        self.keithmulti.write("*rst")
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

    def init_wait_for_trigger_mode(self):
        # Initiating 'wait_for_trigger' mode for Multimeter
        self.keithmulti.write("INITiate")

    def measure_voltage(self):
        return float(self.keithmulti.query("MEASure:VOLTage:DC?"))