from __future__ import annotations

from safeid.adapters.filesystem.local_filesystem import LocalFileSystemAdapter
from safeid.adapters.image.pillow_decoder import PillowImageDecoderAdapter
from safeid.adapters.pdf.reportlab_renderer import ReportLabPdfRendererAdapter
from safeid.core.use_cases.create_watermarked_pdf import CreateWatermarkedPdfUseCase


def build_create_watermarked_pdf_use_case() -> CreateWatermarkedPdfUseCase:
    return CreateWatermarkedPdfUseCase(
        image_decoder=PillowImageDecoderAdapter(),
        pdf_renderer=ReportLabPdfRendererAdapter(),
        filesystem=LocalFileSystemAdapter()
    )