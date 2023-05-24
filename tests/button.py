from Qt import QtWidgets

from chroma_wdigets.common.qt import application
from chroma_wdigets.common.icon import ChromaIcon,Action
from chroma_wdigets.components.widgets.button import (
    PushButton, PrimaryPushButton, HyperlinkButton, RadioButton,
    ToolButton, PrimaryToolButton, DropDownPushButton
)
from chroma_wdigets.components.widgets.menu import RoundMenu


class W(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(W, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        self.setStyleSheet('QDialog{background-color: #242732}')

        btn0 = PushButton('Standard push button')
        btn1 = PushButton('Standard push button with icon', ChromaIcon.FOLDER)
        btn1.setEnabled(False)
        btn2 = PrimaryPushButton('你好')
        btn3 = HyperlinkButton('https://github.com/', '你好')
        btn4 = RadioButton('测试')
        btn5 = ToolButton(ChromaIcon.ACCEPT)
        btn6 = PrimaryToolButton(ChromaIcon.ACCEPT)

        btn7 = DropDownPushButton('Email')
        menu = RoundMenu(parent=self)
        menu.add_action(Action(ChromaIcon.BASKETBALL, 'Basketball'))
        menu.add_action(Action(ChromaIcon.ALBUM, 'Sing'))
        menu.add_action(Action(ChromaIcon.MUSIC, 'Music'))
        btn7.set_menu(menu)


        layout.addWidget(btn0)
        layout.addWidget(btn1)
        layout.addWidget(btn2)
        layout.addWidget(btn3)
        layout.addWidget(btn4)
        layout.addWidget(btn5)
        layout.addWidget(btn6)
        layout.addWidget(btn7)


if __name__ == '__main__':
    with application():
        w = W()
        w.show()
