from __future__ import annotations

from pathlib import Path
from typing import Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from safeid.core.domain.errors import SafeIdError
from safeid.core.domain.models import (
    CreateWatermarkedPdfRequest,
    ImageSource,
    WatermarkSpec
)
from safeid.core.use_cases.create_watermarked_pdf import CreateWatermarkedPdfUseCase
from safeid.ui.qt.dialogs import show_error_dialog, show_success_dialog
from safeid.ui.qt.mappers import map_error_to_dialog


class MainWindow(QMainWindow):
    def __init__(
        self,
        *,
        create_watermarked_pdf_use_case: CreateWatermarkedPdfUseCase
    ) -> None:
        super().__init__()
        
        self._create_watermarked_pdf_use_case = create_watermarked_pdf_use_case
        self._selected_images: list[Path] = []
        
        self.setWindowTitle("SafeID")
        self.resize(500, 500)
        
        self._build_ui()
        self._connect_signals()
        self._refresh_ui_state()
        
    def _build_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main dark background
        central_widget.setStyleSheet(
            """
            QWidget {
                background-color: #222126;
                color: #f2f2f2;
                font-size: 14px;
            }

            QLabel#titleLabel {
                font-size: 24px;
                color: #f5f5f7;
            }

            QLabel#subtitleLabel {
                font-size: 14px;
                color: #c7c7cc;
            }

            QLabel.sectionLabel {
                font-size: 12px;
                color: #f2f2f2;
            }

            QLabel.hintLabel {
                font-size: 10px;
                color: #8e8e93;
            }

            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
                font-size: 12px;
                color: #cdcbd1;
                padding: 0px;
            }

            QListWidget::item {
                padding: 14px 12px;
                border-bottom: 1px solid #2c2c2e;
            }

            QListWidget::item:selected {
                background-color: #1c1c1e;
                border-radius: 8px;
            }

            QLineEdit {
                background-color: #1c1c1e;
                border: 1px solid #3a3a3c;
                border-radius: 8px;
                padding: 12px 14px;
                color: #f2f2f2;
                font-size: 12px;
                min-height: 20px;
            }

            QLineEdit:focus {
                border: 1px solid #0a84ff;
            }

            QPushButton {
                border-radius: 8px;
                padding: 5px 5px;
                font-size: 16px;
            }

            QPushButton#secondaryButton {
                background-color: #2c2c2e;
                border: 1px solid #3a3a3c;
                color: #f2f2f2;
            }

            QPushButton#secondaryButton:hover {
                background-color: #3a3a3c;
            }

            QPushButton#primaryButton {
                background-color: #0a84ff;
                border: none;
                color: white;
            }

            QPushButton#primaryButton:hover {
                background-color: #3395ff;
            }

            QPushButton#primaryButton:disabled {
                background-color: #2c2c2e;
                color: #8e8e93;
            }

            QFrame.separator {
                background-color: #2c2c2e;
                max-height: 1px;
                min-height: 1px;
            }
            """
        )

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(32, 28, 32, 15)
        root_layout.setSpacing(0)
        central_widget.setLayout(root_layout)

        # Center the content horizontally
        outer_row = QHBoxLayout()
        outer_row.setContentsMargins(0, 0, 0, 0)

        content_widget = QWidget()
        content_widget.setMaximumWidth(760)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_widget.setLayout(content_layout)

        outer_row.addWidget(content_widget)

        root_layout.addLayout(outer_row)

        # Title
        self.title_label = QLabel("SafeID")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.subtitle_label = QLabel(
            "Generate a watermarked PDF from 1 or 2 ID images"
        )
        self.subtitle_label.setObjectName("subtitleLabel")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.subtitle_label.setWordWrap(True)

        content_layout.addSpacing(16)
        content_layout.addWidget(self.title_label)
        content_layout.addSpacing(10)
        content_layout.addWidget(self.subtitle_label)
        content_layout.addSpacing(26)

        # Select button
        self.select_images_button = QPushButton("Select Images")
        self.select_images_button.setObjectName("secondaryButton")
        self.select_images_button.setMinimumHeight(35)
        self.select_images_button.setStyleSheet("font-size: 14px;")
        content_layout.addWidget(self.select_images_button)
        content_layout.addSpacing(12)

        # Separator
        separator_1 = QFrame()
        separator_1.setObjectName("separator")
        separator_1.setProperty("class", "separator")
        separator_1.setFrameShape(QFrame.Shape.NoFrame)
        content_layout.addWidget(separator_1)
        content_layout.addSpacing(12)

        # Selected files
        self.selected_files_label = QLabel("Selected files:")
        self.selected_files_label.setProperty("class", "sectionLabel")
        self.selected_files_label.setStyleSheet("font-size: 14px;")

        self.selected_files_list = QListWidget()
        self.selected_files_list.setMinimumHeight(105)
        self.selected_files_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.selected_files_list.setSpacing(0)

        content_layout.addWidget(self.selected_files_label)
        content_layout.addSpacing(10)
        content_layout.addWidget(self.selected_files_list)
        content_layout.addSpacing(10)

        self.selection_hint_label = QLabel("Select 1 or 2 JPG/PNG images.")
        self.selection_hint_label.setProperty("class", "hintLabel")
        content_layout.addWidget(self.selection_hint_label)
        content_layout.addSpacing(12)

        # Recipient
        self.recipient_label = QLabel("Recipient / Company")
        self.recipient_label.setStyleSheet("font-size: 14px;")

        self.recipient_input = QLineEdit()
        self.recipient_input.setPlaceholderText("Enter recipient or company name")

        content_layout.addWidget(self.recipient_label)
        content_layout.addSpacing(10)
        content_layout.addWidget(self.recipient_input)
        content_layout.addSpacing(12)

        # Watermark
        self.watermark_label = QLabel("Watermark text (optional)")
        self.watermark_label.setStyleSheet("font-size: 14px;")

        self.watermark_input = QLineEdit()
        self.watermark_input.setPlaceholderText("Leave empty to use recipient name")

        content_layout.addWidget(self.watermark_label)
        content_layout.addSpacing(12)
        content_layout.addWidget(self.watermark_input)
        content_layout.addSpacing(12)

        # Separator
        separator_2 = QFrame()
        separator_2.setObjectName("separator")
        separator_2.setProperty("class", "separator")
        separator_2.setFrameShape(QFrame.Shape.NoFrame)
        content_layout.addWidget(separator_2)
        content_layout.addSpacing(12)

        # Generate button
        self.generate_button = QPushButton("Generate Watermarked PDF")
        self.generate_button.setObjectName("primaryButton")
        self.generate_button.setMinimumHeight(50)

        content_layout.addWidget(self.generate_button)
        content_layout.addSpacing(18)

        # Optional note at bottom
        self.output_note_label = QLabel(
            "The PDF will be saved next to the first selected image."
        )
        self.output_note_label.setProperty("class", "hintLabel")
        self.output_note_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.output_note_label.setWordWrap(True)

        content_layout.addWidget(self.output_note_label)
        # content_layout.addSpacing(12)
        
    def _connect_signals(self) -> None:
        self.select_images_button.clicked.connect(self._on_select_images_clicked)
        self.generate_button.clicked.connect(self._on_generate_clicked)
        self.recipient_input.textChanged.connect(self._refresh_ui_state)
        
    def _on_select_images_clicked(self) -> None:
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select 1 or 2 images",
            "",
            "Images (*.jpg *.jpeg *.png)"
        )
        
        if not file_paths:
            return
        
        selected = [Path(path) for path in file_paths]
        if len(selected) > 2:
            show_error_dialog(self, title="Error", message="Please select only 1 or 2 images")
            return 
        
        self._selected_images = selected
        self._update_selected_files_list()
        self._refresh_ui_state()
        
    def _on_generate_clicked(self) -> None:
        try:
            request = self._build_request()
            result = self._create_watermarked_pdf_use_case.execute(request)
        except SafeIdError as exc:
            dialog_model = map_error_to_dialog(exc)
            show_error_dialog(
                self, 
                title=dialog_model.title, 
                message=dialog_model.message, 
                detail=dialog_model.detail)
            return 
        
        show_success_dialog(
            self,
            title="Success",
            message="PDF created successfully",
            detail=str(result.output_path)
        )
        
    def _build_request(self) -> CreateWatermarkedPdfRequest:
        recipient = self.recipient_input.text().strip()
        watermark_text = self.watermark_input.text().strip()
        
        if watermark_text == "":
            watermark_text = recipient
            
        return CreateWatermarkedPdfRequest(
            images=[ImageSource(path=path) for path in self._selected_images],
            recipient=recipient,
            watermark=WatermarkSpec(text=watermark_text)
        )
        
    def _update_selected_files_list(self) -> None:
        self.selected_files_list.clear()
        for path in self._selected_images:
            self.selected_files_list.addItem(path.name)
            
    def _refresh_ui_state(self) -> None:
        has_valid_image_count = len(self._selected_images) in (1, 2)
        has_recipient = self.recipient_input.text().strip() != ""
        
        self.generate_button.setEnabled(has_valid_image_count and has_recipient)