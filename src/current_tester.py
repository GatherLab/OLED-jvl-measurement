from PySide2 import QtCore

from hardware import ArduinoUno, KeithleySource, KeithleyMultimeter

from tests.tests import MockArduinoUno, MockKeithleySource, MockKeithleyMultimeter

# for testing reasons
import time


class CurrentTester(QtCore.QThread):
    """
    QThread that shall do all the work for the current tester in the setup tab.
    It is mainly needed for updating the current reading. However, I figure
    at the moment, that it is probably also good to have the other current
    tester functionalities in this class. Mainly because it does not make
    sense to return a current reading while the keithley has to be resetted,
    for instance. So it is not only okay but kind of demanded to have this in
    a single thread.
    """

    # Define costum signals
    # https://stackoverflow.com/questions/36434706/pyqt-proper-use-of-emit-and-pyqtsignal
    # With pyside2 https://wiki.qt.io/Qt_for_Python_Signals_and_Slots
    update_ammeter_signal = QtCore.Signal(float)

    def __init__(
        self,
        arduino,
        keithley_source,
        parent=None,
    ):

        super(CurrentTester, self).__init__()

        self.is_killed = False

        # Reset Arduino and Keithley
        self.uno = arduino
        self.keithley_source = keithley_source
        self.keithley_source.as_voltage_source(1.05)
        self.keithley_source.activate_output()

        # Connect signal to the updater from the parent class
        self.update_ammeter_signal.connect(parent.update_ammeter)

    def run(self):
        """
        Class that continuously reads the current on the Keithley source and
        communicates with the main class. It has to be kept in separate
        classes to allow for threading. It is started with the .start()
        method from the QThread class
        """
        import pydevd

        pydevd.settrace(suspend=False)

        while True:
            current_reading = self.keithley_source.read_current()
            self.update_ammeter_signal.emit(current_reading)
            time.sleep(0.5)

            if self.is_killed:
                self.quit()
                break

    def kill(self):
        """
        Kill this thread by stopping the loop
        """
        # Turn arduino relays off
        self.uno.trigger_relay(0)
        self.uno.close_serial_connection()

        # Turn keithley off
        self.keithley_source.deactivate_output()

        # Trigger interruption of run sequence
        self.is_killed = True

    # def toggle_pixel(self, pixel, on_off):
    #     """
    #     This function really only mimics the uno function but is necessary
    #     for the current class nesting
    #     """
    #     # self.uno.open_relay(relay=pixel, state=on_off)
    #     print("Pixel toggled")

    # def set_voltage(self, voltage):
    #     """
    #     Mimics the set_voltage function of the
    #     """
