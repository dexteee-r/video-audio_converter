"""Tests for DownloadHistory (isolated from %APPDATA% via monkeypatch)."""

import pytest

from youtube_converter.core import history as history_mod
from youtube_converter.core.history import DownloadHistory


@pytest.fixture
def temp_history(tmp_path, monkeypatch):
    """Point the history file at a temp location and return a fresh instance."""
    monkeypatch.setattr(history_mod, "HISTORY_FILE", str(tmp_path / "hist.json"))
    return DownloadHistory(max_entries=3)


def _add(h, title, status="success"):
    h.add_entry(url="u", title=title, format_type="mp4",
                quality="MP4 1080p", filepath="", status=status)


def test_add_and_get_most_recent_first(temp_history):
    _add(temp_history, "first")
    _add(temp_history, "second")
    titles = [e["title"] for e in temp_history.get_entries()]
    assert titles == ["second", "first"]


def test_trim_to_max_entries(temp_history):
    for i in range(5):
        _add(temp_history, f"item{i}")
    entries = temp_history.get_entries()
    assert len(entries) == 3
    assert entries[0]["title"] == "item4"  # newest kept


def test_persistence_reload(tmp_path, monkeypatch):
    monkeypatch.setattr(history_mod, "HISTORY_FILE", str(tmp_path / "hist.json"))
    h1 = DownloadHistory(max_entries=10)
    _add(h1, "persisted")
    # New instance loads from the same file.
    h2 = DownloadHistory(max_entries=10)
    assert any(e["title"] == "persisted" for e in h2.get_entries())


def test_clear(temp_history):
    _add(temp_history, "x")
    temp_history.clear()
    assert temp_history.get_entries() == []


def test_export_csv(temp_history, tmp_path):
    _add(temp_history, "exported")
    out = tmp_path / "out.csv"
    temp_history.export_csv(str(out))
    content = out.read_text(encoding="utf-8-sig")
    assert "title" in content  # header
    assert "exported" in content
