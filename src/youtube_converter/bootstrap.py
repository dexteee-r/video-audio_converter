"""
bootstrap.py - Make an externally-updated yt-dlp win over the bundled one.

Deliberately dependency-free (stdlib only) and called at the very TOP of the
package ``__init__``, BEFORE anything imports yt_dlp. That timing is essential:
`python -m youtube_converter` (and the frozen exe) imports this package before
running __main__, so the meta-path override must be installed here to take
effect — source and frozen alike.

The directory below must match config.paths.ytdlp_dir().
"""

import importlib.machinery
import os
import sys

_APP_NAME = "YouTubeConverter"


def _ytdlp_dir() -> str:
    appdata = os.environ.get("APPDATA")
    base = os.path.join(appdata, _APP_NAME) if appdata else \
        os.path.join(os.path.expanduser("~"), ".youtubeconverter")
    return os.path.join(base, "yt-dlp")


class _ExternalYtdlpFinder:
    """Resolve the top-level ``yt_dlp`` package from the external dir first."""

    def __init__(self, directory: str):
        self._dir = directory

    def find_spec(self, fullname, path=None, target=None):
        if fullname == "yt_dlp":
            return importlib.machinery.PathFinder.find_spec(fullname, [self._dir])
        return None


def bootstrap_ytdlp_path():
    """
    If an externally-updated yt_dlp exists, make it take precedence over the
    bundled/pip one. No-op if absent or yt_dlp is already imported. Never raises.
    """
    try:
        d = _ytdlp_dir()
        if os.path.exists(os.path.join(d, "yt_dlp", "__init__.py")) and "yt_dlp" not in sys.modules:
            sys.meta_path.insert(0, _ExternalYtdlpFinder(d))
    except Exception:
        pass  # startup must never fail because of this
