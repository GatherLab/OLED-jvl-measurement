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
        self, com2_address, keithley_source_address, integration_time, parent=None
    ):
        super(SpectrumMeasurement, self).__init__()
        # Variable to kill thread
        self.is_killed = False
        self.integration_time = integration_time

        # Initialise hardware
        self.uno = MockArduinoUno(com2_address)
        self.keithley_source = MockKeithleySource(keithley_source_address, 1.05)
        self.spectrometer = MockOceanSpectrometer(integration_time)

        # Connect signal to the updater from the parent class
        self.update_spectrum_signal.connect(parent.update_spectrum)

    def run(self):
        """
        Class that continuously measures the spectrum
        """
        while True:
            # Measure (data format is a list)
            wavelength, intensity = self.spectrometer.measure()
            self.update_spectrum_signal.emit(wavelength, intensity)

            # The sleep time here is very important because if it is chosen to
            # short, the program may crash. Currently 1 s seems to be save (one can at least go down to 0.5s)
            time.sleep(1)

            if self.is_killed:
                # Close the connection to the spectrometer
                self.spectrometer.spectrometer.close()
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
