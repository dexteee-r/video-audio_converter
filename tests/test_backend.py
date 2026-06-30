"""Tests for the Downloader (URL validation, profiles, sanitization, maps)."""

import pytest

from youtube_converter.core.backend import Downloader


@pytest.mark.parametrize("url", [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "http://youtu.be/dQw4w9WgXcQ",
    "https://vimeo.com/76979871",
    "https://www.tiktok.com/@user/video/123",
])
def test_validate_url_accepts_http(url):
    assert Downloader.validate_url(url) is True


@pytest.mark.parametrize("url", [
    "",
    "   ",
    "not a url",
    "ftp://example.com/file",
    "youtube.com/watch?v=x",  # missing scheme
])
def test_validate_url_rejects_invalid(url):
    assert Downloader.validate_url(url) is False


def test_validate_url_strips_whitespace():
    assert Downloader.validate_url("  https://youtu.be/x  ") is True


def test_apply_profile_known():
    p = Downloader.apply_profile("iPhone")
    assert p["video_format"] == "MP4"
    assert p["video_quality"] == "1080p"
    assert p["compression"] == "Medium"


def test_apply_profile_unknown_returns_defaults():
    p = Downloader.apply_profile("DoesNotExist")
    assert p["video_format"] == "MP4"
    assert "video_quality" in p and "compression" in p


def test_quality_map_values():
    assert Downloader.QUALITY_MAP["1080p"] == 1080
    assert Downloader.QUALITY_MAP["2160p (4K)"] == 2160


def test_sanitize_filename_removes_invalid_chars():
    d = Downloader()
    out = d._sanitize_filename('a<b>c:"d/e\\f|g?h*i')
    for bad in '<>:"/\\|?*':
        assert bad not in out


def test_sanitize_filename_trims_and_limits_length():
    d = Downloader()
    assert d._sanitize_filename("  . spaced .  ") == "spaced"
    assert len(d._sanitize_filename("x" * 500)) <= 200
