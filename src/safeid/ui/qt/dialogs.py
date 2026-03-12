from __future__ import annotations

from PySide6.QtWidgets import QMessageBox, QWidget


def show_success_dialog(
    parent: QWidget, *, title: str, message: str, detail: str | None = None
) -> None:
    dialog = QMessageBox(parent)
    dialog.setIcon(QMessageBox.Icon.Information)
    dialog.setWindowTitle("Error")
    dialog.setText(message)

    if detail:
        dialog.setInformativeText(detail)

    dialog.exec()


def show_error_dialog(
    parent: QWidget, *, title: str, message: str, detail: str | None = None
) -> None:
    dialog = QMessageBox(parent)
    dialog.setIcon(QMessageBox.Icon.Critical)
    dialog.setWindowTitle("Error")
    dialog.setText(message)

    if detail:
        dialog.setInformativeText(detail)

    dialog.exec()
