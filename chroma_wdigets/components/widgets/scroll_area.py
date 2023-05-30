# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from Qt import QtWidgets
from Qt import QtCore

from chroma_wdigets.common.smooth_scroll import SmoothScroll
from chroma_wdigets.components.widgets.scroll_bar import (
    SmoothScrollBar, SmoothScrollDelegate)


class ScrollArea(QtWidgets.QScrollArea):
    """ Smooth scroll area """

    def __init__(self, parent=None):
        super(ScrollArea, self).__init__(parent)
        self.scroll_delegate = SmoothScrollDelegate(self)


class SingleDirectionScrollArea(QtWidgets.QScrollArea):
    """ Single direction scroll area"""

    def __init__(self, parent=None, orient=QtCore.Qt.Vertical):
        super(SingleDirectionScrollArea, self).__init__(parent)
        self.smooth_scroll = SmoothScroll(self, orient)
        self.v_scroll_bar = SmoothScrollBar(QtCore.Qt.Vertical, self)
        self.h_scroll_bar = SmoothScrollBar(QtCore.Qt.Horizontal, self)

    def setVerticalScrollBarPolicy(self, policy):
        super(SingleDirectionScrollArea, self).setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.v_scroll_bar.set_force_hidden(
            policy == QtCore.Qt.ScrollBarAlwaysOff)

    def setHorizontalScrollBarPolicy(self, policy):
        super(SingleDirectionScrollArea, self).setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.h_scroll_bar.set_force_hidden(
            policy == QtCore.Qt.ScrollBarAlwaysOff)

    def set_smooth_mode(self, mode):
        self.smooth_scroll.set_smooth_mode(mode)

    def wheelEvent(self, e):
        self.smooth_scroll.wheelEvent(e)
        e.setAccepted(True)


class SmoothScrollArea(QtWidgets.QScrollArea):
    """ Smooth scroll area """

    def __init__(self, parent=None):
        super(SmoothScrollArea, self).__init__(parent)
        self.delegate = SmoothScrollDelegate(self, True)

    def set_scroll_animation(self, orient, duration,
                             easing=QtCore.QEasingCurve.OutCubic):
        bar = (self.delegate.h_scroll_bar if
               orient == QtCore.Qt.Horizontal else
               self.delegate.v_scroll_bar)
        bar.set_scroll_animation(duration, easing)
