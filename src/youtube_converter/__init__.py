"""
YouTube Converter - Modern video/audio downloader

A modern, user-friendly YouTube downloader with support for 1000+ websites.
Features include quality selection, format conversion, download queue, and more.
"""

__version__ = "1.0.0"
__author__ = "YouTube Converter Team"

# Must run before anything imports yt_dlp: prefer an externally-updated yt-dlp.
from youtube_converter.bootstrap import bootstrap_ytdlp_path as _bootstrap_ytdlp_path
_bootstrap_ytdlp_path()

from youtube_converter.core.backend import Downloader  # noqa: E402 (after bootstrap)
from youtube_converter.core.queue_manager import DownloadQueue, DownloadTask
from youtube_converter.core.history import DownloadHistory

__all__ = [
    "Downloader",
    "DownloadQueue",
    "DownloadTask",
    "DownloadHistory",
]
