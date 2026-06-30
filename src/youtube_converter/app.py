"""
app.py - Application GUI (pywebview HTML/CSS/JS frontend)

Renders the Terminal Neon Mauve UI with web technologies while reusing the
business logic (Downloader, DownloadQueue, DownloadHistory, i18n) unchanged.

Launch:
    python -m youtube_converter        (after `pip install -e .`)

The Python <-> JS bridge:
- JS calls Python via `window.pywebview.api.<method>(...)` (returns a Promise).
- Python pushes live updates to JS via `window.evaluate_js(window.onPush(...))`.
"""

import json
import os
import threading

import webview

from youtube_converter.core.backend import Downloader
from youtube_converter.core.queue_manager import DownloadQueue, DownloadTask
from youtube_converter.core.history import DownloadHistory
from youtube_converter.config.settings import load_settings, save_settings
from youtube_converter.config.theme import COLORS
from youtube_converter.config.constants import DEVICE_PROFILES
from youtube_converter.config.paths import resource_path
from youtube_converter.utils.i18n import set_language, load_translations

WEB_DIR = resource_path("web")


def _task_to_dict(task: DownloadTask) -> dict:
    """Serialize a DownloadTask for the frontend."""
    return {
        "url": task.url,
        "format_type": task.format_type,
        "quality": task.quality_label(),
        "status": task.status,
    }


class Api:
    """Bridge object exposed to JavaScript as `window.pywebview.api`."""

    def __init__(self):
        self._window = None
        self._settings = load_settings()
        set_language(self._settings.get("language", "fr"))
        self.output_dir = self._settings["output_dir"]
        self._history = DownloadHistory(max_entries=self._settings.get("max_history", 50))
        self._queue = DownloadQueue(
            output_dir=self.output_dir,
            on_task_start=lambda t, i: self._push("task_start", {"index": i, "task": _task_to_dict(t)}),
            on_task_complete=self._on_task_complete,
            on_queue_empty=lambda: self._push("queue_empty", {}),
            on_progress=lambda p: self._push("progress", {"percent": round(p, 1)}),
            on_status=lambda m: self._push("status", {"message": m}),
        )

    # ---- window wiring -------------------------------------------------
    def set_window(self, window):
        self._window = window

    def _push(self, event: str, data: dict):
        """Send an event to the frontend (safe to call from worker threads)."""
        if not self._window:
            return
        payload = json.dumps(data)
        try:
            self._window.evaluate_js(f"window.onPush({json.dumps(event)}, {payload})")
        except Exception:
            pass  # window closed mid-update

    def _on_task_complete(self, task: DownloadTask, index: int, result: dict):
        filepath = result.get("filepath", "")
        title = filepath.split(os.sep)[-1] if filepath else task.url
        self._history.add_entry(
            url=task.url,
            title=title,
            format_type=task.format_type,
            quality=task.quality_label(),
            filepath=filepath,
            status=task.status,
            error_message=result.get("message", "") if not result["success"] else "",
        )
        self._push("task_complete", {
            "index": index,
            "task": _task_to_dict(task),
            "success": result["success"],
            "message": result.get("message", ""),
            "filepath": filepath,
        })

    # ---- methods callable from JS --------------------------------------
    def get_config(self) -> dict:
        """Initial state for the frontend."""
        lang = self._settings.get("language", "fr")
        return {
            "colors": COLORS,
            "output_dir": self.output_dir,
            "ffmpeg_ok": Downloader.check_ffmpeg(),
            "language": lang,
            "translations": load_translations(lang),
            "profiles": DEVICE_PROFILES,
            "defaults": {
                "video_quality": self._settings.get("video_quality", "1080p"),
                "video_format": self._settings.get("video_format", "MP4"),
                "audio_format": self._settings.get("audio_format", "mp3"),
                "audio_bitrate": self._settings.get("audio_bitrate", "192"),
                "compression_preset": self._settings.get("compression_preset", "Medium"),
                "compression_enabled": self._settings.get("compression_enabled", False),
            },
            "history": self._history.get_entries()[:30],
        }

    def set_language(self, lang: str) -> dict:
        """Persist and apply a new language; return its translation dict."""
        self._settings["language"] = lang
        save_settings(self._settings)
        set_language(lang)
        return load_translations(lang)

    def save_pref(self, key: str, value) -> bool:
        """Persist a single user preference."""
        self._settings[key] = value
        save_settings(self._settings)
        return True

    def apply_profile(self, name: str) -> dict:
        """Return the format/quality/compression for a device profile."""
        if name == "Custom":
            return {}
        return Downloader.apply_profile(name)

    def export_history_csv(self) -> str:
        """Open a save dialog and export the history to CSV. Returns the path."""
        result = self._window.create_file_dialog(
            webview.SAVE_DIALOG, save_filename="historique_youtube.csv",
            file_types=("CSV (*.csv)",),
        )
        if not result:
            return ""
        path = result if isinstance(result, str) else result[0]
        self._history.export_csv(path)
        return path

    def clear_history(self) -> list:
        self._history.clear()
        return []

    def validate_url(self, url: str) -> bool:
        return Downloader.validate_url(url or "")

    def browse_folder(self) -> str:
        result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        if result:
            folder = result[0]
            self.output_dir = folder
            self._queue.output_dir = folder
            self._settings["output_dir"] = folder
            save_settings(self._settings)
            return folder
        return self.output_dir

    def add_task(self, payload: dict) -> list:
        compression = payload.get("compression_preset") if payload.get("compression_enabled") else None
        task = DownloadTask(
            url=payload["url"],
            format_type=payload["format_type"],
            video_quality=payload.get("video_quality", "1080p"),
            audio_format=payload.get("audio_format", "mp3"),
            audio_bitrate=payload.get("audio_bitrate", "192"),
            filename_template=payload.get("filename_template", "%(title)s_%(id)s.%(ext)s"),
            video_format=payload.get("video_format", "MP4"),
            compression_preset=compression,
        )
        self._queue.add(task)
        return self.get_queue()

    def remove_task(self, index: int) -> list:
        self._queue.remove(index)
        return self.get_queue()

    def clear_queue(self) -> list:
        self._queue.clear_pending()
        return self.get_queue()

    def get_queue(self) -> list:
        return [_task_to_dict(t) for t in self._queue.get_tasks()
                if t.status in ("pending", "downloading")]

    def start_queue(self) -> bool:
        if self._queue.is_running or self._queue.pending_count == 0:
            return False
        self._queue.start()
        return True

    def stop_queue(self) -> bool:
        self._queue.stop()
        return True

    def get_history(self) -> list:
        return self._history.get_entries()[:30]

    def open_folder(self):
        threading.Thread(target=lambda: os.startfile(self.output_dir), daemon=True).start()

    def play_file(self, path: str) -> bool:
        if path and os.path.exists(path):
            threading.Thread(target=lambda: os.startfile(path), daemon=True).start()
            return True
        return False


def main():
    api = Api()
    window = webview.create_window(
        title="YouTube Converter — Web UI (prototype)",
        url=os.path.join(WEB_DIR, "index.html"),
        js_api=api,
        width=1080,
        height=860,
        min_size=(940, 760),
        background_color="#0B0E14",
    )
    api.set_window(window)
    webview.start()


if __name__ == "__main__":
    main()
