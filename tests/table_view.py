from Qt import QtWidgets

from chroma_wdigets import TableWidget, application


class Widget(QtWidgets.QDialog):

    def __init__(self):
        super(Widget, self).__init__()

        self.h_box_layout = QtWidgets.QHBoxLayout(self)
        self.table_view = TableWidget(self)

        self.table_view.setWordWrap(False)
        self.table_view.setRowCount(60)
        self.table_view.setColumnCount(5)
        song_infos = [
            ['かばん', 'aiko', 'かばん', '2004', '5:04'],
            ['爱你', '王心凌', '爱你', '2004', '3:39'],
            ['星のない世界', 'aiko', '星のない世界/横顔', '2007', '5:30'],
            ['横顔', 'aiko', '星のない世界/横顔', '2007', '5:06'],
            ['秘密', 'aiko', '秘密', '2008', '6:27'],
            ['シアワセ', 'aiko', '秘密', '2008', '5:25'],
            ['二人', 'aiko', '二人', '2008', '5:00'],
            ['スパークル', 'RADWIMPS', '君の名は。', '2016', '8:54'],
            ['なんでもないや', 'RADWIMPS', '君の名は。', '2016', '3:16'],
            ['前前前世', 'RADWIMPS', '人間開花', '2016', '4:35'],
            ['恋をしたのは', 'aiko', '恋をしたのは', '2016', '6:02'],
            ['夏バテ', 'aiko', '恋をしたのは', '2016', '4:41'],
            ['もっと', 'aiko', 'もっと', '2016', '4:50'],
            ['問題集', 'aiko', 'もっと', '2016', '4:18'],
            ['半袖', 'aiko', 'もっと', '2016', '5:50'],
            ['ひねくれ', '鎖那', 'Hush a by little girl', '2017', '3:54'],
            ['シュテルン', '鎖那', 'Hush a by little girl', '2017', '3:16'],
            ['愛は勝手', 'aiko', '湿った夏の始まり', '2018', '5:31'],
        ]
        song_infos += song_infos
        for i, songInfo in enumerate(song_infos):
            for j in range(5):
                self.table_view.setItem(
                    i, j, QtWidgets.QTableWidgetItem(songInfo[j]))

        self.table_view.verticalHeader().hide()
        self.table_view.setHorizontalHeaderLabels(
            ['Title', 'Artist', 'Album', 'Year', 'Duration'])
        self.table_view.resizeColumnsToContents()
        # self.table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # self.table_view.setSortingEnabled(True)

        self.setStyleSheet('QDialog{background-color: #242732}')
        self.h_box_layout.setContentsMargins(0, 0, 0, 0)
        self.h_box_layout.addWidget(self.table_view)
        self.resize(635, 700)


if __name__ == "__main__":
    # enable dpi scale
    with application():
        w = Widget()
        w.show()

