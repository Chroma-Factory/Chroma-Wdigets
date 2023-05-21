from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import contextlib

from Qt import QtWidgets
from Qt import QtCore


@contextlib.contextmanager
def application(enabled_dpi=True, *args):
    app = QtWidgets.QApplication.instance()
    if not app:
        if enabled_dpi:
            QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(
                QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
            QtWidgets.QApplication.setAttribute(
                QtCore.Qt.AA_EnableHighDpiScaling)
            QtWidgets.QApplication.setAttribute(
                QtCore.Qt.AA_UseHighDpiPixmaps)

        app = QtWidgets.QApplication(list(args))
        yield app
        app.exec_()
    else:
        yield app
