from pathlib import Path

import pytest

from PIL import Image

from safeid.adapters.image.pillow_decoder import PillowImageDecoderAdapter
from safeid.core.domain.errors import ImageTooSmallError, UnsupportedFormatError


def test_decode_valid_jpeg(tmp_path: Path):
    adapter = PillowImageDecoderAdapter()
    image_path = tmp_path / "valid.jpg"

    Image.new("RGB", (800, 600), color="white").save(image_path, format="JPEG")

    asset = adapter.decode(image_path)

    assert asset.size_px.width == 800
    assert asset.size_px.height == 600
    assert asset.mode == "RGB"
    assert isinstance(asset.pixel_bytes, bytes)
    assert len(asset.pixel_bytes) > 0


def test_decode_valid_png(tmp_path: Path):
    adapter = PillowImageDecoderAdapter()
    image_path = tmp_path / "valid.png"

    Image.new("RGB", (700, 900), color="white").save(image_path, format="PNG")

    asset = adapter.decode(image_path)

    assert asset.size_px.width == 700
    assert asset.size_px.height == 900
    assert asset.mode == "RGB"
    assert isinstance(asset.pixel_bytes, bytes)
    assert len(asset.pixel_bytes) > 0


def test_decode_raises_for_too_small_image(tmp_path: Path):
    adapter = PillowImageDecoderAdapter()
    image_path = tmp_path / "small.jpg"

    Image.new("RGB", (500, 500), color="white").save(image_path, format="JPEG")

    with pytest.raises(ImageTooSmallError):
        adapter.decode(image_path)


def test_decode_raises_for_unidentified_file(tmp_path: Path):
    adapter = PillowImageDecoderAdapter()
    file_path = tmp_path / "not_an_image.jpg"
    file_path.write_text("hello")

    with pytest.raises(UnsupportedFormatError):
        adapter.decode(file_path)


def test_decode_raises_for_unsupported_format(tmp_path: Path):
    adapter = PillowImageDecoderAdapter()
    image_path = tmp_path / "image.bmp"

    Image.new("RGB", (800, 800), color="white").save(image_path, format="BMP")

    with pytest.raises(UnsupportedFormatError):
        adapter.decode(image_path)
