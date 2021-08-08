# -*- coding: utf-8 -*-

import pyvisa  # Keithley Module
import serial  # Arduino Module

from PySide2 import QtCore

from hardware import ArduinoUno, KeithleySource, KeithleyMultimeter
from tests.tests import MockArduinoUno, MockKeithleySource, MockKeithleyMultimeter

# My suspicion about the queue module is that it is only there for logging. If
# that is really the case I would rather not use it to simplify things
# import queue
import time
import datetime as dt
import sys
import core_functions as cf

import os

import pandas as pd
import numpy as np
import math


class AutotubeMeasurement(QtCore.QThread):
    """
    Class that contains all the relevant functions for the autotube EL measurement task
    """

    update_plot = QtCore.Signal(list, list, list)
    update_progress_bar = QtCore.Signal(str, float)
    hide_progress_bar = QtCore.Signal()
    reset_start_button = QtCore.Signal(bool)

    def __init__(
        self,
        keithley_source,
        keithley_multimeter,
        arduino,
        measurement_parameters,
        setup_parameters,
        multimeter_latency,
        selected_pixels,
        parent=None,
    ):
        """
        Initialise class. Measurement parameters are handed over from the GUI
        """
        super(AutotubeMeasurement, self).__init__()

        # Assign hardware and reset
        self.uno = arduino
        self.uno.init_serial_connection()
        self.keithley_source = keithley_source
        self.keithley_source.as_voltage_source(
            measurement_parameters["scan_compliance"]
        )
        self.keithley_multimeter = keithley_multimeter
        self.keithley_multimeter.reset()
        self.multimeter_latency = multimeter_latency

        # Now set the input parameters as parameters of the datastructure
        self.measurement_parameters = measurement_parameters
        self.setup_parameters = setup_parameters
        # self.PDcutoff = self.set_photodiode_gain(photodiode_gain)
        self.selected_pixels = selected_pixels

        # Since the data shall be plotted after each measurement (it could also
        # be done while measuring but I think there is not much benefit and the
        # programming is uglier), only one pixel is scanned at a time
        self.df_data = pd.DataFrame(columns=["voltage", "current", "pd_voltage"])

        # Connect the signals
        self.update_plot.connect(parent.plot_autotube_measurement)
        self.update_progress_bar.connect(parent.progressBar.setProperty)
        self.hide_progress_bar.connect(parent.progressBar.hide)
        self.reset_start_button.connect(
            parent.aw_start_measurement_pushButton.setChecked
        )

        # Variable that stops the measurement
        self.stop = False

        self.parent = parent

    def run(self):
        """
        Function that does the actual measurement. I am not sure yet, if I
        want to do the data saving part in this class as well, definitely not
        in this function. For the time being it might be better to just
        return a pandas dataframe as a result. Also I am not sure yet where I
        am going to save the header parameters but definitely this is not
        done in this function!
        """

        import pydevd

        pydevd.settrace(suspend=False)
        if self.measurement_parameters["auto_spectrum"]:
            cf.log_message("Motor is moving to Photodiode Position")
            pd_position = 90
            self.parent.motor.move_to(pd_position)

            # motor_position = self.parent.motor.read_position()
            # motor_position_initial = self.parent.motor.read_position()

            # while not math.isclose(pd_position, motor_position, abs_tol=0.01):
            #     motor_position = self.parent.motor.read_position()

            #     self.update_progress_bar.emit(
            #         "value",
            #         int(
            #             abs(motor_position - motor_position_initial)
            #             / abs(pd_position - motor_position_initial)
            #             * 100
            #         ),
            #     )
            #     time.sleep(0.05)

            # self.parent.gw_animation.move(motor_position)

        cf.log_message("Motor arrived at Photodiode Position")

        # Define voltage steps
        # Voltage points for low OLED voltage
        low_vlt = np.arange(
            self.measurement_parameters["min_voltage"],
            self.measurement_parameters["changeover_voltage"],
            self.measurement_parameters["low_voltage_step"],
        )
        # Voltage points for high OLED voltage
        high_vlt = np.arange(
            self.measurement_parameters["changeover_voltage"],
            self.measurement_parameters["max_voltage"] + 0.1,
            self.measurement_parameters["high_voltage_step"],
        )

        voltages_to_scan = np.append(low_vlt, high_vlt)

        # To update progres bar
        progress = 0

        # Init buffer before the measurement
        # self.keithley_source.init_buffer(
        #     "OLEDbuffer", 10 * len(low_vlt) + len(high_vlt)
        # )
        # Turn all pixels off at the beginning
        self.uno.trigger_relay(0)

        self.update_progress_bar.emit("value", 0)

        # Iterate over all selected pixels
        max_luminances = []

        for pixel in self.selected_pixels:
            # self.keithley_source.empty_buffer("OLEDbuffer")

            cf.log_message("Running on Pixel " + str(pixel))

            # Take PD voltage reading from Multimeter for background
            background_diodevoltage = self.keithley_multimeter.measure_voltage()

            # Activate the relay of the selected pixel
            self.uno.trigger_relay(pixel)

            # Turn on the voltage
            self.keithley_source.activate_output()

            # Low Voltage Readings
            i = 0
            for voltage in voltages_to_scan:
                # self.queue.put("\nOLED Voltage : " + str(voltage) + " V")
                # Set voltage to source_value
                self.keithley_source.set_voltage(str(voltage))

                # Keithley has a latency. This value is higher if we consider
                # the range change of the automatic function of our multimeter
                # if self.measurement_parameters["fixed_multimeter_range"]:
                # time.sleep(0.1)
                # else:
                time.sleep(self.multimeter_latency)

                # Take PD voltage reading from Multimeter
                # if self.measurement_parameters["fixed_multimeter_range"]:
                # diode_voltage = self.keithley_multimeter.measure_voltage(1)
                # else:
                diode_voltage = self.keithley_multimeter.measure_voltage()
                # Take OLED current reading from Sourcemeter
                oled_current = self.keithley_source.read_current()

                # check if compliance is reached
                if abs(oled_current) >= self.measurement_parameters["scan_compliance"]:
                    self.keithley_source.deactivate_output()
                    self.log_message("Current compliance reached")
                    break

                # # check for a bad contact
                # bad_contact = False

                # if self.measurement_parameters["check_bad_contacts"] == True and (
                #     voltage > 0 and voltage < 2
                # ):
                #     # If the OLED shows for a small voltage (lower 2 V) already
                #     # 50 % of the compliance, it is regarded as being shorted
                #     if (
                #         abs(oled_current)
                #         >= 0.5 * self.measurement_parameters["scan_compliance"]
                #     ):
                #         self.keithley_source.deactivate_output()  # Turn power off
                #         cf.log_message(
                #             "Pixel "
                #             + str(pixel)
                #             + " probably has a bad contact. Measurement aborted."
                #         )

                #         # Wait a second so that the user can read the message
                #         time.sleep(1)
                #         bad_contact = True
                #         break

                if (
                    diode_voltage
                    >= self.measurement_parameters["photodiode_saturation"]
                ):
                    cf.log_message(
                        "Photodiode reached saturation. You might want to adjust the photodiode gain."
                    )

                    # Wait a second so that the user can read the message
                    time.sleep(1)
                    break

                self.df_data.loc[i, "pd_voltage"] = (
                    diode_voltage - background_diodevoltage
                )
                # Current should be in mA
                self.df_data.loc[i, "current"] = oled_current * 1e3
                self.df_data.loc[i, "voltage"] = voltage

                i += 1

                # Breaks out of the voltage loop
                if self.stop == True:
                    break

            # If a bad contact was detected, jump this iteration (no saving etc.)
            # if bad_contact == True:
            #     continue

            # Turn keithley off
            self.keithley_source.deactivate_output()

            # Turn off all relays
            self.uno.trigger_relay(pixel)

            # Breaks the pixel loop so that only the output is deactivated etc.
            if self.stop == True:
                break

            # Save data
            self.save_data(pixel)

            # Update the plot
            self.update_plot.emit(
                self.df_data["voltage"].to_numpy(dtype=float),
                self.df_data["current"].to_numpy(dtype=float),
                self.df_data["pd_voltage"].to_numpy(dtype=float),
            )

            # Append the last luminance measured for automatic spectrum measurement
            max_luminances.append(float(self.df_data["pd_voltage"].to_numpy()[-1]))

            # Update progress bar
            progress += 1

            self.update_progress_bar.emit(
                "value", int(progress / len(self.selected_pixels) * 100)
            )

            # Update GUI while being in a loop. It would be better to use
            # separate threads but for now this is the easiest way
            # app.processEvents()

            # Wait a few seconds so that the user can have a look at the graph
            time.sleep(1)

        # Breaks the pixel loop so that only the output is deactivated etc.
        if self.stop == True:
            cf.log_message("Autotube measurement interrupted by user")
            self.hide_progress_bar.emit()
            return

        if self.measurement_parameters["auto_spectrum"]:
            cf.log_message("Motor is moving to Spectrometer Position")
            spectrometer_position = 0
            self.parent.motor.move_to(spectrometer_position)

            # motor_position = self.parent.motor.read_position()
            # motor_position_initial = self.parent.motor.read_position()

            # while not math.isclose(0, motor_position, abs_tol=0.01):
            #     motor_position = self.parent.motor.read_position()

            #     self.update_progress_bar.emit(
            #         "value",
            #         int(
            #             abs(motor_position - motor_position_initial)
            #             / abs(spectrometer_position - motor_position_initial)
            #             * 100
            #         ),
            #     )

            #     time.sleep(0.05)

            # self.parent.gw_animation.move(motor_position)

            cf.log_message("Motor finished moving to Spectrometer Position")

            # Select the pixel to measure according to the highest luminance at maximum tested voltage
            pixel_with_highest_luminance = self.selected_pixels[
                np.argmax(np.array(max_luminances))
            ]

            self.parent.specw_pushbutton_array[
                pixel_with_highest_luminance - 1
            ].setChecked(True)
            self.parent.toggle_pixel(pixel_with_highest_luminance, "specw")
            # self.keithley_source.set_voltage(str(voltages_to_scan[-1]))
            # self.keithley_source.activate_output()
            self.parent.specw_voltage_spinBox.setValue(voltages_to_scan[-1])
            self.parent.tabWidget.setCurrentIndex(2)

            # # self.progressBar.setProperty("value", 0)
            # self.update_progress_bar.emit("value", 0)

            # # Activate the relay of the selected pixel
            # self.uno.trigger_relay(pixel_with_highest_luminance)

            # # Set voltage to source_value
            # self.keithley_source.set_voltage(str(voltages_to_scan[-1]))

            # # Turn on the voltage
            # self.keithley_source.activate_output()

            # # Store data in pd dataframe
            # df_spectrum_data = pd.DataFrame(
            #     columns=["wavelength", "background", "intensity"]
            # )

            # # Get wavelength and intensity of spectrum under light conditions
            # (
            #     df_spectrum_data["wavelength"],
            #     df_spectrum_data["intensity"],
            # ) = self.parent.spectrometer.measure()

            # self.update_progress_bar.emit("value", 50)

            # # Turn off all pixels wait two seconds to ensure that there is no light left and measure again
            # # self.unselect_all_pixels()
            # self.uno.trigger_relay(pixel_with_highest_luminance)
            # self.keithley_source.deactivate_output()
            # time.sleep(2)
            # (
            #     wavelength,
            #     df_spectrum_data["background"],
            # ) = self.parent.spectrometer.measure()

            # # Save data
            # file_path = (
            #     self.setup_parameters["folder_path"]
            #     + dt.date.today().strftime("%Y-%m-%d_")
            #     + self.setup_parameters["batch_name"]
            #     + "_d"
            #     + str(self.setup_parameters["device_number"])
            #     + "_p"
            #     + str(pixel)
            #     + "_spec"
            #     + ".csv"
            # )

            # # Define header line with voltage and integration time
            # # line01 = (
            # #     "Voltage: "
            # #     + str(self.specw_voltage_spinBox.value())
            # #     + " V\t"
            # #     + "Integration Time: "
            # #     + str(self.spectrum_measurement.spectrometer.integration_time)
            # #     + " ms"
            # #     + "Non-linearity Correction: "
            # #     + str(bool(global_settings["spectrometer_non_linearity_correction"]))
            # # )

            # line02 = "### Measurement data ###"
            # line03 = "Wavelength\t Background\t Intensity"
            # line04 = "nm\t counts\t counts\n"
            # header_lines = [
            #     # line01,
            #     line02,
            #     line03,
            #     line04,
            # ]

            # # Format the dataframe for saving (no. of digits)
            # df_spectrum_data["wavelength"] = df_spectrum_data["wavelength"].map(
            #     lambda x: "{0:.2f}".format(x)
            # )
            # df_spectrum_data["background"] = df_spectrum_data["background"].map(
            #     lambda x: "{0:.1f}".format(x)
            # )
            # df_spectrum_data["intensity"] = df_spectrum_data["intensity"].map(
            #     lambda x: "{0:.1f}".format(x)
            # )

            # cf.save_file(df_spectrum_data, file_path, header_lines)

            # # Write header lines to file
            # with open(file_path, "a") as the_file:
            #     the_file.write("\n".join(header_lines))

            # # Now write pandas dataframe to file
            # df_spectrum_data.to_csv(
            #     file_path, index=False, mode="a", header=False, sep="\t"
            # )

            self.update_progress_bar.emit("value", 100)

            # self.parent.save_spectrum()

        # Untoggle the pushbutton
        self.reset_start_button.emit(False)

        # Update statusbar
        cf.log_message("Autotube measurement finished")

        # Hise progress bar
        self.hide_progress_bar.emit()

        # close COM port
        # self.uno.close_serial_connection()

    def save_data(self, pixel):
        """
        Function to save the measured data to file. This should probably be
        integrated into the AutotubeMeasurement class
        """
        # Define Header
        line03 = (
            "Min voltage:   "
            + str(self.measurement_parameters["min_voltage"])
            + " V   "
            + "Max voltage:   "
            + str(self.measurement_parameters["max_voltage"])
            + " V    "
            + "Change voltage:   "
            + str(self.measurement_parameters["changeover_voltage"])
            + " V"
        )
        line04 = (
            "Step voltage at low voltages:   "
            + str(self.measurement_parameters["low_voltage_step"])
            + " V"
        )
        line05 = (
            "Step voltage at high voltages:   "
            + str(self.measurement_parameters["high_voltage_step"])
            + " V"
        )
        line06 = (
            "Current Compliance:   "
            + str(self.measurement_parameters["scan_compliance"])
            + " A"
        )
        line07 = "### Measurement data ###"
        line08 = "OLEDVoltage\t OLEDCurrent\t Photodiode Voltage"
        line09 = "V\t mA\t V\n"

        header_lines = [
            line03,
            line04,
            line05,
            line06,
            line07,
            line08,
            line09,
        ]

        # Write header lines to file
        file_path = (
            self.setup_parameters["folder_path"]
            + dt.date.today().strftime("%Y-%m-%d_")
            + self.setup_parameters["batch_name"]
            + "_d"
            + str(self.setup_parameters["device_number"])
            + "_p"
            + str(pixel)
            + "_jvl"
            + ".csv"
        )

        # Format the dataframe for saving (no. of digits)
        self.df_data["voltage"] = self.df_data["voltage"].map(
            lambda x: "{0:.2f}".format(x)
        )
        self.df_data["current"] = self.df_data["current"].map(
            lambda x: "{0:.6f}".format(x)
        )
        self.df_data["pd_voltage"] = self.df_data["pd_voltage"].map(
            lambda x: "{0:.7f}".format(x)
        )

        # Save file
        cf.save_file(self.df_data, file_path, header_lines)

        # with open(file_path, "a") as the_file:
        #     the_file.write("\n".join(header_lines))

        # # Now write pandas dataframe to file
        # self.df_data.to_csv(file_path, index=False, mode="a", header=False, sep="\t")

    # def get_data(self):
    #     """
    #     Function to return the data that is stored in the class' file structure.
    #     """
    #     return self.df_data