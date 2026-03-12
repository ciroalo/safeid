from __future__ import annotations

from pathlib import Path
from typing import Protocol

from safeid.core.domain.models import ImageAsset


class ImageDecoderPort(Protocol):
    """Port for loading and normalizing user-selected images.

    This port is implemented by an adapter.
    The core relies on this to:
        - accept only supported formats (JPG, PNG for MVP),
        - enforce minimum dimensions,
        - normalize orientations if necessary
        - return normalized pixel data without EXIF metadata
    """

    def decode(self, path: Path, *, min_side_px: int = 600) -> ImageAsset:
        """Decode and normalize an image file.

        Args:
            path: Path to a user-selected image.
            min_side_px: Minimum allowed size for both width and height

        Returns:
            ImageAsset: normalized pixel data and dimensions.

        Raises:
                UnsupportedFormatError: If file format is not supported (JPG/PNG)
                ImageTooSmallError: If width or height is less than min_side_px
                InvalidInputError: For other invalid inputs or decode failures
        """
