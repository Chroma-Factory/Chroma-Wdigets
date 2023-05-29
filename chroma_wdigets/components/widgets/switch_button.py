# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from enum import Enum

from Qt import QtGui
from Qt import QtCore
from Qt import QtWidgets

from chroma_wdigets.common.theme import ChromaStyleSheet
from chroma_wdigets.common.config import PRIMARY_COLOR


class Indicator(QtWidgets.QToolButton):
    """ Indicator of switch button """

    checked_changed = QtCore.Signal(bool)

    def __init__(self, parent):
        super(Indicator, self).__init__(parent=parent)
        self.setCheckable(True)
        self.setChecked(False)
        self.resize(37, 16)
        self._slider_on_color = QtGui.QColor(QtCore.Qt.white)
        self._slider_off_color = QtGui.QColor(PRIMARY_COLOR)
        self._slider_disabled_color = QtGui.QColor(QtGui.QColor(155, 154, 153))
        self.timer = QtCore.QTimer(self)
        self.padding = self.height() // 4
        self.slider_x = self.padding
        self.slider_radius = (self.height() - 2 * self.padding) // 2
        self.slider_end_x = self.width() - 2 * self.slider_radius
        self.slider_step = self.width() / 50
        self.timer.timeout.connect(self._update_slider_pos)

    def _update_slider_pos(self):
        """ update slider position """
        if self.isChecked():
            if self.slider_x + self.slider_step < self.slider_end_x:
                self.slider_x += self.slider_step
            else:
                self.slider_x = self.slider_end_x
                self.timer.stop()
        else:
            if self.slider_x - self.slider_step > self.slider_end_x:
                self.slider_x -= self.slider_step
            else:
                self.slider_x = self.padding
                self.timer.stop()

        self.style().polish(self)

    def setChecked(self, is_checked):
        """ set checked state """
        if is_checked == self.isChecked():
            return

        super(Indicator, self).setChecked(is_checked)
        self.slider_radius = (self.height() - 2 * self.padding) // 2
        self.slider_end_x = (
            self.width() - 2 * self.slider_radius - self.padding
            if is_checked else self.padding
        )
        self.timer.start(5)

    def toggle(self):
        self.setChecked(not self.isChecked())

    def mouseReleaseEvent(self, e):
        """ toggle checked state when mouse release"""
        super(Indicator, self).mouseReleaseEvent(e)
        self.slider_end_x = (
            self.width() - 2 * self.slider_radius - self.padding
            if self.isChecked() else self.padding
        )
        self.timer.start(5)
        self.checked_changed.emit(self.isChecked())

    def resizeEvent(self, e):
        self.padding = self.height() // 4
        self.slider_radius = (self.height() - 2 * self.padding) // 2
        self.slider_step = self.width() / 50
        self.slider_end_x = (
            self.width() - 2 * self.slider_radius - self.padding
            if self.isChecked() else self.padding
        )
        self.update()

    def paintEvent(self, e):
        """ paint indicator """
        # the background and border are specified by qss
        super(Indicator, self).paintEvent(e)

        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing)
        painter.setPen(QtCore.Qt.NoPen)

        if self.isEnabled():
            color = (self.get_slider_on_color()
                     if self.isChecked() else
                     self.get_slider_off_color())
        else:
            color = self.get_slider_disabled_color()

        painter.setBrush(color)
        painter.drawEllipse(int(self.slider_x), int(self.padding),
                            self.slider_radius * 2, self.slider_radius * 2)

    def get_slider_on_color(self):
        return self._slider_on_color

    def set_slider_on_color(self, color):
        self._slider_on_color = color
        self.update()

    def get_slider_off_color(self):
        return self._slider_off_color

    def set_slider_off_color(self, color):
        self._slider_off_color = color
        self.update()

    def get_slider_disabled_color(self):
        return self._slider_disabled_color

    def set_slider_disabled_color(self, color):
        self._slider_disabled_color = color
        self.update()


