"""Hardlinks are one on-disk file, so they must not inflate duplicate results."""
import os

import pytest

from panther.services.duplicate_detector import DuplicateDetector
from panther.services.file_scanner import FileScanner


def _write(root, rel, data):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(data)
    return path


def _link_or_skip(source, target):
    try:
        os.link(source, target)
    except (OSError, NotImplementedError, AttributeError):
        pytest.skip("hardlinks are not supported on this filesystem")


def test_scanner_records_filesystem_identity(tmp_path):
    _write(tmp_path, "a.bin", b"x" * 10)
    record = FileScanner().scan_directory(str(tmp_path))[0]
    assert "device" in record and "inode" in record


def test_hardlinks_alone_are_not_duplicates(tmp_path):
    original = _write(tmp_path, "a/report.bin", b"x" * 5000)
    _link_or_skip(original, tmp_path / "a" / "hardlink.bin")
    files = FileScanner().scan_directory(str(tmp_path))
    assert len(files) == 2
    assert DuplicateDetector().find_duplicates(files) == []


def test_hardlink_does_not_inflate_real_duplicate_savings(tmp_path):
    original = _write(tmp_path, "a/report.bin", b"x" * 5000)
    _write(tmp_path, "b/copy.bin", b"x" * 5000)
    _link_or_skip(original, tmp_path / "a" / "hardlink.bin")
    groups = DuplicateDetector().find_duplicates(
        FileScanner().scan_directory(str(tmp_path))
    )
    assert len(groups) == 1
    assert groups[0]["count"] == 2
    assert groups[0]["potential_savings"] == 5000


def test_records_without_identity_still_group_by_content(tmp_path):
    """Records from other sources may lack device/inode; they must still work."""
    a = _write(tmp_path, "a.bin", b"y" * 100)
    b = _write(tmp_path, "b.bin", b"y" * 100)
    records = [{"path": a, "size": 100}, {"path": b, "size": 100}]
    groups = DuplicateDetector().find_duplicates(records)
    assert len(groups) == 1 and groups[0]["count"] == 2


def test_detector_does_not_mutate_input_records(tmp_path):
    a = _write(tmp_path, "a.bin", b"z" * 50)
    b = _write(tmp_path, "b.bin", b"z" * 50)
    records = [{"path": a, "size": 50}, {"path": b, "size": 50}]
    DuplicateDetector().find_duplicates(records)
    assert all("hash" not in record for record in records)
