# coding:utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from Qt import QtGui
from Qt import QtCore

from .progress_bar import ProgressBar
from chroma_wdigets.common.theme import theme_color, is_dark_theme
from chroma_wdigets.common.font import set_font


class ProgressRing(ProgressBar):
    """ Progress ring """

    def __init__(self, parent=None, use_ani=True):
        super(ProgressRing, self).__init__(parent, use_ani=use_ani)
        self.light_background_color = QtGui.QColor(0, 0, 0, 34)
        self.dark_background_color = QtGui.QColor(255, 255, 255, 34)

        self.setTextVisible(False)
        self.setFixedSize(100, 100)

        set_font(self)

    def _draw_text(self, painter, text):
        """ draw text """
        painter.setFont(self.font())
        painter.setPen(QtCore.Qt.white if is_dark_theme() else QtCore.Qt.black)
        painter.drawText(self.rect(), QtCore.Qt.AlignCenter, text)

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing)

        cw = 6  # circle thickness
        w = min(self.height(), self.width()) - cw
        rc = QtCore.QRectF(cw / 2, self.height() / 2 - w / 2, w, w)

        # draw background
        bc = self.dark_background_color if is_dark_theme() else self.light_background_color
        pen = QtGui.QPen(bc, cw, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawArc(rc, 0, 360 * 16)

        if self.maximum() <= self.minimum():
            return

        # draw bar
        pen.setColor(theme_color())
        painter.setPen(pen)
        degree = int(self.val / (self.maximum() - self.minimum()) * 360)
        painter.drawArc(rc, 90 * 16, -degree * 16)

        # draw text
        if self.isTextVisible():
            self._draw_text(painter, self.val_text())
