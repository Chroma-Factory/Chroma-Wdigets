# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from enum import Enum

from Qt import QtGui
from Qt import QtCore
from Qt import QtWidgets

from chroma_wdigets.common.theme import ChromaStyleSheet


class ToolTipPosition(Enum):
    """ Info bar position """

    TOP = 0
    BOTTOM = 1
    LEFT = 2
    RIGHT = 3
    TOP_LEFT = 4
    TOP_RIGHT = 5
    BOTTOM_LEFT = 6
    BOTTOM_RIGHT = 7


class ToolTip(QtWidgets.QFrame):
    """ Tool tip """

    def __init__(self, text='', parent=None):
        super(ToolTip, self).__init__(parent=parent)
        self._text = text
        self._duration = 1000

        self.container = QtWidgets.QFrame(self)
        self.timer = QtCore.QTimer(self)

        self.setLayout(QtWidgets.QHBoxLayout())
        self.container_layout = QtWidgets.QHBoxLayout(self.container)
        self.label = QtWidgets.QLabel(text, self)

        # set layout
        self.layout().setContentsMargins(12, 8, 12, 12)
        self.layout().addWidget(self.container)
        self.container_layout.addWidget(self.label)
        self.container_layout.setContentsMargins(8, 6, 8, 6)

        # add opacity effect
        self.opacity_ani = QtCore.QPropertyAnimation(
            self, b'windowOpacity', self)
        self.opacity_ani.setDuration(150)

        # add shadow
        self.shadow_effect = QtWidgets.QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(25)
        self.shadow_effect.setColor(QtGui.QColor(0, 0, 0, 60))
        self.shadow_effect.setOffset(0, 5)
        self.container.setGraphicsEffect(self.shadow_effect)

        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

        # set style
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
        self._set_qss()

    def text(self):
        return self._text

    def set_text(self, text):
        """ set text on tooltip """
        self._text = text
        self.label.setText(text)
        self.container.adjustSize()
        self.adjustSize()

    def duration(self):
        return self._duration

    def set_duration(self, duration):
        """ set tooltip duration in milliseconds
            if `duration <= 0`, tooltip won't disappear automatically
        """
        self._duration = duration

    def _set_qss(self):
        """ set style sheet """
        self.container.setObjectName("container")
        self.label.setObjectName("contentLabel")
        ChromaStyleSheet.TOOLTIP.apply(self)
        self.label.adjustSize()
        self.adjustSize()

    def showEvent(self, e):
        self.opacity_ani.setStartValue(0)
        self.opacity_ani.setEndValue(1)
        self.opacity_ani.start()

        self.timer.stop()
        if self.duration() > 0:
            self.timer.start(self._duration + self.opacity_ani.duration())

        super(ToolTip, self).showEvent(e)

    def hideEvent(self, e):
        self.timer.stop()
        super(ToolTip, self).hideEvent(e)

    def adjust_pos(self, widget, position: ToolTipPosition):
        """ adjust the position of tooltip relative to widget """
        manager = ToolTipPositionManager.make(position)
        self.move(manager.position(self, widget))


class ToolTipPositionManager(object):
    """ Tooltip position manager """

    def position(self, tooltip, parent):
        pos = self._pos(tooltip, parent)
        x, y = pos.x(), pos.y()

        rect = QtWidgets.QApplication.screenAt(
            QtGui.QCursor.pos()).availableGeometry()
        x = min(max(-2, x) if QtGui.QCursor().pos().x() >= 0 else x,
                rect.width() - tooltip.width() - 4)
        y = min(max(-2, y), rect.height() - tooltip.height() - 4)
        return QtCore.QPoint(x, y)

    def _pos(self, tooltip, parent):
        raise NotImplementedError

    @staticmethod
    def make(position):
        """ mask info bar manager according to the display position """
        managers = {
            ToolTipPosition.TOP: TopToolTipManager,
            ToolTipPosition.BOTTOM: BottomToolTipManager,
            ToolTipPosition.LEFT: LeftToolTipManager,
            ToolTipPosition.RIGHT: RightToolTipManager,
            ToolTipPosition.TOP_RIGHT: TopRightToolTipManager,
            ToolTipPosition.BOTTOM_RIGHT: BottomRightToolTipManager,
            ToolTipPosition.TOP_LEFT: TopLeftToolTipManager,
            ToolTipPosition.BOTTOM_LEFT: BottomLeftToolTipManager,
        }

        if position not in managers:
            raise ValueError('`{}` is an invalid info bar position.'.format(
                position))

        return managers[position]()


class TopToolTipManager(ToolTipPositionManager):
    """ Top tooltip position manager """

    def _pos(self, tooltip, parent):
        pos = parent.mapToGlobal(QtCore.QPoint())
        x = pos.x() + parent.width() // 2 - tooltip.width() // 2
        y = pos.y() - tooltip.height()
        return QtCore.QPoint(x, y)


