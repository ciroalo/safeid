from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from safeid.app.container import build_create_watermarked_pdf_use_case
from safeid.ui.qt.main_window import MainWindow
from safeid.ui.qt.resources import resource_path


def run() -> int:
    """Start the Qt application"""
    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName("SafeID")
    qt_app.setOrganizationName("SafeID")
    qt_app.setWindowIcon(
        QIcon(str(resource_path("safeid", "ui", "assets", "icons", "safeid-icon.icns")))
    )

    use_case = build_create_watermarked_pdf_use_case()
    window = MainWindow(create_watermarked_pdf_use_case=use_case)
    window.show()

    return qt_app.exec()
