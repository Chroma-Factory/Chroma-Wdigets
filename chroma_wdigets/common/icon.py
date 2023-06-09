from enum import Enum

from Qt.QtWidgets import QAction
from Qt.QtGui import QIcon, QIconEngine
from Qt.QtCore import QFile, QRectF, Qt
from Qt.QtXml import QDomDocument
from Qt.QtSvg import QSvgRenderer

from chroma_wdigets.common.config import Theme, RESOURCES_PATH


def write_svg(icon_path, indexes=None, **attributes):
    if not icon_path.lower().endswith(".svg"):
        return ""

    f = QFile(icon_path)
    f.open(QFile.ReadOnly)

    dom = QDomDocument()
    dom.setContent(f.readAll())

    f.close()

    # change the color of each path
    path_nodes = dom.elementsByTagName('path')
    indexes = range(path_nodes.length()) if not indexes else indexes
    for i in indexes:
        element = path_nodes.at(i).toElement()

        for k, v in attributes.items():
            element.setAttribute(k, v)

    return dom.toString()


def draw_svg_icon(icon, painter, rect):
    renderer = QSvgRenderer(icon)
    renderer.render(painter, QRectF(rect))


class ChromaIconBase(object):
    """ Fluent icon base class """

    def path(self, theme=Theme.DARK):
        raise NotImplementedError

    def icon(self, theme=Theme.DARK):
        return QIcon(self.path(theme))

    def render(self, painter, rect, theme=Theme.DARK, indexes=None,
               **attributes):
        if attributes:
            svg = write_svg(self.path(theme), indexes, **attributes).encode()
        else:
            svg = self.path(theme)

        draw_svg_icon(svg, painter, rect)


def to_icon(icon):
    if isinstance(icon, str):
        return QIcon(icon)

    if isinstance(icon, ChromaIconBase):
        return icon.icon()

    return icon


def draw_icon(icon, painter, rect, **attributes):
    if isinstance(icon, ChromaIconBase):
        icon.render(painter, rect, **attributes)
    else:
        icon = QIcon(icon)
        rect = QRectF(rect).toRect()
        image = icon.pixmap(rect.width(), rect.height())
        painter.drawPixmap(rect, image)


def get_icon_color(theme=Theme.DARK, reverse=False):
    if not reverse:
        lc, dc = "black", "white"
    else:
        lc, dc = "white", "black"

    color = dc if theme == Theme.DARK else lc
    return color


class ChromaIcon(ChromaIconBase, Enum):
    ADD = "Add"
    CUT = "Cut"
    PIN = "Pin"
    TAG = "Tag"
    CHAT = "Chat"
    COPY = "Copy"
    CODE = "Code"
    EDIT = "Edit"
    FONT = "Font"
    HELP = "Help"
    HIDE = "Hide"
    HOME = "Home"
    INFO = "Info"
    LINK = "Link"
    MAIL = "Mail"
    MENU = "Menu"
    MORE = "More"
    SAVE = "Save"
    SEND = "Send"
    SYNC = "Sync"
    VIEW = "View"
    ZOOM = "Zoom"
    ALBUM = "Album"
    BRUSH = "Brush"
    CLOSE = "Close"
    EMBED = "Embed"
    GLOBE = "Globe"
    HEART = "Heart"
    MEDIA = "Media"
    MOVIE = "Movie"
    MUSIC = "Music"
    PASTE = "Paste"
    PHOTO = "Photo"
    PHONE = "Phone"
    PRINT = "Print"
    SHARE = "Share"
    UNPIN = "Unpin"
    VIDEO = "Video"
    ACCEPT = "Accept"
    CAMERA = "Camera"
    CANCEL = "Cancel"
    DELETE = "Delete"
    FOLDER = "Folder"
    SCROLL = "Scroll"
    LAYOUT = "Layout"
    GITHUB = "GitHub"
    UPDATE = "Update"
    RETURN = "Return"
    RINGER = "Ringer"
    SEARCH = "Search"
    SAVE_AS = "SaveAs"
    ZOOM_IN = "ZoomIn"
    HISTORY = "History"
    SETTING = "Setting"
    PALETTE = "Palette"
    MESSAGE = "Message"
    ZOOM_OUT = "ZoomOut"
    CALENDAR = "Calendar"
    FEEDBACK = "Feedback"
    MINIMIZE = "Minimize"
    CHECKBOX = "CheckBox"
    DOCUMENT = "Document"
    LANGUAGE = "Language"
    DOWNLOAD = "Download"
    QUESTION = "Question"
    DATE_TIME = "DateTime"
    SEND_FILL = "SendFill"
    COMPLETED = "Completed"
    CONSTRACT = "Constract"
    ALIGNMENT = "Alignment"
    BOOK_SHELF = "BookShelf"
    HIGHTLIGHT = "Highlight"
    FOLDER_ADD = "FolderAdd"
    PENCIL_INK = "PencilInk"
    ZIP_FOLDER = "ZipFolder"
    BASKETBALL = "Basketball"
    MICROPHONE = "Microphone"
    ARROW_DOWN = "ChevronDown"
    TRANSPARENT = "Transparent"
    MUSIC_FOLDER = "MusicFolder"
    CARE_UP_SOLID = "CareUpSolid"
    CHEVRON_RIGHT = "ChevronRight"
    CARE_DOWN_SOLID = "CareDownSolid"
    CARE_LEFT_SOLID = "CareLeftSolid"
    BACKGROUND_FILL = "BackgroundColor"
    CARE_RIGHT_SOLID = "CareRightSolid"
    EMOJI_TAB_SYMBOLS = "EmojiTabSymbols"

    def path(self, theme=Theme.DARK):
        return '{}/images/icons/{}_{}.svg'.format(
            RESOURCES_PATH, self.value, get_icon_color(theme)
        )


class Icon(QIcon):
    def __init__(self, icon):
        super().__init__(icon.path())
        self.chroma_icon = icon


class MenuIconEngine(QIconEngine):

    def __init__(self, icon):
        super().__init__()
        self.icon = icon

    def paint(self, painter, rect, mode, state):
        painter.save()

        if mode == QIcon.Disabled:
            painter.setOpacity(0.5)
        elif mode == QIcon.Selected:
            painter.setOpacity(0.7)

        # change icon color according to the theme
        icon = self.icon
        if isinstance(self.icon, Icon):
            icon = self.icon.chroma_icon.icon()

        # prevent the left side of the icon from being cropped
        rect.adjust(-1, 0, 0, 0)

        icon.paint(painter, rect, Qt.AlignHCenter, QIcon.Normal, state)
        painter.restore()


class Action(QAction):
    def __init__(self, icon=None, text='', parent=None, **kwargs):
        if isinstance(icon, ChromaIconBase):
            _icon = icon.icon()
        else:
            _icon = icon
        super(Action, self).__init__(
            text=text, icon=_icon, parent=parent, **kwargs)
        self.chroma_icon = icon

    def icon(self):
        if self.chroma_icon:
            return Icon(self.chroma_icon)

        return super(Action, self).icon()

    def setIcon(self, icon):
        if isinstance(icon, ChromaIconBase):
            self.chroma_icon = icon
            icon = icon.icon()

        super(Action, self).setIcon(icon)
