from Qt import QtCore


class AnimationBase(QtCore.QObject):
    """ Animation base class """

    def __init__(self, parent):
        super(AnimationBase, self).__init__(parent=parent)
        parent.installEventFilter(self)

    def _on_hover(self, event):
        pass

    def _on_leave(self, event):
        pass

    def _on_press(self, event):
        pass

    def _on_release(self, event):
        pass

    def eventFilter(self, obj, e):
        if obj is self.parent():
            if e.type() == QtCore.QEvent.MouseButtonPress:
                self._on_press(e)
            elif e.type() == QtCore.QEvent.MouseButtonRelease:
                self._on_release(e)
            elif e.type() == QtCore.QEvent.Enter:
                self._on_hover(e)
            elif e.type() == QtCore.QEvent.Leave:
                self._on_leave(e)

        return super().eventFilter(obj, e)


class TranslateYAnimation(AnimationBase):
    value_changed = QtCore.Signal(float)

    def __init__(self, parent, offset=2):
        super().__init__(parent)
        self._y = 0
        self.max_offset = offset
        self.ani = QtCore.QPropertyAnimation(self, b'y', self)

    def get_y(self):
        return self._y

    def set_y(self, y):
        self._y = y
        self.parent().update()
        self.value_changed.emit(y)

    def _on_press(self, e):
        """ arrow down """
        self.ani.setEndValue(self.max_offset)
        self.ani.setEasingCurve(QtCore.QEasingCurve.OutQuad)
        self.ani.setDuration(150)
        self.ani.start()

    def _onrelease(self, e):
        """ arrow up """
        self.ani.setEndValue(0)
        self.ani.setDuration(500)
        self.ani.setEasingCurve(QtCore.QEasingCurve.OutElastic)
        self.ani.start()

    y = QtCore.Property(float, get_y, set_y)
