from __future__ import annotations

from pathlib import Path

from safeid.core.domain.errors import ExportFailedError, OutputAlreadyExistsError
from safeid.core.ports.filesystem import FileSystemPort

class LocalFileSystemAdapter(FileSystemPort):
    """Local filesystem adapter for exporting generated files"""
    
    def exists(self, path: Path) -> bool:
        return path.exists()
    
    def write_new_bytes(self, path: Path, data: bytes) -> None:
        """ Write bytes to a new file, failing if it already exists."""
        if path.exists():
            raise OutputAlreadyExistsError.for_path(path)
        
        try:
            with path.open("xb") as file_obj:
                file_obj.write(data)
        except FileExistsError as exc:
            raise OutputAlreadyExistsError.for_path(path) from exc
        except OSError as exc:
            raise ExportFailedError.for_path(path, detail=str(exc)) from exc