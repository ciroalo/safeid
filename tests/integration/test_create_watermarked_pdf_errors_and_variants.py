from pathlib import Path

import pytest
from PIL import Image

from safeid.app.container import build_create_watermarked_pdf_use_case
from safeid.core.domain.errors import (
    ImageTooSmallError,
    OutputAlreadyExistsError,
    UnsupportedFormatError,
)
from safeid.core.domain.models import (
    CreateWatermarkedPdfRequest,
    ImageSource,
    WatermarkSpec,
)


def test_create_watermarked_pdf_raises_if_output_exists(tmp_path: Path):
    image_path = tmp_path / "passport.jpg"
    Image.new("RGB", (1200, 800), color="white").save(image_path, format="JPEG")

    existing_output = tmp_path / "passport_ACME_watermarked.pdf"
    existing_output.write_bytes(b"already here")

    use_case = build_create_watermarked_pdf_use_case()

    request = CreateWatermarkedPdfRequest(
        images=[ImageSource(path=image_path)],
        recipient="ACME",
        watermark=WatermarkSpec(text="ACME"),
    )

    with pytest.raises(OutputAlreadyExistsError):
        use_case.execute(request=request)


def test_create_watermarked_pdf_raises_for_too_small_image(tmp_path: Path):
    image_path = tmp_path / "passport.jpg"
    Image.new("RGB", (1200, 500), color="white").save(image_path, format="JPEG")

    use_case = build_create_watermarked_pdf_use_case()

    request = CreateWatermarkedPdfRequest(
        images=[ImageSource(path=image_path)],
        recipient="ACME",
        watermark=WatermarkSpec(text="ACME"),
    )

    with pytest.raises(ImageTooSmallError):
        use_case.execute(request=request)


def test_create_watermarked_pdf_raises_for_unsupported_format(tmp_path: Path):
    image_path = tmp_path / "passport.bmp"
    Image.new("RGB", (1200, 800), color="white").save(image_path, format="BMP")

    use_case = build_create_watermarked_pdf_use_case()

    request = CreateWatermarkedPdfRequest(
        images=[ImageSource(path=image_path)],
        recipient="ACME",
        watermark=WatermarkSpec(text="ACME"),
    )

    with pytest.raises(UnsupportedFormatError):
        use_case.execute(request=request)


def test_create_watermarked_pdf_raises_for_invalid_image_content(tmp_path: Path):
    image_path = tmp_path / "fake.jpg"
    image_path.write_text("this is not a real image")

    use_case = build_create_watermarked_pdf_use_case()

    request = CreateWatermarkedPdfRequest(
        images=[ImageSource(path=image_path)],
        recipient="ACME",
        watermark=WatermarkSpec(text="ACME"),
    )

    with pytest.raises(UnsupportedFormatError):
        use_case.execute(request=request)
