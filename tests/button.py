from Qt import QtWidgets

from chroma_wdigets.common.qt import application
from chroma_wdigets.common.icon import ChromaIcon, Action
from chroma_wdigets.components.widgets import (
    PushButton, PrimaryPushButton, HyperlinkButton, RadioButton,
    ToolButton, PrimaryToolButton, DropDownPushButton,
    PrimaryDropDownPushButton, PrimaryDropDownToolButton, SplitPushButton,
    PrimarySplitPushButton, ToggleButton, TransparentToolButton
)
from chroma_wdigets.components.widgets import RoundMenu


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

        btn8 = PrimaryDropDownPushButton('AAA')
        btn8.set_menu(menu)

        btn9 = PrimaryDropDownToolButton(ChromaIcon.BOOK_SHELF)
        btn9.set_menu(menu)

        btn10 = SplitPushButton('Split push button')
        btn11 = PrimarySplitPushButton('P Split push button', ChromaIcon.GITHUB,
                                       parent=self)
        btn10.set_menu(menu)
        btn11.set_menu(menu)

        btn12 = ToggleButton('AAAA')

        btn13 = TransparentToolButton(ChromaIcon.CHEVRON_RIGHT)

        layout.addWidget(btn0)
        layout.addWidget(btn1)
        layout.addWidget(btn2)
        layout.addWidget(btn3)
        layout.addWidget(btn4)
        layout.addWidget(btn5)
        layout.addWidget(btn6)
        layout.addWidget(btn7)
        layout.addWidget(btn8)
        layout.addWidget(btn9)
        layout.addWidget(btn10)
        layout.addWidget(btn11)
        layout.addWidget(btn12)
        layout.addWidget(btn13)



if __name__ == '__main__':
    with application():
        w = W()
        w.show()
