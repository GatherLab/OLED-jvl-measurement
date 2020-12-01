from PySide2 import QtCore

from hardware import ArduinoUno, KeithleySource, KeithleyMultimeter


class CurrentTester(QtCore.QThread):
    """
    QThread that shall do all the work for the current tester in the setup tab
    """

    def __init__(self, arduino_com_address, keithley_source_address):

        super(CurrentTester, self).__init__()

        # Initialise arduino and Keithley source and multimeter with the input addresses
        self.uno = ArduinoUno(arduino_com_address)
        self.keithley_source = KeithleySource(keithley_source_address, 1.05)
