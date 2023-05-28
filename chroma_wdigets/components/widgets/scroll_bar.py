# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from Qt import QtWidgets
from Qt import QtCore
from Qt import QtGui

from chroma_wdigets.common.smooth_scroll import SmoothScroll
from chroma_wdigets.common.icon import ChromaIcon
from chroma_wdigets.common.theme import is_dark_theme


class ArrowButton(QtWidgets.QToolButton):
    """ Arrow button """

    def __init__(self, icon, parent=None):
        super().__init__(parent=parent)
        self.setFixedSize(10, 10)
        self._icon = icon

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing)

        s = 7 if self.isDown() else 8
        x = (self.width() - s) / 2
        self._icon.render(painter, QtCore.QRectF(x, x, s, s), fill="#858789")


class ScrollBarGroove(QtWidgets.QWidget):
    """ Scroll bar groove """

    def __init__(self, orient, parent):
        super(ScrollBarGroove, self).__init__(parent=parent)
        if orient == QtCore.Qt.Vertical:
            self.setFixedWidth(12)
            self.up_button = ArrowButton(ChromaIcon.CARE_UP_SOLID, self)
            self.down_button = ArrowButton(ChromaIcon.CARE_DOWN_SOLID, self)
            self.setLayout(QtWidgets.QVBoxLayout(self))
            self.layout().addWidget(self.up_button, 0, QtCore.Qt.AlignHCenter)
            self.layout().addStretch(1)
            self.layout().addWidget(self.down_button, 0, QtCore.Qt.AlignHCenter)
            self.layout().setContentsMargins(0, 3, 0, 3)
        else:
            self.setFixedHeight(12)
            self.up_button = ArrowButton(ChromaIcon.CARE_LEFT_SOLID, self)
            self.down_button = ArrowButton(ChromaIcon.CARE_RIGHT_SOLID, self)
            self.setLayout(QtWidgets.QHBoxLayout(self))
            self.layout().addWidget(self.up_button, 0, QtCore.Qt.AlignVCenter)
            self.layout().addStretch(1)
            self.layout().addWidget(self.down_button, 0, QtCore.Qt.AlignVCenter)
            self.layout().setContentsMargins(3, 0, 3, 0)

        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.opacity_ani = QtCore.QPropertyAnimation(
            self.opacity_effect, b'opacity', self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

    def fade_in(self):
        self.opacity_ani.setEndValue(1)
        self.opacity_ani.setDuration(150)
        self.opacity_ani.start()

    def fade_out(self):
        self.opacity_ani.setEndValue(0)
        self.opacity_ani.setDuration(150)
        self.opacity_ani.start()

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing)
        painter.setPen(QtCore.Qt.NoPen)

        if not is_dark_theme():
            painter.setBrush(QtGui.QColor(252, 252, 252, 217))
        else:
            painter.setBrush(QtGui.QColor(44, 44, 44, 245))

        painter.drawRoundedRect(self.rect(), 6, 6)


class ScrollBarHandle(QtWidgets.QWidget):
    def __init__(self, orient, parent=None):
        super(ScrollBarHandle, self).__init__(parent)
        self.orient = orient
        if orient == QtCore.Qt.Vertical:
            self.setFixedWidth(3)
        else:
            self.setFixedHeight(3)

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing)
        painter.setPen(QtCore.Qt.NoPen)

        r = (self.width() / 2 if self.orient == QtCore.Qt.Vertical
             else self.height() / 2)
        c = (QtGui.QColor(255, 255, 255, 139) if is_dark_theme()
             else QtGui.QColor(0, 0, 0, 114))
        painter.setBrush(c)
        painter.drawRoundedRect(self.rect(), r, r)


