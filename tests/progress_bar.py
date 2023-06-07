# coding:utf-8

from Qt.QtWidgets import QDialog, QVBoxLayout
from chroma_wdigets import IndeterminateProgressBar, ProgressBar, application


class Widget(QDialog):
    def __init__(self):
        super(Widget, self).__init__()
        self.v_box_layout = QVBoxLayout(self)
        self.progressBar = ProgressBar(self)
        self.setStyleSheet('QDialog{background-color: #242732}')
        self.inProgressBar = IndeterminateProgressBar(self)

        self.progressBar.setValue(50)
        self.v_box_layout.addWidget(self.progressBar)
        self.v_box_layout.addWidget(self.inProgressBar)
        self.v_box_layout.setContentsMargins(30, 30, 30, 30)
        self.resize(400, 400)


if __name__ == '__main__':
    with application():
        w = Widget()
        w.show()
