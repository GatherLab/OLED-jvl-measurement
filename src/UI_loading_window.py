# -*- coding: utf-8 -*-

# Template by Wanderson-Magalhaes

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtGui import QLinearGradient


class Ui_LoadingWindow(object):
    def setupUi(self, LoadingWindow):
        if LoadingWindow.objectName():
            LoadingWindow.setObjectName(u"LoadingWindow")
        LoadingWindow.resize(680, 400)
        self.centralwidget = QtWidgets.QWidget()
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(LoadingWindow)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.dropShadowFrame = QtWidgets.QFrame(self.centralwidget)
        self.dropShadowFrame.setObjectName(u"dropShadowFrame")
        self.dropShadowFrame.setStyleSheet(
            u"QFrame {	\n"
            "background-color: rgb(44, 49, 60);\n"
            "	color: rgb(220, 220, 220);\n"
            "	border-radius: 10px;\n"
            "}"
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
        self.dropShadowFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.dropShadowFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label_title = QtWidgets.QLabel(self.dropShadowFrame)
        self.label_title.setObjectName(u"label_title")
        self.label_title.setGeometry(QtCore.QRect(0, 90, 661, 61))
        font = QtGui.QFont()
        font.setFamily(u"Segoe UI")
        font.setPointSize(40)
        self.label_title.setFont(font)
        self.label_title.setStyleSheet(u"color: rgb(85, 170, 255);")
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        self.label_description = QtWidgets.QLabel(self.dropShadowFrame)
        self.label_description.setObjectName(u"label_description")
        self.label_description.setGeometry(QtCore.QRect(0, 150, 661, 31))
        font1 = QtGui.QFont()
        font1.setFamily(u"Segoe UI")
        font1.setPointSize(14)
        self.label_description.setFont(font1)
        self.label_description.setStyleSheet(u"color: rgb(98, 114, 164);")
        self.label_description.setAlignment(QtCore.Qt.AlignCenter)

        # self.horizontal_layout = QtWidgets.QGridLayout(self.dropShadowFrame)
        # self.horizontal_layout.setGeometry(QtCore.QRect(0, 150, 661, 31))
        self.button_retry = QtWidgets.QPushButton(self.dropShadowFrame)
        self.button_retry.setGeometry(QtCore.QRect(100, 220, 220, 31))
        self.button_continue = QtWidgets.QPushButton(self.dropShadowFrame)
        self.button_continue.setGeometry(QtCore.QRect(360, 220, 220, 31))

        # Hide because they shall be only shown sometimes
        self.button_retry.hide()
        self.button_continue.hide()

        self.progressBar = QtWidgets.QProgressBar(self.dropShadowFrame)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QtCore.QRect(50, 280, 561, 23))
        self.progressBar.setStyleSheet(
            u"QProgressBar {\n"
            "	\n"
            "	background-color: rgb(98, 114, 164);\n"
            "	color: rgb(20, 20, 20);\n"
            "	border-style: none;\n"
            "	border-radius: 10px;\n"
            "	text-align: center;\n"
            "}\n"
            "QProgressBar::chunk{\n"
            "	border-radius: 10px;\n"
            "	background-color: qlineargradient(spread:pad, x1:0, y1:0.511364, x2:1, y2:0.523, stop:0 rgb(85, 139, 255), stop:1 rgb(85, 255, 232));\n"
            "}"
        )
        self.progressBar.setValue(24)
        self.label_loading = QtWidgets.QLabel(self.dropShadowFrame)
        self.label_loading.setObjectName(u"label_loading")
        self.label_loading.setGeometry(QtCore.QRect(0, 320, 661, 21))
        font2 = QtGui.QFont()
        font2.setFamily(u"Segoe UI")
        font2.setPointSize(12)
        self.label_loading.setFont(font2)
        self.label_loading.setStyleSheet(u"color: rgb(98, 114, 164);")
        self.label_loading.setAlignment(QtCore.Qt.AlignCenter)
        self.label_credits = QtWidgets.QLabel(self.dropShadowFrame)
        self.label_credits.setObjectName(u"label_credits")
        self.label_credits.setGeometry(QtCore.QRect(20, 350, 621, 21))
        font3 = QtGui.QFont()
        font3.setFamily(u"Segoe UI")
        font3.setPointSize(10)
        self.label_credits.setFont(font3)
        self.label_credits.setStyleSheet(u"color: rgb(98, 114, 164);")
        self.label_credits.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )

        self.verticalLayout.addWidget(self.dropShadowFrame)

        # LoadingWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(LoadingWindow)

        QtCore.QMetaObject.connectSlotsByName(LoadingWindow)

    # setupUi

    def retranslateUi(self, LoadingWindow):

        _translate = QtCore.QCoreApplication.translate
        LoadingWindow.setWindowTitle(_translate("LoadingWindow", u"MainWindow", None))
        self.label_title.setText(
            _translate("LoadingWindow", u"<strong>OLED</strong> Characterisation", None)
        )
        self.label_description.setText(
            _translate("LoadingWindow", u"<strong>APP</strong> DESCRIPTION", None)
        )
        self.label_loading.setText(_translate("LoadingWindow", u"loading...", None))
        self.label_credits.setText(
            _translate(
                "LoadingWindow",
                u"GatherLab",
                None,
            )
        )
        self.button_retry.setText(_translate("MainWindow", "Retry"))
        self.button_continue.setText(_translate("MainWindow", "Continue Anyways"))