class BottomToolTipManager(ToolTipPositionManager):
    """ Bottom tooltip position manager """

    def _pos(self, tooltip, parent):
        pos = parent.mapToGlobal(QtCore.QPoint())
        x = pos.x() + parent.width() // 2 - tooltip.width() // 2
        y = pos.y() + parent.height()
        return QtCore.QPoint(x, y)


class LeftToolTipManager(ToolTipPositionManager):
    """ Left tooltip position manager """

    def _pos(self, tooltip, parent):
        pos = parent.mapToGlobal(QtCore.QPoint())
        x = pos.x() - tooltip.width()
        y = pos.y() + (parent.height() - tooltip.height()) // 2
        return QtCore.QPoint(x, y)


class RightToolTipManager(ToolTipPositionManager):
    """ Right tooltip position manager """

    def _pos(self, tooltip, parent):
        pos = parent.mapToGlobal(QtCore.QPoint())
        x = pos.x() + parent.width()
        y = pos.y() + (parent.height() - tooltip.height()) // 2
        return QtCore.QPoint(x, y)


class TopRightToolTipManager(ToolTipPositionManager):
    """ Top right tooltip position manager """

    def _pos(self, tooltip, parent):
        pos = parent.mapToGlobal(QtCore.QPoint())
        x = (pos.x() + parent.width() - tooltip.width() +
             tooltip.layout().contentsMargins().right())
        y = pos.y() - tooltip.height()
        return QtCore.QPoint(x, y)


class TopLeftToolTipManager(ToolTipPositionManager):
    """ Top left tooltip position manager """

    def _pos(self, tooltip, parent):
        pos = parent.mapToGlobal(QtCore.QPoint())
        x = pos.x() - tooltip.layout().contentsMargins().left()
        y = pos.y() - tooltip.height()
        return QtCore.QPoint(x, y)


class BottomRightToolTipManager(ToolTipPositionManager):
    """ Bottom right tooltip position manager """

    def _pos(self, tooltip, parent):
        pos = parent.mapToGlobal(QtCore.QPoint())
        x = (pos.x() + parent.width() - tooltip.width() +
             tooltip.layout().contentsMargins().right())
        y = pos.y() + parent.height()
        return QtCore.QPoint(x, y)


class BottomLeftToolTipManager(ToolTipPositionManager):
    """ Bottom left tooltip position manager """

    def _pos(self, tooltip, parent):
        pos = parent.mapToGlobal(QtCore.QPoint())
        x = pos.x() - tooltip.layout().contentsMargins().left()
        y = pos.y() + parent.height()
        return QtCore.QPoint(x, y)


class ToolTipFilter(QtCore.QObject):
    """ Tool button with a tool tip """

    def __init__(self, parent, show_delay=300, position=ToolTipPosition.TOP):
        super(ToolTipFilter, self).__init__(parent=parent)
        self.is_enter = False
        self._tooltip = None
        self._tooltip_delay = show_delay
        self.position = position
        self.timer = QtCore.QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.show_tool_tip)

    def eventFilter(self, obj, e):
        if e.type() == QtCore.QEvent.ToolTip:
            return True
        elif e.type() in [QtCore.QEvent.Hide, QtCore.QEvent.Leave]:
            self.hide_tool_tip()
        elif e.type() == QtCore.QEvent.Enter:
            self.is_enter = True
            parent = self.parent()
            if self._can_show_tool_tip():
                if self._tooltip is None:
                    self._tooltip = ToolTip(parent.toolTip(), parent.window())

                t = (parent.toolTipDuration()
                     if parent.toolTipDuration() > 0 else -1)
                self._tooltip.set_duration(t)

                # show the tool tip after delay
                self.timer.start(self._tooltip_delay)
        elif e.type() == QtCore.QEvent.MouseButtonPress:
            self.hide_tool_tip()

        return super(ToolTipFilter, self).eventFilter(obj, e)

    def hide_tool_tip(self):
        """ hide tool tip """
        self.is_enter = False
        self.timer.stop()
        if self._tooltip:
            self._tooltip.hide()

    def show_tool_tip(self):
        """ show tool tip """
        if not self.is_enter:
            return

        parent = self.parent()
        self._tooltip.set_text(parent.toolTip())
        self._tooltip.adjust_pos(parent, self.position)
        self._tooltip.show()

    def set_tool_tip_delay(self, delay):
        self._tooltip_delay = delay

    def _can_show_tool_tip(self):
        parent = self.parent()
        return parent.isWidgetType() and parent.toolTip() and parent.isEnabled()
