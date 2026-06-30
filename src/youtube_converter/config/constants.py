"""
constants.py - Shared constants for YouTube Converter

Centralizes all constants used across multiple modules to avoid duplication.
"""

# Video and audio formats
VIDEO_FORMATS = ["MP4", "MKV", "WEBM", "AVI", "MOV"]
COMPRESSION_PRESETS = ["High", "Medium", "Low"]
DEVICE_PROFILES = ["iPhone", "Android", "TV", "Web", "Custom"]

# Filename templates for yt-dlp
FILENAME_TEMPLATES = {
    "Titre": "%(title)s.%(ext)s",
    "Titre + ID": "%(title)s_%(id)s.%(ext)s",
    "Chaîne - Titre": "%(uploader)s - %(title)s.%(ext)s",
    "Date + Titre": "%(upload_date)s_%(title)s.%(ext)s",
}

# Status colors for task cards
STATUS_COLORS = {
    "pending": "#6B7280",
    "downloading": "#F59E0B",
    "completed": "#10B981",
    "error": "#EF4444"
}
