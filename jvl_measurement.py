from UI_main_window import Ui_MainWindow
from UI_settings_window import Ui_Settings

from autotube_measurement import AutotubeMeasurement

from PySide2 import QtCore, QtGui, QtWidgets

import time
import matplotlib.pylab as plt

# Set the keithley source and multimeter addresses that are needed for
# communication
keithley_source_address = u"USB0::0x05E6::0x2450::04102170::INSTR"
keithley_multimeter_address = u"USB0::0x05E6::0x2100::8003430::INSTR"
com2_address = u"ASRL3::INSTR"
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

        return measurement_parameters, selected_pixels

    def plot_autotube_measurement(self, jvl_data):
        """
        Function to plot the results from the autotube measurement to the central graph.
        """
        # self.aw_fig.figure()

        # Plot current
        self.aw_ax.plot(jvl_data.voltage, jvl_data.current, color="orange", marker="o")
        # twin object for two different y-axis on the sample plot
        # make a plot with different y-axis using second axis object
        self.aw_ax2.plot(
            jvl_data.voltage, jvl_data.pd_voltage, color="blue", marker="o"
        )

        plt.show()

        return jvl_data

    def start_autotube_measurement(self):
        """
        Function that executes the actual measurement (the logic of which is
        stored in autotube_measurement.py). Iteration over the selected
        pixels as well as a call for the plotting happens here.
        """
        # Set progress bar to zero
        self.progressBar.setProperty("value", 0)

        # Read out measurement and setup parameters from GUI
        measurement_parameters, selected_pixels = self.read_autotube_parameters()
        setup_parameters = self.read_setup_parameters()

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

            # Instantiate our class
            measurement = AutotubeMeasurement(
                keithley_source_address,
                keithley_multimeter_address,
                com2_address,
                photodiode_gain,
                measurement_parameters,
                pixel,
                file_path,
            )

            # Call measurement.measure() to measure and save all the measured data into the class itself
            measurement.measure()

            # Call measurement.save_data() to directly save the data to a file
            measurement.save_data()

            # Call measurement.get_data() that returns the actual data
            # so that we can feed it into plot_autotube_measurement
            self.plot_autotube_measurement(measurement.get_data())

            # Update progress bar
            progress += 1
            self.progressBar.setProperty("value", int(progress / len(selected_pixels)))

            # Wait a few seconds so that the user can have a look at the graph
            time.sleep(5)


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