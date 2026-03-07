from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from safeid.core.domain.errors import (
    EmptyRecipientError,
    InvalidImageCountError,
    InvalidInputError,
    OutputAlreadyExistsError,
    EmptyWatermarkTextError,
)
from safeid.core.domain.models import (
    CreateWatermarkedPdfRequest,
    CreateWatermarkedPdfResult,
    ImageAsset,
    LayoutPlan,
    PageSpec,
    RectPt
)
from safeid.core.ports.filesystem import FileSystemPort
from safeid.core.ports.image_decoder import ImageDecoderPort
from safeid.core.ports.pdf_renderer import PdfRendererPort


@dataclass(frozen=True)
class CreateWatermarkedPdfUseCase:
    """Orchestrates the MVP flow: decode -> plan -> render -> export
    
    This is inside the application core. It must not import any concrete adapter
    libraries. Only ports + domain models
    """
    image_decoder: ImageDecoderPort
    pdf_renderer: PdfRendererPort
    filesystem: FileSystemPort
    
    def execute(self, request: CreateWatermarkedPdfRequest) -> CreateWatermarkedPdfResult:
        self._validate_request(request)
        
        # 1) Decode images (adapter responsibility: jpg/png only, min size check, exif normalize)
        decoded: list[ImageAsset] = []
        for src in request.images:
            decoded.append(self.image_decoder.decode(src.path))
            
        # 2) Build output path (deterministic)
        output_path = self._build_output_path(request)
        
        # 3) Enforce no overwrite (PRD)
        if self.filesystem.exists(output_path):
            raise OutputAlreadyExistsError.for_path(output_path)
        
        # 4) Play layout + watermark target area (TODO)
        layout = self._plan_layout(decoded)
        
        # 5) Render PDF bytes
        pdf_bytes = self.pdf_renderer.render_pdf_bytes(images=decoded, layout=layout, watermark=request.watermark)
        
        # 6) Export
        self.filesystem.write_new_bytes(output_path, pdf_bytes)
        
        return CreateWatermarkedPdfResult(output_path=output_path)
    
    @staticmethod
    def _validate_request(request: CreateWatermarkedPdfRequest) -> None:
        count = len(request.images)
        if count not in (1, 2):
            raise InvalidImageCountError.for_count(count=count)
        
        if request.recipient.strip() == "":
            raise EmptyRecipientError(user_message="Recipient cannot be empty")
        
        if request.watermark.text.strip() == "":
            raise EmptyWatermarkTextError(user_message="Watermark text cannot be empty")
    
    @staticmethod
    def _build_output_path(request: CreateWatermarkedPdfRequest) -> Path:
        # Naming rule <first_file>_<recipient>_watermarked.pdf
        first_path = request.images[0].path
        first_stem = first_path.stem
        
        # Minimal sanitization
        recipient_safe = request.recipient.strip().replace(" ", "_")
        
        filename = f"{first_stem}_{recipient_safe}_watermarked.pdf"
        return first_path.parent / filename
    
    @staticmethod
    def _plan_layout(images: Sequence[ImageAsset]) -> LayoutPlan:
        # TODO: replace with LayoutPlanner in core/planne/layout_planner.py
        # For now, this is a placeholder that makes the sue case compile
        # We will implement determistic A4 placement next
        
        # Placeholder "full-page photo area" so renderer can still tile watermark
        # if you choose to implement rendering full layout
        page = PageSpec(size="A4", margin_mm=19.0)
        
        # Until placement is implemented, fail fast to avoid silently wrong PDFs
        raise InvalidInputError(user_message="Layout planning not implemented yet", detail=f"Got {len(images)} image(s).")
