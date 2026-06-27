import os
from enum import Enum

from PySide6 import QtWidgets


class QtStretches(Enum):
    HORIZONTAL = 0
    VERTICAL = 1


class QtHelpers:
    @staticmethod
    def terminate_application() -> None:
        """Immediately terminate the process.

        Background QThreads (lockfile watcher, LCU event processor) have no
        graceful stop mechanism, so a normal QApplication.quit() would leave
        them running and the process hanging. os._exit() is used deliberately
        until those workers support cooperative shutdown.
        """
        os._exit(0)

    @staticmethod
    def create_size_policy(stretch: QtStretches, factor: int) -> QtWidgets.QSizePolicy:
        sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        if stretch is QtStretches.HORIZONTAL:
            sp.setHorizontalStretch(factor)
        elif stretch is QtStretches.VERTICAL:
            sp.setVerticalStretch(factor)
        return sp

    @staticmethod
    def clear_qlayout(layout: QtWidgets.QLayout):
        while layout.count():
            child = layout.takeAt(0)
            child_widget = child.widget()
            if child_widget:
                child_widget.setVisible(False)
                child_widget.setParent(None)
                child_widget.deleteLater()
