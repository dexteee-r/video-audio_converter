"""Tests for DownloadTask labels."""

from youtube_converter.core.queue_manager import DownloadTask


def test_quality_label_audio_lossy():
    t = DownloadTask("u", "audio", audio_format="mp3", audio_bitrate="192")
    assert t.quality_label() == "MP3 192kbps"


def test_quality_label_audio_lossless_has_no_bitrate():
    t = DownloadTask("u", "audio", audio_format="flac", audio_bitrate="320")
    assert t.quality_label() == "FLAC"


def test_quality_label_video():
    t = DownloadTask("u", "mp4", video_format="MKV", video_quality="1440p")
    assert t.quality_label() == "MKV 1440p"


def test_format_label():
    assert DownloadTask("u", "audio").format_label() == "Audio"
    assert DownloadTask("u", "mp4", video_format="WEBM").format_label() == "WEBM"


def test_new_task_is_pending():
    assert DownloadTask("u", "mp4").status == "pending"
