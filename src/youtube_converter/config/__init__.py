"""
Config module - Application configuration and constants

Contains settings management and application constants.
"""

from youtube_converter.config.settings import load_settings, save_settings, DEFAULTS
from youtube_converter.config.constants import (
    VIDEO_FORMATS,
    COMPRESSION_PRESETS,
    DEVICE_PROFILES,
    FILENAME_TEMPLATES,
    STATUS_COLORS,
)

__all__ = [
    "load_settings",
    "save_settings",
    "DEFAULTS",
    "VIDEO_FORMATS",
    "COMPRESSION_PRESETS",
    "DEVICE_PROFILES",
    "FILENAME_TEMPLATES",
    "STATUS_COLORS",
]
