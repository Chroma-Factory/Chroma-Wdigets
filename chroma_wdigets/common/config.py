from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import json
import codecs
from tempfile import gettempdir
from enum import Enum

from Qt.QtCore import QObject, Signal
from Qt.QtGui import QColor

PRIMARY_COLOR = "#8A379B"
DARK_BACKGROUND_COLOR = "#242732"

RESOURCES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "resources"
).replace('\\', '/')


class Theme(Enum):
    LIGHT = "Light"
    DARK = "Dark"


class ConfigValidator(object):
    def validate(self, value):
        return True

    def correct(self, value):
        return value


class ColorValidator(ConfigValidator):
    """ RGB color validator """

    def __init__(self, default):
        self.default = QColor(default)

    def validate(self, color):
        try:
            return QColor(color).isValid()
        except:
            return False

    def correct(self, value):
        return QColor(value) if self.validate(value) else self.default


class OptionsValidator(ConfigValidator):
    """ Options validator """

    def __init__(self, options):
        if not options:
            raise ValueError("The `options` can't be empty.")

        if isinstance(options, Enum):
            options = options._member_map_.values()

        self.options = list(options)

    def validate(self, value):
        return value in self.options

    def correct(self, value):
        return value if self.validate(value) else self.options[0]


class ConfigSerializer(object):
    def serialize(self, value):
        return value

    def deserialize(self, value):
        return value


class ColorSerializer(ConfigSerializer):
    """ QColor serializer """

    def serialize(self, value):
        return value.name(QColor.HexArgb)

    def deserialize(self, value):
        if isinstance(value, list):
            return QColor(*value)

        return QColor(value)


class EnumSerializer(ConfigSerializer):
    def __init__(self, enum_class):
        self.enumClass = enum_class

    def serialize(self, value):
        return value.value

    def deserialize(self, value):
        return self.enumClass(value)


class ConfigItem(QObject):
    """ Config item """

    value_changed = Signal(object)

    def __init__(self, group, name, default, validator=None, serializer=None,
                 restart=False):
        super(ConfigItem, self).__init__()
        self.group = group
        self.name = name
        self.validator = validator or ConfigValidator()
        self.serializer = serializer or ConfigSerializer()
        self._value = default
        self.value = default
        self.restart = restart
        self.defaultValue = self.validator.correct(default)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        v = self.validator.correct(v)
        ov = self._value
        self._value = v
        if ov != v:
            self.value_changed.emit(v)

    @property
    def key(self):
        return self.group + "." + self.name if self.name else self.group

    def __str__(self):
        return f'{self.__class__.__name__}[value={self.value}]'

    def serialize(self):
        return self.serializer.serialize(self.value)

    def deserialize_from(self, value):
        self.value = self.serializer.deserialize(value)


class OptionsConfigItem(ConfigItem):
    @property
    def options(self):
        return self.validator.options

    def __str__(self):
        return '{}[options={}, value={}]'.format(
            self.__class__.__name__, self.options, self.value)


class ColorConfigItem(ConfigItem):
    def __init__(self, group, name, default, restart=False):
        super(ColorConfigItem, self).__init__(
            group, name, QColor(default), ColorValidator(default),
            ColorSerializer(), restart
        )

    def __str__(self):
        return '{}[value={}]'.format(self.__class__.__name__, self.value.name())


class QConfig(QObject):
    app_restarted = Signal()
    theme_changed = Signal(Theme)
    theme_color_changed = Signal(QColor)

    theme_mode = OptionsConfigItem(
        "ChromaWidgets", "ThemeMode", Theme.DARK, OptionsValidator(Theme),
        EnumSerializer(Theme))
    theme_color = ColorConfigItem("ChromaWidgets", "ThemeColor", PRIMARY_COLOR)

    def __init__(self):
        super(QConfig, self).__init__()
        self.file = os.path.join(gettempdir(), "chroma_widgets/config.json")
        self._theme = Theme.DARK

    def get(self, item):
        return item.value

    def set(self, item, value, save=True):
        if item.value == value:
            return

        item.value = value

        if save:
            self.save()

        if item.restart:
            self.app_restarted.emit()

        if item is self.theme_mode:
            self.theme = value
            self.theme_changed.emit(value)

        if item is self.theme_color:
            self.theme_color_changed.emit(value)

    def to_dict(self, serialize=True):
        """ convert config items to `dict` """
        items = {}
        for name in dir(self.__class__):
            item = getattr(self.__class__, name)
            if not isinstance(item, ConfigItem):
                continue

            value = item.serialize() if serialize else item.value
            if not items.get(item.group):
                if not item.name:
                    items[item.group] = value
                else:
                    items[item.group] = {}

            if item.name:
                items[item.group][item.name] = value

        return items

    def save(self):
        if not os.path.exists(os.path.dirname(self.file)):
            os.makedirs(os.path.dirname(self.file))

        with codecs.open(self.file, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)

    @property
    def theme(self):
        return self._theme

    @theme.setter
    def theme(self, t):
        self._theme = t


qconfig = QConfig()


def is_dark_theme():
    return qconfig.theme == Theme.DARK


def theme():
    return qconfig.theme
