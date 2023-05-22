from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from Qt import QtWidgets
from Qt import QtCore
from Qt import QtGui

from chroma_wdigets.common.theme import ChromaStyleSheet
from chroma_wdigets.common.icon import to_q_icon, draw_icon, ChromaIconBase
from chroma_wdigets.common.config import Theme, is_dark_theme


class ButtonBase(object):
    def _position_initial(self):
        pass

    def icon(self):
        return to_q_icon(self._icon)

    def setProperty(self, name, value):
        if name != 'icon':
            return super(PushButton, self).setProperty(name, value)

        return True

    def mousePressEvent(self, e):
        self.is_pressed = True
        super(PushButton, self).mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.is_pressed = False
        super(PushButton, self).mouseReleaseEvent(e)

    def enterEvent(self, e):
        self.is_hover = True
        self.update()

    def leaveEvent(self, e):
        self.is_hover = False
        self.update()

    def draw_icon(self, icon, painter, rect):
        draw_icon(icon, painter, rect)


class PrimaryButtonBase(object):
    def draw_icon(self, icon, painter, rect):
        if isinstance(icon, ChromaIconBase) and self.isEnabled():
            # reverse icon color
            theme = Theme.DARK if not is_dark_theme() else Theme.LIGHT
            icon = icon.icon(theme)
        elif not self.isEnabled():
            painter.setOpacity(0.786 if is_dark_theme() else 0.9)
            icon = icon.icon(Theme.DARK)

        super(PrimaryPushButton, self).draw_icon(icon, painter, rect)


class PushButton(QtWidgets.QPushButton, ButtonBase):
    def __init__(self, text, icon=None, parent=None, *args, **kwargs):
        super(PushButton, self).__init__(
            text=text, parent=parent, *args, **kwargs)
        ChromaStyleSheet.BUTTON.apply(self)

        self.is_pressed = False
        self.is_hover = False

        self.setIconSize(QtCore.QSize(16, 16))
        self.set_icon(icon)

        self._position_initial()

    def set_icon(self, icon):
        if isinstance(icon, ChromaIconBase):
            icon = icon.icon()

        self.setProperty('hasIcon', icon is not None)
        self.setStyle(QtWidgets.QApplication.style())
        self._icon = icon or QtGui.QIcon()
        self.update()

    def paintEvent(self, e):
        super(PushButton, self).paintEvent(e)
        if self._icon is None:
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing |
                               QtGui.QPainter.SmoothPixmapTransform)

        if not self.isEnabled():
            painter.setOpacity(0.43)
        elif self.is_pressed:
            painter.setOpacity(0.63)

        w, h = self.iconSize().width(), self.iconSize().height()
        y = (self.height() - h) / 2
        mw = self.minimumSizeHint().width()
        if mw > 0:
            self.draw_icon(self._icon, painter, QtCore.QRectF(
                12 + (self.width() - mw) // 2, y, w, h))
        else:
            self.draw_icon(self._icon, painter, QtCore.QRectF(12, y, w, h))


class PrimaryPushButton(PushButton, PrimaryButtonBase):
    pass


class HyperlinkButton(QtWidgets.QPushButton):
    """ Hyperlink button """

    def __init__(self, url, text, parent=None):
        super(HyperlinkButton, self).__init__(text=text, parent=parent)
        self._url = QtCore.QUrl()
        ChromaStyleSheet.BUTTON.apply(self)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.clicked.connect(lambda i: QtGui.QDesktopServices.openUrl(
            self.get_url()))

        self.set_url(url)

    def get_url(self):
        return self._url

    def set_url(self, url):
        self._url = QtCore.QUrl(url)


class ToolButton(QtWidgets.QToolButton, ButtonBase):
    def __init__(self, icon, parent=None):
        super().__init__(parent)
        ChromaStyleSheet.BUTTON.apply(self)
        self.is_pressed = False
        self.is_hover = False

        self.setIconSize(QtCore.QSize(16, 16))
        self.set_icon(icon)
        self._position_initial()

    def set_icon(self, icon):
        self._icon = icon
        self.update()

    def paintEvent(self, e):
        super().paintEvent(e)
        if self._icon is None:
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing |
                               QtGui.QPainter.SmoothPixmapTransform)

        if not self.isEnabled():
            painter.setOpacity(0.43)
        elif self.is_pressed:
            painter.setOpacity(0.63)

        w, h = self.iconSize().width(), self.iconSize().height()
        y = (self.height() - h) / 2
        x = (self.width() - w) / 2
        self.draw_icon(self._icon, painter, QtCore.QRectF(x, y, w, h))


class PrimaryToolButton(ToolButton, PrimaryButtonBase):
    pass


class RadioButton(QtWidgets.QRadioButton):
    def __init__(self, text, parent=None):
        super(RadioButton, self).__init__(text=text, parent=parent)
        ChromaStyleSheet.BUTTON.apply(self)
