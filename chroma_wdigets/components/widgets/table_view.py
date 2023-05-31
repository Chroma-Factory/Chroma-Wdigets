# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from Qt import QtWidgets
from Qt import QtGui
from Qt import QtCore

from chroma_wdigets.common.font import get_font
from chroma_wdigets.common.theme import (
    is_dark_theme, ChromaStyleSheet, theme_color
)
from chroma_wdigets.components.widgets.line_edit import LineEdit
from chroma_wdigets.components.widgets.scroll_bar import SmoothScrollDelegate


class TableItemDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent):
        super(TableItemDelegate, self).__init__(parent)
        self.margin = 2
        self.hover_row = -1
        self.pressed_row = -1
        self.selected_rows = set()

    def set_hover_row(self, row):
        self.hover_row = row

    def set_pressed_row(self, row):
        self.pressed_row = row

    def set_selected_rows(self, indexes):
        self.selected_rows.clear()
        for index in indexes:
            self.selected_rows.add(index.row())
            if index.row() == self.pressed_row:
                self.pressed_row = -1

    def sizeHint(self, option, index):
        # increase original sizeHint to accommodate space needed for border
        size = super(TableItemDelegate, self).sizeHint(option, index)
        size = size.grownBy(QtCore.QMargins(0, self.margin, 0, self.margin))
        return size

    def createEditor(self, parent, option, index):
        line_edit = LineEdit(parent)
        line_edit.setStyle(QtWidgets.QApplication.style())
        line_edit.setText(option.text)
        line_edit.setClearButtonEnabled(True)
        return line_edit

    def updateEditorGeometry(self, editor, option, index):
        rect = option.rect
        y = rect.y() + (rect.height() - editor.height()) // 2
        x, w = max(8, rect.x()), rect.width()
        if index.column() == 0:
            w -= 8

        editor.setGeometry(x, y, w, rect.height())

    def _draw_background(self, painter, option, index):
        """ draw row background """
        r = 5
        if index.column() == 0:
            rect = option.rect.adjusted(4, 0, r + 1, 0)
            painter.drawRoundedRect(rect, r, r)
        elif index.column() == index.model().columnCount(index.parent()) - 1:
            rect = option.rect.adjusted(-r - 1, 0, -4, 0)
            painter.drawRoundedRect(rect, r, r)
        else:
            rect = option.rect.adjusted(-1, 0, 1, 0)
            painter.drawRect(rect)

    def _draw_indicator(self, painter, option, index):
        """ draw indicator """
        y, h = option.rect.y(), option.rect.height()
        ph = round(0.4 * h if self.pressed_row == index.row() else 0.26 * h)
        painter.setBrush(theme_color())
        painter.drawRoundedRect(5, ph + y, 3, h - 2 * ph, 1.5, 1.5)

    def initStyleOption(self, option, index):
        super(TableItemDelegate, self).initStyleOption(option, index)
        option.font = get_font(13)
        if is_dark_theme():
            option.palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
            option.palette.setColor(
                QtGui.QPalette.HighlightedText, QtCore.Qt.white)
        else:
            option.palette.setColor(QtGui.QPalette.Text, QtCore.Qt.black)
            option.palette.setColor(
                QtGui.QPalette.HighlightedText, QtCore.Qt.black)

    def paint(self, painter, option, index):
        painter.save()
        painter.setPen(QtCore.Qt.NoPen)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # set clipping rect of painter to avoid painting outside the borders
        painter.setClipping(True)
        painter.setClipRect(option.rect)

        # call original paint method where option.rect is adjusted to account
        # for border
        option.rect.adjust(0, self.margin, 0, -self.margin)

        # draw highlight background
        is_hover = self.hover_row == index.row()
        is_pressed = self.pressed_row == index.row()
        is_alternate = (index.row() % 2 == 0 and
                        self.parent().alternatingRowColors())
        is_dark = is_dark_theme()

        c = 255 if is_dark else 0
        alpha = 0

        if index.row() not in self.selected_rows:
            if is_pressed:
                alpha = 9 if is_dark else 6
            elif is_hover:
                alpha = 12
            elif is_alternate:
                alpha = 5
        else:
            if is_pressed:
                alpha = 15 if is_dark else 9
            elif is_hover:
                alpha = 25
            else:
                alpha = 17

            # draw indicator
            if (index.column() == 0 and
                    self.parent().horizontalScrollBar().value() == 0):
                self._draw_indicator(painter, option, index)

        painter.setBrush(QtGui.QColor(c, c, c, alpha))
        self._draw_background(painter, option, index)

        painter.restore()
        super(TableItemDelegate, self).paint(painter, option, index)


