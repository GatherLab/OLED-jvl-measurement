# -*- coding: utf-8 -*-

from PySide2 import QtCore, QtWidgets

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
import core_functions as cf

import time
import numpy as np
import pandas as pd
import datetime as dt


class GoniometerMeasurement(QtCore.QThread):
    """
    Thread class to do the goniometer measurement
    """

    update_goniometer_spectrum_signal = QtCore.Signal(list, list)
    update_animation = QtCore.Signal(float)
    update_progress_bar = QtCore.Signal(str, float)
    hide_progress_bar = QtCore.Signal()
    pause_thread_pl = QtCore.Signal()
    reset_start_button = QtCore.Signal(bool)

    def __init__(
        self,
        keithley_source,
        keithley_multimeter,
        arduino_uno,
        motor,
        spectrometer,
        pixel,
        goniometer_measurement_parameters,
        autotube_measurement_parameters,
        setup_parameters,
        parent=None,
    ):
        super(GoniometerMeasurement, self).__init__()

        # Initialise member variables
        self.goniometer_measurement_parameters = goniometer_measurement_parameters
        self.autotube_measurement_parameters = autotube_measurement_parameters
        self.setup_parameters = setup_parameters

        self.pixel = pixel
        self.parent = parent

        # Initialise hardware
        self.spectrometer = spectrometer
        self.motor = motor

        self.uno = arduino_uno
        self.keithley_source = keithley_source
        self.keithley_source.as_voltage_source(
            autotube_measurement_parameters["scan_compliance"]
        )
        self.keithley_multimeter = keithley_multimeter
        self.keithley_multimeter.reset()

        # Connect signal to the updater from the parent class
        self.update_goniometer_spectrum_signal.connect(
            parent.update_goniometer_spectrum
        )
        self.update_animation.connect(parent.gw_animation.move)
        self.update_progress_bar.connect(parent.progressBar.setProperty)
        self.hide_progress_bar.connect(parent.progressBar.hide)
        self.pause_thread_pl.connect(parent.pause_goniometer_measurement)
        self.reset_start_button.connect(
            parent.gw_start_measurement_pushButton.setChecked
        )

        # Declare the data structures that are used in the goniometer measurement
        self.iv_data = pd.DataFrame()
        self.spectrum_data = pd.DataFrame()
        self.specific_oled_voltage = 0
        self.specific_oled_current = 0
        self.specific_pd_voltage = 0

        # Introduce a pause variable
        self.pause = "False"

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
        time.sleep(self.goniometer_measurement_parameters["homing_time"])
        cf.log_message("Moved to home position")

        # The following is only needed for EL measurement
        if not self.goniometer_measurement_parameters["el_or_pl"]:
            if self.goniometer_measurement_parameters["voltage_scan"]:
                autotube_measurement = AutotubeMeasurement(
                    self.keithley_source,
                    self.keithley_multimeter,
                    self.uno,
                    self.autotube_measurement_parameters,
                    self.setup_parameters,
                    self.pixel,
                    devices_already_initialised=True,
                    parent=self.parent,
                )

                # Here the thread is not started as a thread but only the class
                # function is called, because the goniometer thread should wait
                # for the autotube thread to be finished
                autotube_measurement.run()

            # Take background voltage and measure specific current and voltage of photodiode and oled
            background_diode_voltage = self.keithley_multimeter.measure_voltage()

            # Depending on if the user selected constant current or constant
            # voltage it is selected in the following what the Keithley source
            # should be
            if not self.goniometer_measurement_parameters["voltage_or_current"]:
                self.keithley_source.as_voltage_source(
                    self.goniometer_measurement_parameters["vc_compliance"]
                )
                self.keithley_source.set_voltage(
                    self.goniometer_measurement_parameters["vc_value"]
                )
                cf.log_message("Keithley source initialised as voltage source")
            else:
                self.keithley_source.as_current_source(
                    self.goniometer_measurement_parameters["vc_compliance"]
                )
                self.keithley_source.set_current(
                    self.goniometer_measurement_parameters["vc_value"]
                )
                cf.log_message("Keithley source initialised as current source")

            self.keithley_source.init_buffer("pulsebuffer", buffer_length=1000)

            # Now activate the output to measure the specific voltages/current
            self.uno.open_relay(relay=self.pixel[0], state=1)
            self.keithley_source.activate_output()

            self.specific_pd_voltage = (
                self.keithley_multimeter.measure_voltage() - background_diode_voltage
            )
            self.specific_oled_current = self.keithley_source.read_current()
            self.specific_oled_voltage = self.keithley_source.read_voltage()

            # Deactivate output
            self.keithley_source.deactivate_output()
            self.uno.open_relay(relay=self.pixel[0], state=0)

            cf.log_message("Specific voltages measured")

        # PL from here on
        self.motor.move_to(self.goniometer_measurement_parameters["minimum_angle"])
        self.update_animation.emit(
            self.goniometer_measurement_parameters["minimum_angle"]
        )

        cf.log_message(
            "Motor moved to minimum angle: "
            + str(self.goniometer_measurement_parameters["minimum_angle"])
            + " °"
        )
        time.sleep(self.goniometer_measurement_parameters["homing_time"])

        # Take calibration readings
        calibration_spectrum = self.spectrometer.measure()
        self.spectrum_data["wavelength"] = calibration_spectrum[0]
        self.spectrum_data["background"] = calibration_spectrum[1]
        cf.log_message("Calibration spectrum measured")

        # Initial processing time in seconds
        # I am not quite sure why this is done and if there is no better way of doing it
        processing_time = 0.5

        # Empty list, stores the data as multiple dicts to later generate a pd dataframe
        rows_list = []

        progress = 0

        # If el measurement was selected, activate the selected pixel already
        if not self.goniometer_measurement_parameters["el_or_pl"]:
            self.uno.open_relay(relay=self.pixel[0], state=1)
        else:
            # Check first if user already aborted the measurement
            if self.pause == "return":
                cf.log_message("Goniometer measurement aborted")
                self.hide_progress_bar.emit()
                self.reset_start_button.emit(False)
                return

            # If not, in the case of PL open up a pop-up window that the UV lamp can
            # now be turned on, only continue if the continue button was
            # pressed
            self.pause = "True"
            self.pause_thread_pl.emit()

            while self.pause == "True":
                time.sleep(0.1)
                if self.pause == "break":
                    break
                elif self.pause == "return":
                    return

        # Move motor by given increment while giving current to OLED and reading spectrum
        for angle in np.arange(
            self.goniometer_measurement_parameters["minimum_angle"],
            self.goniometer_measurement_parameters["maximum_angle"] + 1,
            self.goniometer_measurement_parameters["step_angle"],
        ):

            # This is checked in each iteration so that the user can interrupt
            # the measurement after each iterration by simply pressing the
            # pushButton again
            if self.pause == "return":
                cf.log_message(
                    "Goniometer measurement aborted at angle " + str(angle) + "°"
                )
                self.hide_progress_bar.emit()
                self.reset_start_button.emit(False)
                return

            self.motor.move_to(angle)
            # self.parent.gw_animation.move(angle)
            self.update_animation.emit(angle)
            time.sleep(self.goniometer_measurement_parameters["moving_time"])
            cf.log_message("Moved to angle " + str(angle) + " °")

            # Only activate output for EL measurement
            if not self.goniometer_measurement_parameters["el_or_pl"]:
                self.keithley_source.activate_output()

            time.sleep(
                self.goniometer_measurement_parameters["pulse_duration"]
                - processing_time
            )

            start_process = time.process_time()

            # These measurements are only taken for el measurements
            if not self.goniometer_measurement_parameters["el_or_pl"]:
                temp_buffer = self.keithley_source.read_current()

                # In the case of a voltage scan
                if self.goniometer_measurement_parameters["voltage_or_current"]:
                    data_dict = {
                        "angle": angle,
                        "voltage": temp_buffer,
                        "current": self.goniometer_measurement_parameters["vc_value"],
                    }
                else:
                    data_dict = {
                        "angle": angle,
                        "voltage": self.goniometer_measurement_parameters["vc_value"],
                        "current": temp_buffer,
                    }

                rows_list.append(data_dict)

            # Now measure spectrum (wavelength and intensity) (done for EL and pl)
            self.spectrum_data[str(angle)] = self.spectrometer.measure()[1]

            # Emit a signal to update the plot (unfortunately with python 3.9
            # or windows one can not emit pandas dataframes. Therefore, it has
            # to be converted to a list.)
            self.update_goniometer_spectrum_signal.emit(
                self.spectrum_data.columns.values.tolist(),
                self.spectrum_data.values.tolist(),
            )

            # Only deactivate output for el (otherwise it was never activated)
            if not self.goniometer_measurement_parameters["el_or_pl"]:
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

        cf.log_message("Measurement finished")

        if not self.goniometer_measurement_parameters["el_or_pl"]:
            # Close relay and serial connection as well
            self.uno.open_relay(relay=self.pixel[0], state=0)
            self.uno.close_serial_connection()  # close COM port

            # Only save iv data for el measurement, because it otherwise does not exist
            self.iv_data = pd.DataFrame(rows_list)
            self.save_iv_data()

        self.save_spectrum_data()
        self.hide_progress_bar.emit()
        self.reset_start_button.emit(False)

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

        file_path = (
            self.setup_parameters["folder_path"]
            + dt.date.today().strftime("%Y-%m-%d_")
            + self.setup_parameters["batch_name"]
            + "_d"
            + str(self.setup_parameters["device_number"])
            + "_p"
            + str(self.pixel[0])
            + "_gon-jvl"
            + ".csv"
        )
        # Write header lines to file
        with open(file_path, "a") as the_file:
            the_file.write("\n".join(header_lines))

        # Now write pandas dataframe to file
        self.iv_data.to_csv(
            file_path,
            index=False,
            mode="a",
            header=False,
            sep="\t",
        )
        cf.log_message("IV data saved")

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
        line03 = "### Measurement data ###\n"

        header_lines = [
            line01,
            line02,
            line03,
        ]

        file_path = (
            self.setup_parameters["folder_path"]
            + dt.date.today().strftime("%Y-%m-%d_")
            + self.setup_parameters["batch_name"]
            + "_d"
            + str(self.setup_parameters["device_number"])
            + "_p"
            + str(self.pixel[0])
            + "_gon-spec"
            + ".csv"
        )
        # Write header lines to file
        with open(file_path, "a") as the_file:
            the_file.write("\n".join(header_lines))

        # Now write pandas dataframe to file with header names
        self.spectrum_data.to_csv(
            file_path,
            index=False,
            mode="a",
            header=True,
            sep="\t",
        )

        cf.log_message("Spectral data saved")
