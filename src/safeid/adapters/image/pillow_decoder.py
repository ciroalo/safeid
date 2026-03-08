from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from safeid.core.domain.errors import (
    ImageTooSmallError, 
    InvalidInputError,
    UnsupportedFormatError
)
from safeid.core.domain.models import ImageAsset, SizePx
from safeid.core.ports.image_decoder import ImageDecoderPort


class PillowImageDecoderAdapter(ImageDecoderPort):
    """Decode and normalize user-selected images using Pillow."""
    
    _SUPPORTED_FORMATS = {"JPEG", "PNG"}
    
    def decode(
        self, 
        path: Path,
        *,
        min_side_px: int = 600
    ) -> ImageAsset:
        
        try:
            with Image.open(path) as img:
                image_format = img.format
                if image_format not in self._SUPPORTED_FORMATS:
                    raise UnsupportedFormatError
                
                normalized = ImageOps.exif_transpose(img)
                
                # MVP choice: normalize everything to RGB
                # This keeps the renderer path simpler and avoids carrying alpha complexity
                if normalized.mode != "RGB":
                    normalized = normalized.convert("RGB")
                    
                width, height = normalized.size
                if width < min_side_px or height < min_side_px:
                    raise ImageTooSmallError.for_dims(
                        path=path,
                        min_px=min_side_px,
                        width_px=width,
                        height_px=height
                    )
                
                pixel_bytes = normalized.tobytes()
                
                return ImageAsset(
                    size_px=SizePx(width=width, height=height),
                    mode=normalized.mode,
                    pixel_bytes=pixel_bytes
                )
        
        except UnsupportedFormatError:
            raise
        except ImageTooSmallError:
            raise
        except UnidentifiedImageError as exc:
            raise UnsupportedFormatError.for_path(path) from exc
        except OSError as exc:
            raise InvalidInputError(
                user_message="Failed to read the selected image",
                detail=f"{path}: {exc}"
            ) from exc