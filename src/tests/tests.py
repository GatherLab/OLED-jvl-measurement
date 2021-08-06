import psutil
import numpy as np


class MockArduinoUno:
    """
    Mock class for testing
    """

    def __init__(self, com2_address):
        print(com2_address)

    def close_serial_connection(self):
        print("serial connection closed")

    def trigger_relay(self, relay):
        print("relay " + str(relay) + " opened or closed")

    def init_serial_connection(self):
        print("Serial connection initiated")


class MockKeithleySource:
    """
    Mock class for testing
    """

    def __init__(self, keithley_source_address, current_compliance):
        print(keithley_source_address + str(current_compliance))

    def as_voltage_source(self, current_compliance):
        print("Keithley initialised as voltage source")

    def as_current_source(self, voltage_compliance):
        print("Keithley initialised as current source")

    def reset(self):
        print("Keithley source resetted")

    def init_buffer(self, buffer_name, buffer_length):
        print("Buffer written")

    def empty_buffer(self, buffer_name):
        print("MockKeithleySource buffer emptied")

    def activate_output(self):
        print("Output activated")

    def deactivate_output(self):
        print("output deactivated")

    def read_current(self):
        return float(psutil.cpu_percent() / 100)

    def read_voltage(self):
        return float(psutil.cpu_percent() / 100)

    def set_voltage(self, voltage):
        print("Voltage set to " + str(voltage))

    def set_current(self, current):
        print("Current set to " + str(current))


class MockKeithleyMultimeter:
    """
    Mock class for testing
    """

    def __init__(self, keithley_multimeter_address):
        print(keithley_multimeter_address)

    def reset(self):
        print("Multimeter resetted")

    def set_fixed_range(self, value):
        print("Fixed range set")

    def set_auto_range(self):
        print("Auto range set")

    def measure_voltage(self):
        print("Voltage read")
        return float(psutil.cpu_percent() / 100)


class MockOceanSpectrometer:
    """
    Mock class for testing
    """

    def __init__(self):
        print("Mock spectrometer initialized")

    def measure(self):
        return np.arange(350, 830, 1), np.random.rand(480) * 100

    def set_integration_time_ms(self, integration_time):
        print("Integration time set to " + str(integration_time) + " ms")


class MockThorlabMotor:
    """
    Mock class for testing
    """

    def __init__(self, motor_number, offset_angle):
        self.position = 0

    def move_to(self, angle):
        self.position = angle
        print("Moved to angle " + str(angle))

    def read_position(self):
        return float(self.position)