class IndicatorPosition(Enum):
    """ Indicator position """
    LEFT = 0
    RIGHT = 1


class SwitchButton(QtWidgets.QWidget):
    """ Switch button class """

    checked_changed = QtCore.Signal(bool)

    def __init__(self, text='', parent=None,
                 indicator_pos=IndicatorPosition.LEFT):
        super(SwitchButton, self).__init__(parent=parent)
        self._text = 'Off'
        self._off_text = text or 'Off'
        self._on_text = 'On'
        self._spacing = 12
        self.indicator_pos = indicator_pos
        self.h_box = QtWidgets.QHBoxLayout(self)
        self.indicator = Indicator(self)
        self.label = QtWidgets.QLabel(self._text, self)
        self._init_widget()

        if text:
            self.set_text(text)

    def _init_widget(self):
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setFixedHeight(37)
        self.installEventFilter(self)

        # set layout
        self.h_box.setSpacing(self._spacing)
        self.h_box.setContentsMargins(2, 0, 0, 0)

        if self.indicator_pos == IndicatorPosition.LEFT:
            self.h_box.addWidget(self.indicator)
            self.h_box.addWidget(self.label)
            self.h_box.setAlignment(QtCore.Qt.AlignLeft)
        else:
            self.h_box.addWidget(self.label, 0, QtCore.Qt.AlignRight)
            self.h_box.addWidget(self.indicator, 0, QtCore.Qt.AlignRight)
            self.h_box.setAlignment(QtCore.Qt.AlignRight)

        ChromaStyleSheet.SWITCH_BUTTON.apply(self)

        self.indicator.toggled.connect(self._update_text)
        self.indicator.toggled.connect(self.checked_changed)

    def eventFilter(self, obj, e):
        if obj is self:
            if e.type() == QtCore.QEvent.MouseButtonPress:
                self.indicator.setDown(True)
            elif e.type() == QtCore.QEvent.MouseButtonRelease:
                self.indicator.setDown(False)
                self.indicator.toggle()
            elif e.type() == QtCore.QEvent.Enter:
                self.indicator.setAttribute(QtCore.Qt.WA_UnderMouse, True)
                e = QtGui.QHoverEvent(
                    QtCore.QEvent.HoverEnter, QtCore.QPoint(),
                    QtCore.QPoint(1, 1)
                )
                QtWidgets.QApplication.sendEvent(self.indicator, e)
            elif e.type() == QtCore.QEvent.Leave:
                self.indicator.setAttribute(QtCore.Qt.WA_UnderMouse, False)
                e = QtGui.QHoverEvent(
                    QtCore.QEvent.HoverLeave, QtCore.QPoint(1, 1),
                    QtCore.QPoint()
                )
                QtWidgets.QApplication.sendEvent(self.indicator, e)

        return super(SwitchButton, self).eventFilter(obj, e)

    def is_checked(self):
        return self.indicator.isChecked()

    def set_checked(self, isChecked):
        """ set checked state """
        self._update_text()
        self.indicator.setChecked(isChecked)

    def toggle_checked(self):
        """ toggle checked state """
        self.indicator.setChecked(not self.indicator.isChecked())

    def _update_text(self):
        self.set_text(self.get_on_text()
                      if self.is_checked() else
                      self.get_off_text())
        self.adjustSize()

    def get_text(self):
        return self._text

    def set_text(self, text):
        self._text = text
        self.label.setText(text)
        self.adjustSize()

    def get_spacing(self):
        return self._spacing

    def set_spacing(self, spacing):
        self._spacing = spacing
        self.h_box.setSpacing(spacing)
        self.update()

    def get_on_text(self):
        return self._on_text

    def set_on_text(self, text):
        self._on_text = text
        self._update_text()

    def get_off_text(self):
        return self._off_text

    def set_off_text(self, text):
        self._off_text = text
        self._update_text()
