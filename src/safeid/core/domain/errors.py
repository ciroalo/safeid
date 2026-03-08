from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass(frozen=True, kw_only=True)
class SafeIdError(Exception):
    """Base class for all domain/application errors intended to be shown to the user."""
    user_message: str
    detail: Optional[str] = None
    
    def __str__(self) -> str:
        if self.detail:
            return f"{self.user_message} ({self.detail})"
        return self.user_message
    

# --- Validation / Input errors

@dataclass(frozen=True, kw_only=True)
class InvalidInputError(SafeIdError):
    """Generic invalid input error"""
    
    
@dataclass(frozen=True, kw_only=True)
class InvalidImageCountError(SafeIdError):
    """Raised when user selects an invalid number of images"""
    count: int = 0
    
    @classmethod
    def for_count(cls, count: int) -> "InvalidImageCountError":
        return cls(
            user_message="Please select 1 or 2 images.",
            detail=f"Selected {count}",
            count=count,
        )
        
@dataclass(frozen=True, kw_only=True)
class UnsupportedFormatError(SafeIdError):
    """Raised when an input image format is not supported"""
    path: Optional[Path] = None
    
    @classmethod
    def for_path(cls, path: Path) -> "UnsupportedFormatError":
        return cls(
            user_message="Unsupported file format. Please use JPG or PNG.",
            detail=str(path),
            path=path,
        )
        

@dataclass(frozen=True, kw_only=True)
class ImageTooSmallError(SafeIdError):
    """Raised when an image does not meet minimum dimension requirements"""
    
    path: Optional[Path] = None
    min_px: int = 600
    width_px: Optional[int] = None
    height_px: Optional[int] = None
    
    @classmethod
    def for_dims(cls, path: Path, *, min_px: int, width_px: int, height_px: int) -> "ImageTooSmallError":
        return cls(
            user_message=f"Image is too small. Minimum size is {min_px} px on both sides",
            detail=f"{path} is {width_px}x{height_px}px.",
            path=path,
            min_px=min_px,
            width_px=width_px,
            height_px=height_px,
        )
        
        
@dataclass(frozen=True, kw_only=True)
class LayoutDoesNotFitError(SafeIdError):
    """Raised when images cannot fit on the page under the selected layout policy"""
    
    @classmethod
    def for_policy(cls, *, detail: str) -> "LayoutDoesNotFitError":
        return cls(
            user_message="The selected image do not fit on the page with the current layout settings. Allow scaling to scale down the image.",
            detail=detail
        )

@dataclass(frozen=True, kw_only=True)
class EmptyRecipientError(SafeIdError):
    """Raised when recipient is empty or whitespace."""
    

@dataclass(frozen=True)
class EmptyWatermarkTextError(SafeIdError):
    """Raised when watermark text is empty or whitespace"""
    
    
# --- Export / filesystem related ---

@dataclass(frozen=True)
class OutputAlreadyExistsError(SafeIdError):
    """Raised when output file already exists and overwriting is not allowed."""
    output_path: Path
    
    @classmethod
    def for_path(cls, output_path: Path) -> "OutputAlreadyExistsError":
        return cls(
            user_message="Output file already exits. Please chose another recipient or file",
            detail=str(output_path),
            output_path=output_path,
        )
        

@dataclass(frozen=True, kw_only=True)
class ExportFailedError(SafeIdError):
    """Raised when writing the output file fails for an unexepected reason"""
    output_path: Optional[Path] = None
    
    @classmethod
    def for_path(cls, output_path: Path, *, detail: str) -> "ExportFailedError":
        return cls(
            user_message="Failed to export to PDF.",
            detail=detail,
            output_path=output_path,
        )