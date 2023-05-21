from Qt import QtWidgets
from chroma_wdigets.common.qt import application


class TWidget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(TWidget, self).__init__(parent)


if __name__ == '__main__':
    with application():
        t = TWidget()
        t.show()
