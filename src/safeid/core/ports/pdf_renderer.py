from __future__ import annotations

from typing import Protocol, Sequence

from safeid.core.domain.errors import InvalidInputError
from safeid.core.domain.models import (
    ImageAsset,
    LayoutPlan,
    WatermarkPlan,
    WatermarkSpec,
)


class PdfRendererPort(Protocol):
    """Port responsible for producing a single-page A4 PDF
    
    Implemented by a PDF adapter
    The core passes fully-decoded image pixels plus an explicit layout plan
    """
    
    def render_pdf_bytes(self, *, images: Sequence[ImageAsset], layout: LayoutPlan, watermark: WatermarkSpec, watermark_plan: WatermarkPlan) -> bytes:
        """Render the final PDF as bytes
        
        Args:
            images: Decoded, normalized pixel data (lenght 1-2)
            layout: Precomputed placement plan for the page and images
            watermark: Watermark styling config (text, font, opacity, angle, spacing)
            watermark_plan: Precomputed target area the watermark must cover
            
        Returns: 
            PDF file bytes representing exactly one page
            
        Raises: 
            InvalidInputError:
                - if rendering fails
                - if plans are inconsistent
        """