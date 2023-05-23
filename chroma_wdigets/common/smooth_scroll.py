from collections import deque
from enum import Enum
from math import cos, pi

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets


class SmoothMode(Enum):
    """ Smooth mode """
    NO_SMOOTH = 0
    CONSTANT = 1
    LINEAR = 2
    QUADRATI = 3
    COSINE = 4


class SmoothScroll(object):
    """ Scroll smoothly """

    def __init__(self, widget, orient=QtCore.Qt.Vertical):
        """
        Parameters
        ----------
        widget: QScrollArea
            scroll area to scroll smoothly

        orient: Orientation
            scroll orientation
        """
        self.widget = widget
        self.orient = orient
        self.fps = 60
        self.duration = 400
        self.steps_total = 0
        self.step_ratio = 1.5
        self.acceleration = 1
        self.last_wheel_event = None
        self.scroll_stamps = deque()
        self.steps_left_queue = deque()
        self.smooth_move_timer = QtCore.QTimer(widget)
        self.smooth_mode = SmoothMode(SmoothMode.LINEAR)
        self.smooth_move_timer.timeout.connect(self._smooth_move)

    def set_smooth_mode(self, smoothMode):
        """ set smooth mode """
        self.smooth_mode = smoothMode

    def wheelEvent(self, e):
        # only process the wheel events triggered by mouse
        delta = e.angleDelta().y() if e.angleDelta().y() != 0 else e.angleDelta().x()
        if self.smooth_mode == SmoothMode.NO_SMOOTH or abs(delta) % 120 != 0:
            QtWidgets.QAbstractScrollArea.wheelEvent(self.widget, e)
            return

        # push current time to queque
        now = QtCore.QDateTime.currentDateTime().toMSecsSinceEpoch()
        self.scroll_stamps.append(now)
        while now - self.scroll_stamps[0] > 500:
            self.scroll_stamps.popleft()

        # adjust the acceration ratio based on unprocessed events
        acceration_ratio = min(len(self.scroll_stamps) / 15, 1)
        self.last_wheel_pos = QtCore.QPointF(e.pos())
        self.last_wheel_global_pos = QtCore.QPointF(e.globalPos())

        # get the number of steps
        self.steps_total = self.fps * self.duration / 1000

        # get the moving distance corresponding to each event
        delta = delta * self.step_ratio
        if self.acceleration > 0:
            delta += delta * self.acceleration * acceration_ratio

        # form a list of moving distances and steps, and insert it into the queue for processing.
        self.steps_left_queue.append([delta, self.steps_total])

        # overflow time of timer: 1000ms/frames
        self.smooth_move_timer.start(int(1000 / self.fps))

    def _smooth_move(self):
        """ scroll smoothly when timer time out """
        total_delta = 0

        # Calculate the scrolling distance of all unprocessed events,
        # the timer will reduce the number of steps by 1 each time it overflows.
        for i in self.steps_left_queue:
            total_delta += self._sub_delta(i[0], i[1])
            i[1] -= 1

        # If the event has been processed, move it out of the queue
        while self.steps_left_queue and self.steps_left_queue[0][1] == 0:
            self.steps_left_queue.popleft()

        # construct wheel event
        if self.orient == QtCore.Qt.Orientation.Vertical:
            pixelDelta = QtCore.QPoint(round(total_delta), 0)
            bar = self.widget.verticalScrollBar()
        else:
            pixelDelta = QtCore.QPoint(0, round(total_delta))
            bar = self.widget.horizontalScrollBar()

        e = QtGui.QWheelEvent(
            self.last_wheel_pos,
            self.last_wheel_global_pos,
            pixelDelta,
            QtCore.QPoint(round(total_delta), 0),
            QtCore.Qt.MouseButton.LeftButton,
            QtCore.Qt.KeyboardModifier.NoModifier,
            QtCore.Qt.ScrollPhase.ScrollBegin,
            False,
        )

        # send wheel event to app
        QtWidgets.QApplication.sendEvent(bar, e)

        # stop scrolling if the queque is empty
        if not self.steps_left_queue:
            self.smooth_move_timer.stop()

    def _sub_delta(self, delta, stepsLeft):
        """ get the interpolation for each step """
        m = self.steps_total / 2
        x = abs(self.steps_total - stepsLeft - m)

        res = 0
        if self.smooth_mode == SmoothMode.NO_SMOOTH:
            res = 0
        elif self.smooth_mode == SmoothMode.CONSTANT:
            res = delta / self.steps_total
        elif self.smooth_mode == SmoothMode.LINEAR:
            res = 2 * delta / self.steps_total * (m - x) / m
        elif self.smooth_mode == SmoothMode.QUADRATI:
            res = 3 / 4 / m * (1 - x * x / m / m) * delta
        elif self.smooth_mode == SmoothMode.COSINE:
            res = (cos(x * pi / m) + 1) / (2 * m) * delta

        return res
