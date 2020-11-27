# -*- coding: utf-8 -*-

# Initial gui design with QtCreator then translated into python code and adjusted

from PySide2 import QtCore, QtGui, QtWidgets


class Ui_Settings(object):
    def setupUi(self, Settings):
        Settings.setObjectName("Settings")
        Settings.resize(509, 317)
        Settings.setStyleSheet(
            "background-color: rgb(44, 49, 60);\n"
            "color: rgb(255, 255, 255);\n"
            'font: 63 10pt "Segoe UI";\n'
            ""
        )
        self.gridLayout = QtWidgets.QGridLayout(Settings)
        self.gridLayout.setContentsMargins(25, 10, 25, 10)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(Settings)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(Settings)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 5, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(Settings)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(Settings)
        self.label_5.setMinimumSize(QtCore.QSize(0, 20))
        self.label_5.setStyleSheet('font: 75 bold 10pt "Noto Sans";')
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 2)
        self.doubleSpinBox_4 = QtWidgets.QDoubleSpinBox(Settings)
        self.doubleSpinBox_4.setObjectName("doubleSpinBox_4")
        self.gridLayout.addWidget(self.doubleSpinBox_4, 5, 1, 1, 1)
        self.pushButton = QtWidgets.QPushButton(Settings)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 7, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(Settings)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(Settings)
        self.label.setMinimumSize(QtCore.QSize(0, 20))
        self.label.setStyleSheet('font: 75 bold 10pt "Noto Sans";')
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.doubleSpinBox_2 = QtWidgets.QDoubleSpinBox(Settings)
        self.doubleSpinBox_2.setObjectName("doubleSpinBox_2")
        self.gridLayout.addWidget(self.doubleSpinBox_2, 2, 1, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(Settings)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 7, 1, 1, 1)
        self.doubleSpinBox_3 = QtWidgets.QDoubleSpinBox(Settings)
        self.doubleSpinBox_3.setObjectName("doubleSpinBox_3")
        self.gridLayout.addWidget(self.doubleSpinBox_3, 3, 1, 1, 1)
        self.doubleSpinBox = QtWidgets.QDoubleSpinBox(Settings)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.gridLayout.addWidget(self.doubleSpinBox, 1, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(Settings)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 6, 0, 1, 1)
        self.doubleSpinBox_5 = QtWidgets.QDoubleSpinBox(Settings)
        self.doubleSpinBox_5.setObjectName("doubleSpinBox_5")
        self.gridLayout.addWidget(self.doubleSpinBox_5, 6, 1, 1, 1)

        self.retranslateUi(Settings)
        QtCore.QMetaObject.connectSlotsByName(Settings)

    def retranslateUi(self, Settings):
        _translate = QtCore.QCoreApplication.translate
        Settings.setWindowTitle(_translate("Settings", "Options"))
        self.label_2.setText(_translate("Settings", "TextLabel"))
        self.label_6.setText(_translate("Settings", "TextLabel"))
        self.label_4.setText(_translate("Settings", "TextLabel"))
        self.label_5.setText(_translate("Settings", "Other Settings"))
        self.pushButton.setText(_translate("Settings", "Save Settings"))
        self.label_3.setText(_translate("Settings", "TextLabel"))
        self.label.setText(_translate("Settings", "Global Settings"))
        self.pushButton_2.setText(_translate("Settings", "Cancel"))
        self.label_7.setText(_translate("Settings", "TextLabel"))

    # ------------------------------------------------------------------------ #
    # ----------------- User Defined UI related Functions -------------------- #
    # ------------------------------------------------------------------------ #

    def center(self):
        # position and size of main window

        # self.showFullScreen()
        qc = self.frameGeometry()
        # desktopWidget = QtWidgets.QApplication.desktop()
        # PCGeometry = desktopWidget.screenGeometry()
        # self.resize(PCGeometry.height(), PCGeometry.height())
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qc.moveCenter(cp)
        self.move(qc.topLeft())


# if __name__ == "__main__":
# import sys
#
# app = QtWidgets.QApplication(sys.argv)
# Settings = QtWidgets.QWidget()
# ui = Ui_Settings()
# ui.setupUi(Settings)
# Settings.show()
# sys.exit(app.exec_())
