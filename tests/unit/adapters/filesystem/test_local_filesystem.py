from pathlib import Path

import pytest

from safeid.adapters.filesystem.local_filesystem import LocalFileSystemAdapter
from safeid.core.domain.errors import OutputAlreadyExistsError


def test_exists_returns_false_for_missing_file(tmp_path: Path):
    adapter = LocalFileSystemAdapter()
    target = tmp_path / "missing.pdf"

    assert adapter.exists(target) is False


def test_write_new_bytes_creates_file(tmp_path: Path):
    adapter = LocalFileSystemAdapter()
    target = tmp_path / "output.pdf"
    payload = b"%PDF-fake"

    adapter.write_new_bytes(path=target, data=payload)

    assert target.exists()
    assert target.read_bytes() == payload


def test_write_new_bytes_raises_if_file_exists(tmp_path: Path):
    adapter = LocalFileSystemAdapter()
    target = tmp_path / "output.pdf"

    target.write_bytes(b"existing")

    with pytest.raises(OutputAlreadyExistsError):
        adapter.write_new_bytes(target, b"PDF-new")


def test_exists_returns_true_for_existing_file(tmp_path: Path):
    adapter = LocalFileSystemAdapter()
    target = tmp_path / "output.pdf"
    target.write_bytes(b"existing")

    assert adapter.exists(target)
