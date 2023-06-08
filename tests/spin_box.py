# coding:utf-8
from PySide2.QtWidgets import QDialog, QVBoxLayout

from chroma_wdigets import SpinBox, DoubleSpinBox, DateTimeEdit, DateEdit, TimeEdit, application


class Demo(QDialog):

    def __init__(self):
        super().__init__()
        self.v_box_layout = QVBoxLayout(self)

        self.spin_box = SpinBox(self)
        self.time_edit = TimeEdit(self)
        self.date_edit = DateEdit(self)
        self.date_time_edit = DateTimeEdit(self)
        self.double_spin_box = DoubleSpinBox(self)

        self.resize(500, 500)
        self.setStyleSheet('QDialog{background-color: #242732}')

        self.v_box_layout.setContentsMargins(100, 50, 100, 50)
        self.v_box_layout.addWidget(self.spin_box)
        self.v_box_layout.addWidget(self.double_spin_box)
        self.v_box_layout.addWidget(self.time_edit)
        self.v_box_layout.addWidget(self.date_edit)
        self.v_box_layout.addWidget(self.date_time_edit)


if __name__ == '__main__':
    with application():
        w = Demo()
        w.show()
