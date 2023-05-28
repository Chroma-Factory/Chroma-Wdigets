from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import codecs
import weakref
from string import Template
from enum import Enum

from Qt import QtGui

from chroma_wdigets.common.config import (
    Theme,
    qconfig,
    is_dark_theme,
    RESOURCES_PATH,
    DARK_BACKGROUND_COLOR
)


class StyleSheetManager(object):
    def __init__(self):
        self._widgets = weakref.WeakKeyDictionary()

    def register(self, style_sheet_obj, widget):
        if widget not in self._widgets:
            widget.destroyed.connect(self.deregister)

        self._widgets[widget] = style_sheet_obj

    def deregister(self, widget):
        if widget not in self._widgets:
            return

        self._widgets.pop(widget)

    def items(self):
        return self._widgets.items()


style_sheet_manager = StyleSheetManager()


class QssTemplate(Template):
    delimiter = '--'


class ThemeColor(Enum):
    PRIMARY = "ThemeColorPrimary"
    DARK_1 = "ThemeColorDark1"
    DARK_2 = "ThemeColorDark2"
    DARK_3 = "ThemeColorDark3"
    DARK_BACKGROUND = "DarkBackground"
    LIGHT_1 = "ThemeColorLight1"
    LIGHT_2 = "ThemeColorLight2"
    LIGHT_3 = "ThemeColorLight3"

    def name(self):
        return self.color().name()

    def color(self):
        color = qconfig.get(qconfig.theme_color)
        # transform color into hsv space
        h, s, v, _ = color.getHsvF()

        if is_dark_theme():
            s *= 0.73
            v = 0.73
            if self == self.DARK_1:
                v *= 0.9
            elif self == self.DARK_2:
                s *= 0.977
                v *= 0.82
            elif self == self.DARK_3:
                s *= 0.95
                v *= 0.7
            elif self == self.LIGHT_1:
                s *= 0.92
            elif self == self.LIGHT_2:
                s *= 0.78
            elif self == self.LIGHT_3:
                s *= 0.65
            elif self == self.DARK_BACKGROUND:
                return QtGui.QColor(DARK_BACKGROUND_COLOR)
        else:
            if self == self.DARK_1:
                v *= 0.75
            elif self == self.DARK_2:
                s *= 1.05
                v *= 0.5
            elif self == self.DARK_3:
                s *= 1.1
                v *= 0.4
            elif self == self.LIGHT_1:
                v *= 1.05
            elif self == self.LIGHT_2:
                s *= 0.75
                v *= 1.05
            elif self == self.LIGHT_3:
                s *= 0.65
                v *= 1.05

        return QtGui.QColor.fromHsvF(h, min(s, 1), min(v, 1))


class ThemePath(Enum):
    SRC_ROOT = 'SRC_ROOT'

    def path(self):
        path_by_name = {
            'SRC_ROOT': RESOURCES_PATH
        }
        return path_by_name[self.value]


def apply_theme_color(qss):
    template = QssTemplate(qss)
    color_mappings = {c.value: c.name() for c in
                      ThemeColor._member_map_.values()}
    path_mappings = {p.value: p.path() for p in
                     ThemePath._member_map_.values()}
    return template.safe_substitute({**color_mappings, **path_mappings})


def get_style_sheet(style_sheet_obj, theme=Theme.DARK):
    file_path = style_sheet_obj.path(theme)

    with codecs.open(file_path, encoding='utf-8') as f:
        qss = f.read()

    return apply_theme_color(qss)


def set_style_sheet(widget, style_sheet_obj, theme=Theme.DARK, register=True):
    if register:
        style_sheet_manager.register(style_sheet_obj, widget)

    widget.setStyleSheet(get_style_sheet(style_sheet_obj, theme))


class StyleSheetBase(object):
    def path(self, theme=Theme.DARK):
        raise NotImplementedError

    def apply(self, widget, theme=Theme.DARK):
        set_style_sheet(widget, self, theme)


class ChromaStyleSheet(StyleSheetBase, Enum):
    """ Fluent style sheet """

    MENU = "menu"
    PIVOT = "pivot"
    BUTTON = "button"
    DIALOG = "dialog"
    SLIDER = "slider"
    INFO_BAR = "info_bar"
    SPIN_BOX = "spin_box"
    TOOL_TIP = "tool_tip"
    CHECKBOX = "checkbox"
    COMBO_BOX = "combo_box"
    LINE_EDIT = "line_edit"
    LIST_VIEW = "list_view"
    TREE_VIEW = "tree_view"
    TABLE_VIEW = "table_view"
    TIME_PICKER = "time_picker"
    SETTING_CARD = "setting_card"
    COLOR_DIALOG = "color_dialog"
    SWITCH_BUTTON = "switch_button"
    MESSAGE_DIALOG = "message_dialog"
    STATE_TOOL_TIP = "state_tool_tip"
    FOLDER_LIST_DIALOG = "folder_list_dialog"
    SETTING_CARD_GROUP = "setting_card_group"
    EXPAND_SETTING_CARD = "expand_setting_card"
    NAVIGATION_INTERFACE = "navigation_interface"

    def path(self, theme=Theme.DARK):
        return "{}/qss/{}/{}.qss".format(
            RESOURCES_PATH, theme.value.lower(), self.value)


def update_style_sheet():
    """ update the style sheet of all fluent widgets """
    removes = []
    for widget, file in style_sheet_manager.items():
        try:
            set_style_sheet(widget, file, qconfig.theme)
        except RuntimeError:
            removes.append(widget)

    for widget in removes:
        style_sheet_manager.deregister(widget)


def set_theme(theme: Theme, save=False):
    qconfig.set(qconfig.theme_mode, theme, save)
    update_style_sheet()


def theme_color():
    """ get theme color """
    return ThemeColor.PRIMARY.color()


def set_theme_color(color, save=False):
    color = QtGui.QColor(color)
    qconfig.set(qconfig.themeColor, color, save=save)
    update_style_sheet()