class ScrollBar(QtWidgets.QWidget):
    """ Fluent scroll bar """

    range_changed = QtCore.Signal(tuple)
    value_changed = QtCore.Signal(int)
    slider_pressed = QtCore.Signal()
    slider_released = QtCore.Signal()
    slider_moved = QtCore.Signal()

    def __init__(self, orient, parent):
        super(ScrollBar, self).__init__(parent)
        self.groove = ScrollBarGroove(orient, self)
        self.handle = ScrollBarHandle(orient, self)
        self.timer = QtCore.QTimer(self)

        self._orientation = orient
        self._singleStep = 1
        self._pageStep = 50
        self._padding = 14

        self._minimum = 0
        self._maximum = 0
        self._value = 0

        self._is_pressed = False
        self._is_enter = False
        self._is_expanded = False
        self._pressed_pos = QtCore.QPoint()
        self._is_force_hidden = False

        if orient == QtCore.Qt.Vertical:
            self.partnerBar = parent.verticalScrollBar()
            QtWidgets.QAbstractScrollArea.setVerticalScrollBarPolicy(
                parent, QtCore.Qt.ScrollBarAlwaysOff)
        else:
            self.partnerBar = parent.horizontalScrollBar()
            QtWidgets.QAbstractScrollArea.setHorizontalScrollBarPolicy(
                parent, QtCore.Qt.ScrollBarAlwaysOff)

        self._init_widget(parent)

    def _init_widget(self, parent):
        self.groove.up_button.clicked.connect(self._on_page_up)
        self.groove.down_button.clicked.connect(self._on_page_down)
        self.groove.opacity_ani.valueChanged.connect(
            self._on_opacity_ani_value_changed)

        self.partnerBar.range_changed.connect(self.set_range)
        self.partnerBar.value_changed.connect(self._on_value_changed)
        self.value_changed.connect(self.partnerBar.setValue)

        parent.installEventFilter(self)

        self.set_range(self.partnerBar.minimum(), self.partnerBar.maximum())
        self.setVisible(self.maximum() > 0 and not self._is_force_hidden)
        self._adjust_pos(self.parent().size())

    def _on_page_up(self):
        self.set_value(self.value() - self.page_step())

    def _on_page_down(self):
        self.set_value(self.value() + self.page_step())

    def _on_value_changed(self, value):
        self.val = value

    def value(self):
        return self._value

    @QtCore.Property(int, notify=value_changed)
    def val(self):
        return self._value

    @val.setter
    def val(self, value):
        if value == self.value():
            return

        value = max(self.minimum(), min(value, self.maximum()))
        self._value = value
        self.value_changed.emit(value)

        # adjust the position of handle
        self._adjust_handle_pos()

    def minimum(self):
        return self._minimum

    def maximum(self):
        return self._maximum

    def orientation(self):
        return self._orientation

    def page_step(self):
        return self._pageStep

    def single_step(self):
        return self._singleStep

    def is_slider_down(self):
        return self._is_pressed

    def set_value(self, value):
        self.val = value

    def set_minimum(self, min):
        if min == self.minimum():
            return

        self._minimum = min
        self.range_changed.emit((min, self.maximum()))

    def set_maximum(self, max: int):
        if max == self.maximum():
            return

        self._maximum = max
        self.range_changed.emit((self.minimum(), max))

    def set_range(self, min, max):
        if min > max or (min == self.minimum() and max == self.maximum()):
            return

        self.set_minimum(min)
        self.set_maximum(max)

        self._adjust_handle_size()
        self._adjust_handle_pos()
        self.setVisible(max > 0 and not self._is_force_hidden)

        self.range_changed.emit((min, max))

    def set_page_step(self, step):
        if step >= 1:
            self._pageStep = step

    def set_single_step(self, step):
        if step >= 1:
            self._singleStep = step

    def set_slider_down(self, isDown):
        self._is_pressed = True
        if isDown:
            self.slider_pressed.emit()
        else:
            self.slider_released.emit()

    def expand(self):
        """ expand scroll bar """
        if self._is_expanded or not self.is_enter:
            return

        self._is_expanded = True
        self.groove.fade_in()

    def collapse(self):
        """ collapse scroll bar """
        if not self._is_expanded or self.is_enter:
            return

        self._is_expanded = False
        self.groove.fade_out()

    def enterEvent(self, e):
        self.is_enter = True
        self.timer.stop()
        self.timer.singleShot(200, self.expand)

    def leaveEvent(self, e):
        self.is_enter = False
        self.timer.stop()
        self.timer.singleShot(200, self.collapse)

    def eventFilter(self, obj, e):
        if obj is not self.parent():
            return super().eventFilter(obj, e)

        # adjust the position of slider
        if e.type() == QtCore.QEvent.Resize:
            self._adjust_pos(e.size())

        return super(ScrollBar, self).eventFilter(obj, e)

    def resizeEvent(self, e):
        self.groove.resize(self.size())

    def mousePressEvent(self, e):
        super(ScrollBar, self).mousePressEvent(e)
        self._is_pressed = True
        self._pressed_pos = e.pos()

        if self.childAt(e.pos()) is self.handle or not self._is_slide_resion(e.pos()):
            return

        if self.orientation() == QtCore.Qt.Vertical:
            if e.pos().y() > self.handle.geometry().bottom():
                value = e.pos().y() - self.handle.height() - self._padding
            else:
                value = e.pos().y() - self._padding
        else:
            if e.pos().x() > self.handle.geometry().right():
                value = e.pos().x() - self.handle.width() - self._padding
            else:
                value = e.pos().x() - self._padding

        self.set_value(int(value / self._slide_length() * self.maximum()))
        self.slider_pressed.emit()

    def mouseReleaseEvent(self, e):
        super(ScrollBar, self).mouseReleaseEvent(e)
        self._is_pressed = False
        self.slider_released.emit()

    def mouseMoveEvent(self, e):
        if self.orientation() == QtCore.Qt.Vertical:
            dv = e.pos().y() - self._pressed_pos.y()
        else:
            dv = e.pos().x() - self._pressed_pos.x()

        # don't use `self.setValue()`, because it could be reimplemented
        dv = dv / self._slide_length() * (self.maximum() - self.minimum())
        ScrollBar.set_value(self, self.value() + dv)

        self._pressed_pos = e.pos()
        self.slider_moved.emit()

    def _adjust_pos(self, size):
        if self.orientation() == QtCore.Qt.Vertical:
            self.resize(12, size.height() - 2)
            self.move(size.width() - 13, 1)
        else:
            self.resize(size.width() - 2, 12)
            self.move(1, size.height() - 13)

    def _adjust_handle_size(self):
        p = self.parent()
        if self.orientation() == QtCore.Qt.Vertical:
            total = self.maximum() - self.minimum() + p.height()
            s = int(self._groove_length() * p.height() / max(total, 1))
            self.handle.setFixedHeight(max(40, s))
        else:
            total = self.maximum() - self.minimum() + p.width()
            s = int(self._groove_length() * p.width() / max(total, 1))
            self.handle.setFixedWidth(max(40, s))

    def _adjust_handle_pos(self):
        total = max(self.maximum() - self.minimum(), 1)
        delta = int(self.value() / total * self._slide_length())

        if self.orientation() == QtCore.Qt.Vertical:
            x = self.width() - self.handle.width() - 3
            self.handle.move(x, self._padding + delta)
        else:
            y = self.height() - self.handle.height() - 3
            self.handle.move(self._padding + delta, y)

    def _groove_length(self):
        if self.orientation() == QtCore.Qt.Vertical:
            return self.height() - 2 * self._padding

        return self.width() - 2 * self._padding

    def _slide_length(self):
        if self.orientation() == QtCore.Qt.Vertical:
            return self._groove_length() - self.handle.height()

        return self._groove_length() - self.handle.width()

    def _is_slide_resion(self, pos):
        if self.orientation() == QtCore.Qt.Vertical:
            return self._padding <= pos.y() <= self.height() - self._padding

        return self._padding <= pos.x() <= self.width() - self._padding

    def _on_opacity_ani_value_changed(self):
        opacity = self.groove.opacity_effect.opacity()
        if self.orientation() == QtCore.Qt.Vertical:
            self.handle.setFixedWidth(int(3 + opacity * 3))
        else:
            self.handle.setFixedHeight(int(3 + opacity * 3))

        self._adjust_handle_pos()

    def set_force_hidden(self, isHidden: bool):
        """ whether to force the scrollbar to be hidden """
        self._is_force_hidden = isHidden
        self.setVisible(self.maximum() > 0 and not isHidden)

    def wheelEvent(self, e):
        QtWidgets.QApplication.sendEvent(self.parent().viewport(), e)


