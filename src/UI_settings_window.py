# -*- coding: utf-8 -*-
from PySide2 import QtCore, QtGui, QtWidgets

import json
import core_functions as cf

from loading_window import LoadingWindow


class Ui_Settings(object):
    def setupUi(self, Settings, parent=None):
        # Note: this is not how it should be done but currently I don't know
        # how to do it differently. This is only needed to be able to emit
        # signals to the main window
        self.parent = parent

        Settings.setObjectName("Settings")
        Settings.resize(509, 317)
        Settings.setStyleSheet(
            "QWidget {\n"
            "            background-color: rgb(44, 49, 60);\n"
            "            color: rgb(255, 255, 255);\n"
            "            font: 63 10pt 'Segoe UI';\n"
            "}\n"
            "QPushButton {\n"
            "            border: 2px solid rgb(52, 59, 72);\n"
            "            border-radius: 5px;\n"
            "            background-color: rgb(52, 59, 72);\n"
            "            color: rgb(255, 255, 255);\n"
            "            font: 63 bold 10pt 'Segoe UI';\n"
            "}\n"
            "QPushButton:hover {\n"
            "            background-color: rgb(57, 65, 80);\n"
            "            border: 2px solid rgb(61, 70, 86);\n"
            "}\n"
            "QPushButton:pressed {\n"
            "            background-color: rgb(35, 40, 49);\n"
            "            border: 2px solid rgb(43, 50, 61);\n"
            "}\n"
            "QPushButton:checked {\n"
            "            background-color: rgb(35, 40, 49);\n"
            "            border: 2px solid rgb(85, 170, 255);\n"
            "}"
        )
        self.gridLayout = QtWidgets.QGridLayout(Settings)
        self.gridLayout.setContentsMargins(25, 10, 25, 10)
        self.gridLayout.setObjectName("gridLayout")

        # Device settings
        self.device_settings_header_label = QtWidgets.QLabel(Settings)
        self.device_settings_header_label.setMinimumSize(QtCore.QSize(0, 20))
        self.device_settings_header_label.setStyleSheet(
            'font: 75 bold 10pt "Segoe UI";'
        )
        self.device_settings_header_label.setObjectName("device_settings_header_label")
        self.gridLayout.addWidget(self.device_settings_header_label, 0, 0, 1, 2)

        self.header_line_1 = QtWidgets.QFrame()
        self.header_line_1.setFrameShape(QtWidgets.QFrame.HLine)
        self.header_line_1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.gridLayout.addWidget(self.header_line_1, 1, 0, 1, 2)

        # Keithley source address
        self.keithley_source_address_label = QtWidgets.QLabel(Settings)
        self.keithley_source_address_label.setObjectName(
            "keithley_source_address_label"
        )
        self.gridLayout.addWidget(self.keithley_source_address_label, 2, 0, 1, 1)
        self.keithley_source_address_lineEdit = QtWidgets.QLineEdit(Settings)
        self.keithley_source_address_lineEdit.setObjectName(
            "keithley_source_address_lineEdit"
        )
        # self.keithley_source_address_lineEdit.setText(
        # u"USB0::0x05E6::0x2450::04102170::INSTR"
        # )
        self.gridLayout.addWidget(self.keithley_source_address_lineEdit, 2, 1, 1, 1)

        # Keithley multimeter address
        self.keithley_multimeter_address_label = QtWidgets.QLabel(Settings)
        self.keithley_multimeter_address_label.setObjectName(
            "keithley_multimeter_address_label"
        )
        self.gridLayout.addWidget(self.keithley_multimeter_address_label, 3, 0, 1, 1)
        self.keithley_multimeter_address_lineEdit = QtWidgets.QLineEdit(Settings)
        self.keithley_multimeter_address_lineEdit.setObjectName(
            "keithley_multimeter_address_lineEdit"
        )
        # self.keithley_multimeter_address_lineEdit.setText(
        # u"USB0::0x05E6::0x2100::8003430::INSTR"
        # )
        self.gridLayout.addWidget(self.keithley_multimeter_address_lineEdit, 3, 1, 1, 1)

        # Arduino COM address
        self.arduino_com_address_label = QtWidgets.QLabel(Settings)
        self.arduino_com_address_label.setObjectName("arduino_com_address_label")
        self.gridLayout.addWidget(self.arduino_com_address_label, 4, 0, 1, 1)
        self.arduino_com_address_lineEdit = QtWidgets.QLineEdit(Settings)
        self.arduino_com_address_lineEdit.setObjectName("arduino_com_address_lineEdit")
        self.gridLayout.addWidget(self.arduino_com_address_lineEdit, 4, 1, 1, 1)

        # Motor number
        self.motor_number_label = QtWidgets.QLabel(Settings)
        self.motor_number_label.setObjectName("motor_number_label")
        self.gridLayout.addWidget(self.motor_number_label, 5, 0, 1, 1)
        self.motor_number_lineEdit = QtWidgets.QLineEdit(Settings)
        self.motor_number_lineEdit.setObjectName("motor_number_lineEdit")
        self.gridLayout.addWidget(self.motor_number_lineEdit, 5, 1, 1, 1)

        # Motor offset
        self.motor_offset_label = QtWidgets.QLabel(Settings)
        self.motor_offset_label.setObjectName("motor_offset_label")
        self.gridLayout.addWidget(self.motor_offset_label, 6, 0, 1, 1)
        self.motor_offset_lineEdit = QtWidgets.QLineEdit(Settings)
        self.motor_offset_lineEdit.setObjectName("motor_offset_lineEdit")
        self.gridLayout.addWidget(self.motor_offset_lineEdit, 6, 1, 1, 1)

        # Spectrum integration time for goniometer measurement
        self.spectrum_integration_time_label = QtWidgets.QLabel(Settings)
        self.spectrum_integration_time_label.setObjectName(
            "spectrum_integration_time_label"
        )
        self.gridLayout.addWidget(self.spectrum_integration_time_label, 7, 0, 1, 1)
        self.spectrum_integration_time_lineEdit = QtWidgets.QLineEdit(Settings)
        self.spectrum_integration_time_lineEdit.setObjectName(
            "spectrum_integration_time_lineEdit"
        )
        self.gridLayout.addWidget(self.spectrum_integration_time_lineEdit, 7, 1, 1, 1)

        # Photodiode gain
        self.photodiode_gain_label = QtWidgets.QLabel(Settings)
        self.photodiode_gain_label.setObjectName("photodiode_gain_label")
        self.gridLayout.addWidget(self.photodiode_gain_label, 8, 0, 1, 1)
        self.photodiode_gain_lineEdit = QtWidgets.QLineEdit(Settings)
        self.photodiode_gain_lineEdit.setObjectName("photodiode_gain_lineEdit")
        self.gridLayout.addWidget(self.photodiode_gain_lineEdit, 8, 1, 1, 1)

        # Photodiode Saturation Voltage
        self.photodiode_saturation_label = QtWidgets.QLabel(Settings)
        self.photodiode_saturation_label.setObjectName("photodiode_saturation_label")
        self.gridLayout.addWidget(self.photodiode_saturation_label, 9, 0, 1, 1)
        self.photodiode_saturation_lineEdit = QtWidgets.QLineEdit(Settings)
        self.photodiode_saturation_lineEdit.setObjectName(
            "photodiode_saturation_lineEdit"
        )
        self.gridLayout.addWidget(self.photodiode_saturation_lineEdit, 9, 1, 1, 1)

        # Push Buttons
        self.buttons_HBoxLayout = QtWidgets.QHBoxLayout()
        self.load_defaults_pushButton = QtWidgets.QPushButton(Settings)
        self.load_defaults_pushButton.setObjectName("load_defaults_pushButton")
        self.buttons_HBoxLayout.addWidget(self.load_defaults_pushButton)

        self.save_settings_pushButton = QtWidgets.QPushButton(Settings)
        self.save_settings_pushButton.setObjectName("save_settings_pushButton")
        self.buttons_HBoxLayout.addWidget(self.save_settings_pushButton)

        self.gridLayout.addLayout(self.buttons_HBoxLayout, 10, 0, 1, 2)

        self.retranslateUi(Settings)
        QtCore.QMetaObject.connectSlotsByName(Settings)

    def retranslateUi(self, Settings):
        _translate = QtCore.QCoreApplication.translate
        Settings.setWindowTitle(_translate("Settings", "Options"))
        self.device_settings_header_label.setText(
            _translate("Settings", "Device Settings")
        )
        self.keithley_source_address_label.setText(
            _translate("Settings", "Keithley Source Address")
        )
        self.keithley_multimeter_address_label.setText(
            _translate("Settings", "Keithley Multimeter Address")
        )
        self.arduino_com_address_label.setText(
            _translate("Settings", "Arduino Com Address")
        )
        self.motor_number_label.setText(_translate("Settings", "Motor Number"))
        self.motor_offset_label.setText(
            _translate("Settings", "Motor Offset Angle (°)")
        )
        self.spectrum_integration_time_label.setText(
            _translate("Settings", "Goniometer Spectrum Integration Time (us)")
        )
        self.photodiode_gain_label.setText(
            _translate("Settings", "Photodiode Gain (dB)")
        )
        self.photodiode_saturation_label.setText(
            _translate("Settings", "Photodiode Saturation (V)")
        )

        self.save_settings_pushButton.setText(_translate("Settings", "Save Settings"))
        self.load_defaults_pushButton.setText(_translate("Settings", "Load Defaults"))