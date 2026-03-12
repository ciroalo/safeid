from pathlib import Path

import pytest

from safeid.core.use_cases.create_watermarked_pdf import CreateWatermarkedPdfUseCase
from safeid.core.domain.models import (
    CreateWatermarkedPdfRequest,
    ImageSource,
    WatermarkSpec,
    ImageAsset,
    SizePx,
)
from safeid.core.domain.errors import InvalidImageCountError


class FakeDecoder:
    def decode(self, path):
        return ImageAsset(
            size_px=SizePx(width=1200, height=800), mode="RGB", pixel_bytes=b""
        )


class FakeRenderer:
    def __init__(self):
        self.called = False
        self.layout = None

    def render_pdf_bytes(self, *, images, layout, watermark):
        self.called = True
        self.layout = layout
        return b"%PDF-fake"


class FakeFileSystem:
    def exists(self, path):
        return False

    def write_new_bytes(self, path, data):
        pass


def build_use_case(image_decoder=None, pdf_renderer=None, filesystem=None):
    if image_decoder is None:
        image_decoder = FakeDecoder()
    if pdf_renderer is None:
        pdf_renderer = FakeRenderer()
    if filesystem is None:
        filesystem = FakeFileSystem()

    return CreateWatermarkedPdfUseCase(
        image_decoder=image_decoder,
        pdf_renderer=pdf_renderer,
        filesystem=filesystem,
    )


def test_invalid_image_count():
    use_case = build_use_case()

    request = CreateWatermarkedPdfRequest(
        images=[], recipient="ACME", watermark=WatermarkSpec(text="ACME")
    )

    with pytest.raises(InvalidImageCountError):
        use_case.execute(request)


def test_output_filename_generation():
    use_case = build_use_case()

    request = CreateWatermarkedPdfRequest(
        images=[
            ImageSource(
                path=Path(
                    "/Users/ciroa/Documents/projects/safeid/tests/fixtures/images/mock_passport.jpg"
                )
            )
        ],
        recipient="ACME Corp",
        watermark=WatermarkSpec(text="ACME"),
    )

    path = use_case._build_output_path(request)

    assert path.name == "mock_passport_ACME_Corp_watermarked.pdf"


def test_use_case_builds_layout_and_calls_renderer():
    renderer = FakeRenderer()
    use_case = build_use_case(pdf_renderer=renderer)

    request = CreateWatermarkedPdfRequest(
        images=[ImageSource(path=Path("tests/fixtures/images/mock_passport.jpg"))],
        recipient="ACME",
        watermark=WatermarkSpec(text="ACME"),
    )

    result = use_case.execute(request)

    assert renderer.called is True
    assert renderer.layout is not None
    assert len(renderer.layout.placed_images) == 1
    assert result.output_path.name == "mock_passport_ACME_watermarked.pdf"