class TableBase(object):
    """ Table base class """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.delegate = TableItemDelegate(self)
        self.scroll_delegate = SmoothScrollDelegate(self)

        # set style sheet
        ChromaStyleSheet.TABLE_VIEW.apply(self)

        self.setShowGrid(False)
        self.setMouseTracking(True)
        self.setAlternatingRowColors(True)
        self.setItemDelegate(self.delegate)
        self.setSelectionBehavior(TableWidget.SelectRows)

        self.entered.connect(lambda i: self._set_hover_row(i.row()))
        self.pressed.connect(lambda i: self._set_pressed_row(i.row()))
        self.verticalHeader().sectionClicked.connect(self.selectRow)

    def showEvent(self, e):
        QtWidgets.QTableView.showEvent(self, e)
        self.resizeRowsToContents()

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
        QtWidgets.QTableView.leaveEvent(self, e)
        self._set_hover_row(-1)

    def resizeEvent(self, e):
        QtWidgets.QTableView.resizeEvent(self, e)
        self.viewport().update()

    def keyPressEvent(self, e):
        QtWidgets.QTableView.keyPressEvent(self, e)
        self._update_selected_rows()

    def mousePressEvent(self, e):
        if e.button() == QtCore.Qt.LeftButton:
            QtWidgets.QTableView.mousePressEvent(self, e)
        else:
            self._set_pressed_row(self.indexAt(e.pos()).row())

    def mouseReleaseEvent(self, e):
        QtWidgets.QTableView.mouseReleaseEvent(self, e)

        row = self.indexAt(e.pos()).row()
        if row >= 0 and e.button() != QtCore.Qt.RightButton:
            self._update_selected_rows()
        else:
            self._set_pressed_row(-1)

    def setItemDelegate(self, delegate):
        self.delegate = delegate
        super(TableBase, self).setItemDelegate(delegate)

    def selectAll(self):
        QtWidgets.QTableView.selectAll(self)
        self._update_selected_rows()

    def selectRow(self, row):
        QtWidgets.QTableView.selectRow(self, row)
        self._update_selected_rows()

    def setSelection(self, rect, command):
        QtWidgets.QTableView.setSelection(self, rect, command)
        self._update_selected_rows()

    def clearSelection(self):
        QtWidgets.QTableView.clearSelection(self)
        self._update_selected_rows()

    def setCurrentIndex(self, index):
        QtWidgets.QTableView.setCurrentIndex(self, index)
        self._update_selected_rows()

    def _update_selected_rows(self):
        self._set_selected_rows(self.selectedIndexes())


class TableWidget(TableBase, QtWidgets.QTableWidget):
    """ Table widget """

    def __init__(self, parent=None):
        super(TableWidget, self).__init__(parent)

    def setCurrentCell(self, row, column, command=None):
        self.setCurrentItem(self.item(row, column), command)

    def setCurrentItem(self, item, command=None):
        if not command:
            super(TableWidget, self).setCurrentItem(item)
        else:
            super(TableWidget, self).setCurrentItem(item, command)

        self._update_selected_rows()


class TableView(TableBase, QtWidgets.QTableView):
    """ Table view """

    def __init__(self, parent=None):
        super(TableView, self).__init__(parent)
