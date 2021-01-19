from PySide2 import QtCore, QtGui, QtWidgets
from init_thread import InitThread
from UI_loading_window import Ui_LoadingWindow


class LoadingWindow(QtWidgets.QDialog):
    """
    Window that appears when program is loaded
    """

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_LoadingWindow()
        self.ui.setupUi(self)

        self.parent = parent

        ## REMOVE TITLE BAR
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        ## DROP SHADOW EFFECT
        self.shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 60))
        self.ui.dropShadowFrame.setGraphicsEffect(self.shadow)

        # Initial Text
        self.ui.label_description.setText("<strong>STARTING</strong> PROGRAM")

        self.ui.button_retry.clicked.connect(self.retry_connecting_hardware)
        self.ui.button_continue.clicked.connect(self.kill_dialog)

        self.show()
        self.init_thread = InitThread(self)
        self.init_thread.start()

    @QtCore.Slot(int, str)
    def update_loading_dialog(self, progress, message):
        """
        Update the dialog on signal receive
        """
        self.ui.progressBar.setProperty("value", progress)
        self.ui.label_description.setText("<strong>" + message + "</strong>")

    @QtCore.Slot()
    def kill_dialog(self):
        """
        When the initialisation thread is done, kill this dialog and continue
        """
        self.close()

    @QtCore.Slot()
    def ask_retry(self):
        self.ui.button_retry.show()
        self.ui.button_continue.show()

    def retry_connecting_hardware(self):
        """
        Function that triggers a retry of the initialisation
        """
        self.init_thread = InitThread(self)
        self.init_thread.start()