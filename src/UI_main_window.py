from costum_widgets import (
    HumbleDoubleSpinBox,
    HumbleSpinBox,
    ToggleSwitch,
    Ui_GoniometerAnimation,
)

from PySide6 import QtCore, QtGui, QtWidgets

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure


# ---------------------------------------------------------------------------- #
# --------------------------- Define Main Window ----------------------------- #
# ---------------------------------------------------------------------------- #
class Ui_MainWindow(object):
    """
    Class that contains all information about the main window
    """

    def setupUi(self, MainWindow):
        """
        Setup that sets all gui widgets at their place
        """

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 800)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(0, 0))
        MainWindow.setStyleSheet(
            "QWidget {\n"
            "            background-color: rgb(44, 49, 60);\n"
            "            color: rgb(255, 255, 255);\n"
            '            font: 63 10pt "Segoe UI";\n'
            "}\n"
            "QPushButton {\n"
            "            border: 2px solid rgb(52, 59, 72);\n"
            "            border-radius: 5px;\n"
            "            background-color: rgb(52, 59, 72);\n"
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
            "QLineEdit {\n"
            "            border: 2px solid rgb(61, 70, 86);\n"
            "            border-radius: 5px;\n"
            "            background-color: rgb(52, 59, 72);\n"
            "}\n"
            "QSpinBox {\n"
            "            border: 2px solid rgb(61, 70, 86);\n"
            "            border-radius: 5px;\n"
            "            background-color: rgb(52, 59, 72);\n"
            "}\n"
            "HumbleDoubleSpinBox {\n"
            "            border: 2px solid rgb(61, 70, 86);\n"
            "            border-radius: 5px;\n"
            "            background-color: rgb(52, 59, 72);\n"
            "}\n"
            "QScrollArea {\n"
            "            border: 2px solid rgb(61, 70, 86);\n"
            "            border-radius: 5px;\n"
            "}\n"
            "QScrollBar {\n"
            "            border-radius: 5px;\n"
            "            background: rgb(61, 70, 86);\n"
            "}\n"
            "QScrollBar:add-page {\n"
            "            background: rgb(52, 59, 72);\n"
            "}\n"
            "QScrollBar:sub-page {\n"
            "            background: rgb(52, 59, 72);\n"
            "}\n"
        )

        self.center()

        # Define central widget of the MainWindow
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        # self.centralwidget.setStyleSheet(
        #     "QLineEdit {\n"
        #     "            border: 2px solid rgb(61, 70, 86);\n"
        #     "            border-radius: 5px;\n"
        #     "            background-color: rgb(52, 59, 72);\n"
        #     "}\n"
        #     "QSpinBox {\n"
        #     "            border: 2px solid rgb(61, 70, 86);\n"
        #     "            border-radius: 5px;\n"
        #     "            background-color: rgb(52, 59, 72);\n"
        #     "}\n"
        #     "HumbleDoubleSpinBox {\n"
        #     "            border: 2px solid rgb(61, 70, 86);\n"
        #     "            border-radius: 5px;\n"
        #     "            background-color: rgb(52, 59, 72);\n"
        #     "}\n"
        #     "QScrollArea {\n"
        #     "            border: 2px solid rgb(61, 70, 86);\n"
        #     "            border-radius: 5px;\n"
        #     "}\n"
        #     "QScrollBar {\n"
        #     # "            border: 2px solid rgb(85, 170, 255);\n"
        #     "            border-radius: 5px;\n"
        #     "            background: rgb(61, 70, 86);\n"
        #     "}\n"
        #     "QScrollBar:add-page {\n"
        #     "            background: rgb(52, 59, 72);\n"
        #     "}\n"
        #     "QScrollBar:sub-page {\n"
        #     "            background: rgb(52, 59, 72);\n"
        #     "}\n"
        # )
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(-1, -1, -1, 6)
        self.gridLayout.setObjectName("gridLayout")

        # This here shall be the logo of the program
        # self.gatherlab_picture = QtWidgets.QWidget(self.centralwidget)
        # self.gatherlab_picture.setObjectName("gatherlab_picture")
        self.gatherlab_label = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap("icons/blue_cropped.png")
        self.gatherlab_label.setPixmap(pixmap)
        self.gatherlab_label.setScaledContents(True)
        # self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        # self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        # self.gatherlab_picture.setLayout(self.horizontalLayout_2)
        self.gridLayout.addWidget(self.gatherlab_label, 0, 0, 1, 1)

        # Tab widget
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setStyleSheet(
            "QTabBar {\n"
            "        font-weight: bold;\n"
            "}\n"
            "QTabBar:tab {\n"
            "            background: rgb(52, 59, 72);\n"
            "}\n"
            "QTabBar:tab:selected {\n"
            "            background: rgb(61, 70, 86);\n"
            "            color: rgb(85, 170, 255);\n"
            "}\n"
            "QTabBar:tab:hover {\n"
            "            color: rgb(85, 170, 255);\n"
            "}\n"
            "QTabWidget:pane {\n"
            "            border: 2px solid rgb(52, 59, 72);\n"
            "}\n"
        )

        # -------------------------------------------------------------------- #
        # --------------------------- Setup widget --------------------------- #
        # -------------------------------------------------------------------- #
        self.setup_widget = QtWidgets.QWidget()
        self.setup_widget.setObjectName("setup_widget")
        # self.gridLayout_5 = QtWidgets.QGridLayout(self.setup_widget)
        # self.gridLayout_5.setObjectName("gridLayout_5")
        # self.setup_sub_widget = QtWidgets.QWidget(self.setup_widget)
        # self.setup_sub_widget.setObjectName("setup_sub_widget")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.setup_widget)
        self.gridLayout_7.setObjectName("gridLayout_7")

        # Setup widget base folder path
        self.sw_folder_path_horizontalLayout = QtWidgets.QHBoxLayout()
        self.sw_folder_path_horizontalLayout.setObjectName(
            "sw_folder_path_horizontalLayout"
        )
        self.sw_folder_path_lineEdit = QtWidgets.QLineEdit(self.setup_widget)
        self.sw_folder_path_lineEdit.setReadOnly(False)
        self.sw_folder_path_lineEdit.setObjectName("sw_folder_path_lineEdit")
        self.sw_folder_path_horizontalLayout.addWidget(self.sw_folder_path_lineEdit)
        self.sw_browse_pushButton = QtWidgets.QPushButton(self.setup_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.sw_browse_pushButton.sizePolicy().hasHeightForWidth()
        )
        self.sw_browse_pushButton.setSizePolicy(sizePolicy)
        self.sw_browse_pushButton.setMinimumSize(QtCore.QSize(60, 0))
        self.sw_browse_pushButton.setObjectName("sw_browse_pushButton")
        self.sw_folder_path_horizontalLayout.addWidget(self.sw_browse_pushButton)
        self.gridLayout_7.addLayout(self.sw_folder_path_horizontalLayout, 1, 1, 1, 1)
        self.sw_folder_path_label = QtWidgets.QLabel(self.setup_widget)
        self.sw_folder_path_label.setObjectName("sw_folder_path_label")
        self.gridLayout_7.addWidget(self.sw_folder_path_label, 1, 0, 1, 1)

        # Setup widget batch name
        self.sw_batch_name_label = QtWidgets.QLabel(self.setup_widget)
        self.sw_batch_name_label.setObjectName("sw_batch_name_label")
        self.gridLayout_7.addWidget(self.sw_batch_name_label, 2, 0, 1, 1)
        self.sw_batch_name_lineEdit = QtWidgets.QLineEdit(self.setup_widget)
        self.sw_batch_name_lineEdit.setObjectName("sw_batch_name_lineEdit")
        self.gridLayout_7.addWidget(self.sw_batch_name_lineEdit, 2, 1, 1, 1)

        # Setup widget device number
        self.sw_device_number_label = QtWidgets.QLabel(self.setup_widget)
        self.sw_device_number_label.setObjectName("sw_device_number_label")
        self.gridLayout_7.addWidget(self.sw_device_number_label, 3, 0, 1, 1)
        self.sw_device_number_spinBox = HumbleSpinBox(self.setup_widget)
        self.sw_device_number_spinBox.setObjectName("sw_device_number_spinBox")
        self.gridLayout_7.addWidget(self.sw_device_number_spinBox, 3, 1, 1, 1)

        # Setup widget documentation
        # self.sw_documentation_textEdit = QtWidgets.QTextEdit(self.setup_widget)
        # self.sw_documentation_textEdit.setObjectName("sw_documentation_textEdit")
        # self.gridLayout_7.addWidget(self.sw_documentation_textEdit, 12, 1, 1, 1)
        # self.sw_documentation_label = QtWidgets.QLabel(self.setup_widget)
        # self.sw_documentation_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        # self.sw_documentation_label.setObjectName("sw_documentation_label")
        # self.gridLayout_7.addWidget(self.sw_documentation_label, 12, 0, 1, 1)

        # Setup widget header 1
        self.sw_header1_label = QtWidgets.QLabel(self.setup_widget)
        self.sw_header1_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.sw_header1_label.setObjectName("sw_header1_label")
        self.gridLayout_7.addWidget(self.sw_header1_label, 0, 0, 1, 1)

        # ------------- Setup widget, Select pixels to test ------------------ #
        self.sw_select_pixel_widget = QtWidgets.QWidget(self.setup_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(
            self.sw_select_pixel_widget.sizePolicy().hasHeightForWidth()
        )
        self.sw_select_pixel_widget.setSizePolicy(sizePolicy)
        # self.sw_select_pixel_widget.setMinimumSize(QtCore.QSize(150, 0))
        # self.sw_select_pixel_widget.setMaximumSize(QtCore.QSize(250, 200))
        self.sw_select_pixel_widget.setObjectName("sw_select_pixel_widget")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.sw_select_pixel_widget)
        self.gridLayout_6.setObjectName("gridLayout_6")

        # Setup widget header
        self.sw_header2_label = QtWidgets.QLabel(self.setup_widget)
        self.sw_header2_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.sw_header2_label.setObjectName("sw_header2_label")
        self.gridLayout_6.addWidget(self.sw_header2_label, 0, 0, 1, 2)

        # Top or bottom emitting
        self.sw_top_emitting_HLayout = QtWidgets.QHBoxLayout()
        self.sw_top_emitting_toggleSwitch = ToggleSwitch()
        self.sw_top_emitting_label = QtWidgets.QLabel("Top Emitting")
        self.sw_top_emitting_HLayout.addWidget(self.sw_top_emitting_toggleSwitch)
        self.sw_top_emitting_HLayout.addWidget(self.sw_top_emitting_label)
        self.gridLayout_6.addLayout(self.sw_top_emitting_HLayout, 1, 0, 1, 2)

        # pin or nip
        self.sw_nip_HLayout = QtWidgets.QHBoxLayout()
        self.sw_nip_toggleSwitch = ToggleSwitch()
        self.sw_nip_label = QtWidgets.QLabel("common cathode")
        self.sw_nip_HLayout.addWidget(self.sw_nip_toggleSwitch)
        self.sw_nip_HLayout.addWidget(self.sw_nip_label)
        self.gridLayout_6.addLayout(self.sw_nip_HLayout, 2, 0, 1, 2)

        # Activate local mode button
        self.sw_reset_hardware_pushButton = QtWidgets.QPushButton(
            self.sw_select_pixel_widget
        )
        self.sw_reset_hardware_pushButton.setObjectName("sw_reset_hardware_pushButton")
        # self.sw_reset_hardware_horizontalLayout.addWidget(self.sw_browse_pushButton)
        self.gridLayout_6.addWidget(self.sw_reset_hardware_pushButton, 3, 0, 1, 2)

        # Select pixel label
        self.sw_pixel_label = QtWidgets.QLabel(self.sw_select_pixel_widget)
        self.sw_pixel_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.sw_pixel_label.setObjectName("sw_pixel_label")
        self.gridLayout_6.addWidget(self.sw_pixel_label, 4, 0, 1, 1)

        # Pixel 1
        self.sw_pixel1_pushButton = QtWidgets.QPushButton(self.sw_select_pixel_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.sw_pixel1_pushButton.sizePolicy().hasHeightForWidth()
        )
        self.sw_pixel1_pushButton.setSizePolicy(sizePolicy)
        self.sw_pixel1_pushButton.setMinimumSize(QtCore.QSize(0, 0))
        self.sw_pixel1_pushButton.setCheckable(True)
        self.sw_pixel1_pushButton.setChecked(False)
        self.sw_pixel1_pushButton.setAutoRepeat(False)
        self.sw_pixel1_pushButton.setObjectName("sw_pixel1_pushButton")
        self.gridLayout_6.addWidget(self.sw_pixel1_pushButton, 5, 0, 1, 1)

        # Pixel 2
        self.sw_pixel2_pushButton = QtWidgets.QPushButton(self.sw_select_pixel_widget)
        self.sw_pixel2_pushButton.setCheckable(True)
        self.sw_pixel2_pushButton.setChecked(False)
        self.sw_pixel2_pushButton.setObjectName("sw_pixel2_pushButton")
        self.gridLayout_6.addWidget(self.sw_pixel2_pushButton, 6, 0, 1, 1)

        # Pixel 3
        self.sw_pixel3_pushButton = QtWidgets.QPushButton(self.sw_select_pixel_widget)
        self.sw_pixel3_pushButton.setCheckable(True)
        self.sw_pixel3_pushButton.setChecked(False)
        self.sw_pixel3_pushButton.setObjectName("sw_pixel3_pushButton")
        self.gridLayout_6.addWidget(self.sw_pixel3_pushButton, 7, 0, 1, 1)

        # Pixel 4
        self.sw_pixel4_pushButton = QtWidgets.QPushButton(self.sw_select_pixel_widget)
        self.sw_pixel4_pushButton.setCheckable(True)
        self.sw_pixel4_pushButton.setChecked(False)
        self.sw_pixel4_pushButton.setObjectName("sw_pixel4_pushButton")
        self.gridLayout_6.addWidget(self.sw_pixel4_pushButton, 8, 0, 1, 1)

        # Pixel 5
        self.sw_pixel5_pushButton = QtWidgets.QPushButton(self.sw_select_pixel_widget)
        self.sw_pixel5_pushButton.setCheckable(True)
        self.sw_pixel5_pushButton.setChecked(False)
        self.sw_pixel5_pushButton.setObjectName("sw_pixel5_pushButton")
        self.gridLayout_6.addWidget(self.sw_pixel5_pushButton, 5, 1, 1, 1)

        # Pixel 6
        self.sw_pixel6_pushButton = QtWidgets.QPushButton(self.sw_select_pixel_widget)
        self.sw_pixel6_pushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.sw_pixel6_pushButton.setCheckable(True)
        self.sw_pixel6_pushButton.setChecked(False)
        self.sw_pixel6_pushButton.setObjectName("sw_pixel6_pushButton")
        self.gridLayout_6.addWidget(self.sw_pixel6_pushButton, 6, 1, 1, 1)

        # Pixel 7
        self.sw_pixel7_pushButton = QtWidgets.QPushButton(self.sw_select_pixel_widget)
        self.sw_pixel7_pushButton.setCheckable(True)
        self.sw_pixel7_pushButton.setChecked(False)
        self.sw_pixel7_pushButton.setObjectName("sw_pixel7_pushButton")
        self.gridLayout_6.addWidget(self.sw_pixel7_pushButton, 7, 1, 1, 1)

        # Pixel 8
        self.sw_pixel8_pushButton = QtWidgets.QPushButton(self.sw_select_pixel_widget)
        self.sw_pixel8_pushButton.setCheckable(True)
        self.sw_pixel8_pushButton.setChecked(False)
        self.sw_pixel8_pushButton.setObjectName("sw_pixel8_pushButton")
        self.gridLayout_6.addWidget(self.sw_pixel8_pushButton, 8, 1, 1, 1)

        # Select all
        self.sw_select_all_pushButton = QtWidgets.QPushButton(
            self.sw_select_pixel_widget
        )
        self.sw_select_all_pushButton.setObjectName("sw_select_all_pushButton")
        self.gridLayout_6.addWidget(self.sw_select_all_pushButton, 9, 0, 1, 1)

        # Unselect all
        self.sw_unselect_all_push_button = QtWidgets.QPushButton(
            self.sw_select_pixel_widget
        )
        self.sw_unselect_all_push_button.setObjectName("sw_unselect_all_push_button")
        self.gridLayout_6.addWidget(self.sw_unselect_all_push_button, 9, 1, 1, 1)

        # Prebias all
        self.sw_prebias_pushButton = QtWidgets.QPushButton(self.sw_select_pixel_widget)
        self.sw_prebias_pushButton.setObjectName("sw_prebias_pushButton")
        self.sw_prebias_pushButton.setMinimumHeight(10)
        self.gridLayout_6.addWidget(self.sw_prebias_pushButton, 10, 0, 1, 1)

        # Autotest all
        self.sw_auto_test_pushButton = QtWidgets.QPushButton(
            self.sw_select_pixel_widget
        )
        self.sw_auto_test_pushButton.setObjectName("sw_auto_test_pushButton")
        self.gridLayout_6.addWidget(self.sw_auto_test_pushButton, 10, 1, 1, 1)

        # Setup widget current tester voltage

        self.sw_change_voltage_label = QtWidgets.QLabel(self.sw_select_pixel_widget)
        self.sw_change_voltage_label.setObjectName("sw_change_voltage_label")
        self.gridLayout_6.addWidget(self.sw_change_voltage_label, 11, 0, 1, 2)
        self.sw_ct_voltage_spinBox = HumbleDoubleSpinBox(self.sw_select_pixel_widget)
        self.sw_ct_voltage_spinBox.setObjectName("sw_ct_voltage_spinBox")
        self.gridLayout_6.addWidget(self.sw_ct_voltage_spinBox, 12, 0, 1, 2)

        self.gridLayout_7.addWidget(self.sw_select_pixel_widget, 4, 0, 1, 1)

        # LCD number widget
        self.sw_current_lcdNumber = QtWidgets.QLCDNumber(self.setup_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.sw_current_lcdNumber.sizePolicy().hasHeightForWidth()
        )
        self.sw_current_lcdNumber.setSizePolicy(sizePolicy)
        self.sw_current_lcdNumber.setDigitCount(10)
        self.sw_current_lcdNumber.setAutoFillBackground(False)
        self.sw_current_lcdNumber.setSmallDecimalPoint(False)
        self.sw_current_lcdNumber.setObjectName("sw_current_lcdNumber")
        # self.sw_current_lcdNumber.display("0.0001 A")
        self.gridLayout_7.addWidget(self.sw_current_lcdNumber, 4, 1, 1, 1)

        self.tabWidget.addTab(self.setup_widget, "")

        # -------------------------------------------------------------------- #
        # ---------------------- Define Autotube Widget ---------------------- #
        # -------------------------------------------------------------------- #
        self.autotube_widget = QtWidgets.QWidget()
        self.autotube_widget.setObjectName("autotube_widget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.autotube_widget)
        self.gridLayout_2.setObjectName("gridLayout_2")

        # --------------- Central Widget with matplotlib graph --------------- #
        self.aw_graph_widget = QtWidgets.QWidget(self.autotube_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.aw_graph_widget.sizePolicy().hasHeightForWidth()
        )
        self.aw_graph_widget.setSizePolicy(sizePolicy)
        self.aw_graph_widget.setMinimumSize(QtCore.QSize(0, 442))
        self.aw_graph_widget.setObjectName("aw_graph_widget")
        self.aw_mpl_graph_gridLayout = QtWidgets.QGridLayout(self.aw_graph_widget)
        self.aw_mpl_graph_gridLayout.setObjectName("aw_mpl_graph_gridLayout")
        self.gridLayout_2.addWidget(self.aw_graph_widget, 0, 1, 1, 1)

        # Define figure
        figureSize = (11, 10)
        self.aw_fig = FigureCanvas(Figure(figsize=figureSize))
        self.aw_mpl_graph_gridLayout.addWidget(self.aw_fig)

        self.aw_ax = self.aw_fig.figure.subplots()
        self.aw_ax.set_facecolor("#FFFFFF")
        self.aw_ax.grid(True)
        self.aw_ax.set_yscale("log")
        self.aw_ax.set_xlabel("Voltage (V)", fontsize=14)
        self.aw_ax.set_ylabel(
            "Abs. Current (mA)", color=(68 / 255, 188 / 255, 65 / 255), fontsize=14
        )
        self.aw_ax.axhline(linewidth=1, color="black")
        # self.aw_ax.axvline(linewidth=1, color="black")
        self.aw_ax2 = self.aw_ax.twinx()
        self.aw_ax2.set_yscale("log")
        self.aw_ax2.set_ylabel(
            "Photodiode Voltage (V)",
            color=(85 / 255, 170 / 255, 255 / 255),
            fontsize=14,
        )
        self.aw_fig.figure.set_facecolor("#FFFFFF")
        self.aw_mplToolbar = NavigationToolbar(self.aw_fig, self.aw_graph_widget)
        self.aw_mplToolbar.setStyleSheet("background-color:#FFFFFF; color:black;")
        self.aw_mpl_graph_gridLayout.addWidget(self.aw_mplToolbar)

        # ----------------------- Define scroll area ---------------------------
        self.aw_scrollArea = QtWidgets.QScrollArea(self.autotube_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.aw_scrollArea.sizePolicy().hasHeightForWidth()
        )
        self.aw_scrollArea.setSizePolicy(sizePolicy)
        self.aw_scrollArea.setMinimumSize(QtCore.QSize(200, 0))
        self.aw_scrollArea.setWidgetResizable(True)
        self.aw_scrollArea.setObjectName("aw_scrollArea")
        self.aw_scrollAreaWidgetContents = QtWidgets.QWidget()
        self.aw_scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 170, 655))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.aw_scrollAreaWidgetContents.sizePolicy().hasHeightForWidth()
        )
        self.aw_scrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.aw_scrollAreaWidgetContents.setObjectName("aw_scrollAreaWidgetContents")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.aw_scrollAreaWidgetContents)
        self.gridLayout_3.setObjectName("gridLayout_3")

        self.aw_header1_label = QtWidgets.QLabel(self.aw_scrollAreaWidgetContents)
        self.aw_header1_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.aw_header1_label.setObjectName("aw_header1_label")
        self.gridLayout_3.addWidget(self.aw_header1_label, 0, 0, 1, 1)
        self.aw_scrollArea.setWidget(self.aw_scrollAreaWidgetContents)
        self.gridLayout_2.addWidget(self.aw_scrollArea, 0, 3, 1, 1)

        # Max voltage
        self.aw_max_voltage_spinBox = HumbleDoubleSpinBox(
            self.aw_scrollAreaWidgetContents
        )
        self.aw_max_voltage_spinBox.setObjectName("aw_max_voltage_spinBox")
        self.gridLayout_3.addWidget(self.aw_max_voltage_spinBox, 4, 0, 1, 1)
        self.aw_max_voltage_label = QtWidgets.QLabel(self.aw_scrollAreaWidgetContents)
        self.aw_max_voltage_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.aw_max_voltage_label.setObjectName("aw_max_voltage_label")
        self.gridLayout_3.addWidget(self.aw_max_voltage_label, 3, 0, 1, 1)

        # High voltage step
        self.aw_high_voltage_step_label = QtWidgets.QLabel(
            self.aw_scrollAreaWidgetContents
        )
        self.aw_high_voltage_step_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.aw_high_voltage_step_label.setObjectName("aw_high_voltage_step_label")
        self.gridLayout_3.addWidget(self.aw_high_voltage_step_label, 9, 0, 1, 1)
        self.aw_high_voltage_step_spinBox = HumbleDoubleSpinBox(
            self.aw_scrollAreaWidgetContents
        )
        self.aw_high_voltage_step_spinBox.setObjectName("aw_high_voltage_step_spinBox")
        self.gridLayout_3.addWidget(self.aw_high_voltage_step_spinBox, 10, 0, 1, 1)

        # ---------------------- Select pixel widget ------------------------- #
        self.aw_select_pixel_widget = QtWidgets.QWidget(
            self.aw_scrollAreaWidgetContents
        )
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.aw_select_pixel_widget.sizePolicy().hasHeightForWidth()
        )
        self.aw_select_pixel_widget.setSizePolicy(sizePolicy)
        self.aw_select_pixel_widget.setMinimumSize(QtCore.QSize(100, 0))
        self.aw_select_pixel_widget.setMaximumSize(QtCore.QSize(150, 124))
        self.aw_select_pixel_widget.setObjectName("aw_select_pixel_widget")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.aw_select_pixel_widget)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.aw_select_pixel_label = QtWidgets.QLabel(self.aw_scrollAreaWidgetContents)
        self.aw_select_pixel_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.aw_select_pixel_label.setObjectName("aw_select_pixel_label")
        self.gridLayout_3.addWidget(self.aw_select_pixel_label, 14, 0, 1, 1)

        # Pixel 1
        self.aw_pixel1_pushButton = QtWidgets.QPushButton(self.aw_select_pixel_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.aw_pixel1_pushButton.sizePolicy().hasHeightForWidth()
        )
        self.aw_pixel1_pushButton.setSizePolicy(sizePolicy)
        self.aw_pixel1_pushButton.setMinimumSize(QtCore.QSize(0, 0))
        self.aw_pixel1_pushButton.setCheckable(True)
        # self.aw_pixel1_pushButton.setChecked(True)
        self.aw_pixel1_pushButton.setAutoRepeat(False)
        self.aw_pixel1_pushButton.setObjectName("aw_pixel1_pushButton")
        self.gridLayout_4.addWidget(self.aw_pixel1_pushButton, 0, 0, 1, 1)

        # Pixel 2
        self.aw_pixel2_pushButton = QtWidgets.QPushButton(self.aw_select_pixel_widget)
        self.aw_pixel2_pushButton.setCheckable(True)
        # self.aw_pixel2_pushButton.setChecked(True)
        self.aw_pixel2_pushButton.setObjectName("aw_pixel2_pushButton")
        self.gridLayout_4.addWidget(self.aw_pixel2_pushButton, 2, 0, 1, 1)

        # Pixel 3
        self.aw_pixel3_pushButton = QtWidgets.QPushButton(self.aw_select_pixel_widget)
        self.aw_pixel3_pushButton.setCheckable(True)
        # self.aw_pixel3_pushButton.setChecked(True)
        self.aw_pixel3_pushButton.setObjectName("aw_pixel3_pushButton")
        self.gridLayout_4.addWidget(self.aw_pixel3_pushButton, 3, 0, 1, 1)

        # Pixel 4
        self.aw_pixel4_pushButton = QtWidgets.QPushButton(self.aw_select_pixel_widget)
        self.aw_pixel4_pushButton.setCheckable(True)
        # self.aw_pixel4_pushButton.setChecked(True)
        self.aw_pixel4_pushButton.setObjectName("aw_pixel4_pushButton")
        self.gridLayout_4.addWidget(self.aw_pixel4_pushButton, 4, 0, 1, 1)

        # Pixel 5
        self.aw_pixel5_pushButton = QtWidgets.QPushButton(self.aw_select_pixel_widget)
        self.aw_pixel5_pushButton.setCheckable(True)
        # self.aw_pixel5_pushButton.setChecked(True)
        self.aw_pixel5_pushButton.setObjectName("aw_pixel5_pushButton")
        self.gridLayout_4.addWidget(self.aw_pixel5_pushButton, 0, 1, 1, 1)

        # Pixel 6
        self.aw_pixel6_pushButton = QtWidgets.QPushButton(self.aw_select_pixel_widget)
        self.aw_pixel6_pushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.aw_pixel6_pushButton.setCheckable(True)
        # self.aw_pixel6_pushButton.setChecked(True)
        self.aw_pixel6_pushButton.setObjectName("aw_pixel6_pushButton")
        self.gridLayout_4.addWidget(self.aw_pixel6_pushButton, 2, 1, 1, 1)

        # Pixel 7
        self.aw_pixel7_pushButton = QtWidgets.QPushButton(self.aw_select_pixel_widget)
        self.aw_pixel7_pushButton.setCheckable(True)
        # self.aw_pixel7_pushButton.setChecked(True)
        self.aw_pixel7_pushButton.setObjectName("aw_pixel7_pushButton")
        self.gridLayout_4.addWidget(self.aw_pixel7_pushButton, 3, 1, 1, 1)

        # Pixel 8
        self.aw_pixel8_pushButton = QtWidgets.QPushButton(self.aw_select_pixel_widget)
        self.aw_pixel8_pushButton.setCheckable(True)
        # self.aw_pixel8_pushButton.setChecked(True)
        self.aw_pixel8_pushButton.setObjectName("aw_pixel8_pushButton")
        self.gridLayout_4.addWidget(self.aw_pixel8_pushButton, 4, 1, 1, 1)

        self.gridLayout_3.addWidget(
            self.aw_select_pixel_widget, 15, 0, 1, 1, QtCore.Qt.AlignHCenter
        )

        # Min voltage
        self.aw_min_voltage_label = QtWidgets.QLabel(self.aw_scrollAreaWidgetContents)
        self.aw_min_voltage_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.aw_min_voltage_label.setObjectName("aw_min_voltage_label")
        self.gridLayout_3.addWidget(self.aw_min_voltage_label, 1, 0, 1, 1)
        self.aw_min_voltage_spinBox = HumbleDoubleSpinBox(
            self.aw_scrollAreaWidgetContents
        )
        self.aw_min_voltage_spinBox.setObjectName("aw_min_voltage_spinBox")
        self.gridLayout_3.addWidget(self.aw_min_voltage_spinBox, 2, 0, 1, 1)

        # Low voltage step
        self.aw_low_voltage_step_label = QtWidgets.QLabel(
            self.aw_scrollAreaWidgetContents
        )
        self.aw_low_voltage_step_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.aw_low_voltage_step_label.setObjectName("aw_low_voltage_step_label")
        self.gridLayout_3.addWidget(self.aw_low_voltage_step_label, 5, 0, 1, 1)
        self.aw_low_voltage_step_spinBox = HumbleDoubleSpinBox(
            self.aw_scrollAreaWidgetContents
        )
        self.aw_low_voltage_step_spinBox.setObjectName("aw_low_voltage_step_spinBox")
        self.gridLayout_3.addWidget(self.aw_low_voltage_step_spinBox, 6, 0, 1, 1)

        # Changeover voltage
        self.aw_changeover_voltage_label = QtWidgets.QLabel(
            self.aw_scrollAreaWidgetContents
        )
        self.aw_changeover_voltage_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.aw_changeover_voltage_label.setObjectName("aw_changeover_voltage_label")
        self.gridLayout_3.addWidget(self.aw_changeover_voltage_label, 7, 0, 1, 1)
        self.aw_changeover_voltage_spinBox = HumbleDoubleSpinBox(
            self.aw_scrollAreaWidgetContents
        )
        self.aw_changeover_voltage_spinBox.setObjectName(
            "aw_changeover_voltage_spinBox"
        )
        self.gridLayout_3.addWidget(self.aw_changeover_voltage_spinBox, 8, 0, 1, 1)

        # Scan compliance
        self.aw_scan_compliance_spinBox = HumbleDoubleSpinBox(
            self.aw_scrollAreaWidgetContents
        )
        self.aw_scan_compliance_spinBox.setObjectName("aw_scan_compliance_spinBox")
        self.gridLayout_3.addWidget(self.aw_scan_compliance_spinBox, 12, 0, 1, 1)
        self.aw_scan_compliance_label = QtWidgets.QLabel(
            self.aw_scrollAreaWidgetContents
        )
        self.aw_scan_compliance_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.aw_scan_compliance_label.setObjectName("aw_scan_compliance_label")
        self.gridLayout_3.addWidget(self.aw_scan_compliance_label, 11, 0, 1, 1)

        # Auto measure spectrum
        self.aw_auto_measure_HLayout = QtWidgets.QHBoxLayout()
        self.aw_auto_measure_toggleSwitch = ToggleSwitch()
        self.aw_auto_measure_label = QtWidgets.QLabel("Auto Position")
        self.aw_auto_measure_HLayout.addWidget(self.aw_auto_measure_toggleSwitch)
        self.aw_auto_measure_HLayout.addWidget(self.aw_auto_measure_label)
        self.gridLayout_3.addLayout(self.aw_auto_measure_HLayout, 13, 0, 1, 1)

        # PD saturation checkbox
        # self.aw_pd_saturation_HLayout = QtWidgets.QHBoxLayout()
        # self.aw_pd_saturation_toggleSwitch = ToggleSwitch()
        # self.aw_pd_saturation_label = QtWidgets.QLabel("PD Saturation")
        # self.aw_pd_saturation_HLayout.addWidget(self.aw_pd_saturation_toggleSwitch)
        # self.aw_pd_saturation_HLayout.addWidget(self.aw_pd_saturation_label)

        # self.aw_pd_saturation_checkBox = QtWidgets.QCheckBox(
        # self.aw_scrollAreaWidgetContents
        # )
        # self.aw_pd_saturation_checkBox.setObjectName("aw_pd_saturation_checkBox")
        # self.gridLayout_3.addLayout(self.aw_pd_saturation_HLayout, 14, 0, 1, 1)

        # Check for bad contacts
        # self.aw_bad_contacts_HLayout = QtWidgets.QHBoxLayout()
        # self.aw_bad_contacts_toggleSwitch = ToggleSwitch()
        # self.aw_bad_contacts_label = QtWidgets.QLabel("Check Bad Contacts")
        # self.aw_bad_contacts_HLayout.addWidget(self.aw_bad_contacts_toggleSwitch)
        # self.aw_bad_contacts_HLayout.addWidget(self.aw_bad_contacts_label)
        # self.gridLayout_3.addLayout(self.aw_bad_contacts_HLayout, 13, 0, 1, 1)

        # Manually set multimeter range
        # self.aw_set_fixed_multimeter_range_HLayout = QtWidgets.QHBoxLayout()
        # self.aw_set_fixed_multimeter_range_toggleSwitch = ToggleSwitch()
        # self.aw_set_fixed_multimeter_range_label = QtWidgets.QLabel("Set Fixed Range")
        # self.aw_set_fixed_multimeter_range_HLayout.addWidget(
        # self.aw_set_fixed_multimeter_range_toggleSwitch
        # )
        # self.aw_set_fixed_multimeter_range_HLayout.addWidget(
        # self.aw_set_fixed_multimeter_range_label
        # )
        # self.gridLayout_3.addLayout(
        # self.aw_set_fixed_multimeter_range_HLayout, 13, 0, 1, 1
        # )

        # Start measurement button
        self.aw_start_measurement_pushButton = QtWidgets.QPushButton(
            self.aw_scrollAreaWidgetContents
        )
        self.aw_start_measurement_pushButton.setCheckable(True)
        self.aw_start_measurement_pushButton.setObjectName(
            "aw_start_measurement_pushButton"
        )
        self.gridLayout_3.addWidget(self.aw_start_measurement_pushButton, 16, 0, 1, 1)

        self.tabWidget.addTab(self.autotube_widget, "")

        # -------------------------------------------------------------------- #
        # ---------------------- Define Spectrum Widget ---------------------- #
        # -------------------------------------------------------------------- #
        self.spectrum_widget = QtWidgets.QWidget()
        self.spectrum_widget.setObjectName("spectrum_widget")
        self.spectrum_widget_gridLayout = QtWidgets.QGridLayout(self.spectrum_widget)
        self.spectrum_widget_gridLayout.setObjectName("spectrum_widget_gridLayout")

        # --------------- Central Widget with matplotlib graph --------------- #
        self.specw_graph_widget = QtWidgets.QWidget(self.spectrum_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.specw_graph_widget.sizePolicy().hasHeightForWidth()
        )
        self.specw_graph_widget.setSizePolicy(sizePolicy)
        self.specw_graph_widget.setMinimumSize(QtCore.QSize(0, 442))
        self.specw_graph_widget.setObjectName("specw_graph_widget")
        self.specw_mpl_graph_gridLayout = QtWidgets.QGridLayout(self.specw_graph_widget)
        self.specw_mpl_graph_gridLayout.setObjectName("specw_mpl_graph_gridLayout")
        self.spectrum_widget_gridLayout.addWidget(self.specw_graph_widget, 0, 1, 1, 1)

        # Define figure
        figureSize = (11, 10)
        self.specw_fig = FigureCanvas(Figure(figsize=figureSize))
        self.specw_mpl_graph_gridLayout.addWidget(self.specw_fig)

        self.specw_ax = self.specw_fig.figure.subplots()
        self.specw_ax.set_facecolor("#FFFFFF")
        self.specw_ax.grid(True)
        self.specw_ax.set_xlabel("Wavelength (nm)", fontsize=14)
        self.specw_ax.set_ylabel("Intensity (a.u.)", fontsize=14)
        self.specw_ax.set_xlim([350, 930])

        self.specw_ax.axhline(linewidth=1, color="black")
        self.specw_ax.axvline(linewidth=1, color="black")

        self.specw_fig.figure.set_facecolor("#FFFFFF")
        self.specw_mplToolbar = NavigationToolbar(
            self.specw_fig, self.specw_graph_widget
        )
        self.specw_mplToolbar.setStyleSheet("background-color:#FFFFFF; color: black;")
        self.specw_mpl_graph_gridLayout.addWidget(self.specw_mplToolbar)

        # ----------------------- Define scroll area ---------------------------
        self.specw_scrollArea = QtWidgets.QScrollArea(self.spectrum_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.specw_scrollArea.sizePolicy().hasHeightForWidth()
        )
        self.specw_scrollArea.setSizePolicy(sizePolicy)
        self.specw_scrollArea.setMinimumSize(QtCore.QSize(200, 0))
        self.specw_scrollArea.setWidgetResizable(True)
        self.specw_scrollArea.setObjectName("specw_scrollArea")
        self.specw_scrollAreaWidgetContents = QtWidgets.QWidget()
        self.specw_scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 170, 655))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.specw_scrollAreaWidgetContents.sizePolicy().hasHeightForWidth()
        )
        self.specw_scrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.specw_scrollAreaWidgetContents.setObjectName(
            "specw_scrollAreaWidgetContents"
        )
        self.specw_scrollArea_gridLayout = QtWidgets.QGridLayout(
            self.specw_scrollAreaWidgetContents
        )
        self.specw_scrollArea_gridLayout.setObjectName("specw_scrollArea_gridLayout")

        self.specw_header1_label = QtWidgets.QLabel(self.specw_scrollAreaWidgetContents)
        self.specw_header1_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.specw_header1_label.setObjectName("specw_header1_label")
        self.specw_scrollArea_gridLayout.addWidget(self.specw_header1_label, 0, 0, 1, 1)
        self.specw_scrollArea.setWidget(self.specw_scrollAreaWidgetContents)
        self.spectrum_widget_gridLayout.addWidget(self.specw_scrollArea, 0, 3, 1, 1)

        # Set voltage
        self.specw_voltage_label = QtWidgets.QLabel(self.specw_scrollAreaWidgetContents)
        self.specw_voltage_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.specw_voltage_label.setObjectName("specw_voltage_label")
        self.specw_scrollArea_gridLayout.addWidget(self.specw_voltage_label, 1, 0, 1, 1)
        self.specw_voltage_spinBox = HumbleDoubleSpinBox(
            self.specw_scrollAreaWidgetContents
        )
        self.specw_voltage_spinBox.setObjectName("specw_voltage_spinBox")
        self.specw_scrollArea_gridLayout.addWidget(
            self.specw_voltage_spinBox, 2, 0, 1, 1
        )

        # Integration time
        self.specw_integration_time_label = QtWidgets.QLabel(
            self.specw_scrollAreaWidgetContents
        )
        self.specw_integration_time_label.setStyleSheet(
            'font: 63 bold 10pt "Segoe UI";'
        )
        self.specw_integration_time_label.setObjectName("specw_integration_time_label")
        self.specw_scrollArea_gridLayout.addWidget(
            self.specw_integration_time_label, 3, 0, 1, 1
        )
        self.specw_integration_time_spinBox = HumbleDoubleSpinBox(
            self.specw_scrollAreaWidgetContents
        )
        self.specw_integration_time_spinBox.setObjectName(
            "specw_integration_time_spinBox"
        )
        self.specw_scrollArea_gridLayout.addWidget(
            self.specw_integration_time_spinBox, 4, 0, 1, 1
        )

        # ---------------------- Select pixel widget ------------------------- #
        self.specw_select_pixel_widget = QtWidgets.QWidget(
            self.specw_scrollAreaWidgetContents
        )
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.specw_select_pixel_widget.sizePolicy().hasHeightForWidth()
        )
        self.specw_select_pixel_widget.setSizePolicy(sizePolicy)
        self.specw_select_pixel_widget.setMinimumSize(QtCore.QSize(100, 0))
        self.specw_select_pixel_widget.setMaximumSize(QtCore.QSize(150, 124))
        self.specw_select_pixel_widget.setObjectName("specw_select_pixel_widget")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.specw_select_pixel_widget)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.specw_select_pixel_label = QtWidgets.QLabel(
            self.specw_scrollAreaWidgetContents
        )
        self.specw_select_pixel_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.specw_select_pixel_label.setObjectName("specw_select_pixel_label")
        self.specw_scrollArea_gridLayout.addWidget(
            self.specw_select_pixel_label, 5, 0, 1, 1
        )

        # Pixel 1
        self.specw_pixel1_pushButton = QtWidgets.QPushButton(
            self.specw_select_pixel_widget
        )
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.specw_pixel1_pushButton.sizePolicy().hasHeightForWidth()
        )
        self.specw_pixel1_pushButton.setSizePolicy(sizePolicy)
        self.specw_pixel1_pushButton.setMinimumSize(QtCore.QSize(0, 0))
        self.specw_pixel1_pushButton.setCheckable(True)
        self.specw_pixel1_pushButton.setChecked(False)
        self.specw_pixel1_pushButton.setAutoRepeat(False)
        self.specw_pixel1_pushButton.setObjectName("specw_pixel1_pushButton")
        self.gridLayout_4.addWidget(self.specw_pixel1_pushButton, 0, 0, 1, 1)

        # Pixel 2
        self.specw_pixel2_pushButton = QtWidgets.QPushButton(
            self.specw_select_pixel_widget
        )
        self.specw_pixel2_pushButton.setCheckable(True)
        self.specw_pixel2_pushButton.setChecked(False)
        self.specw_pixel2_pushButton.setObjectName("specw_pixel2_pushButton")
        self.gridLayout_4.addWidget(self.specw_pixel2_pushButton, 2, 0, 1, 1)

        # Pixel 3
        self.specw_pixel3_pushButton = QtWidgets.QPushButton(
            self.specw_select_pixel_widget
        )
        self.specw_pixel3_pushButton.setCheckable(True)
        self.specw_pixel3_pushButton.setChecked(False)
        self.specw_pixel3_pushButton.setObjectName("specw_pixel3_pushButton")
        self.gridLayout_4.addWidget(self.specw_pixel3_pushButton, 3, 0, 1, 1)

        # Pixel 4
        self.specw_pixel4_pushButton = QtWidgets.QPushButton(
            self.specw_select_pixel_widget
        )
        self.specw_pixel4_pushButton.setCheckable(True)
        self.specw_pixel4_pushButton.setChecked(False)
        self.specw_pixel4_pushButton.setObjectName("specw_pixel4_pushButton")
        self.gridLayout_4.addWidget(self.specw_pixel4_pushButton, 4, 0, 1, 1)

        # Pixel 5
        self.specw_pixel5_pushButton = QtWidgets.QPushButton(
            self.specw_select_pixel_widget
        )
        self.specw_pixel5_pushButton.setCheckable(True)
        self.specw_pixel5_pushButton.setChecked(False)
        self.specw_pixel5_pushButton.setObjectName("specw_pixel5_pushButton")
        self.gridLayout_4.addWidget(self.specw_pixel5_pushButton, 0, 1, 1, 1)

        # Pixel 6
        self.specw_pixel6_pushButton = QtWidgets.QPushButton(
            self.specw_select_pixel_widget
        )
        self.specw_pixel6_pushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.specw_pixel6_pushButton.setCheckable(True)
        self.specw_pixel6_pushButton.setChecked(False)
        self.specw_pixel6_pushButton.setObjectName("specw_pixel6_pushButton")
        self.gridLayout_4.addWidget(self.specw_pixel6_pushButton, 2, 1, 1, 1)

        # Pixel 7
        self.specw_pixel7_pushButton = QtWidgets.QPushButton(
            self.specw_select_pixel_widget
        )
        self.specw_pixel7_pushButton.setCheckable(True)
        self.specw_pixel7_pushButton.setChecked(False)
        self.specw_pixel7_pushButton.setObjectName("specw_pixel7_pushButton")
        self.gridLayout_4.addWidget(self.specw_pixel7_pushButton, 3, 1, 1, 1)

        # Pixel 8
        self.specw_pixel8_pushButton = QtWidgets.QPushButton(
            self.specw_select_pixel_widget
        )
        self.specw_pixel8_pushButton.setCheckable(True)
        self.specw_pixel8_pushButton.setChecked(False)
        self.specw_pixel8_pushButton.setObjectName("specw_pixel8_pushButton")
        self.gridLayout_4.addWidget(self.specw_pixel8_pushButton, 4, 1, 1, 1)

        self.specw_scrollArea_gridLayout.addWidget(
            self.specw_select_pixel_widget, 6, 0, 1, 1, QtCore.Qt.AlignHCenter
        )

        # Save Spectrum button
        self.specw_save_spectrum_pushButton = QtWidgets.QPushButton(
            self.specw_scrollAreaWidgetContents
        )
        self.specw_save_spectrum_pushButton.setObjectName(
            "specw_save_spectrum_pushButton"
        )
        self.specw_scrollArea_gridLayout.addWidget(
            self.specw_save_spectrum_pushButton, 7, 0, 1, 1
        )

        self.tabWidget.addTab(self.spectrum_widget, "")

        # -------------------------------------------------------------------- #
        # ------------------- Define Stability Scan Widget ------------------- #
        # -------------------------------------------------------------------- #
        self.stability_widget = QtWidgets.QWidget()
        self.stability_widget.setObjectName("stability_widget")
        self.ltw_gridLayout_2 = QtWidgets.QGridLayout(self.stability_widget)
        self.ltw_gridLayout_2.setObjectName("ltw_gridLayout_2")

        # --------------- Central Widget with matplotlib graph --------------- #
        self.ltw_graph_widget = QtWidgets.QWidget(self.stability_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.ltw_graph_widget.sizePolicy().hasHeightForWidth()
        )
        self.ltw_graph_widget.setSizePolicy(sizePolicy)
        self.ltw_graph_widget.setMinimumSize(QtCore.QSize(0, 442))
        self.ltw_graph_widget.setObjectName("ltw_graph_widget")
        self.ltw_mpl_graph_gridLayout = QtWidgets.QGridLayout(self.ltw_graph_widget)
        self.ltw_mpl_graph_gridLayout.setObjectName("ltw_mpl_graph_gridLayout")
        self.ltw_gridLayout_2.addWidget(self.ltw_graph_widget, 0, 1, 1, 1)

        # Define figure
        figureSize = (11, 10)
        self.ltw_fig = FigureCanvas(Figure(figsize=figureSize))
        self.ltw_mpl_graph_gridLayout.addWidget(self.ltw_fig)

        self.ltw_ax = self.ltw_fig.figure.subplots()
        self.ltw_ax.set_facecolor("#FFFFFF")
        self.ltw_ax.grid(True)
        # self.ltw_ax.set_yscale("log")
        self.ltw_ax.set_xlabel("Time (s)", fontsize=14)
        self.ltw_ax.set_ylabel("Photodiode Voltage (V)", fontsize=14)
        self.ltw_ax.axhline(linewidth=1, color="black")

        self.ltw_ax2 = self.ltw_ax.twinx()
        self.ltw_ax2.set_ylabel(
            "Voltage (V)",
            color=(85 / 255, 170 / 255, 255 / 255),
            fontsize=14,
        )

        # self.ltw_ax.axvline(linewidth=1, color="black")
        self.ltw_fig.figure.set_facecolor("#FFFFFF")
        self.ltw_mplToolbar = NavigationToolbar(self.ltw_fig, self.ltw_graph_widget)
        self.ltw_mplToolbar.setStyleSheet("background-color:#FFFFFF; color:black;")
        self.ltw_mpl_graph_gridLayout.addWidget(self.ltw_mplToolbar)

        # ----------------------- Define scroll area ---------------------------
        self.ltw_scrollArea = QtWidgets.QScrollArea(self.stability_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.ltw_scrollArea.sizePolicy().hasHeightForWidth()
        )
        self.ltw_scrollArea.setSizePolicy(sizePolicy)
        self.ltw_scrollArea.setMinimumSize(QtCore.QSize(200, 0))
        self.ltw_scrollArea.setWidgetResizable(True)
        self.ltw_scrollArea.setObjectName("ltw_scrollArea")
        self.ltw_scrollAreaWidgetContents = QtWidgets.QWidget()
        self.ltw_scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 170, 655))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.ltw_scrollAreaWidgetContents.sizePolicy().hasHeightForWidth()
        )
        self.ltw_scrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.ltw_scrollAreaWidgetContents.setObjectName("ltw_scrollAreaWidgetContents")
        self.ltw_gridLayout_3 = QtWidgets.QGridLayout(self.ltw_scrollAreaWidgetContents)
        self.ltw_gridLayout_3.setObjectName("ltw_gridLayout_3")

        self.ltw_header1_label = QtWidgets.QLabel(self.ltw_scrollAreaWidgetContents)
        self.ltw_header1_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.ltw_header1_label.setObjectName("ltw_header1_label")
        self.ltw_gridLayout_3.addWidget(self.ltw_header1_label, 0, 0, 1, 1)
        self.ltw_scrollArea.setWidget(self.ltw_scrollAreaWidgetContents)
        self.ltw_gridLayout_2.addWidget(self.ltw_scrollArea, 0, 3, 1, 1)

        # ---------------------- Select pixel widget ------------------------- #
        self.ltw_select_pixel_widget = QtWidgets.QWidget(
            self.ltw_scrollAreaWidgetContents
        )
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.ltw_select_pixel_widget.sizePolicy().hasHeightForWidth()
        )
        self.ltw_select_pixel_widget.setSizePolicy(sizePolicy)
        self.ltw_select_pixel_widget.setMinimumSize(QtCore.QSize(100, 0))
        self.ltw_select_pixel_widget.setMaximumSize(QtCore.QSize(150, 124))
        self.ltw_select_pixel_widget.setObjectName("ltw_select_pixel_widget")
        self.ltw_gridLayout_4 = QtWidgets.QGridLayout(self.ltw_select_pixel_widget)
        self.ltw_gridLayout_4.setObjectName("ltw_gridLayout_4")
        self.ltw_select_pixel_label = QtWidgets.QLabel(
            self.ltw_scrollAreaWidgetContents
        )
        self.ltw_select_pixel_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.ltw_select_pixel_label.setObjectName("ltw_select_pixel_label")
        self.ltw_gridLayout_3.addWidget(self.ltw_select_pixel_label, 10, 0, 1, 1)

        # Pixel 1
        self.ltw_pixel1_pushButton = QtWidgets.QPushButton(self.ltw_select_pixel_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.ltw_pixel1_pushButton.sizePolicy().hasHeightForWidth()
        )
        self.ltw_pixel1_pushButton.setSizePolicy(sizePolicy)
        self.ltw_pixel1_pushButton.setMinimumSize(QtCore.QSize(0, 0))
        self.ltw_pixel1_pushButton.setCheckable(True)
        self.ltw_pixel1_pushButton.setAutoRepeat(False)
        self.ltw_pixel1_pushButton.setObjectName("ltw_pixel1_pushButton")
        self.ltw_gridLayout_4.addWidget(self.ltw_pixel1_pushButton, 0, 0, 1, 1)

        # Pixel 2
        self.ltw_pixel2_pushButton = QtWidgets.QPushButton(self.ltw_select_pixel_widget)
        self.ltw_pixel2_pushButton.setCheckable(True)
        self.ltw_pixel2_pushButton.setObjectName("ltw_pixel2_pushButton")
        self.ltw_gridLayout_4.addWidget(self.ltw_pixel2_pushButton, 2, 0, 1, 1)

        # Pixel 3
        self.ltw_pixel3_pushButton = QtWidgets.QPushButton(self.ltw_select_pixel_widget)
        self.ltw_pixel3_pushButton.setCheckable(True)
        # self.ltw_pixel3_pushButton.setChecked(True)
        self.ltw_pixel3_pushButton.setObjectName("ltw_pixel3_pushButton")
        self.ltw_gridLayout_4.addWidget(self.ltw_pixel3_pushButton, 3, 0, 1, 1)

        # Pixel 4
        self.ltw_pixel4_pushButton = QtWidgets.QPushButton(self.ltw_select_pixel_widget)
        self.ltw_pixel4_pushButton.setCheckable(True)
        # self.ltw_pixel4_pushButton.setChecked(True)
        self.ltw_pixel4_pushButton.setObjectName("ltw_pixel4_pushButton")
        self.ltw_gridLayout_4.addWidget(self.ltw_pixel4_pushButton, 4, 0, 1, 1)

        # Pixel 5
        self.ltw_pixel5_pushButton = QtWidgets.QPushButton(self.ltw_select_pixel_widget)
        self.ltw_pixel5_pushButton.setCheckable(True)
        # self.ltw_pixel5_pushButton.setChecked(True)
        self.ltw_pixel5_pushButton.setObjectName("ltw_pixel5_pushButton")
        self.ltw_gridLayout_4.addWidget(self.ltw_pixel5_pushButton, 0, 1, 1, 1)

        # Pixel 6
        self.ltw_pixel6_pushButton = QtWidgets.QPushButton(self.ltw_select_pixel_widget)
        self.ltw_pixel6_pushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.ltw_pixel6_pushButton.setCheckable(True)
        # self.ltw_pixel6_pushButton.setChecked(True)
        self.ltw_pixel6_pushButton.setObjectName("ltw_pixel6_pushButton")
        self.ltw_gridLayout_4.addWidget(self.ltw_pixel6_pushButton, 2, 1, 1, 1)

        # Pixel 7
        self.ltw_pixel7_pushButton = QtWidgets.QPushButton(self.ltw_select_pixel_widget)
        self.ltw_pixel7_pushButton.setCheckable(True)
        # self.ltw_pixel7_pushButton.setChecked(True)
        self.ltw_pixel7_pushButton.setObjectName("ltw_pixel7_pushButton")
        self.ltw_gridLayout_4.addWidget(self.ltw_pixel7_pushButton, 3, 1, 1, 1)

        # Pixel 8
        self.ltw_pixel8_pushButton = QtWidgets.QPushButton(self.ltw_select_pixel_widget)
        self.ltw_pixel8_pushButton.setCheckable(True)
        # self.ltw_pixel8_pushButton.setChecked(True)
        self.ltw_pixel8_pushButton.setObjectName("ltw_pixel8_pushButton")
        self.ltw_gridLayout_4.addWidget(self.ltw_pixel8_pushButton, 4, 1, 1, 1)

        self.ltw_gridLayout_3.addWidget(
            self.ltw_select_pixel_widget, 11, 0, 1, 1, QtCore.Qt.AlignHCenter
        )

        # Voltage or current
        self.ltw_voltage_or_current_HLayout = QtWidgets.QHBoxLayout()
        self.ltw_voltage_or_current_toggleSwitch = ToggleSwitch()
        self.ltw_voltage_or_current_label = QtWidgets.QLabel("Current Bias")
        self.ltw_voltage_or_current_HLayout.addWidget(
            self.ltw_voltage_or_current_toggleSwitch
        )
        self.ltw_voltage_or_current_HLayout.addWidget(self.ltw_voltage_or_current_label)
        self.ltw_gridLayout_3.addLayout(self.ltw_voltage_or_current_HLayout, 1, 0, 1, 1)

        # Set Voltage
        self.ltw_voltage_label = QtWidgets.QLabel(self.ltw_scrollAreaWidgetContents)
        self.ltw_voltage_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.ltw_voltage_label.setObjectName("ltw_voltage_label")
        self.ltw_gridLayout_3.addWidget(self.ltw_voltage_label, 2, 0, 1, 1)
        self.ltw_voltage_spinBox = HumbleDoubleSpinBox(
            self.ltw_scrollAreaWidgetContents
        )
        self.ltw_voltage_spinBox.setObjectName("ltw_voltage_spinBox")
        self.ltw_gridLayout_3.addWidget(self.ltw_voltage_spinBox, 3, 0, 1, 1)

        # Set maximum current
        self.ltw_max_current_label = QtWidgets.QLabel(self.ltw_scrollAreaWidgetContents)
        self.ltw_max_current_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.ltw_max_current_label.setObjectName("ltw_max_current_label")
        self.ltw_gridLayout_3.addWidget(self.ltw_max_current_label, 4, 0, 1, 1)
        self.ltw_max_current_spinBox = HumbleDoubleSpinBox(
            self.ltw_scrollAreaWidgetContents
        )
        self.ltw_max_current_spinBox.setObjectName("ltw_max_current_spinBox")
        self.ltw_gridLayout_3.addWidget(self.ltw_max_current_spinBox, 5, 0, 1, 1)

        # Total on time
        self.ltw_on_time_label = QtWidgets.QLabel(self.ltw_scrollAreaWidgetContents)
        self.ltw_on_time_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.ltw_on_time_label.setObjectName("ltw_on_time_label")
        self.ltw_gridLayout_3.addWidget(self.ltw_on_time_label, 6, 0, 1, 1)
        self.ltw_on_time_spinBox = HumbleDoubleSpinBox(
            self.ltw_scrollAreaWidgetContents
        )
        self.ltw_on_time_spinBox.setObjectName("ltw_on_time_spinBox")
        self.ltw_gridLayout_3.addWidget(self.ltw_on_time_spinBox, 7, 0, 1, 1)

        # Measurement Interval
        self.ltw_measurement_interval_label = QtWidgets.QLabel(
            self.ltw_scrollAreaWidgetContents
        )
        self.ltw_measurement_interval_label.setStyleSheet(
            'font: 63 bold 10pt "Segoe UI";'
        )
        self.ltw_measurement_interval_label.setObjectName(
            "ltw_measurement_interval_label"
        )
        self.ltw_gridLayout_3.addWidget(self.ltw_measurement_interval_label, 8, 0, 1, 1)
        self.ltw_measurement_interval_spinBox = HumbleDoubleSpinBox(
            self.ltw_scrollAreaWidgetContents
        )
        self.ltw_measurement_interval_spinBox.setObjectName(
            "ltw_measurement_interval_spinBox"
        )
        self.ltw_gridLayout_3.addWidget(
            self.ltw_measurement_interval_spinBox, 9, 0, 1, 1
        )

        # All pixel mode
        self.ltw_all_pixel_mode_HLayout = QtWidgets.QHBoxLayout()
        self.ltw_all_pixel_mode_toggleSwitch = ToggleSwitch()
        self.ltw_all_pixel_mode_label = QtWidgets.QLabel("Turn all Pixels on")
        self.ltw_all_pixel_mode_HLayout.addWidget(self.ltw_all_pixel_mode_toggleSwitch)
        self.ltw_all_pixel_mode_HLayout.addWidget(self.ltw_all_pixel_mode_label)
        self.ltw_gridLayout_3.addLayout(self.ltw_all_pixel_mode_HLayout, 12, 0, 1, 1)

        # Start measurement button
        self.ltw_start_measurement_pushButton = QtWidgets.QPushButton(
            self.ltw_scrollAreaWidgetContents
        )
        self.ltw_start_measurement_pushButton.setCheckable(True)
        self.ltw_start_measurement_pushButton.setObjectName(
            "ltw_start_measurement_pushButton"
        )
        self.ltw_gridLayout_3.addWidget(
            self.ltw_start_measurement_pushButton, 13, 0, 1, 1
        )

        self.tabWidget.addTab(self.stability_widget, "")

        # -------------------------------------------------------------------- #
        # -------------------- Define Goniometer Window ---------------------- #
        # -------------------------------------------------------------------- #
        self.goniometer_widget = QtWidgets.QWidget()
        self.goniometer_widget.setObjectName("goniometer_widget")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.goniometer_widget)
        self.gridLayout_8.setObjectName("gridLayout_8")

        # --------------- Central Widget with matplotlib graph --------------- #
        self.gw_graph_widget = QtWidgets.QWidget(self.goniometer_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.gw_graph_widget.sizePolicy().hasHeightForWidth()
        )
        self.gw_graph_widget.setSizePolicy(sizePolicy)
        self.gw_graph_widget.setMinimumSize(QtCore.QSize(0, 442))
        self.gw_graph_widget.setObjectName("gw_graph_widget")
        self.gw_mpl_graph_gridLayout = QtWidgets.QGridLayout(self.gw_graph_widget)
        self.gw_mpl_graph_gridLayout.setObjectName("gw_mpl_graph_gridLayout")
        self.gridLayout_8.addWidget(self.gw_graph_widget, 0, 1, 1, 1)

        # Define figure
        figureSize = (11, 10)
        self.gw_fig = FigureCanvas(Figure(figsize=figureSize))
        self.gw_mpl_graph_gridLayout.addWidget(self.gw_fig)

        self.gw_ax1 = self.gw_fig.figure.subplots()
        self.gw_ax1.set_facecolor("#FFFFFF")
        self.gw_fig.figure.set_facecolor("#FFFFFF")
        self.gw_mplToolbar = NavigationToolbar(self.gw_fig, self.gw_graph_widget)
        self.gw_mplToolbar.setStyleSheet("background-color:#FFFFFF; color: black;")
        self.gw_mpl_graph_gridLayout.addWidget(self.gw_mplToolbar)

        # ------------------------- Scroll Area ------------------------------ #
        self.gw_scrollArea = QtWidgets.QScrollArea(self.goniometer_widget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.gw_scrollArea.sizePolicy().hasHeightForWidth()
        )
        self.gw_scrollArea.setSizePolicy(sizePolicy)
        self.gw_scrollArea.setMinimumSize(QtCore.QSize(200, 0))
        self.gw_scrollArea.setWidgetResizable(True)
        self.gw_scrollArea.setObjectName("gw_scrollArea")
        self.gw_scrollAreaWidgetContents = QtWidgets.QWidget()
        self.gw_scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, -382, 169, 912))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.gw_scrollAreaWidgetContents.sizePolicy().hasHeightForWidth()
        )
        self.gw_scrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.gw_scrollAreaWidgetContents.setObjectName("gw_scrollAreaWidgetContents")
        self.gridLayout_9 = QtWidgets.QGridLayout(self.gw_scrollAreaWidgetContents)
        self.gridLayout_9.setObjectName("gridLayout_9")

        self.gw_header1 = QtWidgets.QLabel(self.gw_scrollAreaWidgetContents)
        self.gw_header1.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.gw_header1.setObjectName("gw_header1")
        self.gridLayout_9.addWidget(self.gw_header1, 2, 0, 1, 1)

        self.gw_header2 = QtWidgets.QLabel(self.gw_scrollAreaWidgetContents)
        self.gw_header2.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.gw_header2.setObjectName("gw_header2")
        self.gridLayout_9.addWidget(self.gw_header2, 9, 0, 1, 1)

        # Select Pixel Label
        self.gw_select_pixel_label = QtWidgets.QLabel(self.gw_scrollAreaWidgetContents)
        self.gw_select_pixel_label.setStyleSheet('font: 75 bold 10pt "Noto Sans";')
        self.gw_select_pixel_label.setObjectName("gw_select_pixel_label")
        self.gridLayout_9.addWidget(self.gw_select_pixel_label, 31, 0, 1, 1)

        # Background at every step
        self.gw_background_every_step_HLayout = QtWidgets.QHBoxLayout()
        self.gw_background_every_step_toggleSwitch = ToggleSwitch()
        self.gw_background_every_step_label = QtWidgets.QLabel("Multi Background")
        self.gw_background_every_step_HLayout.addWidget(
            self.gw_background_every_step_toggleSwitch
        )
        self.gw_background_every_step_HLayout.addWidget(
            self.gw_background_every_step_label
        )

        self.gridLayout_9.addLayout(self.gw_background_every_step_HLayout, 24, 0, 1, 1)

        # Offset angle
        self.gw_offset_angle_label = QtWidgets.QLabel(self.gw_scrollAreaWidgetContents)
        self.gw_offset_angle_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.gw_offset_angle_label.setObjectName("gw_offset_angle_label")
        self.gridLayout_9.addWidget(self.gw_offset_angle_label, 4, 0, 1, 1)

        self.gw_offset_angle_spinBox = HumbleDoubleSpinBox(
            self.gw_scrollAreaWidgetContents
        )
        self.gw_offset_angle_spinBox.setObjectName("gw_offset_angle_spinBox")
        self.gridLayout_9.addWidget(self.gw_offset_angle_spinBox, 5, 0, 1, 1)

        # Start measurement
        self.gw_start_measurement_pushButton = QtWidgets.QPushButton(
            self.gw_scrollAreaWidgetContents
        )
        self.gw_start_measurement_pushButton.setCheckable(True)
        self.gw_start_measurement_pushButton.setObjectName(
            "gw_start_measurement_pushButton"
        )
        self.gridLayout_9.addWidget(self.gw_start_measurement_pushButton, 31, 0, 1, 1)

        # Stage position
        self.gw_stage_position_label = QtWidgets.QLabel(
            self.gw_scrollAreaWidgetContents
        )
        self.gw_stage_position_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.gw_stage_position_label.setObjectName("gw_stage_position_label")
        self.gridLayout_9.addWidget(self.gw_stage_position_label, 0, 0, 1, 1)

        # Step angle
        self.gw_step_angle_label = QtWidgets.QLabel(self.gw_scrollAreaWidgetContents)
        self.gw_step_angle_label.setStyleSheet('font: 75 bold 10pt "Noto Sans";')
        self.gw_step_angle_label.setObjectName("gw_step_angle_label")
        self.gridLayout_9.addWidget(self.gw_step_angle_label, 14, 0, 1, 1)

        self.gw_step_angle_spinBox = HumbleDoubleSpinBox(
            self.gw_scrollAreaWidgetContents
        )
        self.gw_step_angle_spinBox.setMaximum(180.0)
        self.gw_step_angle_spinBox.setProperty("value", 1.0)
        self.gw_step_angle_spinBox.setObjectName("gw_step_angle_spinBox")
        self.gridLayout_9.addWidget(self.gw_step_angle_spinBox, 15, 0, 1, 1)

        # Voltage or current
        self.gw_voltage_or_current_HLayout = QtWidgets.QHBoxLayout()
        self.gw_voltage_or_current_toggleSwitch = ToggleSwitch()
        self.gw_voltage_or_current_label = QtWidgets.QLabel("Current Bias")
        self.gw_voltage_or_current_HLayout.addWidget(
            self.gw_voltage_or_current_toggleSwitch
        )
        self.gw_voltage_or_current_HLayout.addWidget(self.gw_voltage_or_current_label)

        self.gridLayout_9.addLayout(self.gw_voltage_or_current_HLayout, 25, 0, 1, 1)
        # self.gw_voltage_or_current_pushButton = QtWidgets.QPushButton(
        # self.gw_scrollAreaWidgetContents
        # )
        # self.gw_voltage_or_current_pushButton.setCheckable(True)
        # self.gw_voltage_or_current_pushButton.setObjectName(
        # "gw_voltage_or_current_pushButton"
        # )
        # Pulse duration
        # self.gw_oled_on_time_label = QtWidgets.QLabel(self.gw_scrollAreaWidgetContents)
        # self.gw_oled_on_time_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        # self.gw_oled_on_time_label.setObjectName("gw_oled_on_time_label")
        # self.gridLayout_9.addWidget(self.gw_oled_on_time_label, 26, 0, 1, 1)

        # self.gw_oled_on_time_spinBox = HumbleDoubleSpinBox(
        #     self.gw_scrollAreaWidgetContents
        # )
        # self.gw_oled_on_time_spinBox.setObjectName("gw_oled_on_time_spinBox")
        # self.gridLayout_9.addWidget(self.gw_oled_on_time_spinBox, 27, 0, 1, 1)

        # Set voltage or current value
        self.gw_vc_value_label = QtWidgets.QLabel(self.gw_scrollAreaWidgetContents)
        self.gw_vc_value_label.setStyleSheet('font: 75 bold 10pt "Noto Sans";')
        self.gw_vc_value_label.setObjectName("gw_vc_value_label")
        self.gridLayout_9.addWidget(self.gw_vc_value_label, 26, 0, 1, 1)
        self.gw_vc_value_spinBox = HumbleDoubleSpinBox(self.gw_scrollAreaWidgetContents)
        self.gw_vc_value_spinBox.setObjectName("gw_vc_value_spinBox")
        self.gridLayout_9.addWidget(self.gw_vc_value_spinBox, 27, 0, 1, 1)

        # Set voltage or current compliance
        self.gw_vc_compliance_label = QtWidgets.QLabel(self.gw_scrollAreaWidgetContents)
        self.gw_vc_compliance_label.setStyleSheet('font: 75 bold 10pt "Noto Sans";')
        self.gw_vc_compliance_label.setObjectName("gw_vc_compliance_label")
        self.gridLayout_9.addWidget(self.gw_vc_compliance_label, 28, 0, 1, 1)
        self.gw_vc_compliance_spinBox = HumbleDoubleSpinBox(
            self.gw_scrollAreaWidgetContents
        )
        self.gw_vc_compliance_spinBox.setObjectName("gw_vc_compliance_spinBox")
        self.gridLayout_9.addWidget(self.gw_vc_compliance_spinBox, 29, 0, 1, 1)

        # ------------------------ Pixel selection --------------------------- #
        self.widget_7 = QtWidgets.QWidget(self.gw_scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_7.sizePolicy().hasHeightForWidth())
        self.widget_7.setSizePolicy(sizePolicy)
        self.widget_7.setMinimumSize(QtCore.QSize(100, 0))
        self.widget_7.setMaximumSize(QtCore.QSize(150, 124))
        self.widget_7.setObjectName("widget_7")
        self.gridLayout_10 = QtWidgets.QGridLayout(self.widget_7)
        self.gridLayout_10.setObjectName("gridLayout_10")

        # Pixel 2
        self.gw_pixel2_pushButton = QtWidgets.QPushButton(self.widget_7)
        self.gw_pixel2_pushButton.setCheckable(True)
        self.gw_pixel2_pushButton.setChecked(False)
        self.gw_pixel2_pushButton.setObjectName("gw_pixel2_pushButton")
        self.gridLayout_10.addWidget(self.gw_pixel2_pushButton, 2, 0, 1, 1)

        # Pixel 1
        self.gw_pixel1_pushButton = QtWidgets.QPushButton(self.widget_7)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.gw_pixel1_pushButton.sizePolicy().hasHeightForWidth()
        )
        self.gw_pixel1_pushButton.setSizePolicy(sizePolicy)
        self.gw_pixel1_pushButton.setMinimumSize(QtCore.QSize(0, 0))
        self.gw_pixel1_pushButton.setCheckable(True)
        self.gw_pixel1_pushButton.setChecked(False)
        self.gw_pixel1_pushButton.setAutoRepeat(False)
        self.gw_pixel1_pushButton.setObjectName("gw_pixel1_pushButton")
        self.gridLayout_10.addWidget(self.gw_pixel1_pushButton, 0, 0, 1, 1)

        # Pixel 4
        self.gw_pixel4_pushButton = QtWidgets.QPushButton(self.widget_7)
        self.gw_pixel4_pushButton.setCheckable(True)
        self.gw_pixel4_pushButton.setChecked(False)
        self.gw_pixel4_pushButton.setObjectName("gw_pixel4_pushButton")
        self.gridLayout_10.addWidget(self.gw_pixel4_pushButton, 4, 0, 1, 1)

        # Pixel 3
        self.gw_pixel3_pushButton = QtWidgets.QPushButton(self.widget_7)
        self.gw_pixel3_pushButton.setCheckable(True)
        self.gw_pixel3_pushButton.setChecked(False)
        self.gw_pixel3_pushButton.setObjectName("gw_pixel3_pushButton")
        self.gridLayout_10.addWidget(self.gw_pixel3_pushButton, 3, 0, 1, 1)

        # Pixel 8
        self.gw_pixel8_pushButton = QtWidgets.QPushButton(self.widget_7)
        self.gw_pixel8_pushButton.setCheckable(True)
        self.gw_pixel8_pushButton.setChecked(False)
        self.gw_pixel8_pushButton.setObjectName("gw_pixel8_pushButton")
        self.gridLayout_10.addWidget(self.gw_pixel8_pushButton, 4, 1, 1, 1)

        # Pixel 7
        self.gw_pixel7_pushButton = QtWidgets.QPushButton(self.widget_7)
        self.gw_pixel7_pushButton.setCheckable(True)
        self.gw_pixel7_pushButton.setChecked(False)
        self.gw_pixel7_pushButton.setObjectName("gw_pixel7_pushButton")
        self.gridLayout_10.addWidget(self.gw_pixel7_pushButton, 3, 1, 1, 1)

        # Pixel 6
        self.gw_pixel6_pushButton = QtWidgets.QPushButton(self.widget_7)
        self.gw_pixel6_pushButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.gw_pixel6_pushButton.setCheckable(True)
        self.gw_pixel6_pushButton.setChecked(False)
        self.gw_pixel6_pushButton.setObjectName("gw_pixel6_pushButton")
        self.gridLayout_10.addWidget(self.gw_pixel6_pushButton, 2, 1, 1, 1)

        # Pixel 5
        self.gw_pixel5_pushButton = QtWidgets.QPushButton(self.widget_7)
        self.gw_pixel5_pushButton.setCheckable(True)
        self.gw_pixel5_pushButton.setChecked(False)
        self.gw_pixel5_pushButton.setObjectName("gw_pixel5_pushButton")
        self.gridLayout_10.addWidget(self.gw_pixel5_pushButton, 0, 1, 1, 1)
        self.gridLayout_9.addWidget(self.widget_7, 30, 0, 1, 1, QtCore.Qt.AlignHCenter)

        # Degradation check
        self.gw_degradation_check_HLayout = QtWidgets.QHBoxLayout()
        self.gw_degradation_check_toggleSwitch = ToggleSwitch()
        self.gw_degradation_check_label = QtWidgets.QLabel("Degradation Check")
        self.gw_degradation_check_HLayout.addWidget(
            self.gw_degradation_check_toggleSwitch
        )
        self.gw_degradation_check_HLayout.addWidget(self.gw_degradation_check_label)
        self.gridLayout_9.addLayout(self.gw_degradation_check_HLayout, 22, 0, 1, 1)

        # El or pl selection
        self.gw_el_or_pl_HLayout = QtWidgets.QHBoxLayout()
        self.gw_el_or_pl_toggleSwitch = ToggleSwitch()
        self.gw_el_or_pl_label = QtWidgets.QLabel("Photoluminescence")
        self.gw_el_or_pl_HLayout.addWidget(self.gw_el_or_pl_toggleSwitch)
        self.gw_el_or_pl_HLayout.addWidget(self.gw_el_or_pl_label)
        self.gridLayout_9.addLayout(self.gw_el_or_pl_HLayout, 23, 0, 1, 1)

        # Move goniometer motor
        self.gw_move_pushButton = QtWidgets.QPushButton(
            self.gw_scrollAreaWidgetContents
        )
        self.gw_move_pushButton.setObjectName("gw_move_pushButton")
        self.gridLayout_9.addWidget(self.gw_move_pushButton, 8, 0, 1, 1)

        # Integration time
        self.gw_integration_time_label = QtWidgets.QLabel(
            self.gw_scrollAreaWidgetContents
        )
        self.gw_integration_time_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        self.gw_integration_time_label.setObjectName("gw_integration_time_label")
        self.gridLayout_9.addWidget(self.gw_integration_time_label, 16, 0, 1, 1)
        self.gw_integration_time_spinBox = HumbleDoubleSpinBox(
            self.gw_scrollAreaWidgetContents
        )
        self.gw_integration_time_spinBox.setObjectName("gw_integration_time_spinBox")
        self.gridLayout_9.addWidget(self.gw_integration_time_spinBox, 17, 0, 1, 1)

        # Homing time
        # self.gw_homing_time_label = QtWidgets.QLabel(self.gw_scrollAreaWidgetContents)
        # self.gw_homing_time_label.setStyleSheet('font: 63 bold 10pt "Segoe UI";')
        # self.gw_homing_time_label.setObjectName("gw_homing_time_label")
        # self.gridLayout_9.addWidget(self.gw_homing_time_label, 18, 0, 1, 1)

        # Animation widget

        # self.frame = QtGui.QFrame()
        # self.frame.resize(300,300)
        self.gw_animation = Ui_GoniometerAnimation()
        # layout.addWidget(self._bar)

        # self.gw_animation_widget = QtWidgets.QWidget()
        # self.horizontalLayout10 = QtWidgets.QHBoxLayout()

        # self.gw_animation = QtGui.QPainter()
        # self.gw_animation.resize(300, 300)
        # self.gw_animation.setStyleSheet("background-color: rgb(0, 0, 0)")
        # self.gw_animation.setObjectName("gw_animation")
        # self.gw_animation.setFrameStyle(
        # QtWidgets.QFrame.Panel | QtWidgets.QFrame.Raised
        # )
        # self.gw_animation.setGeometry(150, 30, 100, 100)
        # self.horizontalLayout10.addWidget(self.gw_animation)

        # self.gw_animation_widget.setLayout(self.horizontalLayout10)
        self.gridLayout_9.addWidget(self.gw_animation, 1, 0, 1, 1)

        # Minimum angle
        self.gw_minimum_angle_label = QtWidgets.QLabel(self.gw_scrollAreaWidgetContents)
        self.gw_minimum_angle_label.setStyleSheet('font: 75 bold 10pt "Noto Sans";')
        self.gw_minimum_angle_label.setObjectName("gw_minimum_angle_label")
        self.gridLayout_9.addWidget(self.gw_minimum_angle_label, 10, 0, 1, 1)

        self.gw_minimum_angle_spinBox = HumbleSpinBox(self.gw_scrollAreaWidgetContents)
        self.gw_minimum_angle_spinBox.setMinimum(-180)
        self.gw_minimum_angle_spinBox.setMaximum(180)
        self.gw_minimum_angle_spinBox.setProperty("value", 180)
        self.gw_minimum_angle_spinBox.setObjectName("gw_minimum_angle_spinBox")
        self.gridLayout_9.addWidget(self.gw_minimum_angle_spinBox, 11, 0, 1, 1)

        # Maximum angle
        self.gw_maximum_angle_label = QtWidgets.QLabel(self.gw_scrollAreaWidgetContents)
        self.gw_maximum_angle_label.setStyleSheet('font: 75 bold 10pt "Noto Sans";')
        self.gw_maximum_angle_label.setObjectName("gw_maximum_angle_label")
        self.gridLayout_9.addWidget(self.gw_maximum_angle_label, 12, 0, 1, 1)

        self.gw_maximum_angle_spinBox = HumbleSpinBox(self.gw_scrollAreaWidgetContents)
        self.gw_maximum_angle_spinBox.setMinimum(-180)
        self.gw_maximum_angle_spinBox.setMaximum(180)
        self.gw_maximum_angle_spinBox.setProperty("value", 180)
        self.gw_maximum_angle_spinBox.setObjectName("gw_maximum_angle_spinBox")
        self.gridLayout_9.addWidget(self.gw_maximum_angle_spinBox, 13, 0, 1, 1)

        self.gw_scrollArea.setWidget(self.gw_scrollAreaWidgetContents)

        self.gridLayout_8.addWidget(self.gw_scrollArea, 0, 2, 1, 1)

        self.tabWidget.addTab(self.goniometer_widget, "")

        self.gridLayout.addWidget(self.tabWidget, 1, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        # -------------------------------------------------------------------- #
        # ------------------------- Define Menubar --------------------------- #
        # -------------------------------------------------------------------- #

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 973, 31))
        self.menubar.setObjectName("menubar")
        # self.menudfg = QtWidgets.QMenu(self.menubar)
        # self.menudfg.setObjectName("menudfg")
        self.menuSettings = QtWidgets.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        MainWindow.setMenuBar(self.menubar)

        # Define actions for menubar
        self.actionOpen_Logs = QtGui.QAction(MainWindow)
        self.actionOpen_Logs.setObjectName("actionOpen_Logs")
        # self.actionOpen_Logfile_on_Machine = QtGui.QAction(MainWindow)
        # self.actionOpen_Logfile_on_Machine.setObjectName(
        # "actionOpen_Logfile_on_Machine"
        # )

        self.actionChange_Path = QtGui.QAction(MainWindow)
        self.actionChange_Path.setObjectName("actionChange_Path")

        self.actionOptions = QtGui.QAction(MainWindow)
        self.actionOptions.setObjectName("actionOptions")

        self.actionDocumentation = QtGui.QAction(MainWindow)
        self.actionDocumentation.setObjectName("actionDocumentation")

        self.actionLoad_Measurement_Parameters = QtGui.QAction(MainWindow)
        self.actionLoad_Measurement_Parameters.setObjectName(
            "actionLoad_Measurement_Parameters"
        )
        self.actionSave_Measurement_Parameters = QtGui.QAction(MainWindow)
        self.actionSave_Measurement_Parameters.setObjectName(
            "actionSave_Measurement_Parameters"
        )
        self.actionOpen_Log = QtGui.QAction(MainWindow)
        self.actionOpen_Log.setObjectName("actionOpen_Log")
        # self.menudfg.addAction(self.actionLoad_Measurement_Parameters)
        # self.menudfg.addAction(self.actionSave_Measurement_Parameters)
        self.menuSettings.addAction(self.actionOptions)
        self.menuSettings.addAction(self.actionDocumentation)
        self.menuSettings.addAction(self.actionOpen_Log)
        # self.menubar.addAction(self.menudfg.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())

        # -------------------------------------------------------------------- #
        # ----------------------- Define Statusbar --------------------------- #
        # -------------------------------------------------------------------- #

        # Define progress bar in the status bar
        self.progressBar = QtWidgets.QProgressBar()
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressBar.sizePolicy().hasHeightForWidth())
        self.progressBar.setSizePolicy(sizePolicy)
        self.progressBar.setMinimumSize(QtCore.QSize(150, 15))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setStyleSheet(
            "QProgressBar"
            "{"
            "border-radius: 5px;"
            "background-color: #FFFFFF;"
            "text-align: center;"
            "color: black;"
            'font: 63 bold 10pt "Segoe UI";'
            "}"
            "QProgressBar::chunk "
            "{"
            "background-color: rgb(85, 170, 255);"
            "border-radius: 5px;"
            "}"
        )

        # Define the statusbar itself
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setToolTip("")
        self.statusbar.setStatusTip("")
        self.statusbar.setWhatsThis("")
        self.statusbar.setAccessibleName("")
        self.statusbar.setObjectName("statusbar")
        self.statusbar.addPermanentWidget(self.progressBar)
        # self.statusbar.showMessage("Ready", 10000000)

        MainWindow.setStatusBar(self.statusbar)

        # -------------------------------------------------------------------- #
        # --------------------- Some General things -------------------------- #
        # -------------------------------------------------------------------- #
        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        """
        This function basicall contains all the text that is visible in the window.
        I think it is good practice to keep this seperate just in case the program
        would be translated to other languages.
        """

        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "OLED Characterisation"))
        # self.gatherlab_label.setText(
        # _translate("MainWindow", "Gatherlab JVL Measurement")
        # )
        self.sw_header2_label.setText(_translate("MainWindow", "Current Tester"))
        self.sw_browse_pushButton.setText(_translate("MainWindow", "Browse"))
        self.sw_ct_voltage_spinBox.setSuffix(_translate("MainWindow", " V"))
        self.sw_batch_name_label.setText(_translate("MainWindow", "Batch Name"))
        self.sw_batch_name_lineEdit.setStatusTip(
            "Batch name must not contain underscores!"
        )
        self.sw_device_number_label.setText(_translate("MainWindow", "Device Number"))
        # self.sw_header1_label.setToolTip(
        # _translate(
        # "MainWindow",
        # "<html><head/><body><p>The file name the data is saved in in the end"
        # " will be in the format"
        # " yyyy-mm-dd_&lt;batch-name&gt;_d&lt;device-number&gt;_p&lt;pixel-number&gt;.csv.</p></body></html>",
        # )
        # )
        self.sw_header1_label.setText(
            _translate("MainWindow", "Batch Name and File Path")
        )
        self.sw_reset_hardware_pushButton.setText(
            _translate("MainWindow", "Reset Hardware")
        )
        self.sw_pixel_label.setText(_translate("MainWindow", "Select Pixel"))
        self.sw_pixel2_pushButton.setText(_translate("MainWindow", "2"))
        self.sw_pixel1_pushButton.setText(_translate("MainWindow", "1"))
        self.sw_pixel3_pushButton.setText(_translate("MainWindow", "3"))
        self.sw_select_all_pushButton.setText(_translate("MainWindow", "Select All"))
        self.sw_unselect_all_push_button.setText(
            _translate("MainWindow", "Unselect All")
        )
        self.sw_pixel4_pushButton.setText(_translate("MainWindow", "4"))
        self.sw_prebias_pushButton.setText(_translate("MainWindow", "Pre-Bias"))
        self.sw_auto_test_pushButton.setText(_translate("MainWindow", "Auto Test"))
        self.sw_pixel8_pushButton.setText(_translate("MainWindow", "8"))
        self.sw_pixel7_pushButton.setText(_translate("MainWindow", "7"))
        self.sw_pixel6_pushButton.setText(_translate("MainWindow", "6"))
        self.sw_pixel5_pushButton.setText(_translate("MainWindow", "5"))
        self.sw_change_voltage_label.setText(_translate("MainWindow", "Voltage (V)"))
        # self.sw_documentation_label.setToolTip(
        # _translate(
        # "MainWindow",
        # "<html><head/><body><p>Please write here any comments to the"
        # " measurement of your batch. The comments will be saved as .md file"
        # " within your selected file path. If there are any issues with the"
        # " measurement setup or the software document it in a seperate line"
        # " starting with [!] to ensure easy debugging.</p></body></html>",
        # )
        # )
        # self.sw_documentation_label.setText(_translate("MainWindow", "Documentation"))
        self.sw_folder_path_label.setText(_translate("MainWindow", "Folder Path"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.setup_widget),
            _translate("MainWindow", "Pixel Tester"),
        )
        self.aw_high_voltage_step_label.setText(
            _translate("MainWindow", "High Voltage Step (V)")
        )
        self.aw_pixel2_pushButton.setText(_translate("MainWindow", "2"))
        self.aw_pixel1_pushButton.setText(_translate("MainWindow", "1"))
        self.aw_pixel4_pushButton.setText(_translate("MainWindow", "4"))
        self.aw_pixel3_pushButton.setText(_translate("MainWindow", "3"))
        self.aw_pixel8_pushButton.setText(_translate("MainWindow", "8"))
        self.aw_pixel7_pushButton.setText(_translate("MainWindow", "7"))
        self.aw_pixel6_pushButton.setText(_translate("MainWindow", "6"))
        self.aw_pixel5_pushButton.setText(_translate("MainWindow", "5"))
        self.aw_max_voltage_label.setText(_translate("MainWindow", "Max Voltage (V)"))
        self.aw_min_voltage_label.setText(_translate("MainWindow", "Min Voltage (V)"))
        self.aw_changeover_voltage_label.setText(
            _translate("MainWindow", "Changeover Voltage (V)")
        )
        self.aw_low_voltage_step_label.setText(
            _translate("MainWindow", "Low Voltage Step (V)")
        )
        self.aw_scan_compliance_label.setText(
            _translate("MainWindow", "Max. Current (mA)")
        )
        # self.aw_pd_saturation_checkBox.setText(
        # _translate("MainWindow", "Check for PD Saturation")
        # )
        self.aw_select_pixel_label.setText(_translate("MainWindow", "Select Pixels"))
        # self.aw_bad_contact_checkBox.setText(
        # _translate("MainWindow", "Check fo Bad Contacts")
        # )
        self.aw_start_measurement_pushButton.setText(
            _translate("MainWindow", "Start Measurement")
        )
        self.aw_header1_label.setText(
            _translate("MainWindow", "Measurement Parameters")
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.autotube_widget),
            _translate("MainWindow", "JVL Characterisation"),
        )

        # self.specw_high_voltage_step_label.setText(
        # _translate("MainWindow", "High Voltage Step (V)")
        # )
        self.specw_pixel2_pushButton.setText(_translate("MainWindow", "2"))
        self.specw_pixel1_pushButton.setText(_translate("MainWindow", "1"))
        self.specw_pixel4_pushButton.setText(_translate("MainWindow", "4"))
        self.specw_pixel3_pushButton.setText(_translate("MainWindow", "3"))
        self.specw_pixel8_pushButton.setText(_translate("MainWindow", "8"))
        self.specw_pixel7_pushButton.setText(_translate("MainWindow", "7"))
        self.specw_pixel6_pushButton.setText(_translate("MainWindow", "6"))
        self.specw_pixel5_pushButton.setText(_translate("MainWindow", "5"))
        # self.specw_max_voltage_label.setText(
        # _translate("MainWindow", "Max Voltage (V)")
        # )
        self.specw_voltage_label.setText(_translate("MainWindow", "Set Voltage (V)"))
        self.specw_voltage_spinBox.setSuffix(_translate("MainWindow", " V"))

        self.specw_integration_time_label.setText(
            _translate("MainWindow", "Integration Time (ms)")
        )
        # self.specw_changeover_voltage_label.setText(
        # _translate("MainWindow", "Changeover Voltage (V)")
        # )
        # self.specw_low_voltage_step_label.setText(
        # _translate("MainWindow", "Low Voltage Step (V)")
        # )
        # self.specw_scan_compliance_label.setText(
        # _translate("MainWindow", "Scan Compliance (A)")
        # )
        # self.specw_pd_saturation_checkBox.setText(
        # _translate("MainWindow", "Check for PD Saturation")
        # )
        self.specw_select_pixel_label.setText(_translate("MainWindow", "Select Pixels"))
        # self.specw_bad_contact_checkBox.setText(
        # _translate("MainWindow", "Check fo Bad Contacts")
        # )
        self.specw_save_spectrum_pushButton.setText(
            _translate("MainWindow", "Save Spectrum")
        )
        self.specw_header1_label.setText(
            _translate("MainWindow", "Measurement Parameters")
        )

        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.spectrum_widget),
            _translate("MainWindow", "Spectrum"),
        )

        self.ltw_pixel1_pushButton.setText(_translate("MainWindow", "1"))
        self.ltw_pixel2_pushButton.setText(_translate("MainWindow", "2"))
        self.ltw_pixel3_pushButton.setText(_translate("MainWindow", "3"))
        self.ltw_pixel4_pushButton.setText(_translate("MainWindow", "4"))
        self.ltw_pixel5_pushButton.setText(_translate("MainWindow", "5"))
        self.ltw_pixel6_pushButton.setText(_translate("MainWindow", "6"))
        self.ltw_pixel7_pushButton.setText(_translate("MainWindow", "7"))
        self.ltw_pixel8_pushButton.setText(_translate("MainWindow", "8"))
        self.ltw_on_time_label.setText(_translate("MainWindow", "On Time (s)"))
        self.ltw_measurement_interval_label.setText(
            _translate("MainWindow", "Measurement Interval (s)")
        )
        # self.ltw_pd_saturation_checkBox.setText(
        # _translate("MainWindow", "Check for PD Saturation")
        # )
        self.ltw_select_pixel_label.setText(_translate("MainWindow", "Select Pixels"))
        # self.ltw_bad_contact_checkBox.setText(
        # _translate("MainWindow", "Check fo Bad Contacts")
        # )
        self.ltw_start_measurement_pushButton.setText(
            _translate("MainWindow", "Start Measurement")
        )
        self.ltw_header1_label.setText(
            _translate("MainWindow", "Measurement Parameters")
        )

        self.ltw_voltage_label.setText(_translate("MainWindow", "Max. Voltage (V)"))
        self.ltw_max_current_label.setText(
            _translate("MainWindow", "Applied Current (mA)")
        )

        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.stability_widget),
            _translate("MainWindow", "Lifetime"),
        )

        self.gw_header2.setText(_translate("MainWindow", "Measurement Parameters"))
        # self.gw_oled_on_time_label.setText(
        # _translate("MainWindow", "Pulse duration (s)")
        # )
        # self.gw_voltage_scan_checkBox.setToolTip(
        # _translate(
        # "MainWindow",
        # "<html><head/><body><p>The parameters for the voltage scan can be set"
        # " in the JVL tab.</p></body></html>",
        # )
        # )
        # self.gw_voltage_scan_checkBox.setText(_translate("MainWindow", "Voltage Scan"))
        self.gw_header1.setText(_translate("MainWindow", "Setup"))
        self.gw_select_pixel_label.setText(_translate("MainWindow", "Select Pixel"))
        # self.gw_moving_time_label.setText(_translate("MainWindow", "Moving Time (s)"))
        self.gw_offset_angle_label.setText(
            _translate("MainWindow", "Motor Position (°)")
        )
        self.gw_start_measurement_pushButton.setText(
            _translate("MainWindow", "Start Measurement")
        )
        self.gw_stage_position_label.setText(_translate("MainWindow", "Stage Position"))
        # self.gw_voltage_or_current_pushButton.setText(
        # _translate("MainWindow", "V or C")
        # )
        self.gw_pixel2_pushButton.setText(_translate("MainWindow", "2"))
        self.gw_pixel1_pushButton.setText(_translate("MainWindow", "1"))
        self.gw_pixel4_pushButton.setText(_translate("MainWindow", "4"))
        self.gw_pixel3_pushButton.setText(_translate("MainWindow", "3"))
        self.gw_pixel8_pushButton.setText(_translate("MainWindow", "8"))
        self.gw_pixel7_pushButton.setText(_translate("MainWindow", "7"))
        self.gw_pixel6_pushButton.setText(_translate("MainWindow", "6"))
        self.gw_pixel5_pushButton.setText(_translate("MainWindow", "5"))
        self.gw_minimum_angle_label.setText(
            _translate("MainWindow", "Minimum Angle (°)")
        )
        self.gw_maximum_angle_label.setText(
            _translate("MainWindow", "Maximum Angle (°)")
        )
        self.gw_el_or_pl_toggleSwitch.setText(_translate("MainWindow", "EL or PL"))
        self.gw_move_pushButton.setText(_translate("MainWindow", "Move"))
        self.gw_step_angle_label.setText(_translate("MainWindow", "Step Angle (°)"))
        self.gw_vc_value_label.setText(_translate("MainWindow", "Applied Current (mA)"))
        self.gw_vc_compliance_label.setText(
            _translate("MainWindow", "Max. Voltage (V)")
        )
        self.gw_integration_time_label.setText(
            _translate("MainWindow", "Integration Time (ms)")
        )

        self.gw_start_measurement_pushButton.setStatusTip(
            "To evaluate EL data, the scan must include the range of [0°, 90°]!"
        )
        # self.gw_homing_time_label.setText(_translate("MainWindow", "Homing Time (s)"))
        # self.gw_animation.setText(_translate("MainWindow", "small animation"))

        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.goniometer_widget),
            _translate("MainWindow", "Goniometer"),
        )
        # self.menudfg.setTitle(_translate("MainWindow", "File"))
        self.menuSettings.setTitle(_translate("MainWindow", "Settings"))

        # self.actionOpen_Logs.setText(_translate("MainWindow", "Open Logs"))
        # self.actionOpen_Logfile_on_Machine.setText(
        # _translate("MainWindow", "Open Logfile on Machine")
        # )
        self.actionChange_Path.setText(_translate("MainWindow", "Change Saving Path"))
        self.actionOptions.setText(_translate("MainWindow", "Options"))
        self.actionDocumentation.setText(_translate("MainWindow", "Help"))
        self.actionLoad_Measurement_Parameters.setText(
            _translate("MainWindow", "Load Measurement Parameters")
        )
        self.actionSave_Measurement_Parameters.setText(
            _translate("MainWindow", "Save Measurement Settings")
        )
        self.actionOpen_Log.setText(_translate("MainWindow", "Open Log"))

    # ------------------------------------------------------------------------ #
    # ----------------- User Defined UI related Functions -------------------- #
    # ------------------------------------------------------------------------ #
    def center(self):
        # position and size of main window

        # self.showFullScreen()
        qc = self.frameGeometry()
        screen = QtWidgets.QApplication.primaryScreen()
        cp = screen.availableGeometry().center()
        qc.moveCenter(cp)
        self.move(qc.topLeft())
