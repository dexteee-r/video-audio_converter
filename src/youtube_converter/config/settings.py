"""
settings.py - User Settings Persistence

Saves and loads user preferences (output folder, etc.) to a JSON file
located next to the application executable or script.
"""

import json
import os

from youtube_converter.config.paths import user_data_file
from youtube_converter.utils.logger import get_logger

log = get_logger("settings")

# Settings file stored in the writable per-user data directory (%APPDATA%)
SETTINGS_FILE = user_data_file("settings.json")

# Default settings
DEFAULTS = {
    "output_dir": os.path.join(os.path.expanduser("~"), "Downloads", "YouTube_Downloads"),
    "video_quality": "1080p",
    "audio_format": "mp3",
    "audio_bitrate": "192",
    "max_history": 50,
    "filename_template": "%(title)s_%(id)s.%(ext)s",
    "language": "fr",  # fr | en | es | de
    "video_format": "MP4",  # MP4 | MKV | WEBM | AVI | MOV
    "compression_preset": "Medium",  # High | Medium | Low (only when enabled)
    "compression_enabled": False,    # Re-encode off by default (direct download)
}


def load_settings() -> dict:
    """
    Load user settings from the JSON file.
    Returns defaults if the file does not exist or is corrupted.
    """
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULTS.copy()

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Merge with defaults to handle missing keys after updates
        merged = DEFAULTS.copy()
        merged.update(data)
        return merged
    except (json.JSONDecodeError, OSError) as e:
        log.warning(f"Failed to load settings: {e}. Using defaults.")
        return DEFAULTS.copy()


def save_settings(settings: dict):
    """
    Save user settings to the JSON file.

    Args:
        settings: Dictionary of settings to persist.
    """
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except OSError as e:
        log.error(f"Failed to save settings to {SETTINGS_FILE}: {e}")
