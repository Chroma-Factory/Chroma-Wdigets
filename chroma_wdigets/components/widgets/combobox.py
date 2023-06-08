# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from Qt import QtWidgets
from Qt import QtGui
from Qt import QtCore

from chroma_wdigets.components.widgets.menu import RoundMenu, MenuItemDelegate, MenuAnimationType
from chroma_wdigets.components.widgets.line_edit import LineEdit, LineEditButton
from chroma_wdigets.common.animation import TranslateYAnimation
from chroma_wdigets.common.icon import ChromaIcon
from chroma_wdigets.common.theme import ChromaStyleSheet, theme_color, \
    is_dark_theme


class ComboItem(object):
    def __init__(self, text, icon=None, userData=None):
        self.text = text
        self.userData = userData
        self.icon = icon

    @property
    def icon(self):
        if isinstance(self._icon, QtGui.QIcon):
            return self._icon

        return self._icon.icon()

    @icon.setter
    def icon(self, ico):
        if ico:
            self._icon = QtGui.QIcon(ico) if isinstance(ico, str) else ico
        else:
            self._icon = QtGui.QIcon()


class ComboMenuItemDelegate(MenuItemDelegate):
    """ Combo box drop menu item delegate """

    def paint(self, painter, option, index):
        super(ComboMenuItemDelegate, self).paint(painter, option, index)
        if not option.state & QtWidgets.QStyle.State_Selected:
            return

        painter.save()
        painter.setRenderHints(
            QtGui.QPainter.Antialiasing |
            QtGui.QPainter.SmoothPixmapTransform |
            QtGui.QPainter.TextAntialiasing
        )

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(theme_color())
        painter.drawRoundedRect(2, 11 + option.rect.y(), 3, 16, 1.5, 1.5)

        painter.restore()


class ComboBoxMenu(RoundMenu):
    """ Combo box menu """

    def __init__(self, parent=None):
        super(ComboBoxMenu, self).__init__(title="", parent=parent)

        self.view.setViewportMargins(5, 2, 5, 6)
        self.view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.view.setItemDelegate(ComboMenuItemDelegate(self))

        ChromaStyleSheet.COMBOBOX.apply(self)
        self.set_item_height(33)

    def exec(self, pos, ani=True, ani_type=MenuAnimationType.DROP_DOWN):
        # todo 应该只这里的问题
        self.view.adjust_size(pos, ani_type)
        self.adjustSize()
        return super(ComboBoxMenu, self).exec(pos, ani, ani_type)


