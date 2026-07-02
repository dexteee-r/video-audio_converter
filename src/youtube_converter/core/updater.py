"""
updater.py - Keep yt-dlp fresh.

yt-dlp must stay recent or sites (YouTube, TikTok, ...) throttle or reject
downloads. When frozen into a PyInstaller .exe the bundled ``yt_dlp`` cannot be
pip-updated, so we keep an *external, writable* copy under %APPDATA% and make it
take precedence over the bundled/pip one. Updates are downloaded in the
background and become active on the next launch.

The meta-path override that makes an external copy win lives in
youtube_converter/bootstrap.py (it must run before the first ``import yt_dlp``).
This module only handles the background version check + download.
"""

import io
import json
import os
import shutil
import threading
import urllib.request
import zipfile

from youtube_converter.config.paths import ytdlp_dir
from youtube_converter.utils.logger import get_logger

log = get_logger("updater")

_PYPI_URL = "https://pypi.org/pypi/yt-dlp/json"
_TIMEOUT = 15
_UA = {"User-Agent": "YouTubeConverter"}


def _version_tuple(v: str):
    """Turn a date-based version like '2026.06.09' into a comparable int tuple."""
    parts = []
    for chunk in str(v).split("."):
        digits = "".join(ch for ch in chunk if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def _current_version() -> str:
    try:
        import yt_dlp
        return getattr(yt_dlp.version, "__version__", "0")
    except Exception:
        return "0"


def _fetch_latest():
    """Return (version, wheel_url) for the latest yt-dlp release on PyPI."""
    req = urllib.request.Request(_PYPI_URL, headers=_UA)
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        data = json.load(resp)
    version = data["info"]["version"]
    wheel_url = None
    for f in data["releases"].get(version, []):
        if f["filename"].endswith("-py3-none-any.whl"):
            wheel_url = f["url"]
            break
    return version, wheel_url


def _download_and_install(wheel_url: str):
    """Download the wheel and extract its yt_dlp/ package into the external dir."""
    d = ytdlp_dir()
    req = urllib.request.Request(wheel_url, headers=_UA)
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        blob = resp.read()

    tmp = os.path.join(d, ".update_tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        for name in zf.namelist():
            if name.startswith("yt_dlp/"):
                zf.extract(name, tmp)

    src = os.path.join(tmp, "yt_dlp")
    if not os.path.isdir(src):
        shutil.rmtree(tmp, ignore_errors=True)
        raise RuntimeError("wheel did not contain a yt_dlp/ package")

    dst = os.path.join(d, "yt_dlp")
    shutil.rmtree(dst, ignore_errors=True)
    shutil.move(src, dst)
    shutil.rmtree(tmp, ignore_errors=True)


def check_and_update_async(on_status):
    """
    Background: compare the installed yt-dlp with the latest PyPI release and
    download it if newer (active on next launch). Never raises.

    on_status(state, current, latest) is called with state in:
        'checking' | 'uptodate' | 'updated' | 'offline'
    """
    def worker():
        current = _current_version()
        on_status("checking", current, None)
        try:
            latest, wheel_url = _fetch_latest()
        except Exception as e:
            log.warning(f"yt-dlp update check failed: {e}")
            on_status("offline", current, None)
            return
        try:
            if wheel_url and _version_tuple(latest) > _version_tuple(current):
                log.info(f"Updating yt-dlp {current} -> {latest}")
                _download_and_install(wheel_url)
                on_status("updated", current, latest)
            else:
                on_status("uptodate", current, None)
        except Exception as e:
            log.warning(f"yt-dlp update failed: {e}")
            on_status("offline", current, None)

    threading.Thread(target=worker, daemon=True).start()
