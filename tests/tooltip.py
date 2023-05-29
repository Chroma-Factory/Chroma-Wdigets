from chroma_wdigets import ToolTipPosition, ToolTipFilter, PushButton
from chroma_wdigets import application

from Qt import QtWidgets


class Widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        self.setStyleSheet('QDialog{background-color: #242732}')
        self.layout = QtWidgets.QVBoxLayout(self)

        btn1 = PushButton('AAA')
        btn1.setToolTip('aaa')
        btn2 = PushButton('BBB')
        btn2.setToolTip('bbb')
        btn3 = PushButton('CCC')
        btn3.setToolTip('ccc')

        btn1.installEventFilter(ToolTipFilter(btn1, 0, ToolTipPosition.TOP))
        btn2.installEventFilter(ToolTipFilter(btn2, 0, ToolTipPosition.BOTTOM))
        btn3.installEventFilter(
            ToolTipFilter(btn3, 500, ToolTipPosition.TOP_LEFT))

        self.layout.addWidget(btn1)
        self.layout.addWidget(btn2)
        self.layout.addWidget(btn3)


if __name__ == '__main__':
    with application():
        w = Widget()
        w.show()