class ComboBoxBase(object):
    def __init__(self, parent=None, **kwargs):
        pass

    def _set_up_ui(self):
        self.is_hover = False
        self.is_pressed = False
        self.items = []
        self._current_index = -1
        self.drop_menu = None

        ChromaStyleSheet.COMBOBOX.apply(self)
        self.installEventFilter(self)

    def add_item(self, text, icon=None, user_data=None):
        item = ComboItem(text, icon, user_data)
        self.items.append(item)

    def add_items(self, texts):
        for text in texts:
            self.add_item(text)

    def remove_item(self, index):
        """ Removes the item at the given index from the combobox.
        This will update the current index if the index is removed.
        """
        if not 0 <= index < len(self.items):
            return

        self.items.pop(index)

        if index < self.current_index():
            self._on_item_clicked(self._current_index - 1)
        elif index == self.current_index():
            if index > 0:
                self._on_item_clicked(self._current_index - 1)
            else:
                self.set_current_index(0)
                self.current_text_changed.emit(self.current_text())
                self.current_index_changed.emit(0)

    def current_index(self):
        return self._current_index

    def set_current_index(self, index):
        if not 0 <= index < len(self.items):
            return

        self._current_index = index
        self.setText(self.items[index].text)

    def setText(self, text):
        super(ComboBoxBase, self).setText(text)
        self.adjustSize()

    def current_text(self):
        if not 0 <= self.current_index() < len(self.items):
            return ''

        return self.items[self.current_index()].text

    def current_data(self):
        if not 0 <= self.current_index() < len(self.items):
            return None

        return self.items[self.current_index()].userData

    def set_current_text(self, text):
        if text == self.current_text():
            return

        index = self.find_text(text)
        if index >= 0:
            self.set_current_index(index)

    def set_item_text(self, index, text):
        if not 0 <= index < len(self.items):
            return

        self.items[index].text = text
        if self.current_index() == index:
            self.setText(text)

    def item_data(self, index):
        """ Returns the data in the given index """
        if not 0 <= index < len(self.items):
            return None

        return self.items[index].userData

    def item_text(self, index):
        """ Returns the text in the given index """
        if not 0 <= index < len(self.items):
            return ''

        return self.items[index].text

    def item_icon(self, index):
        """ Returns the icon in the given index """
        if not 0 <= index < len(self.items):
            return QtGui.QIcon()

        return self.items[index].icon

    def set_item_data(self, index, value):
        """ Sets the data role for the item on the given index """
        if 0 <= index < len(self.items):
            self.items[index].userData = value

    def set_item_icon(self, index, icon):
        """ Sets the data role for the item on the given index """
        if 0 <= index < len(self.items):
            self.items[index].icon = icon

    def find_data(self, data):
        for i, item in enumerate(self.items):
            if item.userData == data:
                return i

        return -1

    def find_text(self, text):
        for i, item in enumerate(self.items):
            if item.text == text:
                return i

        return -1

    def clear(self):
        if self.current_index() >= 0:
            self.setText('')

        self.items.clear()
        self._current_index = -1

    def count(self):
        """ Returns the number of items in the combobox """
        return len(self.items)

    def insert_item(self, index, text, icon=None, user_data=None):
        """ Inserts item into the combobox at the given index. """
        item = ComboItem(text, icon, user_data)
        self.items.insert(index, item)

        if index <= self.current_index():
            self._on_item_clicked(self.current_index() + 1)

    def insert_items(self, index, texts):
        pos = index
        for text in texts:
            item = ComboItem(text)
            self.items.insert(pos, item)
            pos += 1

        if index <= self.current_index():
            self._on_item_clicked(self.current_index() + pos - index)

    def _close_combo_menu(self):
        if not self.drop_menu:
            return

        self.drop_menu.close()
        self.drop_menu = None

    def _on_drop_menu_closed(self):
        pos = self.mapFromGlobal(QtGui.QCursor.pos())
        if not self.rect().contains(pos):
            self.drop_menu = None

    def _show_combo_menu(self):
        if not self.items:
            return

        menu = ComboBoxMenu(self)
        menu.setMaximumHeight(200)
        for i, item in enumerate(self.items):
            menu.add_action(
                QtWidgets.QAction(
                    item.icon, item.text,
                    triggered=lambda x=i: self._on_item_clicked(x)))

        if menu.view.width() < self.width():
            menu.view.setMinimumWidth(self.width())
            menu.adjustSize()

        menu.closed_signal.connect(self._on_drop_menu_closed)
        self.drop_menu = menu

        # set the selected item
        if self.current_index() >= 0 and self.items:
            menu.set_default_action(menu.menu_actions()[self.current_index()])

        menu.view.setMinimumWidth(self.width())
        menu.adjust_size()

        # show menu
        x = (-menu.width() // 2 +
             menu.layout().contentsMargins().left() +
             self.width() // 2)
        y = self.height()
        pos = self.mapToGlobal(QtCore.QPoint(x, y))
        pos.setY(QtGui.QCursor.pos().y())

        ani_type = MenuAnimationType.DROP_DOWN
        # menu.view.adjust_size(pos, ani_type)

        # fixme 位置不对
        print(y)
        print(menu.view.height())

        if menu.view.height() < 120 and menu.view.items_height() > menu.view.height():
            ani_type = MenuAnimationType.PULL_UP
            pos = self.mapToGlobal(QtCore.QPoint(x, 0))
            menu.view.adjust_size(pos, ani_type)

        menu.exec(pos, ani_type=ani_type)

    def _toggle_combo_menu(self):
        if self.drop_menu:
            self._close_combo_menu()
        else:
            self._show_combo_menu()

    def _on_item_clicked(self, index):
        if index == self.current_index():
            return

        self.set_current_index(index)
        self.current_text_changed.emit(self.current_text())
        self.current_index_changed.emit(index)


class ComboBox(QtWidgets.QPushButton, ComboBoxBase):
    """ Combo box """

    current_index_changed = QtCore.Signal(int)
    current_text_changed = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.arrow_ani = TranslateYAnimation(self)
        self._set_up_ui()

    def eventFilter(self, obj, e):
        if obj is self:
            if e.type() == QtCore.QEvent.MouseButtonPress:
                self.is_pressed = True
            elif e.type() == QtCore.QEvent.MouseButtonRelease:
                self.is_pressed = False
            elif e.type() == QtCore.QEvent.Enter:
                self.is_hover = True
            elif e.type() == QtCore.QEvent.Leave:
                self.is_hover = False

        return super(ComboBox, self).eventFilter(obj, e)

    def set_placeholder_text(self, text):
        self.setText(text)

    def mouseReleaseEvent(self, e):
        super(ComboBox, self).mouseReleaseEvent(e)
        self._toggle_combo_menu()

    def paintEvent(self, e):
        QtWidgets.QPushButton.paintEvent(self, e)
        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing)
        if self.is_hover:
            painter.setOpacity(0.8)
        elif self.is_pressed:
            painter.setOpacity(0.7)

        rect = QtCore.QRectF(self.width() - 22,
                             self.height() / 2 - 5 + self.arrow_ani.y, 10, 10)
        if is_dark_theme():
            ChromaIcon.ARROW_DOWN.render(painter, rect)
        else:
            ChromaIcon.ARROW_DOWN.render(painter, rect, fill="#646464")


