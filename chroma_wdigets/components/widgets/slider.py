# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from Qt import QtCore
from Qt import QtWidgets

from chroma_wdigets.common.theme import ChromaStyleSheet


class Slider(QtWidgets.QSlider):
    """ A slider can be clicked """

    clicked = QtCore.Signal(int)

    def __init__(self, orientation=None, parent=None):
        super(Slider, self).__init__(orientation=orientation, parent=parent)
        ChromaStyleSheet.SLIDER.apply(self)

    def mousePressEvent(self, e):
        super(Slider, self).mousePressEvent(e)

        if self.orientation() == QtCore.Qt.Horizontal:
            value = int(e.pos().x() / self.width() * self.maximum())
        else:
            value = int((self.height() - e.pos().y()) /
                        self.height() * self.maximum())

        self.setValue(value)
        self.clicked.emit(self.value())


class HorizontalSlider(Slider):
    def __init__(self, parent=None):
        super(HorizontalSlider, self).__init__(QtCore.Qt.Horizontal, parent)


class VerticalSlider(Slider):
    def __init__(self, parent=None):
        super(VerticalSlider, self).__init__(QtCore.Qt.Vertical, parent)
