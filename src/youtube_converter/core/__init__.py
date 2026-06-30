"""
Core module - Business logic for YouTube downloading

Contains the main download engine, queue manager, and history tracking.
"""

from youtube_converter.core.backend import Downloader
from youtube_converter.core.queue_manager import DownloadQueue, DownloadTask
from youtube_converter.core.history import DownloadHistory

__all__ = [
    "Downloader",
    "DownloadQueue",
    "DownloadTask",
    "DownloadHistory",
]