class SmoothScrollBar(ScrollBar):
    """ Smooth scroll bar """

    def __init__(self, orient, parent):
        super(SmoothScrollBar, self).__init__(orient, parent)
        self.duration = 500
        self.ani = QtCore.QPropertyAnimation()
        self.ani.setTargetObject(self)
        self.ani.setPropertyName(b"val")
        self.ani.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self.ani.setDuration(self.duration)

        self._value = self.value()

    def set_value(self, value):
        if value == self.value():
            return

        # stop running animation
        self.ani.stop()

        # adjust the duration
        dv = abs(value - self.value())
        if dv < 50:
            self.ani.setDuration(int(self.duration * dv / 70))
        else:
            self.ani.setDuration(self.duration)

        self.ani.setStartValue(self.value())
        self.ani.setEndValue(value)
        self.ani.start()

    def scroll_value(self, value):
        """ scroll the specified distance """
        self._value += value
        self._value = max(self.minimum(), self._value)
        self._value = min(self.maximum(), self._value)
        self.set_value(self._value)

    def scroll_to(self, value):
        """ scroll to the specified position """
        self._value = value
        self._value = max(self.minimum(), self._value)
        self._value = min(self.maximum(), self._value)
        self.set_value(self._value)

    def reset_value(self, value):
        self._value = value

    def mousePressEvent(self, e):
        self.ani.stop()
        super(SmoothScrollBar, self).mousePressEvent(e)
        self._value = self.value()

    def mouseMoveEvent(self, e):
        self.ani.stop()
        super(SmoothScrollBar, self).mouseMoveEvent(e)
        self._value = self.value()

    def set_scroll_animation(self, duration,
                             easing=QtCore.QEasingCurve.OutCubic):
        self.duration = duration
        self.ani.setDuration(duration)
        self.ani.setEasingCurve(easing)


