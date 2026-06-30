"""
queue_manager.py - Download Queue Manager

Manages a FIFO queue of download tasks executed sequentially.
Each task is processed by a Downloader instance in a background thread.
"""

import threading
from typing import Callable, Optional

from youtube_converter.core.backend import Downloader
from youtube_converter.utils.logger import get_logger

log = get_logger("queue")


class DownloadTask:
    """Represents a single download task in the queue."""

    def __init__(
        self,
        url: str,
        format_type: str,
        video_quality: str = "1080p",
        audio_format: str = "mp3",
        audio_bitrate: str = "192",
        filename_template: str = "%(title)s_%(id)s.%(ext)s",
        video_format: str = "MP4",
        compression_preset: str = "Medium",
    ):
        self.url = url
        self.format_type = format_type
        self.video_quality = video_quality
        self.audio_format = audio_format
        self.audio_bitrate = audio_bitrate
        self.filename_template = filename_template
        self.video_format = video_format
        self.compression_preset = compression_preset
        self.status = "pending"  # pending | downloading | success | error | cancelled

    def quality_label(self) -> str:
        """Human-readable quality description."""
        if self.format_type == "audio":
            label = self.audio_format.upper()
            if self.audio_format not in ("flac", "wav"):
                label += f" {self.audio_bitrate}kbps"
            return label
        return f"{self.video_format} {self.video_quality}"

    def format_label(self) -> str:
        """Short format label for display."""
        return "Audio" if self.format_type == "audio" else self.video_format


class DownloadQueue:
    """
    FIFO queue that processes download tasks one at a time.

    Callbacks:
        on_task_start(task, index): Called when a task begins downloading.
        on_task_complete(task, index, result): Called when a task finishes.
        on_queue_empty(): Called when all tasks are done.
        on_progress(percent): Forwarded from Downloader.
        on_status(message): Forwarded from Downloader.
    """

    def __init__(
        self,
        output_dir: str,
        on_task_start: Optional[Callable] = None,
        on_task_complete: Optional[Callable] = None,
        on_queue_empty: Optional[Callable] = None,
        on_progress: Optional[Callable] = None,
        on_status: Optional[Callable] = None,
    ):
        self._queue: list[DownloadTask] = []
        self._output_dir = output_dir
        self._running = False
        self._worker_thread: threading.Thread | None = None
        self._current_index: int = -1
        self._current_downloader: Downloader | None = None
        self._lock = threading.Lock()  # Thread safety for _running and _current_downloader

        # Callbacks
        self._on_task_start = on_task_start or (lambda t, i: None)
        self._on_task_complete = on_task_complete or (lambda t, i, r: None)
        self._on_queue_empty = on_queue_empty or (lambda: None)
        self._on_progress = on_progress or (lambda p: None)
        self._on_status = on_status or (lambda m: None)

    @property
    def output_dir(self) -> str:
        return self._output_dir

    @output_dir.setter
    def output_dir(self, value: str):
        self._output_dir = value

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def task_count(self) -> int:
        return len(self._queue)

    @property
    def pending_count(self) -> int:
        return sum(1 for t in self._queue if t.status == "pending")

    def add(self, task: DownloadTask) -> int:
        """Add a task to the queue. Returns its index."""
        self._queue.append(task)
        index = len(self._queue) - 1
        log.info(f"Task added to queue [{index}]: {task.url} ({task.format_label()})")
        return index

    def remove(self, index: int):
        """Remove a pending task by index."""
        if 0 <= index < len(self._queue):
            task = self._queue[index]
            if task.status == "pending":
                self._queue.pop(index)
                log.info(f"Task removed from queue [{index}]")

    def clear_pending(self):
        """Remove all pending tasks (keep completed/errored)."""
        self._queue = [t for t in self._queue if t.status != "pending"]
        log.info("Pending tasks cleared")

    def get_tasks(self) -> list[DownloadTask]:
        """Return a copy of all tasks."""
        return self._queue.copy()

    def start(self):
        """Start processing the queue sequentially."""
        if self._running:
            return

        pending = [t for t in self._queue if t.status == "pending"]
        if not pending:
            return

        self._running = True
        self._worker_thread = threading.Thread(
            target=self._process_queue, daemon=True
        )
        self._worker_thread.start()
        log.info(f"Queue started with {len(pending)} pending tasks")

    def stop(self):
        """Stop the queue and cancel the current download immediately."""
        with self._lock:
            self._running = False
            if self._current_downloader:
                self._current_downloader.cancel()
        log.info("Queue stop requested")

    def _process_queue(self):
        """Worker thread: process tasks one by one."""
        for i, task in enumerate(self._queue):
            if not self._running:
                break
            if task.status != "pending":
                continue

            self._current_index = i
            task.status = "downloading"
            self._on_task_start(task, i)

            with self._lock:
                self._current_downloader = Downloader(
                    progress_callback=self._on_progress,
                    status_callback=self._on_status,
                    output_dir=self._output_dir,
                )

            result = self._current_downloader.download_video(
                task.url,
                task.format_type,
                task.video_quality,
                task.audio_format,
                task.audio_bitrate,
                task.filename_template,
                task.video_format,
                task.compression_preset,
            )

            task.status = "success" if result["success"] else "error"
            self._on_task_complete(task, i, result)

        self._running = False
        self._current_index = -1
        self._current_downloader = None
        self._on_queue_empty()
        log.info("Queue processing finished")
