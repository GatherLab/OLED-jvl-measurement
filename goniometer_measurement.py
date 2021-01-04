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

    update_goniometer_spectrum_signal = QtCore.Signal(list, list)
    update_log_message = QtCore.Signal(str)
    update_animation = QtCore.Signal(float)
    update_progress_bar = QtCore.Signal(str, float)
    hide_progress_bar = QtCore.Signal()

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

        # Connect signal to the updater from the parent class
        self.update_goniometer_spectrum_signal.connect(
            parent.update_goniometer_spectrum
        )
        self.update_log_message.connect(parent.log_message)
        self.update_animation.connect(parent.gw_animation.move)
        self.update_progress_bar.connect(parent.progressBar.setProperty)
        self.hide_progress_bar.connect(parent.progressBar.hide)

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
        # Move to initial position which is the offset position
        self.motor.move_to(0)
        # self.parent.gw_animation.move(0)
        self.update_animation.emit(0)
        self.update_log_message.emit("Moved to home position")
        time.sleep(self.goniometer_measurement_parameters["homing_time"])

        if self.goniometer_measurement_parameters["voltage_scan"]:
            autotube_measurement = AutotubeMeasurement(
                self.keithley_source_address,
                self.keithley_multimeter_address,
                self.com2_address,
                self.autotube_measurement_parameters,
                self.pixel,
                self.folder_path + "voltage_scan.csv",
            )
            autotube_measurement.run()
            autotube_measurement.save_data()

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
        self.update_log_message.emit("Specific voltages measured")
        # Depending on if the user selected constant current or constant
        # voltage it is selected in the following what the Keithley source
        # should be
        if self.goniometer_measurement_parameters["voltage_or_current"]:
            self.keithley_source.as_voltage_source(
                self.goniometer_measurement_parameters["vc_compliance"]
            )
            self.update_log_message.emit(
                "Keithley source initialised as voltage source"
            )
        else:
            self.keithley_source.as_current_source(
                self.goniometer_measurement_parameters["vc_compliance"]
            )
            self.update_log_message.emit(
                "Keithley source initialised as current source"
            )

        self.keithley_source.init_buffer("pulsebuffer", buffer_length=1000)

        self.motor.move_to(self.goniometer_measurement_parameters["minimum_angle"])
        self.update_animation.emit(
            self.goniometer_measurement_parameters["minimum_angle"]
        )

        self.update_log_message.emit(
            "Motor moved to minimum angle: "
            + str(self.goniometer_measurement_parameters["minimum_angle"])
            + " °"
        )
        time.sleep(self.goniometer_measurement_parameters["homing_time"])

        # Take calibration readings
        calibration_spectrum = self.spectrometer.measure()
        self.spectrum_data["wavelength"] = calibration_spectrum[0]
        self.spectrum_data["background"] = calibration_spectrum[1]
        self.update_log_message.emit("Calibration spectrum measured")
      
        # Initial processing time in seconds
        # I am not quite sure why this is done and if there is no better way of doing it
        processing_time = 0.5

        # Empty list, stores the data as multiple dicts to later generate a pd dataframe
        rows_list = []

        progress = 0


        # Move motor by given increment while giving current to OLED and reading spectrum
        for angle in np.arange(
            self.goniometer_measurement_parameters["minimum_angle"],
            self.goniometer_measurement_parameters["maximum_angle"] + 1,
            self.goniometer_measurement_parameters["step_angle"],
        ):

            self.motor.move_to(angle)
            # self.parent.gw_animation.move(angle)
            self.update_animation.emit(angle)
            self.update_log_message.emit("Moved to angle " + str(angle) + " °")
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

            # In the case of a voltage scan
            if self.goniometer_measurement_parameters["voltage_or_current"]:
                data_dict = {
                    "angle": angle,
                    "voltage": temp_buffer,
                    "current": self.goniometer_measurement_parameters["vc_value"],
                }
"
            else:
                data_dict = {
                    "angle": angle,
                    "voltage": self.goniometer_measurement_parameters["vc_value"],
                    "current": temp_buffer,
                }


            rows_list.append(data_dict)

            # Now measure spectrum (wavelength and intensity)
            self.spectrum_data[str(angle)] = self.spectrometer.measure()[1]

            # Emit a signal to update the plot (unfortunately with python 3.9
            # or windows one can not emit pandas dataframes. Therefore, it has
            # to be converted to a list.)
            self.update_goniometer_spectrum_signal.emit(
                self.spectrum_data.columns.values.tolist(),
                self.spectrum_data.values.tolist(),
            )
     
            self.keithley_source.deactivate_output()

            # Calculate the processing time it took
            end_process = time.process_time()
            processing_time = end_process - start_process

            progress += 1
            self.update_progress_bar.emit(
                "value",
                progress
                / np.size(
                    np.arange(
                        self.goniometer_measurement_parameters["minimum_angle"],
                        self.goniometer_measurement_parameters["maximum_angle"] + 1,
                        self.goniometer_measurement_parameters["step_angle"],
                    )
                )
                * 100,
            )

        self.iv_data = pd.DataFrame(rows_list)
        self.update_log_message.emit("Measurement finished")

        self.save_iv_data()
        self.save_spectrum_data()
        self.hide_progress_bar.emit()

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
        self.update_log_message.emit("IV data saved")

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

        self.update_log_message.emit("Spectral data saved")
