# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from enum import Enum

from Qt import QtWidgets
from Qt import QtCore
from Qt import QtGui

from chroma_wdigets.common.theme import ChromaStyleSheet, theme_color
from chroma_wdigets.common.icon import ChromaIconBase, Theme, get_icon_color
from chroma_wdigets.common.font import set_font
from chroma_wdigets.common.config import RESOURCES_PATH
from chroma_wdigets.components.widgets.menu import LineEditMenu


class SpinIcon(ChromaIconBase, Enum):
    """ Spin icon """

    UP = "Up"
    DOWN = "Down"

    def path(self, theme=Theme.DARK):
        return "{}/images/spin_box/{}_{}.svg".format(
            RESOURCES_PATH, self.value, get_icon_color(theme))


class SpinButton(QtWidgets.QToolButton):
    def __init__(self, icon, parent=None):
        super(SpinButton, self).__init__(parent=parent)
        self.is_pressed = False
        self._icon = icon
        self.setFixedSize(31, 23)
        self.setIconSize(QtCore.QSize(10, 10))
        ChromaStyleSheet.SPIN_BOX.apply(self)

    def mousePressEvent(self, e):
        self.is_pressed = True
        super(SpinButton, self).mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.is_pressed = False
        super(SpinButton, self).mouseReleaseEvent(e)

    def paintEvent(self, e):
        super(SpinButton, self).paintEvent(e)
        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing |
                               QtGui.QPainter.SmoothPixmapTransform)

        if self.is_pressed:
            painter.setOpacity(0.7)

        self._icon.render(painter, QtCore.QRectF(10, 9, 11, 11))


class SpinBoxUI(object):
    """ Spin box ui """

    def _setup_ui(self):
        ChromaStyleSheet.SPIN_BOX.apply(self)
        self.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)
        self.setFixedHeight(33)
        set_font(self)

        self.h_box_layout = QtWidgets.QHBoxLayout(self)
        self.up_button = SpinButton(SpinIcon.UP, self)
        self.down_button = SpinButton(SpinIcon.DOWN, self)

        self.h_box_layout.setContentsMargins(0, 4, 4, 4)
        self.h_box_layout.setSpacing(5)
        self.h_box_layout.addWidget(self.up_button, 0, QtCore.Qt.AlignRight)
        self.h_box_layout.addWidget(self.down_button, 0, QtCore.Qt.AlignRight)
        self.h_box_layout.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.up_button.clicked.connect(self.stepUp)
        self.down_button.clicked.connect(self.stepDown)

        self.setAttribute(QtCore.Qt.WA_MacShowFocusRect, False)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, pos):
        menu = LineEditMenu(self.lineEdit())
        menu.exec(self.mapToGlobal(pos))

    def _draw_border_bottom(self):
        if not self.hasFocus():
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing)
        painter.setPen(QtCore.Qt.NoPen)

        path = QtGui.QPainterPath()
        w, h = self.width(), self.height()
        path.addRoundedRect(QtCore.QRectF(0, h - 10, w, 10), 5, 5)

        rect_path = QtGui.QPainterPath()
        rect_path.addRect(0, h - 10, w, 8)
        path = path.subtracted(rect_path)

        painter.fillPath(path, theme_color())


class SpinBox(QtWidgets.QSpinBox, SpinBoxUI):
    """ Spin box """

    def __init__(self, parent=None):
        super(SpinBox, self).__init__(parent=parent)
        self._setup_ui()

    def paintEvent(self, e):
        super(SpinBox, self).paintEvent(e)
        self._draw_border_bottom()


class DoubleSpinBox(QtWidgets.QDoubleSpinBox, SpinBoxUI):
    """ Double spin box """

    def __init__(self, parent=None):
        super(DoubleSpinBox, self).__init__(parent)
        self._setup_ui()

    def paintEvent(self, e):
        super(DoubleSpinBox, self).paintEvent(e)
        self._draw_border_bottom()


class TimeEdit(QtWidgets.QTimeEdit, SpinBoxUI):
    """ Time edit """

    def __init__(self, parent=None):
        super(TimeEdit, self).__init__(parent)
        self._setup_ui()

    def paintEvent(self, e):
        super(TimeEdit, self).paintEvent(e)
        self._draw_border_bottom()


class DateTimeEdit(QtWidgets.QDateTimeEdit, SpinBoxUI):
    """ Date time edit """

    def __init__(self, parent=None):
        super(DateTimeEdit, self).__init__(parent)
        self._setup_ui()

    def paintEvent(self, e):
        super(DateTimeEdit, self).paintEvent(e)
        self._draw_border_bottom()


class DateEdit(QtWidgets.QDateEdit, SpinBoxUI):
    """ Date edit """

    def __init__(self, parent=None):
        super(DateEdit, self).__init__(parent)
        self._setup_ui()

    def paintEvent(self, e):
        super(DateEdit, self).paintEvent(e)
        self._draw_border_bottom()
