from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from Qt import QtWidgets

from chroma_wdigets import LineEdit, SearchLineEdit
from chroma_wdigets import application


class Widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        self.setStyleSheet('QDialog{background-color: #242732}')

        slider1 = LineEdit()
        slider2 = SearchLineEdit()

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(slider1)
        layout.addWidget(slider2)


if __name__ == '__main__':
    with application():
        w = Widget()
        w.show()
