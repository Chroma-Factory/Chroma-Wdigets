from Qt import QtCore
from Qt.QtWidgets import QDialog, QHBoxLayout
from chroma_wdigets import ProgressRing, application


class Widget(QDialog):
    def __init__(self):
        super(Widget, self).__init__()
        self.setStyleSheet('QDialog{background-color: #242732}')

        self.v_box_layout = QHBoxLayout(self)
        self.progress_ring = ProgressRing(self)

        self.progress_ring.setValue(50)
        self.progress_ring.setTextVisible(True)
        self.progress_ring.setFixedSize(80, 80)

        self.v_box_layout.addWidget(self.progress_ring, 0, QtCore.Qt.AlignCenter)
        self.v_box_layout.setContentsMargins(30, 30, 30, 30)
        self.resize(400, 400)


if __name__ == '__main__':
    with application():
        w = Widget()
        w.show()
