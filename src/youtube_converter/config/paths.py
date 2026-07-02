"""
paths.py - Centralized path resolution

Resolves two kinds of paths reliably, both when running from source and when
frozen into a PyInstaller .exe:

- resource_path(): read-only bundled assets (translations, etc.).
- user_data_dir(): writable per-user data (settings, history, logs) stored in
  %APPDATA%/YouTubeConverter on Windows.
"""

import os
import sys

APP_NAME = "YouTubeConverter"


def _is_frozen() -> bool:
    """True when running inside a PyInstaller bundle."""
    return getattr(sys, "frozen", False)


def resource_path(relative: str) -> str:
    """
    Absolute path to a bundled read-only resource under the package's
    ``resources/`` directory (e.g. "web", "translations/fr.json").

    Resources live inside the package at ``youtube_converter/resources``. When
    frozen, PyInstaller bundles them to ``_MEIPASS/youtube_converter/resources``.

    Args:
        relative: Path relative to the resources root.

    Returns:
        Absolute path to the resource.
    """
    if _is_frozen():
        base = os.path.join(sys._MEIPASS, "youtube_converter", "resources")  # type: ignore[attr-defined]
    else:
        # paths.py lives in youtube_converter/config/ -> package root is one up.
        package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        base = os.path.join(package_root, "resources")
    return os.path.join(base, relative)


def user_data_dir() -> str:
    """
    Writable per-user data directory, created if missing.

    Uses %APPDATA%/YouTubeConverter on Windows, falling back to ~/.youtubeconverter
    on other platforms.
    """
    appdata = os.environ.get("APPDATA")
    if appdata:
        base = os.path.join(appdata, APP_NAME)
    else:
        base = os.path.join(os.path.expanduser("~"), ".youtubeconverter")
    os.makedirs(base, exist_ok=True)
    return base


def user_data_file(filename: str) -> str:
    """Absolute path to a file inside the writable user data directory."""
    return os.path.join(user_data_dir(), filename)


def log_dir() -> str:
    """Writable directory for log files, created if missing."""
    path = os.path.join(user_data_dir(), "logs")
    os.makedirs(path, exist_ok=True)
    return path


def ytdlp_dir() -> str:
    """
    Writable directory holding an externally-updatable copy of yt-dlp.

    Kept outside the (read-only, possibly frozen) bundle so the app can refresh
    yt-dlp over time. When it contains a ``yt_dlp`` package, it takes precedence
    over the bundled one (see core.updater.bootstrap_ytdlp_path).
    """
    path = os.path.join(user_data_dir(), "yt-dlp")
    os.makedirs(path, exist_ok=True)
    return path