class SmoothScrollDelegate(QtCore.QObject):
    """ Smooth scroll delegate """

    def __init__(self, parent, useAni=False):
        super(SmoothScrollDelegate, self).__init__(parent)
        self.use_ani = useAni
        self.v_scroll_bar = SmoothScrollBar(QtCore.Qt.Vertical, parent)
        self.h_scroll_bar = SmoothScrollBar(QtCore.Qt.Horizontal, parent)
        self.vertical_smooth_scroll = SmoothScroll(parent, QtCore.Qt.Vertical)
        self.horizon_smooth_scroll = SmoothScroll(parent, QtCore.Qt.Horizontal)

        if isinstance(parent, QtWidgets.QAbstractItemView):
            parent.setVerticalScrollMode(
                QtWidgets.QAbstractItemView.ScrollPerPixel)
            parent.setHorizontalScrollMode(
                QtWidgets.QAbstractItemView.ScrollPerPixel)
        if isinstance(parent, QtWidgets.QListView):
            parent.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            parent.horizontalScrollBar().setStyleSheet(
                "QScrollBar:horizontal{height: 0px}")

        parent.viewport().installEventFilter(self)
        parent.setVerticalScrollBarPolicy = self.set_vertical_scroll_bar_policy
        parent.setHorizontalScrollBarPolicy = self.set_horizontal_scroll_bar_policy

    def eventFilter(self, obj, e):
        if e.type() == QtCore.QEvent.Wheel:
            if e.angleDelta().y() != 0:
                if not self.use_ani:
                    self.vertical_smooth_scroll.wheelEvent(e)
                else:
                    self.v_scroll_bar.scroll_value(-e.angleDelta().y())
            else:
                if not self.use_ani:
                    self.horizon_smooth_scroll.wheelEvent(e)
                else:
                    self.h_scroll_bar.scroll_value(-e.angleDelta().x())

            e.setAccepted(True)
            return True

        return super(SmoothScrollDelegate, self).eventFilter(obj, e)

    def set_vertical_scroll_bar_policy(self, policy):
        QtWidgets.QAbstractScrollArea.setVerticalScrollBarPolicy(
            self.parent(), QtCore.Qt.ScrollBarAlwaysOff)
        self.v_scroll_bar.set_force_hidden(
            policy == QtCore.Qt.ScrollBarAlwaysOff)

    def set_horizontal_scroll_bar_policy(self, policy):
        QtWidgets.QAbstractScrollArea.setHorizontalScrollBarPolicy(
            self.parent(), QtCore.Qt.ScrollBarAlwaysOff)
        self.h_scroll_bar.set_force_hidden(
            policy == QtCore.Qt.ScrollBarAlwaysOff)

