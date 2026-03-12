from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

# --- Units / Geometry ---


@dataclass(frozen=True)
class SizePx:
    """Pixel dimensions"""

    width: int
    height: int


@dataclass(frozen=True)
class RectPt:
    """Rectangle in PDF points (1 pt = 1/72 inch). Origin is bottom-left in PDF convention"""

    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True)
class PageSpec:
    """Physical page specification"""

    size: Literal["A4"] = "A4"
    margin_mm: float = 19.0


# --- Inputs / Assets ---


@dataclass(frozen=True)
class ImageSource:
    """User selected input image"""

    path: Path


@dataclass(frozen=True)
class ImageAsset:
    """Decoded, normalized image data used by the core.
    Notes:
    - 'pixel_bytes' is raw pixel payload in row-major order.
    - 'mode' examples: 'RGB', 'RGBA'
    - EXIF metadata must not be preserved in this structure.
    """

    size_px: SizePx
    mode: str
    pixel_bytes: bytes


# --- Watermark ---


@dataclass(frozen=True)
class WatermarkSpec:
    """User-configurable and default watermark settings."""

    text: str

    # For MVP is just simple
    font_family: str = "system"
    font_size_pt: float = 14.0

    # Degrees clockwise. Diagonal watermark
    angle_deg: float = 35.0

    # Opacity -> 0.0 (invisible) - 1.0 (solid)
    opacity: float = 0.12

    # Distance between repeated watermark baselines (in points)
    line_spacing_pt: float = 72.0

    # Distance between words in a repeated line
    word_spacing: int = 8


# --- Layout ---


@dataclass(frozen=True)
class LayoutPolicy:
    """Rules controlling how images are arranged on the page"""

    allow_rotation: bool = True
    allow_scaling: bool = True
    min_gap_mm: float = 12.0
    stack_direction: Literal["vertical"] = "vertical"


@dataclass(frozen=True)
class PlacedImage:
    """Placement of a single image on the PDF page."""

    source_index: int  # index into images list (0 or 1)
    rect: RectPt
    rotate_90: bool = False  # True if necessary to rotate


@dataclass(frozen=True)
class LayoutPlan:
    """Computed placement plan for the page"""

    page: PageSpec
    placed_images: Sequence[PlacedImage]

    # Union bounding box of the placed images (useful for watermark area)
    photo_area: RectPt


# --- Export ---


@dataclass(frozen=True)
class ExportSpec:
    """Rules for where/how to export output."""

    output_dir: Path
    output_filename: str  # follow <first_file>_<recipient>_watermarked.pdf


# --- Use case I/0 ---


@dataclass(frozen=True)
class CreateWatermarkedPdfRequest:
    """Input to the main MVP use-case"""

    images: Sequence[ImageSource]  # length 1 or 2
    recipient: str
    watermark: WatermarkSpec


@dataclass(frozen=True)
class CreateWatermarkedPdfResult:
    """Output of the main MVP use-case"""

    output_path: Path
