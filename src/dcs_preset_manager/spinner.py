import os

from PySide2 import QtWidgets, QtCore, QtGui

from .gui import RESOURCE_DIR


class Spinner(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Hide window borders etc.
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Constant blank background
        self.fillColor = QtGui.QColor(30, 30, 30, 120)

        # Icon
        self.pixmap = QtGui.QIcon(os.path.join(RESOURCE_DIR, 'loader.svg')).pixmap(QtCore.QSize(48, 48))

        # Animation Controls
        self.__angle = 0

        self.animation = QtCore.QPropertyAnimation(self, QtCore.QByteArray(b'angle'), self)
        self.animation.setStartValue(0)
        self.animation.setEndValue(360)
        self.animation.setLoopCount(-1)
        self.animation.setDuration(2000)
        self.animation.start()

    def paintEvent(self, evt):

        s = self.size()

        # Background Painter
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing, True)
        qp.setBrush(self.fillColor)
        qp.drawRect(0, 0, s.width(), s.height())

        qp.translate(self.width()/2-24, self.height()/2-24)
        qp.translate(24, 24)
        qp.rotate(self.__angle)
        qp.translate(-24, -24)
        qp.drawPixmap(0, 0, self.pixmap)
        qp.end()

    def _angle(self):
        return self.__angle

    angle = QtCore.Property(int, _angle)

    @angle.setter
    def angle(self, value):
        self.__angle = value
        self.update()
