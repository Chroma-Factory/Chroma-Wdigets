# coding:utf-8
import sys
from Qt.QtCore import Qt
from Qt.QtWidgets import QDialog, QTreeWidgetItem, QHBoxLayout, QTreeWidgetItemIterator

from chroma_wdigets import TreeWidget, TreeView,application


class Widget(QDialog):
    """ 树形控件演示 """

    def __init__(self, enable_check=False):
        super(Widget, self).__init__()
        self.setStyleSheet('QDialog{background-color: #242732}')
        self.h_box_layout = QHBoxLayout(self)

        self.tree = TreeWidget(self)
        self.h_box_layout.addWidget(self.tree)

        item1 = QTreeWidgetItem([self.tr('JoJo 1 - Phantom Blood')])
        item1.addChildren([
            QTreeWidgetItem([self.tr('Jonathan Joestar')]),
            QTreeWidgetItem([self.tr('Dio Brando')]),
            QTreeWidgetItem([self.tr('Will A. Zeppeli')]),
        ])
        self.tree.addTopLevelItem(item1)

        item2 = QTreeWidgetItem([self.tr('JoJo 3 - Stardust Crusaders')])
        item21 = QTreeWidgetItem([self.tr('Jotaro Kujo')])
        item21.addChildren([
            QTreeWidgetItem(['空条承太郎']),
            QTreeWidgetItem(['空条蕉太狼']),
            QTreeWidgetItem(['阿强']),
            QTreeWidgetItem(['卖鱼强']),
            QTreeWidgetItem(['那个无敌的男人']),
        ])
        item2.addChild(item21)
        self.tree.addTopLevelItem(item2)
        self.tree.expandAll()
        self.tree.setHeaderHidden(True)

        self.setFixedSize(300, 380)

        if enable_check:
            it = QTreeWidgetItemIterator(self.tree)
            while it.value():
                it.value().setCheckState(0, Qt.Unchecked)
                it += 1



if __name__ == '__main__':
    with application():
        w = Widget(True)
        w.show()
