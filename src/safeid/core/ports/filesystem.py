from __future__ import annotations

from pathlib import Path
from typing import Protocol

from safeid.core.domain.errors import ExportFailedError, OutputAlreadyExistsError


class FileSystemPort(Protocol):
    """Port for interactin with local filesystem for export."""
    
    def exists(self, path: Path) -> bool:
        """Returns True if the path already exists"""
        
    def write_new_bytes(self, path: Path, data: bytes) -> None:
        """Write bytes to a new file path
        
        Requirements:
            - Must not overwrite existing files.
            - If the file exists, raise OutputAlreadyExistsError
            - Prefer not to leave partially-written files on failure
            
        Raises:
            OutpuAlreadyExistsError: If path already exists
            ExportFailedError: For any other write error
        """