class EditableComboBox(LineEdit, ComboBoxBase):
    """ Editable combo box """

    current_index_changed = QtCore.Signal(int)
    current_text_changed = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(EditableComboBox, self).__init__(parent=parent)
        self._set_up_ui()

        self.drop_button = LineEditButton(ChromaIcon.ARROW_DOWN, self)

        self.setTextMargins(0, 0, 29, 0)
        self.drop_button.setFixedSize(30, 25)
        self.h_layout.addWidget(self.drop_button, 0, QtCore.Qt.AlignRight)

        self.drop_button.clicked.connect(self._toggle_combo_menu)
        self.textEdited.connect(self._on_text_edited)
        self.returnPressed.connect(self._on_return_pressed)

        ChromaStyleSheet.LINE_EDIT.apply(self)

    def current_text(self):
        return self.text()

    def clear(self):
        ComboBoxBase.clear(self)

    def _on_return_pressed(self):
        if not self.text():
            return

        index = self.find_text(self.text())
        if index >= 0 and index != self.current_index():
            self._currentIndex = index
            self.current_index_changed.emit(index)
        elif index == -1:
            self.add_item(self.text())
            self.set_current_index(self.count() - 1)

    def eventFilter(self, obj, e):
        if obj is self:
            if e.type() == QtCore.QEvent.MouseButtonPress:
                self.is_pressed = True
            elif e.type() == QtCore.QEvent.MouseButtonRelease:
                self.is_pressed = False
            elif e.type() == QtCore.QEvent.Enter:
                self.is_hover = True
            elif e.type() == QtCore.QEvent.Leave:
                self.is_hover = False

        return super(EditableComboBox, self).eventFilter(obj, e)

    def _on_text_edited(self, text):
        self._currentIndex = -1
        self.current_text_changed.emit(text)

        for i, item in enumerate(self.items):
            if item.text == text:
                self._currentIndex = i
                self.current_index_changed.emit(i)
                return

    def _on_drop_menu_closed(self):
        self.dropMenu = None

