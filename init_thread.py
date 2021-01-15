from PySide2 import QtCore
import core_functions as cf
import time

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


class InitThread(QtCore.QThread):
    """
    Worker thread that is only meant to do the initialisation, before the program is started
    """

    update_loading_dialog = QtCore.Signal(int, str)
    kill_dialog = QtCore.Signal()
    ask_retry = QtCore.Signal()
    emit_arduino = QtCore.Signal(ArduinoUno)
    emit_motor = QtCore.Signal(ThorlabMotor)
    emit_source = QtCore.Signal(KeithleySource)
    emit_multimeter = QtCore.Signal(KeithleyMultimeter)
    emit_spectrometer = QtCore.Signal(OceanSpectrometer)

    def __init__(self, widget=None):
        super(InitThread, self).__init__()

        # Connect signals
        self.update_loading_dialog.connect(widget.update_loading_dialog)
        self.kill_dialog.connect(widget.kill_dialog)
        self.ask_retry.connect(widget.ask_retry)
        self.emit_arduino.connect(widget.parent.init_arduino)
        self.emit_motor.connect(widget.parent.init_motor)
        self.emit_source.connect(widget.parent.init_source)
        self.emit_multimeter.connect(widget.parent.init_multimeter)
        self.emit_spectrometer.connect(widget.parent.init_spectrometer)

        # Variable that checks if initialisation shall be repeated
        self.repeat = False

    def run(self):
        """
        Function that initialises the parameters before the main program is called
        """
        # self.update_loading_dialog.emit("Test")
        # Read global settings first (what if they are not correct yet?)

        self.update_loading_dialog.emit(0, "Initialising Arduino Connection")
        global_settings = cf.read_global_settings()

        # Try if Arduino can be initialised
        try:
            uno = ArduinoUno(global_settings["arduino_com_address"])
            cf.log_message("Arduino UNO successfully initialised")
            arduino_init = True
            # motor.move_to(-45)
        except:
            uno = MockArduinoUno(global_settings["arduino_com_address"])
            cf.log_message(
                "Arduino UNO could not be initialised. Please reconnect the device or check its com number in the global settings."
            )
            arduino_init = False

        self.emit_arduino.emit(uno)

        time.sleep(0.5)

        self.update_loading_dialog.emit(20, "Initialising Motor")

        # Try if motor can be easily initialised
        try:
            motor = ThorlabMotor(
                global_settings["motor_number"], global_settings["motor_offset"]
            )
            motor.motor.move_home(True)
            cf.log_message("Motor successfully initialised")
            motor_init = True
            # motor.move_to(-45)
        except:
            motor = MockThorlabMotor(
                global_settings["motor_number"], global_settings["motor_offset"]
            )
            cf.log_message(
                "Motor could not be initialised! Please reconnect the device and check the serial number in the settings file!"
            )
            motor_init = False

        self.emit_motor.emit(motor)

        time.sleep(0.5)

        self.update_loading_dialog.emit(40, "Setting up Spectrometer")

        # Try if the spectrometer is present
        try:
            spectrometer = OceanSpectrometer(
                global_settings["spectrum_integration_time"]
            )
            cf.log_message("Spectrometer successfully initialised")
            spectrometer_init = True
        except:
            spectrometer = MockOceanSpectrometer(
                global_settings["spectrum_integration_time"]
            )
            cf.log_message(
                "The spectrometer could not be initialised! Please reconnect the device!"
            )
            spectrometer_init = False

        self.emit_spectrometer.emit(spectrometer)

        time.sleep(0.5)
        self.update_loading_dialog.emit(60, "Checking for Keithley source")

        # Check if Keithley source is on and can be used
        try:
            keithley_source = KeithleySource(
                global_settings["keithley_source_address"],
                1.05,
            )
            cf.log_message("Keithley SourceMeter successfully initialised")
            keithley_source_init = True
        except:
            keithley_source = MockKeithleySource(
                global_settings["keithley_source_address"],
                1.05,
            )
            cf.log_message(
                "The Keithley SourceMeter could not be initialised! Please reconnect the device and check the serial number in the settings file!"
            )
            keithley_source_init = False

        self.emit_source.emit(keithley_source)

        time.sleep(0.5)
        self.update_loading_dialog.emit(80, "Checking for Keithley multimeter")

        # Check if Keithley multimeter is present
        try:
            keithley_multimeter = KeithleyMultimeter(
                global_settings["keithley_multimeter_address"]
            )
            cf.log_message("Keithley Multimeter successfully initialised")
            keithley_multimeter_init = True
        except:
            keithley_multimeter = MockKeithleyMultimeter(
                global_settings["keithley_multimeter_address"]
            )
            cf.log_message(
                "The Keithley Multimeter could not be initialised! Please reconnect the device and check the serial number in the settings file!"
            )
            keithley_multimeter_init = False

        time.sleep(0.5)
        self.emit_multimeter.emit(keithley_multimeter)

        # If one of the devices could not be initialised for whatever reason,
        # ask the user if she wants to retry after reconnecting the devices or
        # continue without some of the devices
        if (
            arduino_init == False
            or motor_init == False
            or spectrometer_init == False
            or keithley_source_init == False
            or keithley_multimeter_init == False
        ):
            self.update_loading_dialog.emit(
                100,
                "Some of the devices could not be initialised.",
            )
            self.ask_retry.emit()

        else:
            self.update_loading_dialog.emit(100, "One more moment")
            time.sleep(0.5)
            self.kill_dialog.emit()
