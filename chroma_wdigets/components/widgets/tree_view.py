# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from Qt import QtWidgets
from Qt import QtGui
from Qt import QtCore

from chroma_wdigets.common.theme import (
    ChromaStyleSheet, theme_color, is_dark_theme)
from chroma_wdigets.common.font import get_font
from chroma_wdigets.components.widgets.scroll_area import SmoothScrollDelegate


class TreeItemDelegate(QtWidgets.QStyledItemDelegate):
    """ Tree item delegate """

    def __init__(self, parent):
        super(TreeItemDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        painter.setRenderHints(
            QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing)
        super(TreeItemDelegate, self).paint(painter, option, index)

        if not (option.state & (
                QtWidgets.QStyle.State_Selected |
                QtWidgets.QStyle.State_MouseOver)):
            return

        painter.save()
        painter.setPen(QtCore.Qt.NoPen)

        # draw background
        h = option.rect.height() - 4
        c = 255 if is_dark_theme() else 0
        painter.setBrush(QtGui.QColor(c, c, c, 9))
        painter.drawRoundedRect(
            0, option.rect.y() + 2, self.parent().width() - 8, h, 4, 4)

        # draw indicator
        if (option.state & QtWidgets.QStyle.State_Selected and
                self.parent().horizontalScrollBar().value() == 0):
            painter.setBrush(theme_color())
            painter.drawRoundedRect(1, 8 + option.rect.y(), 3, h - 11, 1.5, 1.5)

        painter.restore()

    def initStyleOption(self, option, index):
        super(TreeItemDelegate, self).initStyleOption(option, index)
        option.font = get_font(13)
        if is_dark_theme():
            option.palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
            option.palette.setColor(
                QtGui.QPalette.HighlightedText, QtCore.Qt.white)
        else:
            option.palette.setColor(QtGui.QPalette.Text, QtCore.Qt.black)
            option.palette.setColor(
                QtGui.QPalette.HighlightedText, QtCore.Qt.black)


class TreeViewBase(object):
    """ Tree view base class """

    def _init_view(self):
        self.scroll_delegate = SmoothScrollDelegate(self)

        self.setItemDelegate(TreeItemDelegate(self))
        self.setIconSize(QtCore.QSize(16, 16))

        ChromaStyleSheet.TREE_VIEW.apply(self)

    def draw_branches(self, painter, rect, index):
        rect.moveLeft(15)
        return QtWidgets.QTreeView.drawBranches(self, painter, rect, index)


class TreeWidget(TreeViewBase, QtWidgets.QTreeWidget):

    def __init__(self, parent=None):
        super(TreeWidget, self).__init__(parent=parent)
        self._init_view()


class TreeView(TreeViewBase, QtWidgets.QTreeView):

    def __init__(self, parent=None):
        super(TreeView, self).__init__(parent=parent)
        self._init_view()
