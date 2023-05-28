from Qt import QtWidgets

from chroma_wdigets.components.widgets import CheckBox
from chroma_wdigets.common import application


class Widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        self.setStyleSheet('QDialog{background-color: #242732}')
        self.layout = QtWidgets.QVBoxLayout(self)

        checkbox = CheckBox('check box')
        checkbox.setTristate(True)
        self.layout.addWidget(checkbox)


if __name__ == '__main__':
    with application():
        w = Widget()
        w.show()

