"""
YouTube Converter - Modern video/audio downloader

A modern, user-friendly YouTube downloader with support for 1000+ websites.
Features include quality selection, format conversion, download queue, and more.
"""

__version__ = "1.0.0"
__author__ = "YouTube Converter Team"

from youtube_converter.core.backend import Downloader
from youtube_converter.core.queue_manager import DownloadQueue, DownloadTask
from youtube_converter.core.history import DownloadHistory

__all__ = [
    "Downloader",
    "DownloadQueue",
    "DownloadTask",
    "DownloadHistory",
]
