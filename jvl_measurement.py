from UI_main_window import Ui_MainWindow
from UI_settings_window import Ui_Settings

from autotube_measurement import AutotubeMeasurement

from PySide2 import QtCore, QtGui, QtWidgets

import time
import os
import json

import matplotlib.pylab as plt

# Set the keithley source and multimeter addresses that are needed for
# communication
# keithley_source_address = u"USB0::0x05E6::0x2450::04102170::INSTR"
# keithley_multimeter_address = u"USB0::0x05E6::0x2100::8003430::INSTR"
# com2_address = u"ASRL3::INSTR"
photodiode_gain = 50


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """
    This class contains the logic of the program and is explicitly seperated
    from the UI classes. However, it is a child class of Ui_MainWindow.
    """

    def __init__(self):
        """
        Initialise instance
        """
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # Link actions to buttons
        self.aw_start_measurement_pushButton.clicked.connect(
            self.start_autotube_measurement
        )

        # -------------------------------------------------------------------- #
        # --------------------- Set Standard Parameters ---------------------- #
        # -------------------------------------------------------------------- #

        # Set standard parameters for autotube measurement
        self.aw_min_voltage_spinBox.setValue(-2)
        self.aw_min_voltage_spinBox.setMinimum(-50)
        self.aw_max_voltage_spinBox.setValue(5)
        self.aw_max_voltage_spinBox.setMaximum(50)
        self.aw_changeover_voltage_spinBox.setValue(2)
        self.aw_changeover_voltage_spinBox.setSingleStep(0.1)
        self.aw_low_voltage_step_spinBox.setValue(0.5)
        self.aw_low_voltage_step_spinBox.setSingleStep(0.1)
        self.aw_high_voltage_step_spinBox.setValue(0.1)
        self.aw_high_voltage_step_spinBox.setSingleStep(0.1)
        self.aw_scan_compliance_spinBox.setValue(1.05)
        self.aw_scan_compliance_spinBox.setMaximum(1.05)
        self.aw_scan_compliance_spinBox.setSingleStep(0.05)

        # Set standard parameters for Goniometer
        self.gw_offset_angle_spinBox.setValue(0)
        self.gw_offset_angle_spinBox.setMaximum(360)
        self.gw_scanning_angle_spinBox.setValue(180)
        self.gw_scanning_angle_spinBox.setMaximum(360)
        self.gw_step_angle_spinBox.setValue(1)
        self.gw_step_angle_spinBox.setMaximum(360)
        self.gw_integration_time_spinBox.setValue(300)
        self.gw_homing_time_spinBox.setValue(30)
        self.gw_moving_time_spinBox.setValue(1)
        self.gw_pulse_duration_spinBox.setValue(2)
        self.gw_voltage_or_current_spinBox.setValue(5)

        # Set standard parameters for Spectral Measurement
        self.specw_voltage_spinBox.setValue(5)
        self.specw_voltage_spinBox.setMaximum(50)

    def read_setup_parameters(self):
        """
        Function to read out the current fields entered in the setup tab
        """
        setup_parameters = {
            "folder_path": self.sw_folder_path_lineEdit.text(),
            "batch_name": self.sw_batch_name_lineEdit.text(),
            "device_number": self.sw_device_number_spinBox.value(),
            "test_voltage": self.sw_ct_voltage_spinBox.value(),
            "selected_pixel": [
                self.sw_pixel1_pushButton.isChecked(),
                self.sw_pixel2_pushButton.isChecked(),
                self.sw_pixel3_pushButton.isChecked(),
                self.sw_pixel4_pushButton.isChecked(),
                self.sw_pixel5_pushButton.isChecked(),
                self.sw_pixel6_pushButton.isChecked(),
                self.sw_pixel7_pushButton.isChecked(),
                self.sw_pixel8_pushButton.isChecked(),
            ],
            "documentation": self.sw_documentation_textEdit.toPlainText(),
        }

        return setup_parameters

    def read_autotube_parameters(self):
        """
        Function to read out the current measurement parameters that are
        present when clicking the Start Measurement button
        """
        measurement_parameters = {
            "min_voltage": self.aw_min_voltage_spinBox.value(),
            "max_voltage": self.aw_max_voltage_spinBox.value(),
            "changeover_voltage": self.aw_changeover_voltage_spinBox.value(),
            "low_voltage_step": self.aw_low_voltage_step_spinBox.value(),
            "high_voltage_step": self.aw_high_voltage_step_spinBox.value(),
            "scan_compliance": self.aw_scan_compliance_spinBox.value(),
            "check_bad_contacts": self.aw_bad_contacts_toggleSwitch.isChecked(),
            "pd_saturation": self.aw_pd_saturation_toggleSwitch.isChecked(),
        }

        # Boolean list for selected pixels
        selected_pixels = [
            self.aw_pixel1_pushButton.isChecked(),
            self.aw_pixel2_pushButton.isChecked(),
            self.aw_pixel3_pushButton.isChecked(),
            self.aw_pixel4_pushButton.isChecked(),
            self.aw_pixel5_pushButton.isChecked(),
            self.aw_pixel6_pushButton.isChecked(),
            self.aw_pixel7_pushButton.isChecked(),
            self.aw_pixel8_pushButton.isChecked(),
        ]

        # Return only the pixel numbers of the selected pixels
        selected_pixels_numbers = [i + 1 for i, x in enumerate(selected_pixels) if x]

        return measurement_parameters, selected_pixels_numbers

    def plot_autotube_measurement(self, jvl_data):
        """
        Function to plot the results from the autotube measurement to the central graph.
        """
        # self.aw_fig.figure()

        # Plot current
        self.aw_ax.plot(
            jvl_data.voltage.to_list(),
            jvl_data.current.to_list(),
            color=(68 / 255, 188 / 255, 65 / 255),
            marker="o",
        )
        # twin object for two different y-axis on the sample plot
        # make a plot with different y-axis using second axis object
        self.aw_ax2.plot(
            jvl_data.voltage.to_list(),
            jvl_data.pd_voltage.to_list(),
            color=(85 / 255, 170 / 255, 255 / 255),
            marker="o",
        )

        self.aw_fig.draw()

    def read_global_settings(self):
        """
        Read in global settings from file. The file can be changed using the
        settings window.
        """
        # Load from file to fill the lines
        with open("settings.json") as json_file:
            data = json.load(json_file)
        try:
            settings = data["overwrite"]
        except:
            settings = data["default"]
            print("Default device parameters taken")

        return settings[0]

    def start_autotube_measurement(self):
        """
        Function that executes the actual measurement (the logic of which is
        stored in autotube_measurement.py). Iteration over the selected
        pixels as well as a call for the plotting happens here.
        """

        # Read out measurement and setup parameters from GUI
        setup_parameters = self.read_setup_parameters()

        if (
            setup_parameters["folder_path"] == ""
            or setup_parameters["batch_name"] == ""
        ):
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText("Please set folder path and batch name first!")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.setStyleSheet(
                "background-color: rgb(44, 49, 60);\n"
                "color: rgb(255, 255, 255);\n"
                'font: 63 bold 10pt "Segoe UI";\n'
                ""
            )
            msgBox.exec()

            self.aw_start_measurement_pushButton.setChecked(False)

            return

        # Now check if the folder path ends on a / otherwise try to add it
        if not setup_parameters["folder_path"][-1] == "/":
            setup_parameters["folder_path"] = setup_parameters["folder_path"] + "/"
            self.sw_folder_path_lineEdit.setText(setup_parameters["folder_path"])

        # Now check if the read out path is a valid path
        if not os.path.isdir(setup_parameters["folder_path"]):
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText("Please enter a valid folder path")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.setStyleSheet(
                "background-color: rgb(44, 49, 60);\n"
                "color: rgb(255, 255, 255);\n"
                'font: 63 bold 10pt "Segoe UI";\n'
                ""
            )
            msgBox.exec()

            self.aw_start_measurement_pushButton.setChecked(False)

            return

        measurement_parameters, selected_pixels = self.read_autotube_parameters()

        # Set progress bar to zero
        self.progressBar.setProperty("value", 0)

        # Update statusbar message
        self.statusbar.showMessage("Running", 10000000)

        # Now read in the global settings from file
        global_settings = self.read_global_settings()

        # This shall create an instance of the AutotubeMeasurement class
        progress = 0
        for pixel in selected_pixels:
            file_path = (
                setup_parameters["folder_path"]
                + setup_parameters["batch_name"]
                + "_d"
                + str(setup_parameters["device_number"])
                + "_p"
                + str(pixel)
                + ".csv"
            )

            self.statusbar.showMessage("Running on Pixel " + str(pixel), 10000000)

            # Instantiate our class
            measurement = AutotubeMeasurement(
                global_settings["keithley_source_address"],
                global_settings["keithley_multimeter_address"],
                global_settings["arduino_com_address"],
                photodiode_gain,
                measurement_parameters,
                pixel,
                file_path,
            )

            # Call measurement.measure() to measure and save all the measured data into the class itself
            measurement.dummy_measure()

            # Call measurement.save_data() to directly save the data to a file
            measurement.save_data()

            # Call measurement.get_data() that returns the actual data
            # so that we can feed it into plot_autotube_measurement
            self.plot_autotube_measurement(measurement.get_data())

            # Update progress bar
            progress += 1
            self.progressBar.setProperty(
                "value", int(progress / len(selected_pixels) * 100)
            )

            # Update GUI while being in a loop. It would be better to use
            # separate threads but for now this is the easiest way
            app.processEvents()

            # Wait a few seconds so that the user can have a look at the graph
            time.sleep(1)

        # Untoggle the pushbutton
        self.aw_start_measurement_pushButton.setChecked(False)

        # Update statusbar
        self.statusbar.showMessage("Finished Measurement", 10000000)


# ---------------------------------------------------------------------------- #
# -------------------- This is to execute the program ------------------------ #
# ---------------------------------------------------------------------------- #
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    # ui.setupUi(aMainWindow)
    ui.show()
    sys.exit(app.exec_())