from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from enum import Enum

from Qt import QtWidgets
from Qt import QtGui
from Qt import QtCore

from chroma_wdigets.common.config import is_dark_theme
from chroma_wdigets.common.smooth_scroll import SmoothScroll
from chroma_wdigets.common.icon import (
    ChromaIcon, ChromaIconBase, MenuIconEngine)
from chroma_wdigets.common.theme import ChromaStyleSheet


class MenuAnimationType(Enum):
    """ Menu animation type """

    NONE = 0
    DROP_DOWN = 1
    PULL_UP = 2


class MenuAnimationManager(QtCore.QObject):
    """ Menu animation manager """

    managers = {}

    def __init__(self, menu):
        super(MenuAnimationManager, self).__init__()
        self.menu = menu
        self.ani = QtCore.QPropertyAnimation(menu, b'pos', menu)

        self.ani.setDuration(250)
        self.ani.setEasingCurve(QtCore.QEasingCurve.OutQuad)
        self.ani.valueChanged.connect(self._on_value_changed)
        self.ani.valueChanged.connect(self._update_menu_viewport)

    def _on_value_changed(self):
        pass

    def _update_menu_viewport(self):
        self.menu.view.viewport().update()
        self.menu.view.setAttribute(QtCore.Qt.WA_UnderMouse, True)
        e = QtGui.QHoverEvent(QtCore.QEvent.HoverEnter, QtCore.QPoint(),
                              QtCore.QPoint(1, 1))
        QtWidgets.QApplication.sendEvent(self.menu.view, e)

    def _end_position(self, pos):
        m = self.menu
        rect = QtWidgets.QApplication.screenAt(
            QtGui.QCursor.pos()).availableGeometry()
        w, h = m.width() + 5, m.height() + 5
        x = min(pos.x() - m.layout().contentsMargins().left(), rect.right() - w)
        y = min(pos.y() - 4, rect.bottom() - h)
        return QtCore.QPoint(x, y)

    def _menu_size(self):
        m = self.menu.layout().contentsMargins()
        w = self.menu.view.width() + m.left() + m.right() + 120
        h = self.menu.view.height() + m.top() + m.bottom() + 20
        return w, h

    def exec(self, pos):
        self._init_ani(pos)

    @classmethod
    def register(cls, name):
        """ register menu animation manager"""

        def wrapper(Manager):
            if name not in cls.managers:
                cls.managers[name] = Manager
            return Manager

        return wrapper

    @classmethod
    def make(cls, menu, ani_type):
        if ani_type not in cls.managers:
            raise ValueError(f'`{ani_type}` is an invalid menu animation type.')

        return cls.managers[ani_type](menu)


@MenuAnimationManager.register(MenuAnimationType.NONE)
class DummyMenuAnimationManager(MenuAnimationManager):
    """ Dummy menu animation manager """

    def exec(self, pos):
        self.menu.move(self._end_position(pos))


@MenuAnimationManager.register(MenuAnimationType.DROP_DOWN)
class DropDownMenuAnimationManager(MenuAnimationManager):
    """ Drop down menu animation manager """

    def exec(self, pos):
        pos = self._end_position(pos)
        h = self.menu.height() + 5

        self.ani.setStartValue(pos - QtCore.QPoint(0, int(h / 2)))
        self.ani.setEndValue(pos)
        self.ani.start()

    def _on_value_changed(self):
        w, h = self._menu_size()
        y = self.ani.endValue().y() - self.ani.currentValue().y()
        self.menu.setMask(QtGui.QRegion(0, y, w, h))


