from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from enum import Enum

from Qt import QtGui
from Qt import QtWidgets
from Qt import QtCore

from chroma_wdigets.common.icon import ChromaIconBase, Theme, get_icon_color
from chroma_wdigets.common.config import RESOURCES_PATH
from chroma_wdigets.common.theme import ChromaStyleSheet


class CheckBoxIcon(ChromaIconBase, Enum):
    ACCEPT = "Accept"
    PARTIAL_ACCEPT = "PartialAccept"

    def path(self, theme=Theme.DARK):
        c = get_icon_color(theme)
        return '{}/images/checkbox/{}_{}.svg'.format(
            RESOURCES_PATH, self.value, c
        )


class CheckBox(QtWidgets.QCheckBox):
    """ Check box """

    def __init__(self, text='', parent=None):
        super(CheckBox, self).__init__(text=text, parent=parent)
        ChromaStyleSheet.CHECKBOX.apply(self)

    def paintEvent(self, e):
        super(CheckBox, self).paintEvent(e)
        painter = QtGui.QPainter(self)

        if not self.isEnabled():
            painter.setOpacity(0.8)

        # get the rect of indicator
        opt = QtWidgets.QStyleOptionButton()
        opt.initFrom(self)
        rect = self.style().subElementRect(
            QtWidgets.QStyle.SE_CheckBoxIndicator, opt, self)

        # draw indicator
        if self.checkState() == QtCore.Qt.Checked:
            CheckBoxIcon.ACCEPT.render(painter, rect)
        elif self.checkState() == QtCore.Qt.PartiallyChecked:
            CheckBoxIcon.PARTIAL_ACCEPT.render(painter, rect)
