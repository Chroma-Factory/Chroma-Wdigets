# -*- coding: utf-8 -*-
from Qt.QtGui import QFont
from Qt.QtWidgets import QWidget


def set_font(widget: QWidget, fontSize=14):
    widget.setFont(get_font(fontSize))


def get_font(fontSize=14):
    font = QFont()
    font.setFamilies(['Segoe UI', 'Microsoft YaHei'])
    font.setPixelSize(fontSize)
    return font