@MenuAnimationManager.register(MenuAnimationType.PULL_UP)
class PullUpMenuAnimationManager(MenuAnimationManager):
    """ Pull up menu animation manager """

    def _end_position(self, pos):
        m = self.menu
        rect = QtWidgets.QApplication.screenAt(
            QtGui.QCursor.pos()).availableGeometry()
        w, h = m.width() + 5, m.height()
        x = min(pos.x() - m.layout().contentsMargins().left(), rect.right() - w)
        y = max(pos.y() - h + 15, 4)
        return QtCore.QPoint(x, y)

    def exec(self, pos):
        pos = self._end_position(pos)
        h = self.menu.height() + 5

        self.ani.setStartValue(pos + QtCore.QPoint(0, int(h / 2)))
        self.ani.setEndValue(pos)
        self.ani.start()

    def _on_value_changed(self):
        w, h = self._menu_size()
        y = self.ani.endValue().y() - self.ani.currentValue().y()
        self.menu.setMask(QtGui.QRegion(0, y, w, h))


class MenuItemDelegate(QtWidgets.QStyledItemDelegate):
    """ Menu item delegate """

    def paint(self, painter, option, index):
        if index.model().data(index, QtCore.Qt.DecorationRole) != "seperator":
            return super().paint(painter, option, index)

        painter.save()

        c = 0 if not is_dark_theme() else 255
        pen = QtGui.QPen(QtGui.QColor(c, c, c, 25), 1)
        pen.setCosmetic(True)
        painter.setPen(pen)
        rect = option.rect
        painter.drawLine(0, rect.y() + 4, rect.width() + 12, rect.y() + 4)

        painter.restore()


class MenuActionListWidget(QtWidgets.QListWidget):
    """ Menu action list widget """

    def __init__(self, parent=None):
        super(MenuActionListWidget, self).__init__(parent)
        self.setViewportMargins(0, 6, 0, 6)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setTextElideMode(QtCore.Qt.ElideNone)
        self.setDragEnabled(False)
        self.setMouseTracking(True)
        self.setVerticalScrollMode(self.ScrollPerPixel)
        self.setIconSize(QtCore.QSize(14, 14))
        self.setItemDelegate(MenuItemDelegate(self))

        self.smooth_scroll = SmoothScroll(self)
        self.setStyleSheet(
            'MenuActionListWidget{font: 14px "Segoe UI", "Microsoft YaHei"}')

    def wheelEvent(self, e):
        self.smooth_scroll.wheelEvent(e)
        e.setAccepted(True)

    def insert_item(self, row, item):
        """ inserts menu item at the position in the list given by row """
        super(MenuActionListWidget, self).insertItem(row, item)
        self.adjust_size()

    def add_item(self, item):
        """ add menu item at the end """
        super(MenuActionListWidget, self).addItem(item)
        self.adjust_size()

    def take_item(self, row):
        """ delete item from list """
        item = super(MenuActionListWidget, self).takeItem(row)
        self.adjust_size()
        return item

    def adjust_size(self):
        size = QtCore.QSize()
        for i in range(self.count()):
            s = self.item(i).sizeHint()
            size.setWidth(max(s.width(), size.width()))
            size.setHeight(size.height() + s.height())

        # adjust the height of viewport
        ss = QtWidgets.QApplication.screenAt(
            QtGui.QCursor.pos()).availableSize()
        w, h = ss.width() - 100, ss.height() - 100
        v_size = QtCore.QSize(size)
        v_size.setHeight(min(h - 12, v_size.height()))
        v_size.setWidth(min(w - 12, v_size.width()))
        self.viewport().adjustSize()

        # adjust the height of list widget
        m = self.viewportMargins()
        size += QtCore.QSize(m.left() + m.right() + 2, m.top() + m.bottom())
        size.setHeight(min(h, size.height() + 3))
        size.setWidth(min(w, size.width()))
        self.setFixedSize(size)

    def set_item_height(self, height):
        """ set the height of item """
        for i in range(self.count()):
            item = self.item(i)
            item.setSizeHint(item.sizeHint().width(), height)

        self.adjust_size()


