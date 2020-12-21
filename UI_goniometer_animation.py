from PySide2 import QtCore, QtGui, QtWidgets


class Ui_GoniometerAnimation(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )

    def sizeHint(self):
        return QtCore.QSize(40, 120)

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)

        brush = QtGui.QBrush()
        # Set background color
        brush.setColor(QtGui.QColor("#2C313C"))
        brush.setStyle(QtCore.Qt.SolidPattern)
        rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
        painter.fillRect(rect, brush)

        # # Get current state.
        # vmin, vmax = 0, 360
        # value = 100

        # padding = 5

        # # Define our canvas.
        # d_height = painter.device().height() - (padding * 2)
        # d_width = painter.device().width() - (padding * 2)

        # # Draw the bars.
        # step_size = d_height / 5
        # bar_height = step_size * 0.6
        # bar_spacer = step_size * 0.4 / 2

        # pc = (value - vmin) / (vmax - vmin)
        # n_steps_to_draw = int(pc * 5)
        # brush.setColor(QtGui.QColor("red"))
        # for n in range(n_steps_to_draw):
        #     rect = QtCore.QRect(
        #         padding,
        #         padding + d_height - ((n + 1) * step_size) + bar_spacer,
        #         d_width,
        #         bar_height,
        #     )
        #     painter.fillRect(rect, brush)
        position = 360
        painter.setPen(QtGui.QPen(QtGui.QColor("#E0E0E0"), 4, QtCore.Qt.SolidLine))
        painter.drawEllipse(35, 17, 100, 100)
        painter.drawText(142, 72, "0°")
        painter.drawText(75, 10, "90°")
        painter.drawText(8, 72, "180°")
        painter.setPen(QtGui.QPen(QtGui.QColor("#55AAFF"), 14, QtCore.Qt.SolidLine))
        painter.drawArc(45, 27, 80, 80, 0 * 16, -16 * position)
        painter.drawText(75, 72, str(position) + "°")
        painter.end()

    def _trigger_refresh(self):
        self.update()
