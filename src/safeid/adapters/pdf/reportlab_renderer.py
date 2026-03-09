from __future__ import annotations

from io import BytesIO
from typing import Sequence

from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from safeid.core.domain.errors import InvalidInputError
from safeid.core.domain.models import ImageAsset, LayoutPlan, RectPt, WatermarkSpec
from safeid.core.ports.pdf_renderer import PdfRendererPort

A4_WIDTH_PT = 595.275590551
A4_HEIGHT_PT = 841.88976378


class ReportLabPdfRendererAdapter(PdfRendererPort):
    """Render a single-page A4 watermarked PDF using ReportLab"""
    
    def render_pdf_bytes(
        self,
        *,
        images: Sequence[ImageAsset],
        layout: LayoutPlan,
        watermark: WatermarkSpec
    ) -> bytes:
        
        try:
            self._validate_inputs(images=images, layout=layout)
            
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=(A4_WIDTH_PT, A4_HEIGHT_PT))
            
            self._draw_images(pdf=pdf, images=images, layout=layout)
            self._draw_watermark(pdf=pdf, layout=layout, watermark=watermark)
            
            pdf.showPage()
            pdf.save()
        
            return buffer.getvalue()
        
        except InvalidInputError:
            raise
        except Exception as exc:
            raise InvalidInputError(
                user_message="Failed to render the PDF.",
                detail=str(exc)
            ) from exc
    
    def _validate_inputs(
        self,
        *,
        images: Sequence[ImageAsset],
        layout: LayoutPlan
    ) -> None:
        if len(images) not in (1, 2):
            raise InvalidInputError(
                user_message="Renderer requeires 1 or 2 images"
            )
            
        if len(layout.placed_images) != len(images):
            raise InvalidInputError(
                user_message="Layout does not match number of images",
                detail=(
                    f"images={len(images)}, "
                    f"placed images={len(layout.placed_images)}"
                )
            )
        
        for placed in layout.placed_images:
            if placed.source_index < 0 or placed.source_index >= len(images):
                raise InvalidInputError(
                    user_message="Layout references an invalid image index",
                    detail=f"source_index={placed.source_index}"
                )
    
    def _draw_images(
        self,
        *,
        pdf: canvas.Canvas,
        images: Sequence[ImageAsset],
        layout: LayoutPlan
    ) -> None:
        for placed in layout.placed_images:
            asset = images[placed.source_index]
            
            pil_image = self._to_pil_image(asset)
            
            if placed.rotate_90:
                pil_image = pil_image.rotate(-90 * placed.rotate_90, expand=True)
                
            image_reader = ImageReader(pil_image)
            rect = placed.rect
            
            pdf.drawImage(
                image=image_reader,
                x=rect.x,
                y=rect.y,
                width=rect.width,
                height=rect.height,
                preserveAspectRatio=False,
                mask="auto"
            )
    
    def _draw_watermark(
        self,
        *,
        pdf: canvas.Canvas,
        layout: LayoutPlan,
        watermark: WatermarkSpec
    ) -> None:
        target = layout.photo_area
        
        pdf.saveState()
        
        font_name = self._resolve_font_name(watermark.font_family)
        pdf.setFont(font_name, watermark.font_size_pt)
        
        if hasattr(pdf, "setFillAlpha"):
            pdf.setFillAlpha(watermark.opacity)
            
        center_x = target.x + target.width / 2.0
        center_y = target.y + target.height / 2.0
        pdf.translate(center_x, center_y)
        pdf.rotate(watermark.angle_deg)
        
        repeated_text = self._build_repeated_watermark_line(
            text=watermark.text,
            word_spacing=watermark.word_spacing,
            target_width=target.width * 2.0,
            font_name=font_name,
            font_size=watermark.font_size_pt,
            pdf=pdf
        )
        
        start_y = -(target.height)
        end_y = target.height
        
        y = start_y
        while y <= end_y:
            pdf.drawCentredString(0, y, repeated_text)
            y += watermark.line_spacing_pt
            
        pdf.restoreState()
    
    def _build_repeated_watermark_line(
        self,
        *,
        text: str,
        word_spacing: int,
        target_width: float,
        font_name: str,
        font_size: float,
        pdf: canvas.Canvas
    ) -> str:
        separator = " " * max(word_spacing, 1)
        unit = f"{text}{separator}"
        
        line = unit
        while pdf.stringWidth(line, font_name, font_size) < target_width:
            line += unit
        
        return line
    
    @staticmethod
    def _resolve_font_name(font_family: str) -> str:
        if font_family == "system":
            return "Helvetica"
        return "Helvetica"
    
    @staticmethod
    def _to_pil_image(asset: ImageAsset) -> Image:
        width = asset.size_px.width
        height = asset.size_px.height
        
        return Image.frombytes(
            asset.mode,
            (width, height),
            asset.pixel_bytes
        )
