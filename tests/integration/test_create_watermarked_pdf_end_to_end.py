from pathlib import Path

from PIL import Image

from safeid.app.container import build_create_watermarked_pdf_use_case
from safeid.core.domain.models import (
    CreateWatermarkedPdfRequest,
    ImageSource,
    WatermarkSpec
)


def test_create_watermarked_pdf_end_to_end(tmp_path: Path):
    image_path = tmp_path / "passport.jpg"
    Image.new("RGB", (1200, 800), color="white").save(image_path, format="JPEG")
    
    use_case = build_create_watermarked_pdf_use_case()
    
    request = CreateWatermarkedPdfRequest(
        images=[ImageSource(path=image_path)],
        recipient="ACME",
        watermark=WatermarkSpec(text="ACME")
    )
    
    result = use_case.execute(request=request)
    
    assert result.output_path.exists()
    assert result.output_path.name == "passport_ACME_watermarked.pdf"
    assert result.output_path.read_bytes().startswith(b"%PDF")
    

def test_create_watermarked_pdf_two_images_end_to_end(tmp_path: Path):
    front_path = tmp_path / "front.jpg"
    back_path = tmp_path / "back.jpg"
    
    Image.new("RGB", (1200, 800), color="white").save(front_path, format="JPEG")
    Image.new("RGB", (1000, 900), color="white").save(back_path, format="JPEG")
    
    use_case = build_create_watermarked_pdf_use_case()
    
    request = CreateWatermarkedPdfRequest(
        images=[
            ImageSource(path=front_path), 
            ImageSource(path=back_path)
        ],
        recipient="ACME",
        watermark=WatermarkSpec(text="ACME")
    )
    
    result = use_case.execute(request=request)
    
    assert result.output_path.exists()
    assert result.output_path.name == "front_ACME_watermarked.pdf"
    assert result.output_path.read_bytes().startswith(b"%PDF")