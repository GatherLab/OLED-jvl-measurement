from PySide2 import QtCore

from hardware import ArduinoUno, KeithleySource, KeithleyMultimeter, OceanSpectrometer
from tests.tests import (
    MockArduinoUno,
    MockKeithleySource,
    MockKeithleyMultimeter,
    MockOceanSpectrometer,
)

import time


class SpectrumMeasurement(QtCore.QThread):
    """
    Class thread that handles the spectrum measurement
    """

    # Define costum signals
    # https://stackoverflow.com/questions/36434706/pyqt-proper-use-of-emit-and-pyqtsignal
    # With pyside2 https://wiki.qt.io/Qt_for_Python_Signals_and_Slots
    update_spectrum_signal = QtCore.Signal(list, list)

    def __init__(
        self, keithley_source_address, com2_address, integration_time, parent=None
    ):
        # Variable to kill thread
        self.is_killed = False

        # Initialise hardware
        self.uno = MockArduinoUno(com2_address)
        self.keithley_source = MockKeithleySource(keithley_source_address, 1.05)
        self.spectrometer = MockOceanSpectrometer(integration_time)

    def run(self):
        """
        Class that continuously measures the spectrum
        """
        while True:
            # Measure (data format is a list)
            wavelength, intensity = self.spectrometer.measure()
            self.update_spectrum_signal.emit(wavelength, intensity)
            time.sleep(0.1)

            if self.is_killed:
                self.quit()
                break

    def kill(self):
        """
        Kill this thread by stopping the loop
        """
        # Turn arduino relays off
        self.uno.open_relay(1, False)
        self.uno.close_serial_connection()

        # Turn keithley off
        self.keithley_source.deactivate_output()

        # Trigger interruption of run sequence
        self.is_killed = True
