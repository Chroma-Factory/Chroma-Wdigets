# -*- coding: utf-8 -*-


from PySide2.QtWidgets import QHBoxLayout, QLineEdit, QToolButton, QTextEdit, QPlainTextEdit

from chroma_wdigets.components.widgets.menu import LineEditMenu, TextEditMenu
from chroma_wdigets.components.widgets.scroll_bar import SmoothScrollDelegate
from chroma_wdigets.common.icon import ChromaIcon
from chroma_wdigets.common.theme import is_dark_theme, theme_color, ChromaStyleSheet
from chroma_wdigets.common.icon import draw_icon
from chroma_wdigets.common.font import set_font

from Qt import QtGui
from Qt import QtCore
from Qt import QtWidgets


class LineEditButton(QtWidgets.QToolButton):
    """ Line edit button """

    def __init__(self, icon, parent=None):
        super().__init__(parent=parent)
        self._icon = icon
        self.is_pressed = False
        self.setFixedSize(31, 23)
        self.setIconSize(QtCore.QSize(10, 10))
        self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.setObjectName("lineEditButton")
        ChromaStyleSheet.LINE_EDIT.apply(self)

    def mousePressEvent(self, e):
        self.is_pressed = True
        super(LineEditButton, self).mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.is_pressed = False
        super(LineEditButton, self).mouseReleaseEvent(e)

    def paintEvent(self, e):
        super(LineEditButton, self).paintEvent(e)
        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing |
                               QtGui.QPainter.SmoothPixmapTransform)

        iw, ih = self.iconSize().width(), self.iconSize().height()
        w, h = self.width(), self.height()
        rect = QtCore.QRectF((w - iw)/2, (h - ih)/2, iw, ih)

        if self.is_pressed:
            painter.setOpacity(0.7)

        if is_dark_theme():
            draw_icon(self._icon, painter, rect)
        else:
            draw_icon(self._icon, painter, rect, fill='#656565')


class LineEdit(QLineEdit):
    """ Line edit """

    def __init__(self, parent=None):
        super(LineEdit, self).__init__(parent=parent)
        self._is_clear_button_enabled = False

        self.setProperty("transparent", True)
        ChromaStyleSheet.LINE_EDIT.apply(self)
        self.setFixedHeight(33)
        self.setAttribute(QtCore.Qt.WA_MacShowFocusRect, False)
        set_font(self)

        self.h_layout = QHBoxLayout(self)
        self.clear_button = LineEditButton(ChromaIcon.CLOSE, self)

        self.clear_button.setFixedSize(29, 25)
        self.clear_button.hide()

        self.h_layout.setSpacing(3)
        self.h_layout.setContentsMargins(4, 4, 4, 4)
        self.h_layout.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.h_layout.addWidget(self.clear_button, 0, QtCore.Qt.AlignRight)

        self.clear_button.clicked.connect(self.clear)
        self.textChanged.connect(self._on_text_changed)

    def set_clear_button_enabled(self, enable):
        self._is_clear_button_enabled = enable
        self.setTextMargins(0, 0, 28*enable, 0)

    def contextMenuEvent(self, e):
        menu = LineEditMenu(self)
        menu.exec(e.globalPos())

    def is_clear_button_enabled(self):
        return self._is_clear_button_enabled

    def focusOutEvent(self, e):
        super(LineEdit, self).focusOutEvent(e)
        self.clear_button.hide()

    def focusInEvent(self, e):
        super(LineEdit, self).focusInEvent(e)
        if self.is_clear_button_enabled():
            self.clear_button.setVisible(bool(self.text()))

    def _on_text_changed(self, text):
        """ text changed slot """
        if self.is_clear_button_enabled():
            self.clear_button.setVisible(bool(text) and self.hasFocus())

    def paintEvent(self, e):
        super(LineEdit, self).paintEvent(e)
        if not self.hasFocus():
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing)
        painter.setPen(QtCore.Qt.NoPen)

        m = self.contentsMargins()
        path = QtGui.QPainterPath()
        w, h = self.width()-m.left()-m.right(), self.height()
        path.addRoundedRect(QtCore.QRectF(m.left(), h-10, w, 10), 5, 5)

        rect_path = QtGui.QPainterPath()
        rect_path.addRect(m.left(), h-10, w, 8)
        path = path.subtracted(rect_path)

        painter.fillPath(path, theme_color())


class SearchLineEdit(LineEdit):
    """ Search line edit """

    searched = QtCore.Signal(str)
    cleared = QtCore.Signal()

    def __init__(self, parent=None):
        super(SearchLineEdit, self).__init__(parent)
        self.search_button = LineEditButton(ChromaIcon.SEARCH, self)

        self.h_layout.addWidget(self.search_button, 0, QtCore.Qt.AlignRight)
        self.set_clear_button_enabled(True)
        self.setTextMargins(0, 0, 59, 0)

        self.search_button.clicked.connect(self.search)
        self.clear_button.clicked.connect(self.cleared)

    def search(self):
        """ emit search signal """
        text = self.text().strip()
        if text:
            self.searched.emit(text)
        else:
            self.cleared.emit()


class TextEdit(QTextEdit):
    """ Text edit """

    def __init__(self, parent=None):
        super(TextEdit, self).__init__(parent=parent)
        self.scrollDelegate = SmoothScrollDelegate(self)
        ChromaIcon.LINE_EDIT.apply(self)
        set_font(self)

    def contextMenuEvent(self, e):
        menu = TextEditMenu(self)
        menu.exec_(e.globalPos())


class PlainTextEdit(QPlainTextEdit):
    """ Plain text edit """

    def __init__(self, parent=None):
        super(PlainTextEdit, self).__init__(parent=parent)
        self.scrollDelegate = SmoothScrollDelegate(self)
        ChromaIcon.LINE_EDIT.apply(self)
        set_font(self)

    def contextMenuEvent(self, e):
        menu = TextEditMenu(self)
        menu.exec_(e.globalPos())

