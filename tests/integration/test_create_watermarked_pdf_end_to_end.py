from pathlib import Path

from PIL import Image

from safeid.adapters.filesystem.local_filesystem import LocalFileSystemAdapter
from safeid.adapters.image.pillow_decoder import PillowImageDecoderAdapter
from safeid.adapters.pdf.reportlab_renderer import ReportLabPdfRendererAdapter
from safeid.core.domain.models import (
    CreateWatermarkedPdfRequest,
    ImageSource,
    WatermarkSpec
)
from safeid.core.use_cases.create_watermarked_pdf import CreateWatermarkedPdfUseCase


def test_create_watermarked_pdf_end_to_end(tmp_path: Path):
    image_path = tmp_path / "passport.jpg"
    Image.new("RGB", (1200, 800), color="white").save(image_path, format="JPEG")
    
    use_case = CreateWatermarkedPdfUseCase(
        image_decoder=PillowImageDecoderAdapter(),
        pdf_renderer=ReportLabPdfRendererAdapter(),
        filesystem=LocalFileSystemAdapter()
    )
    
    request = CreateWatermarkedPdfRequest(
        images=[ImageSource(path=image_path)],
        recipient="ACME",
        watermark=WatermarkSpec(text="ACME")
    )
    
    result = use_case.execute(request=request)
    
    assert result.output_path.exists()
    assert result.output_path.name == "passport_ACME_watermarked.pdf"
    assert result.output_path.read_bytes().startswith(b"%PDF")