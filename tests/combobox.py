from Qt import QtWidgets

from chroma_wdigets import ComboBox, EditableComboBox
from chroma_wdigets.common import application


class Widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        self.setStyleSheet('QDialog{background-color: #242732}')
        self.layout = QtWidgets.QVBoxLayout(self)

        combobox = ComboBox()
        combobox.add_items(['小明', '小张', '小品'])
        combobox.set_current_index(0)

        combobox1 = EditableComboBox()
        combobox1.add_items(['小明', '小张', '小品'])
        combobox1.set_current_index(0)

        self.layout.addWidget(combobox)
        self.layout.addWidget(combobox1)


if __name__ == '__main__':
    with application():
        w = Widget()
        w.show()
