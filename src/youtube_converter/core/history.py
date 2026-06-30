"""
history.py - Download History Persistence

Stores the last N downloads in a JSON file with status tracking.
Supports re-download and CSV export.
"""

import csv
import json
import os
from datetime import datetime

from youtube_converter.config.paths import user_data_file
from youtube_converter.utils.logger import get_logger

log = get_logger("history")

# Store history in the writable per-user data directory (%APPDATA%)
HISTORY_FILE = user_data_file("download_history.json")
DEFAULT_MAX_ENTRIES = 50


class DownloadHistory:
    """Persists download history in a JSON file."""

    def __init__(self, max_entries: int = DEFAULT_MAX_ENTRIES):
        self._max_entries = max_entries
        self._entries: list[dict] = []
        self._load()

    def _load(self):
        """Load history from disk."""
        if not os.path.exists(HISTORY_FILE):
            self._entries = []
            return
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                self._entries = json.load(f)
        except (json.JSONDecodeError, OSError):
            log.warning("Could not load history file, starting fresh")
            self._entries = []

    def _save(self):
        """Persist history to disk."""
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self._entries, f, indent=2, ensure_ascii=False)
        except OSError:
            log.error("Could not save history file")

    def add_entry(
        self,
        url: str,
        title: str,
        format_type: str,
        quality: str,
        filepath: str,
        status: str,
        error_message: str = "",
    ):
        """
        Add a download entry to the history.

        Args:
            url: YouTube URL.
            title: Video title.
            format_type: "mp4" or "audio".
            quality: Quality description (e.g. "1080p", "MP3 192kbps").
            filepath: Output file path.
            status: "success", "error", or "cancelled".
            error_message: Error details if status is "error".
        """
        entry = {
            "url": url,
            "title": title,
            "format": format_type,
            "quality": quality,
            "filepath": filepath,
            "status": status,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat(),
        }
        self._entries.insert(0, entry)  # Most recent first

        # Trim to max entries
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[: self._max_entries]

        self._save()
        log.info(f"History entry added: {title} [{status}]")

    def get_entries(self) -> list[dict]:
        """Return all history entries (most recent first)."""
        return self._entries.copy()

    def clear(self):
        """Delete all history."""
        self._entries = []
        self._save()
        log.info("History cleared")

    def export_csv(self, filepath: str):
        """
        Export history to a CSV file.

        Args:
            filepath: Destination path for the CSV file.
        """
        fieldnames = [
            "timestamp", "title", "url", "format", "quality",
            "status", "filepath", "error_message",
        ]
        try:
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
                writer.writeheader()
                for entry in self._entries:
                    writer.writerow(entry)
            log.info(f"History exported to CSV: {filepath}")
        except OSError as e:
            log.error(f"CSV export failed: {e}")
            raise
