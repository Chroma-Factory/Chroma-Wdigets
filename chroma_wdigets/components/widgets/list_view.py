# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from Qt import QtWidgets
from Qt import QtCore

from chroma_wdigets.components.widgets.scroll_bar import SmoothScrollDelegate
from chroma_wdigets.components.widgets.table_view import TableItemDelegate
from chroma_wdigets.common.theme import ChromaStyleSheet, theme_color


class ListItemDelegate(TableItemDelegate):
    """ List item delegate """

    def __init__(self, parent):
        super(ListItemDelegate, self).__init__(parent)

    def _draw_background(self, painter, option, index):
        painter.drawRoundedRect(option.rect, 5, 5)

    def _draw_indicator(self, painter, option, index):
        y, h = option.rect.y(), option.rect.height()
        ph = round(0.35 * h if self.pressed_row == index.row() else 0.257 * h)
        painter.setBrush(theme_color())
        painter.drawRoundedRect(0, ph + y, 3, h - 2 * ph, 1.5, 1.5)


class ListBase(object):

    def __init__(self, *args, **kwargs):
        super(ListBase, self).__init__(*args, **kwargs)
        self.delegate = ListItemDelegate(self)
        self.scrollDelegate = SmoothScrollDelegate(self)

        ChromaStyleSheet.LIST_VIEW.apply(self)
        self.setItemDelegate(self.delegate)
        self.setMouseTracking(True)

        self.entered.connect(lambda i: self._set_hover_row(i.row()))
        self.pressed.connect(lambda i: self._set_pressed_row(i.row()))

    def _set_hover_row(self, row):
        """ set hovered row """
        self.delegate.set_hover_row(row)
        self.viewport().update()

    def _set_pressed_row(self, row):
        """ set pressed row """
        self.delegate.set_pressed_row(row)
        self.viewport().update()

    def _set_selected_rows(self, indexes):
        self.delegate.set_selected_rows(indexes)
        self.viewport().update()

    def leaveEvent(self, e):
        QtWidgets.QListView.leaveEvent(self, e)
        self._set_hover_row(-1)

    def resizeEvent(self, e):
        QtWidgets.QListView.resizeEvent(self, e)
        self.viewport().update()

    def keyPressEvent(self, e):
        QtWidgets.QListView.keyPressEvent(self, e)
        self._update_selected_rows()

    def mousePressEvent(self, e):
        if e.button() == QtCore.Qt.LeftButton:
            QtWidgets.QListView.mousePressEvent(self, e)
        else:
            self._set_pressed_row(self.indexAt(e.pos()).row())

    def mouseReleaseEvent(self, e):
        QtWidgets.QListView.mouseReleaseEvent(self, e)

        row = self.indexAt(e.pos()).row()
        if row >= 0 and e.button() != QtCore.Qt.RightButton:
            self._update_selected_rows()
        else:
            self._set_pressed_row(-1)

    def setItemDelegate(self, delegate):
        self.delegate = delegate
        super(ListBase, self).setItemDelegate(delegate)

    def setSelection(self, rect, command):
        QtWidgets.QListView.setSelection(self, rect, command)
        self._update_selected_rows()

    def clearSelection(self):
        QtWidgets.QListView.clearSelection(self)
        self._update_selected_rows()

    def setCurrentIndex(self, index):
        QtWidgets.QListView.setCurrentIndex(self, index)
        self._update_selected_rows()

    def _update_selected_rows(self):
        self._set_selected_rows(self.selectedIndexes())


class ListWidget(ListBase, QtWidgets.QListWidget):
    """ List widget """

    def __init__(self, parent=None):
        super(ListWidget, self).__init__(parent)

    def setCurrentItem(self, item, command=None):
        self.setCurrentRow(self.row(item), command)

    def setCurrentRow(self, row, command=None):
        if not command:
            super(ListWidget, self).setCurrentRow(row)
        else:
            super(ListWidget, self).setCurrentRow(row, command)
        self._update_selected_rows()


class ListView(ListBase, QtWidgets.QListView):
    """ List view """

    def __init__(self, parent=None):
        super(ListView, self).__init__(parent)
