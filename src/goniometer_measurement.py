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
import math


class GoniometerMeasurement(QtCore.QThread):
    """
    Thread class to do the goniometer measurement
    """

    update_goniometer_spectrum_signal = QtCore.Signal(list, list)
    update_simple_spectrum_signal = QtCore.Signal(list, list)
    # update_animation = QtCore.Signal(float)
    update_progress_bar = QtCore.Signal(str, float)
    hide_progress_bar = QtCore.Signal()
    pause_thread_pl = QtCore.Signal(str)
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
        self.spectrometer.set_integration_time_ms(
            self.goniometer_measurement_parameters["integration_time"]
        )
        self.motor = motor

        self.uno = arduino_uno
        self.uno.init_serial_connection()
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
        self.update_simple_spectrum_signal.connect(
            parent.update_goniometer_simple_spectrum
        )
        # self.update_animation.connect(parent.gw_animation.move)
        self.update_progress_bar.connect(parent.progressBar.setProperty)
        self.hide_progress_bar.connect(parent.progressBar.hide)
        self.pause_thread_pl.connect(parent.pause_goniometer_measurement)
        self.reset_start_button.connect(
            parent.gw_start_measurement_pushButton.setChecked
        )

        # Declare the data structures that are used in the goniometer measurement
        self.iv_data = pd.DataFrame()
        self.spectrum_data = pd.DataFrame()
        # self.specific_oled_voltage = 0
        # self.specific_oled_current = 0
        # self.specific_pd_voltage = 0

        # Introduce a pause variable
        self.pause = "False"

        self.pl_elapsed_time = 0
        self.total_oled_on_time = 0

    def run(self):
        """
        Function that runs when the thread is started. It contains the
        measurement routine that is triggered when the measure button is
        pressed
        """

        import pydevd

        pydevd.settrace(suspend=False)

        # The following is only needed for EL measurement
        if not self.goniometer_measurement_parameters["el_or_pl"]:
            if self.goniometer_measurement_parameters["voltage_scan"]:
                # Move to initial position which is the offset position
                if self.setup_parameters["top_emitting"]:
                    pd_position = -90
                else:
                    pd_position = 90

                self.motor.move_to(pd_position)

                # Wait until the motor move is finished
                while not self.parent.motor_run.isFinished():
                    time.sleep(0.1)

                # # Instead of defining a homeing time, just read the motor position and
                # # only start the measurement when the motor is at the right position
                # motor_position = self.motor.read_position()

                # while not math.isclose(motor_position, 0, abs_tol=0.01):
                #     motor_position = self.motor.read_position()
                #     self.update_animation.emit(motor_position)
                #     time.sleep(0.05)

                # # Update animation once more since the position might be 0.9 at this
                # # point (int comparison in the above while loop)
                # self.update_animation.emit(motor_position)

                # Wait one additional second (not really needed but only to be on the
                # save side)
                time.sleep(1)

                # time.sleep(self.goniometer_measurement_parameters["homing_time"])
                cf.log_message("Moved to PD position")

                multimeter_latency = cf.read_global_settings()["multimeter_latency"]

                autotube_measurement = AutotubeMeasurement(
                    self.keithley_source,
                    self.keithley_multimeter,
                    self.uno,
                    self.autotube_measurement_parameters,
                    self.setup_parameters,
                    multimeter_latency,
                    self.pixel,
                    parent=self.parent,
                )

                # Here the thread is not started as a thread but only the class
                # function is called, because the goniometer thread should wait
                # for the autotube thread to be finished
                autotube_measurement.run()

            # # Take background voltage and measure specific current and voltage of photodiode and oled
            # background_diode_voltage = self.keithley_multimeter.measure_voltage()

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

            # self.keithley_source.init_buffer("pulsebuffer", buffer_length=1000)

            # # Now activate the output to measure the specific voltages/current
            # self.uno.trigger_relay(self.pixel[0])
            # oled_on_time_start = time.time()
            # self.keithley_source.activate_output()

            # self.specific_pd_voltage = (
            #     self.keithley_multimeter.measure_voltage() - background_diode_voltage
            # )
            # self.specific_oled_current = self.keithley_source.read_current()
            # self.specific_oled_voltage = self.keithley_source.read_voltage()

            # # Deactivate output
            # self.keithley_source.deactivate_output()
            # self.uno.trigger_relay(0)
            # self.total_oled_on_time += time.time() - oled_on_time_start

            # cf.log_message("Specific voltages measured")

            # time.sleep(0.5)

        # Take calibration readings
        calibration_spectrum = self.spectrometer.measure()
        self.spectrum_data["wavelength"] = calibration_spectrum[0]
        self.spectrum_data["background"] = calibration_spectrum[1]

        self.update_simple_spectrum_signal.emit(
            [
                calibration_spectrum[0],
                calibration_spectrum[1],
            ],
            ["background"],
        )
        cf.log_message("Calibration spectrum measured")

        # If el measurement was selected, activate the selected pixel already
        if not self.goniometer_measurement_parameters["el_or_pl"]:
            self.keithley_source.activate_output()

        # Let user turn on the lamp
        if self.goniometer_measurement_parameters["el_or_pl"]:
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
            self.pause_thread_pl.emit("on")

            while self.pause == "True":
                time.sleep(0.1)
                if self.pause == "break":
                    # Take the time at the beginning to measure the length of the entire
                    # measurement
                    absolute_starting_time = time.time()
                    break
                elif self.pause == "return":
                    return

        # If selected by the user, do a first measurement for the degradation check at zero angle.
        if self.goniometer_measurement_parameters["degradation_check"]:
            self.motor.move_to(0)

            # Wait until the motor move is finished
            while not self.parent.motor_run.isFinished():
                time.sleep(0.1)

            # Only activate output for el
            if not self.goniometer_measurement_parameters["el_or_pl"]:
                self.uno.trigger_relay(self.pixel[0])
                oled_on_time_start = time.time()

            # This here is temporarily saved in another variable to not distort
            # the dataframe column order
            degradation_data_before = self.spectrometer.measure()[1]

            # Only deactivate output for el (otherwise it was never activated)
            if not self.goniometer_measurement_parameters["el_or_pl"]:
                # self.keithley_source.deactivate_output()
                self.uno.trigger_relay(self.pixel[0])
                self.total_oled_on_time += time.time() - oled_on_time_start

        # PL from here on
        self.motor.move_to(self.goniometer_measurement_parameters["minimum_angle"])

        # Wait until the motor move is finished
        while not self.parent.motor_run.isFinished():
            time.sleep(0.1)

        # Instead of defining a homeing time, just read the motor position and
        # only start the measurement when the motor is at the right position
        # motor_position = self.motor.read_position()

        # while not math.isclose(
        #     motor_position,
        #     self.goniometer_measurement_parameters["minimum_angle"],
        #     abs_tol=0.01,
        # ):
        #     motor_position = self.motor.read_position()
        #     self.update_animation.emit(motor_position)
        #     time.sleep(0.05)

        # Update animation once more since the position might be 0.9 at this
        # point (int comparison in the above while loop)
        # self.update_animation.emit(motor_position)

        # cf.log_message(
        # "Motor moved to minimum angle: "
        # + str(self.goniometer_measurement_parameters["minimum_angle"])
        # + " °"
        # )
        # time.sleep(self.goniometer_measurement_parameters["homing_time"])

        # Initial processing time in seconds
        # I am not quite sure why this is done and if there is no better way of doing it
        # processing_time = 0.5

        # Empty list, stores the data as multiple dicts to later generate a pd dataframe
        rows_list = []

        progress = 0

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
            # Wait until the motor move is finished
            while not self.parent.motor_run.isFinished():
                time.sleep(0.1)

            # self.parent.gw_animation.move(angle)
            # self.update_animation.emit(angle)

            # Instead of defining a moving time, just read the motor position and
            # only start the measurement when the motor is at the right position
            # motor_position = self.motor.read_position()

            # while not math.isclose(motor_position, angle, abs_tol=0.01):
            #     motor_position = self.motor.read_position()
            #     self.update_animation.emit(motor_position)
            #     time.sleep(0.05)

            # # Update animation once more since the position might be 0.9 at this
            # # point (int comparison in the above while loop)
            # self.update_animation.emit(motor_position)

            # Wait an additional half a second (not really needed but only to be on the
            # save side)
            time.sleep(0.5)

            # time.sleep(self.goniometer_measurement_parameters["moving_time"])
            # cf.log_message("Moved to angle " + str(angle) + " °")

            # Only activate output for EL measurement
            if not self.goniometer_measurement_parameters["el_or_pl"]:
                self.uno.trigger_relay(self.pixel[0])
                oled_on_time_start = time.time()

                # The pulse duration is a valid parameter for the EL
                # measurements but hinders fast scans for PL measurements
                time.sleep(
                    self.goniometer_measurement_parameters["oled_on_time"]
                    # - processing_time
                )

            # start_process = time.process_time()

            # These measurements are only taken for el measurements
            if not self.goniometer_measurement_parameters["el_or_pl"]:
                # Here the keithley switches from voltage measurement to current
                # measurement

                # In the case of a voltage scan
                if self.goniometer_measurement_parameters["voltage_or_current"]:
                    temp_buffer = self.keithley_source.read_voltage()
                    data_dict = {
                        "angle": angle,
                        "voltage": temp_buffer,
                        "current": self.goniometer_measurement_parameters["vc_value"],
                    }
                else:
                    temp_buffer = self.keithley_source.read_current() * 1e3
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
                # self.keithley_source.deactivate_output()
                self.uno.trigger_relay(self.pixel[0])
                self.total_oled_on_time += time.time() - oled_on_time_start

            # Calculate the processing time it took
            # end_process = time.process_time()
            # processing_time = end_process - start_process

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

        # If the user wants it, move again back to zero angle
        # another spectrum to see if the device degraded already
        if self.goniometer_measurement_parameters["degradation_check"]:
            self.motor.move_to(0)

            # Wait until the motor move is finished
            while not self.parent.motor_run.isFinished():
                time.sleep(0.1)

            # Only activate output for el (otherwise it was never activated)
            if not self.goniometer_measurement_parameters["el_or_pl"]:
                # self.keithley_source.deactivate_output()
                self.uno.trigger_relay(self.pixel[0])
                oled_on_time_start = time.time()

            self.spectrum_data[str(0.0) + "_deg1"] = degradation_data_before
            self.spectrum_data[str(0.0) + "_deg2"] = self.spectrometer.measure()[1]

            # Only deactivate output for el (otherwise it was never activated)
            if not self.goniometer_measurement_parameters["el_or_pl"]:
                self.uno.trigger_relay(self.pixel[0])
                self.total_oled_on_time += time.time() - oled_on_time_start

            # Now plot the spectrum of minimum angle and the final repeated measurement
            self.update_simple_spectrum_signal.emit(
                [
                    self.spectrum_data["wavelength"],
                    self.spectrum_data["0.0_deg1"] - self.spectrum_data["background"],
                    self.spectrum_data["0.0_deg2"] - self.spectrum_data["background"],
                ],
                [
                    "initial spectrum",
                    "after " + str(round(self.total_oled_on_time, 2)) + " s on time",
                ],
            )

            corrected_spectrum_data = self.correct_spectrum_for_degradation()
            self.save_spectrum_data(corrected_spectrum_data, "-deg")

        self.save_spectrum_data(self.spectrum_data)

        self.hide_progress_bar.emit()
        self.reset_start_button.emit(False)

        cf.log_message("Measurement finished")

        if not self.goniometer_measurement_parameters["el_or_pl"]:
            # Close relay only
            # self.uno.trigger_relay(relay=0)
            # self.uno.trigger_relay(self.pixel[0])
            # self.uno.close_serial_connection()  # close COM port
            self.keithley_source.deactivate_output()

            # Only save iv data for el measurement, because it otherwise does not exist
            self.iv_data = pd.DataFrame(rows_list)
            self.save_iv_data()
            self.keithley_source.reset()
            self.keithley_source.set_voltage(self.setup_parameters["test_voltage"])

        else:
            # Show pop_up that asks to shut down the lamp after the measurement
            # was done
            self.pause = "True"
            self.pause_thread_pl.emit("off")

            while self.pause == "True":
                time.sleep(0.1)
                if self.pause == "break":
                    # Print total time elapsed
                    self.pl_elapsed_time = round(
                        time.time() - absolute_starting_time, 2
                    )
                    cf.log_message(
                        str(self.pl_elapsed_time)
                        + " s passed since PL lamp was turned on."
                    )
                    break
                elif self.pause == "return":
                    return

    def correct_spectrum_for_degradation(self):
        """
        In case the degradation check was activated, correct the specturm for
        the degradation.
        """
        # Function to do moving average
        from scipy.ndimage.filters import uniform_filter1d

        initial_maximum_intensity = max(
            uniform_filter1d(self.spectrum_data["0.0_deg1"], 25)
        )
        final_maximum_intensity = max(
            uniform_filter1d(self.spectrum_data["0.0_deg2"], 25)
        )

        # Assuming an exponential decay of the device, calculate the decay
        # constant. Time is replaced by column number.
        decay_constant = -len(self.spectrum_data.columns) / np.log(
            final_maximum_intensity / initial_maximum_intensity
        )

        from copy import copy

        # Apply the correction to the data
        corrected_spectrum_data = copy(self.spectrum_data)
        corrected_spectrum_data.iloc[:, 2:-2] = self.spectrum_data.iloc[:, 2:-2].apply(
            lambda x: x
            * np.exp(
                (self.spectrum_data.iloc[:, 2:-2].columns.get_loc(x.name) + 1)
                / decay_constant
            )
        )

        return corrected_spectrum_data

    def save_iv_data(self):
        """
        Function to save the iv data that contains the data of current and
        voltage at each angle.
        """
        # Header Parameters
        line01 = (
            "Integration time: "
            + str(self.goniometer_measurement_parameters["integration_time"])
            + " ms\t"
            + "OLED on time: "
            + str(self.goniometer_measurement_parameters["oled_on_time"])
            + " s    "
        )
        if self.goniometer_measurement_parameters["voltage_or_current"]:
            line02 = (
                "Source Voltage: "
                + str(self.goniometer_measurement_parameters["vc_value"])
                + " V\t"
                + "Current Compliance: "
                + str(self.goniometer_measurement_parameters["vc_compliance"] * 1e3)
                + " mA"
            )
        else:
            line02 = (
                "Source Current:"
                + str(self.goniometer_measurement_parameters["vc_value"] * 1e3)
                + " mA\t"
                + "Voltage Compliance: "
                + str(self.goniometer_measurement_parameters["vc_compliance"])
                + " V"
            )

        # Save the specific oled and photodiode data
        line03 = "Specific oled and photodiode data"
        # line04 = (
        #     "OLED voltage: "
        #     + str(self.specific_oled_voltage)
        #     + " V\t"
        #     + "OLED current: "
        #     + str(self.specific_oled_current)
        #     + " mA\t"
        #     + "PD voltage: "
        #     + str(self.specific_pd_voltage)
        #     + " V"
        # )
        line05 = "### Measurement data ###"
        line06 = "Angle\t OLED Voltage\t OLED Current"
        line07 = "deg\t V\t mA\n"

        header_lines = [
            line01,
            line02,
            line03,
            # line04,
            line05,
            line06,
            line07,
        ]

        # Depending on if EL or PL was selected make the pixel and device
        # number part of the file name or not
        if self.goniometer_measurement_parameters["el_or_pl"]:
            file_path = (
                self.setup_parameters["folder_path"]
                + dt.date.today().strftime("%Y-%m-%d_")
                + self.setup_parameters["batch_name"]
                + "_gon-jvl"
                + ".csv"
            )
        else:
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

        cf.save_file(self.iv_data, file_path, header_lines)
        # # Write header lines to file
        # with open(file_path, "a") as the_file:
        #     the_file.write("\n".join(header_lines))

        # # Now write pandas dataframe to file
        # self.iv_data.to_csv(
        #     file_path,
        #     index=False,
        #     mode="a",
        #     header=False,
        #     sep="\t",
        # )
        cf.log_message("IV data saved")

    def save_spectrum_data(self, spectrum_data, additional_file_ending=""):
        """
        Function to save the spectrum data to a separate file
        """
        # Header Parameters
        line01 = (
            "Integration time: "
            + str(self.goniometer_measurement_parameters["integration_time"])
            + " us\t"
            + "OLED on time: "
            + str(self.goniometer_measurement_parameters["oled_on_time"])
            + " s"
        )
        if self.goniometer_measurement_parameters["voltage_or_current"]:
            line02 = (
                "Source Voltage: "
                + str(self.goniometer_measurement_parameters["vc_value"])
                + " V\t"
                + "Current Compliance: "
                + str(self.goniometer_measurement_parameters["vc_compliance"] * 1e3)
                + " mA"
            )
        else:
            line02 = (
                "Source Current: "
                + str(self.goniometer_measurement_parameters["vc_value"] * 1e3)
                + " mA\t"
                + "Voltage Compliance: "
                + str(self.goniometer_measurement_parameters["vc_compliance"])
                + " V"
            )
        if not math.isclose(self.goniometer_measurement_parameters["el_or_pl"], 0):
            line03 = (
                "Total on time PL lamp: " + str(round(self.pl_elapsed_time, 2)) + " s"
            )
        else:
            line03 = (
                "Total OLED on time: " + str(round(self.total_oled_on_time, 2)) + " s"
            )

        # Save the specific oled and photodiode data
        line04 = "### Measurement data ###\n"

        header_lines = [
            line01,
            line02,
            line03,
            line04,
        ]

        # Depending on if EL or PL was selected make the pixel and device
        # number part of the file name or not
        if self.goniometer_measurement_parameters["el_or_pl"]:
            file_path = (
                self.setup_parameters["folder_path"]
                + dt.date.today().strftime("%Y-%m-%d_")
                + self.setup_parameters["batch_name"]
                + "_gon-spec"
                + additional_file_ending
                + ".csv"
            )
        else:
            file_path = (
                self.setup_parameters["folder_path"]
                + dt.date.today().strftime("%Y-%m-%d_")
                + self.setup_parameters["batch_name"]
                + "_d"
                + str(self.setup_parameters["device_number"])
                + "_p"
                + str(self.pixel[0])
                + "_gon-spec"
                + additional_file_ending
                + ".csv"
            )

        # Format the dataframe for saving (no. of digits)
        spectrum_data = spectrum_data.apply(
            lambda x: x.map(lambda y: "{0:.1f}".format(y))
        )

        # Save data
        cf.save_file(spectrum_data, file_path, header_lines, save_header=True)

        # # Write header lines to file
        # with open(file_path, "a") as the_file:
        #     the_file.write("\n".join(header_lines))

        # # Now write pandas dataframe to file with header names
        # self.spectrum_data.to_csv(
        #     file_path,
        #     index=False,
        #     mode="a",
        #     header=True,
        #     sep="\t",
        # )

        cf.log_message("Spectral data saved")
