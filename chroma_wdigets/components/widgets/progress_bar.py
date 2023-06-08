# -*- coding: utf-8 -
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from math import floor

from Qt import QtWidgets
from Qt import QtCore
from Qt import QtGui

from chroma_wdigets.common.theme import is_dark_theme, theme_color


class ProgressBar(QtWidgets.QProgressBar):
    def __init__(self, parent=None, use_ani=True):
        super(ProgressBar, self).__init__(parent)
        self._val = 0
        self.setFixedHeight(4)

        self._use_ani = use_ani
        self.light_background_color = QtGui.QColor(0, 0, 0, 155)
        self.dark_background_color = QtGui.QColor(255, 255, 255, 155)
        self.ani = QtCore.QPropertyAnimation(self, b'val', self)

        self._is_paused = False
        self._is_error = False
        self.valueChanged.connect(self._on_value_changed)
        self.setValue(0)

    def get_val(self):
        return self._val

    def set_val(self, v):
        self._val = v
        self.update()

    def is_use_ani(self):
        return self._use_ani

    def set_use_ani(self, is_use):
        self._use_ani = is_use

    def _on_value_changed(self, value):
        if not self.use_ani:
            self._val = value
            return

        self.ani.stop()
        self.ani.setEndValue(value)
        self.ani.setDuration(150)
        self.ani.start()
        super(ProgressBar, self).setValue(value)

    def set_custom_background_color(self, light, dark):
        """ set the custom background color

        Parameters
        ----------
        light, dark: str | Qt.GlobalColor | QColor
            background color in light/dark theme mode
        """
        self.light_background_color = QtGui.QColor(light)
        self.dark_background_color = QtGui.QColor(dark)
        self.update()

    def resume(self):
        self._is_paused = False
        self._is_error = False
        self.update()

    def pause(self):
        self._is_paused = True
        self.update()

    def set_paused(self, is_paused):
        self._is_paused = is_paused
        self.update()

    def is_paused(self):
        return self._is_paused

    def error(self):
        self._is_error = True
        self.update()

    def set_error(self, is_error):
        self._is_error = is_error
        if is_error:
            self.error()
        else:
            self.resume()

    def is_error(self):
        return self._is_error

    def val_text(self):
        if self.maximum() <= self.minimum():
            return ""

        total = self.maximum() - self.minimum()
        result = self.format()
        locale = self.locale()
        locale.setNumberOptions(locale.numberOptions()
                                | QtCore.QLocale.OmitGroupSeparator)
        result = result.replace("%m", locale.toString(total))
        result = result.replace("%v", locale.toString(self.val))

        if total == 0:
            return result.replace("%p", locale.toString(100))

        progress = int((self.val - self.minimum()) * 100 / total)
        return result.replace("%p", locale.toString(progress))

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing)

        # draw background
        bc = self.dark_background_color if is_dark_theme() else self.light_background_color
        painter.setPen(bc)
        y = floor(self.height() / 2)
        painter.drawLine(0, y, self.width(), y)

        if self.minimum() >= self.maximum():
            return

        # draw bar
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(theme_color())
        w = int(self.val / (self.maximum() - self.minimum()) * self.width())
        r = self.height() / 2
        painter.drawRoundedRect(0, 0, w, self.height(), r, r)

    use_ani = QtCore.Property(bool, is_use_ani, set_use_ani)
    val = QtCore.Property(float, get_val, set_val)


class IndeterminateProgressBar(QtWidgets.QProgressBar):
    """ Indeterminate progress bar """

    def __init__(self, parent=None, start=True):
        super(IndeterminateProgressBar, self).__init__(parent=parent)
        self._short_pos = 0
        self._long_pos = 0
        self.short_bar_ani = QtCore.QPropertyAnimation(self, b'shortPos', self)
        self.long_bar_ani = QtCore.QPropertyAnimation(self, b'longPos', self)

        self._is_error = False

        self.ani_group = QtCore.QParallelAnimationGroup(self)
        self.long_bar_ani_group = QtCore.QSequentialAnimationGroup(self)

        self.short_bar_ani.setDuration(833)
        self.long_bar_ani.setDuration(1167)
        self.short_bar_ani.setStartValue(0)
        self.long_bar_ani.setStartValue(0)
        self.short_bar_ani.setEndValue(1.45)
        self.long_bar_ani.setEndValue(1.75)
        self.long_bar_ani.setEasingCurve(QtCore.QEasingCurve.OutQuad)

        self.ani_group.addAnimation(self.short_bar_ani)
        self.long_bar_ani_group.addPause(785)
        self.long_bar_ani_group.addAnimation(self.long_bar_ani)
        self.ani_group.addAnimation(self.long_bar_ani_group)
        self.ani_group.setLoopCount(-1)

        self.setFixedHeight(4)

        if start:
            self.start()

    @QtCore.Property(float)
    def shortPos(self):
        return self._short_pos

    @shortPos.setter
    def shortPos(self, p):
        self._short_pos = p
        self.update()

    @QtCore.Property(float)
    def longPos(self):
        return self._long_pos

    @longPos.setter
    def longPos(self, p):
        self._long_pos = p
        self.update()

    def start(self):
        self.shortPos = 0
        self.longPos = 0
        self.ani_group.start()
        self.update()

    def stop(self):
        self.ani_group.stop()
        self.shortPos = 0
        self.longPos = 0
        self.update()

    def is_started(self):
        return self.ani_group.state() == QtCore.QParallelAnimationGroup.Running

    def pause(self):
        self.ani_group.pause()
        self.update()

    def resume(self):
        self.ani_group.resume()
        self.update()

    def set_paused(self, is_paused):
        self.ani_group.setPaused(is_paused)
        self.update()

    def is_paused(self):
        return self.ani_group.state() == QtCore.QParallelAnimationGroup.Paused

    def error(self):
        self._is_error = True
        self.ani_group.stop()
        self.update()

    def set_error(self, is_error):
        self._is_error = is_error
        if is_error:
            self.error()
        else:
            self.start()

    def is_error(self):
        return self._is_error

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing)

        painter.setPen(QtCore.Qt.NoPen)

        if self.ani_group.state() == QtCore.QPropertyAnimation.Running:
            painter.setBrush(theme_color())
        elif self.ani_group.state() == QtCore.QPropertyAnimation.Paused:
            painter.setBrush(
                QtGui.QColor(252, 225, 0) if is_dark_theme() else QtGui.QColor(157, 93, 0))
        elif self._is_error:
            painter.setBrush(QtGui.QColor(196, 43, 28))

        # draw short bar
        x = int((self.shortPos - 0.4) * self.width())
        w = int(0.4 * self.width())
        r = self.height() / 2
        painter.drawRoundedRect(x, 0, w, self.height(), r, r)

        # draw long bar
        x = int((self.longPos - 0.6) * self.width())
        w = int(0.6 * self.width())
        r = self.height() / 2
        painter.drawRoundedRect(x, 0, w, self.height(), r, r)
