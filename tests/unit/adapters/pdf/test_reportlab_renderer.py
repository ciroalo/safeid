import pytest

from safeid.core.domain.models import (
    ImageAsset,
    LayoutPlan,
    PageSpec,
    PlacedImage,
    RectPt,
    SizePx,
    WatermarkSpec
)
from safeid.core.domain.errors import InvalidInputError
from safeid.adapters.pdf.reportlab_renderer import ReportLabPdfRendererAdapter



# test helper
def make_image(width: int, height: int) -> ImageAsset:
    return ImageAsset(
        size_px=SizePx(width=width, height=height),
        mode="RGB",
        pixel_bytes=b"\xff" * (width * height * 3)
    )
    
    
def test_render_pdf_bytes_returns_pdf_bytes_for_single_image():
    renderer = ReportLabPdfRendererAdapter()
    image = make_image(100, 100)
    
    layout = LayoutPlan(
        page=PageSpec(),
        placed_images=[
            PlacedImage(
                source_index=0,
                rect=RectPt(x=100, y=100, width=200, height=200),
                rotate_90=0,
            )
        ],
        photo_area=RectPt(x=100, y=100, width=200, height=200),
    )
    
    watermark = WatermarkSpec(text="ACME")
    
    pdf_bytes = renderer.render_pdf_bytes(
        images=[image],
        layout=layout,
        watermark=watermark
    )
    
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF")
    
    
def test_render_pdf_bytes_raises_for_layout_image_count_mismatch():
    renderer = ReportLabPdfRendererAdapter()
    image = make_image(100, 100)
    
    layout = LayoutPlan(
        page=PageSpec(),
        placed_images=[],
        photo_area=RectPt(x=100, y=100, width=200, height=200)
    )
    
    watermark = WatermarkSpec(text="ACME")
    
    with pytest.raises(InvalidInputError):
        renderer.render_pdf_bytes(
            images=[image],
            layout=layout,
            watermark=watermark
        )