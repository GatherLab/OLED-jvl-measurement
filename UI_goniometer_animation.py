from PySide2 import QtCore, QtGui, QtWidgets


class Ui_GoniometerAnimation(QtWidgets.QWidget):
    """
    This class represents the goniometer animation that shows the current
    position of the motor stage. It is used to update and draw the animation.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )

        # Initial position
        self.position = 0

    def sizeHint(self):
        """
        Function needed to scale the widget
        """
        return QtCore.QSize(40, 140)

    def paintEvent(self, e):
        """
        Paint event that is called when the update function is called on the class
        """
        painter = QtGui.QPainter(self)

        # Set a plain background in the overall design color
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor("#2C313C"))
        brush.setStyle(QtCore.Qt.SolidPattern)
        rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
        painter.fillRect(rect, brush)
        rect.center()

        # The following looks relatively complicated but in the end it is just
        # some calculations to make the drawing look nice and have everything
        # at its right position
        circle_radius = 52
        circle_thickness = 4
        letter_width = 6
        letter_height = 9
        arc_thickness = 8
        margin = 2

        painter.setPen(
            QtGui.QPen(QtGui.QColor("#E0E0E0"), circle_thickness, QtCore.Qt.SolidLine)
        )
        painter.drawEllipse(rect.center(), circle_radius, circle_radius)
        painter.drawText(
            rect.center().toTuple()[0] + circle_radius + circle_thickness + margin,
            rect.center().toTuple()[1] + letter_height / 2,
            "0°",
        )
        painter.drawText(
            rect.center().toTuple()[0]
            - circle_radius
            - circle_thickness
            - margin
            - letter_width * len(str("180°")),
            rect.center().toTuple()[1] + letter_height / 2,
            "180°",
        )

        painter.drawText(
            rect.center().toTuple()[0] - letter_width * len(str("90°")) / 2,
            rect.center().toTuple()[1] - circle_radius - circle_thickness - margin,
            "90°",
        )
        painter.drawText(
            rect.center().toTuple()[0] - letter_width * len(str("-90°")) / 2,
            rect.center().toTuple()[1]
            + circle_radius
            + circle_thickness
            + margin
            + letter_height,
            "-90°",
        )

        painter.setPen(
            QtGui.QPen(QtGui.QColor("#55AAFF"), arc_thickness, QtCore.Qt.SolidLine)
        )
        painter.drawArc(
            rect.center().toTuple()[0]
            - circle_radius
            + (circle_thickness + arc_thickness + margin) / 2,
            rect.center().toTuple()[1]
            - circle_radius
            + (circle_thickness + arc_thickness + margin) / 2,
            circle_radius * 2 - margin - circle_thickness - arc_thickness,
            circle_radius * 2 - margin - circle_thickness - arc_thickness,
            0 * 16,
            16 * self.position,
        )
        painter.drawText(
            rect.center().toTuple()[0]
            - letter_width * len(str(self.position) + "°") / 2,
            rect.center().toTuple()[1] + letter_height / 2,
            str(self.position) + "°",
        )
        painter.end()

    def _trigger_refresh(self):
        self.update()

    def move(self, position):
        """
        Function to trigger a move of the position animation for the goniometer
        """
        self.position = position
        self.update()
