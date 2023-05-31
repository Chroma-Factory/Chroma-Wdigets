# -*- coding: utf-8 -*-

from Qt import QtWidgets
from Qt import QtCore

from chroma_wdigets import ListWidget,application


class Widget(QtWidgets.QDialog):

    def __init__(self):
        super(Widget, self).__init__()

        self.h_box_layout = QtWidgets.QHBoxLayout(self)
        self.list_widget = ListWidget(self)

        # self.list_widget.setAlternatingRowColors(True)

        stands = [
            '白金之星', '绿色法皇', "天堂制造", "绯红之王",
            '银色战车', '疯狂钻石', "壮烈成仁", "败者食尘",
            "黑蚊子多", '杀手皇后', "金属制品", "石之自由",
            "砸瓦鲁多", '钢链手指', "臭氧宝宝", "华丽挚爱",
            "隐者之紫", "黄金体验", "虚无之王", "纸月之王",
            "骇人恶兽", "男子领域", "20世纪男孩", "牙 Act 4",
            "铁球破坏者", "性感手枪", 'D4C • 爱之列车', "天生完美",
            "软又湿", "佩斯利公园", "奇迹于你", "行走的心",
            "护霜旅行者", "十一月雨", "调情圣手", "片刻静候"
        ]
        for stand in stands:
            item = QtWidgets.QListWidgetItem(stand)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.list_widget.addItem(item)

        self.setStyleSheet('QDialog{background-color: #242732}')
        self.h_box_layout.setContentsMargins(0, 0, 0, 0)
        self.h_box_layout.addWidget(self.list_widget)
        self.resize(300, 400)


if __name__ == "__main__":
    with application():
        w = Widget()
        w.show()