class SubMenuItemWidget(QtWidgets.QWidget):
    """ Sub menu item """

    show_menu_signal = QtCore.Signal(QtWidgets.QListWidgetItem)

    def __init__(self, menu, item, parent=None):
        super().__init__(parent)
        self.menu = menu
        self.item = item

    def enterEvent(self, e):
        super().enterEvent(e)
        self.show_menu_signal.emit(self.item)

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing)

        ChromaIcon.CHEVRON_RIGHT.render(painter, QtCore.QRectF(
            self.width() - 10, self.height() / 2 - 9 / 2, 9, 9))


class RoundMenu(QtWidgets.QWidget):
    """ Round corner menu """

    closed_signal = QtCore.Signal()

    def __init__(self, title="", parent=None):
        super(RoundMenu, self).__init__(parent=parent)
        self._title = title
        self._icon = QtGui.QIcon()
        self._actions = []
        self._sub_menus = []

        self.is_sub_menu = False
        self.parent_menu = None
        self.menu_item = None
        self.last_hover_item = None
        self.last_hover_sub_menu_item = None
        self.is_hide_by_system = True
        self.item_height = 28

        self.h_layout = QtWidgets.QHBoxLayout(self)
        self.view = MenuActionListWidget(self)

        self.ani_manager = None
        self.ani = QtCore.QPropertyAnimation(self, b'pos', self)
        self.timer = QtCore.QTimer(self)

        self._init_widgets()

    def _init_widgets(self):
        self.setWindowFlags(QtCore.Qt.Popup | QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.NoDropShadowWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        self.timer.setSingleShot(True)
        self.timer.setInterval(400)
        self.timer.timeout.connect(self._on_show_menu_time_out)

        self.set_shadow_effect()
        self.h_layout.addWidget(self.view, 1, QtCore.Qt.AlignCenter)

        self.h_layout.setContentsMargins(12, 8, 12, 20)
        ChromaStyleSheet.MENU.apply(self)

        self.view.itemClicked.connect(self._on_item_clicked)
        self.view.itemEntered.connect(self._on_item_entered)

    def set_item_height(self, height):
        """ set the height of menu item """
        if height == self.item_height:
            return

        self.item_height = height
        self.view.set_item_height(height)

    def set_shadow_effect(self, blur_radius=30, offset=(0, 8),
                          color=QtGui.QColor(0, 0, 0, 30)):
        """ add shadow to dialog """
        self.shadow_effect = QtWidgets.QGraphicsDropShadowEffect(self.view)
        self.shadow_effect.setBlurRadius(blur_radius)
        self.shadow_effect.setOffset(*offset)
        self.shadow_effect.setColor(color)
        self.view.setGraphicsEffect(None)
        self.view.setGraphicsEffect(self.shadow_effect)

    def set_parent_menu(self, parent, item):
        self.parent_menu = parent
        self.menu_item = item
        self.is_sub_menu = True if parent else False

    def adjust_size(self):
        m = self.layout().contentsMargins()
        w = self.view.width() + m.left() + m.right()
        h = self.view.height() + m.top() + m.bottom()
        self.setFixedSize(w, h)

    def icon(self):
        return self._icon

    def title(self):
        return self._title

    def clear(self):
        """ clear all actions """
        for i in range(len(self._actions) - 1, -1, -1):
            self.remove_action(self._actions[i])

    def set_icon(self, icon):
        """ set the icon of menu """
        if not isinstance(icon, ChromaIconBase):
            icon = QtGui.QIcon(icon)
        else:
            icon = icon.icon()

        self._icon = icon

    def add_action(self, action):
        item = self._create_action_item(action)
        self.view.add_item(item)
        self.adjust_size()

    def _create_action_item(self, action, before=None):
        """ create menu action item  """
        if not before:
            self._actions.append(action)
        elif before in self._actions:
            index = self._actions.index(before)
            self._actions.insert(index, action)
        else:
            raise ValueError('`before` is not in the action list')

        item = QtWidgets.QListWidgetItem(self._create_item_icon(action),
                                         action.text())
        if not self._has_item_icon():
            w = 40 + self.view.fontMetrics().width(action.text())
        else:
            # add a blank character to increase space between icon and text
            item.setText(" " + item.text())
            w = 60 + self.view.fontMetrics().width(item.text())

        item.setSizeHint(QtCore.QSize(w, self.item_height))
        item.setData(QtCore.Qt.UserRole, action)
        action.setProperty('item', item)
        action.changed.connect(self._on_action_changed)
        return item

    def _has_item_icon(self):
        return any(
            not i.icon().isNull() for i in self._actions + self._sub_menus)

    def _create_item_icon(self, w):
        """ create the icon of menu item """
        has_icon = self._has_item_icon()
        icon = QtGui.QIcon(MenuIconEngine(w.icon()))

        if has_icon and w.icon().isNull():
            pixmap = QtGui.QPixmap(self.view.iconSize())
            pixmap.fill(QtCore.Qt.transparent)
            icon = QtGui.QIcon(pixmap)
        elif not has_icon:
            icon = QtGui.QIcon()

        return icon

    def insert_action(self, before, action):
        """ inserts action to menu, before the action before """
        if before not in self._actions:
            return

        before_item = before.property('item')
        if not before_item:
            return

        index = self.view.row(before_item)
        item = self._create_action_item(action, before)
        self.view.insert_item(index, item)
        self.adjust_size()

    def add_actions(self, actions):
        """ add actions to menu

        Parameters
        ----------
        actions: Iterable[QAction]
            menu actions
        """
        for action in actions:
            self.add_action(action)

    def insert_actions(self, before, actions):
        """ inserts the actions actions to menu, before the action before """
        for action in actions:
            self.insert_action(before, action)

    def remove_action(self, action):
        """ remove action from menu """
        if action not in self._actions:
            return

        index = self._actions.index(action)
        self._actions.remove(action)
        action.setProperty('item', None)
        item = self.view.take_item(index)
        item.setData(QtCore.Qt.UserRole, None)

        # delete widget
        widget = self.view.itemWidget(item)
        if widget:
            widget.deleteLater()

    def set_default_action(self, action):
        """ set the default action """
        if action not in self._actions:
            return

        index = self._actions.index(action)
        self.view.setCurrentRow(index)

    def add_menu(self, menu):
        if not isinstance(menu, RoundMenu):
            raise ValueError('`menu` should be an instance of `RoundMenu`.')

        item, w = self._create_sub_menu_item(menu)
        self.view.add_item(item)
        self.view.setItemWidget(item, w)
        self.adjust_size()

    def insert_menu(self, before, menu):
        """ insert menu before action `before` """
        if not isinstance(menu, RoundMenu):
            raise ValueError('`menu` should be an instance of `RoundMenu`.')

        if before not in self._actions:
            raise ValueError('`before` should be in menu action list')

        item, w = self._create_sub_menu_item(menu)
        self.view.insert_item(self.view.row(before.property('item')), item)
        self.view.setItemWidget(item, w)
        self.adjust_size()

    def _create_sub_menu_item(self, menu):
        self._sub_menus.append(menu)

        item = QtWidgets.QListWidgetItem(
            self._create_item_icon(menu), menu.title())
        if not self._has_item_icon():
            w = 60 + self.view.fontMetrics().width(menu.title())
        else:
            # add a blank character to increase space between icon and text
            item.setText(" " + item.text())
            w = 72 + self.view.fontMetrics().width(item.text())

        # add submenu item
        menu.set_parent_menu(self, item)
        item.setSizeHint(QtCore.QSize(w, self.item_height))
        item.setData(QtCore.Qt.UserRole, menu)
        w = SubMenuItemWidget(menu, item, self)
        w.show_menu_signal.connect(self._show_sub_menu)
        w.resize(item.sizeHint())

        return item, w

    def _show_sub_menu(self, item):
        """ show sub menu """
        self.last_hover_item = item
        self.last_hover_sub_menu_item = item
        # delay 400 ms to anti-shake
        self.timer.stop()
        self.timer.start()

    def _on_show_menu_time_out(self):
        if (self.last_hover_sub_menu_item is None or
                self.last_hover_item is not self.last_hover_sub_menu_item):
            return

        w = self.view.itemWidget(self.last_hover_sub_menu_item)

        if w.menu.parent_menu.isHidden():
            return

        pos = w.mapToGlobal(QtCore.QPoint(w.width() + 5, -5))
        w.menu.exec(pos)

    def add_separator(self):
        """ add seperator to menu """
        m = self.view.viewportMargins()
        w = self.view.width() - m.left() - m.right()

        # add separator to list widget
        item = QtWidgets.QListWidgetItem(self.view)
        item.setFlags(QtCore.Qt.NoItemFlags)
        item.setSizeHint(QtCore.QSize(w, 9))
        self.view.add_item(item)
        item.setData(QtCore.Qt.DecorationRole, "seperator")
        self.adjust_size()

    def _on_item_clicked(self, item):
        action = item.data(QtCore.Qt.UserRole)
        if action not in self._actions or not action.isEnabled():
            return

        self._hide_menu(False)

        if not self.is_sub_menu:
            action.trigger()
            return

        # close parent menu
        self._close_parent_menu()
        action.trigger()

    def _close_parent_menu(self):
        menu = self
        while menu:
            menu.close()
            menu = menu.parent_menu

    def _on_item_entered(self, item):
        self.last_hover_item = item
        if not isinstance(item.data(QtCore.Qt.UserRole), RoundMenu):
            return

        self._show_sub_menu(item)

    def _hide_menu(self, is_hide_by_system=False):
        self.is_hide_by_system = is_hide_by_system
        self.view.clearSelection()
        if self.is_sub_menu:
            self.hide()
        else:
            self.close()

    def hideEvent(self, e):
        if self.is_hide_by_system and self.is_sub_menu:
            self._close_parent_menu()

        self.is_hide_by_system = True
        e.accept()

    def closeEvent(self, e):
        e.accept()
        self.closed_signal.emit()
        self.view.clearSelection()

    def menu_actions(self):
        return self._actions

    def mousePressEvent(self, e):
        if self.childAt(e.pos()) is not self.view:
            self._hide_menu(True)

    def mouseMoveEvent(self, e):
        if not self.is_sub_menu:
            return

        # hide submenu when mouse moves out of submenu item
        pos = e.globalPos()
        view = self.parent_menu.view

        # get the rect of menu item
        margin = view.viewportMargins()
        rect = view.visualItemRect(self.menu_item).translated(
            view.mapToGlobal(QtCore.QPoint()))
        rect = rect.translated(margin.left(), margin.top() + 2)
        if (self.parent_menu.geometry().contains(pos) and
                not rect.contains(pos) and
                not self.geometry().contains(pos)):
            view.clearSelection()
            self._hide_menu(False)

    def _on_action_changed(self):
        """ action changed slot """
        action = self.sender()
        item = action.property('item')
        item.setIcon(self._create_item_icon(action))

        if not self._has_item_icon():
            item.setText(action.text())
            w = 28 + self.view.fontMetrics().width(action.text())
        else:
            # add a blank character to increase space between icon and text
            item.setText(" " + action.text())
            w = 60 + self.view.fontMetrics().width(item.text())

        item.setSizeHint(QtCore.QSize(w, self.item_height))

        if action.isEnabled():
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        else:
            item.setFlags(QtCore.Qt.NoItemFlags)

        self.view.adjust_size()
        self.adjust_size()

    def exec(self, pos, ani=True, ani_type=MenuAnimationType.DROP_DOWN):
        """ show menu"""
        if self.isVisible():
            return

        self.ani_manager = MenuAnimationManager.make(self, ani_type)
        self.ani_manager.exec(pos)

        self.show()

        if self.is_sub_menu:
            self.menu_item.setSelected(True)

    def exec_(self, pos, ani=True, ani_type=MenuAnimationType.DROP_DOWN):
        """ show menu"""
        self.exec(pos, ani, ani_type)


class EditMenu(RoundMenu):
    """ Edit menu """

    def __init__(self, title="", parent=None):
        super(EditMenu, self).__init__(title=title, parent=parent)
        self.create_actions()

    def create_actions(self):
        self.cut_act = QtWidgets.QAction(
            ChromaIcon.CUT.icon(),
            "Cut",
            self,
            shortcut="Ctrl+X",
            triggered=self.parent().cut,
        )
        self.copy_act = QtWidgets.QAction(
            ChromaIcon.COPY.icon(),
            "Copy",
            self,
            shortcut="Ctrl+C",
            triggered=self.parent().copy,
        )
        self.paste_act = QtWidgets.QAction(
            ChromaIcon.PASTE.icon(),
            "Paste",
            self,
            shortcut="Ctrl+V",
            triggered=self.parent().paste,
        )
        self.cancel_act = QtWidgets.QAction(
            ChromaIcon.CANCEL.icon(),
            "Cancel",
            self,
            shortcut="Ctrl+Z",
            triggered=self.parent().undo,
        )
        self.select_all_act = QtWidgets.QAction(
            "Select all",
            self,
            shortcut="Ctrl+A",
            triggered=self.parent().selectAll
        )
        self.action_list = [
            self.cut_act, self.copy_act,
            self.paste_act, self.cancel_act, self.select_all_act
        ]

    def _parent_text(self):
        raise NotImplementedError

    def _parent_selected_text(self):
        raise NotImplementedError

    def exec(self, pos, ani=True, ani_type=MenuAnimationType.DROP_DOWN):
        self.clear()

        clipboard = QtWidgets.QApplication.clipboard()
        if clipboard.mimeData().hasText():
            if self._parent_text():
                if self._parent_selected_text():
                    if self.parent().isReadOnly():
                        self.add_actions([self.copy_act, self.select_all_act])
                    else:
                        self.add_actions(self.action_list)
                else:
                    if self.parent().isReadOnly():
                        self.add_action(self.select_all_act)
                    else:
                        self.add_actions(self.action_list[2:])
            elif not self.parent().isReadOnly():
                self.add_action(self.paste_act)
            else:
                return
        else:
            if not self._parent_text():
                return

            if self._parent_selected_text():
                if self.parent().isReadOnly():
                    self.add_actions([self.copy_act, self.select_all_act])
                else:
                    self.add_actions(
                        self.action_list[:2] + self.action_list[3:])
            else:
                if self.parent().isReadOnly():
                    self.add_action(self.select_all_act)
                else:
                    self.add_actions(self.action_list[3:])

        super(EditMenu, self).exec(pos, ani, ani_type)


class LineEditMenu(EditMenu):
    """ Line edit menu """

    def __init__(self, parent):
        super(LineEditMenu, self).__init__("", parent)
        self.selectionStart = parent.selectionStart()
        self.selectionLength = parent.selectionLength()

    def _on_item_clicked(self, item):
        if self.selectionStart >= 0:
            self.parent().setSelection(self.selectionStart,
                                       self.selectionLength)

        super(LineEditMenu, self)._on_item_clicked(item)

    def _parent_text(self):
        return self.parent().text()

    def _parent_selected_text(self):
        return self.parent().selectedText()


class TextEditMenu(EditMenu):
    """ Text edit menu """

    def __init__(self, parent):
        super(TextEditMenu, self).__init__("", parent)
        cursor = parent.textCursor()
        self.selection_start = cursor.selection_start()
        self.selectionLength = cursor.selectionEnd() - self.selection_start + 1

    def _parent_text(self):
        return self.parent().toPlainText()

    def _parent_selected_text(self):
        return self.parent().textCursor().selectedText()

    def _on_item_clicked(self, item):
        if self.selection_start >= 0:
            cursor = self.parent().textCursor()
            cursor.setPosition(self.selection_start)
            cursor.movePosition(
                QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor,
                self.selectionLength)

        super(TextEditMenu, self)._on_item_clicked(item)
