"""
backend.py - YouTube Video/Audio Downloader Engine

Uses yt-dlp for reliable downloading and FFmpeg for audio extraction.
Provides thread-safe callbacks for UI progress updates.
"""

import os
import re
import subprocess
import shutil
from pathlib import Path
from typing import Callable, Optional

import yt_dlp

from youtube_converter.utils.logger import get_logger
from youtube_converter.utils.i18n import t

log = get_logger("backend")


class Downloader:
    """
    YouTube video/audio downloader using yt-dlp.
    Handles MP4 (video) and MP3 (audio-only) formats.
    Thread-safe progress reporting via callbacks.
    """

    # Default output directory
    DEFAULT_OUTPUT_DIR = os.path.join(
        os.path.expanduser("~"), "Downloads", "YouTube_Downloads"
    )

    def __init__(
        self,
        progress_callback: Optional[Callable[[float], None]] = None,
        status_callback: Optional[Callable[[str], None]] = None,
        output_dir: Optional[str] = None,
    ):
        """
        Initialize the downloader with optional callbacks.

        Args:
            progress_callback: Function to update progress bar (0-100).
            status_callback: Function to update status text.
            output_dir: Custom output directory. Defaults to ~/Downloads/YouTube_Downloads/.
        """
        self.progress_callback = progress_callback or (lambda x: None)
        self.status_callback = status_callback or (lambda x: None)
        self.output_dir = output_dir or self.DEFAULT_OUTPUT_DIR
        self._cancelled = False

    def cancel(self):
        """Request cancellation of the current download."""
        self._cancelled = True

    @staticmethod
    def check_ffmpeg() -> bool:
        """Verify FFmpeg is installed and accessible in PATH."""
        return shutil.which("ffmpeg") is not None

    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Check if the given URL is a valid video/audio URL.

        Accepts any http(s) URL — yt-dlp supports 1000+ sites natively
        (YouTube, TikTok, Instagram, Vimeo, Dailymotion, Twitch, etc.).
        """
        return bool(re.match(r"^https?://\S+", url.strip()))

    def _progress_hook(self, d: dict):
        """
        yt-dlp progress hook callback.
        Extracts download percentage and forwards it to the UI callback.
        """
        if self._cancelled:
            raise yt_dlp.utils.DownloadCancelled(t("backend.download_cancelled"))

        if d["status"] == "downloading":
            # Extract percentage from yt-dlp progress data
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)

            if total and total > 0:
                percent = (downloaded / total) * 100
                self.progress_callback(min(percent, 100.0))

            # Build status message with speed and ETA
            speed = d.get("_speed_str", "N/A")
            eta = d.get("_eta_str", "N/A")
            percent_str = d.get("_percent_str", "0%").strip()
            self.status_callback(
                t("backend.download_status", percent=percent_str, speed=speed, eta=eta)
            )

        elif d["status"] == "finished":
            self.progress_callback(100.0)
            self.status_callback(t("backend.download_finished"))

    def _sanitize_filename(self, title: str) -> str:
        """Remove or replace characters that are invalid in Windows filenames."""
        # Replace invalid chars with underscore
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", title)
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(" .")
        # Limit length to avoid path issues on Windows
        return sanitized[:200]

    # Quality mapping: UI label → yt-dlp height value
    QUALITY_MAP = {
        "360p": 360,
        "480p": 480,
        "720p": 720,
        "1080p": 1080,
        "1440p": 1440,
        "2160p (4K)": 2160,
    }

    # Audio codecs: UI label → yt-dlp codec name
    AUDIO_CODEC_MAP = {
        "mp3": "mp3",
        "m4a": "m4a",
        "flac": "flac",
        "wav": "wav",
        "ogg": "vorbis",
    }

    # Lossless formats (no bitrate setting)
    LOSSLESS_FORMATS = {"flac", "wav"}

    # Video container formats
    VIDEO_FORMATS = {
        "MP4": {"ext": "mp4", "merge_format": "mp4"},
        "MKV": {"ext": "mkv", "merge_format": "mkv"},
        "WEBM": {"ext": "webm", "merge_format": "webm"},
        "AVI": {"ext": "avi", "merge_format": "avi"},
        "MOV": {"ext": "mov", "merge_format": "mov"},
    }

    # Compression presets (CRF values for x264/x265)
    # Lower CRF = better quality, higher file size
    COMPRESSION_PRESETS = {
        "High": 18,    # High quality, large file
        "Medium": 23,  # Balanced (default x264 CRF)
        "Low": 28,     # Lower quality, small file
    }

    # Pre-configured profiles
    DEVICE_PROFILES = {
        "iPhone": {
            "video_format": "MP4",
            "video_quality": "1080p",
            "compression": "Medium",
            "description": "Optimized for iPhone/iPad"
        },
        "Android": {
            "video_format": "MP4",
            "video_quality": "1080p",
            "compression": "Medium",
            "description": "Optimized for Android devices"
        },
        "TV": {
            "video_format": "MP4",
            "video_quality": "2160p (4K)",
            "compression": "High",
            "description": "Optimized for Smart TVs (4K)"
        },
        "Web": {
            "video_format": "WEBM",
            "video_quality": "720p",
            "compression": "Low",
            "description": "Optimized for web streaming"
        }
    }

    # Filename template options
    FILENAME_TEMPLATES = {
        "Titre": "%(title)s.%(ext)s",
        "Titre + ID": "%(title)s_%(id)s.%(ext)s",
        "Chaîne - Titre": "%(uploader)s - %(title)s.%(ext)s",
        "Date + Titre": "%(upload_date)s_%(title)s.%(ext)s",
    }

    @classmethod
    def apply_profile(cls, profile_name: str) -> dict:
        """
        Get settings for a pre-configured device profile.

        Args:
            profile_name: Name of the profile (iPhone, Android, TV, Web).

        Returns:
            dict with: video_format, video_quality, compression
        """
        return cls.DEVICE_PROFILES.get(profile_name, {
            "video_format": "MP4",
            "video_quality": "1080p",
            "compression": "Medium"
        })

    def download_video(
        self,
        url: str,
        format_type: str,
        video_quality: str = "1080p",
        audio_format: str = "mp3",
        audio_bitrate: str = "192",
        filename_template: str = "%(title)s_%(id)s.%(ext)s",
        video_format: str = "MP4",           # NEW
        compression_preset: str = "Medium",  # NEW
    ) -> dict:
        """
        Download a YouTube video in the specified format and quality.

        Args:
            url: YouTube video URL.
            format_type: "mp4" for video or "audio" for audio only.
            video_quality: Video resolution (e.g. "720p", "1080p", "2160p (4K)").
            audio_format: Audio codec (e.g. "mp3", "flac", "wav").
            audio_bitrate: Audio bitrate for lossy formats (e.g. "192", "320").
            filename_template: yt-dlp output template for the filename.

        Returns:
            dict with keys: success (bool), message (str), filepath (str).
        """
        self._cancelled = False
        log.info(f"Download requested: url={url}, format={format_type}, "
                 f"video_quality={video_quality}, audio_format={audio_format}, "
                 f"audio_bitrate={audio_bitrate}")

        # Validate URL
        if not self.validate_url(url):
            log.warning(f"Invalid URL rejected: {url}")
            return {
                "success": False,
                "message": t("backend.invalid_url"),
                "filepath": "",
            }

        # Check FFmpeg for audio conversion and video merging
        if not self.check_ffmpeg():
            log.error("FFmpeg not found")
            if format_type == "audio":
                return {
                    "success": False,
                    "message": t("backend.ffmpeg_missing_audio"),
                    "filepath": "",
                }
            else:
                self.status_callback(
                    t("backend.ffmpeg_warning_video")
                )

        # Create output directory if needed
        try:
            os.makedirs(self.output_dir, exist_ok=True)
        except PermissionError:
            log.error(f"Permission denied for output dir: {self.output_dir}")
            return {
                "success": False,
                "message": t("backend.permission_denied", path=self.output_dir),
                "filepath": "",
            }

        # Build yt-dlp options
        outtmpl = os.path.join(self.output_dir, filename_template)

        # Base options shared by all formats
        ydl_opts = {
            "outtmpl": outtmpl,
            "progress_hooks": [self._progress_hook],
            "quiet": True,
            "no_warnings": True,
            "restrictfilenames": False,
            "windowsfilenames": True,
            "continuedl": True,         # Resume partial downloads (.part files)
            "retries": 3,              # Retry on network errors
            "fragment_retries": 3,     # Retry per fragment (DASH/HLS)
        }

        # Metadata postprocessors (embed metadata)
        metadata_pps = [
            {"key": "FFmpegMetadata"},
        ]

        if format_type == "audio":
            codec = self.AUDIO_CODEC_MAP.get(audio_format, "mp3")
            postprocessor = {
                "key": "FFmpegExtractAudio",
                "preferredcodec": codec,
            }
            # Only set bitrate for lossy formats
            if audio_format not in self.LOSSLESS_FORMATS:
                postprocessor["preferredquality"] = audio_bitrate

            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [postprocessor] + metadata_pps
        else:
            # Video download with format selection
            height = self.QUALITY_MAP.get(video_quality, 1080)
            format_config = self.VIDEO_FORMATS.get(video_format, self.VIDEO_FORMATS["MP4"])

            # Build format string based on container
            if video_format == "WEBM":
                # For WEBM, prefer VP9 codec
                ydl_opts["format"] = (
                    f"bestvideo[height<={height}][ext=webm]+bestaudio[ext=webm]"
                    f"/best[height<={height}]"
                )
            else:
                # For other formats, use general best format
                ydl_opts["format"] = (
                    f"bestvideo[height<={height}]+bestaudio"
                    f"/best[height<={height}]"
                )

            ydl_opts["merge_output_format"] = format_config["merge_format"]
            ydl_opts["postprocessors"] = metadata_pps

            # Add compression postprocessor if preset is specified
            if compression_preset and compression_preset in self.COMPRESSION_PRESETS:
                crf = self.COMPRESSION_PRESETS[compression_preset]
                compression_pp = {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": format_config["ext"],
                    "postprocessor_args": [
                        "-crf", str(crf),
                        "-preset", "medium"  # x264/x265 encoding speed preset
                    ]
                }
                # Insert compression before metadata embedding
                ydl_opts["postprocessors"].insert(0, compression_pp)

        # Execute download
        self.status_callback(t("backend.fetching_info"))
        self.progress_callback(0.0)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                # Use the actual filepath from yt-dlp instead of reconstructing it
                # This handles filename sanitization correctly
                filepath = ydl.prepare_filename(info)

                # For audio conversion, update extension
                if format_type == "audio":
                    filepath = os.path.splitext(filepath)[0] + f".{audio_format}"

                self.progress_callback(100.0)
                log.info(f"Download successful: {filepath}")

                if format_type == "audio":
                    success_msg = t("backend.download_success_audio", filepath=filepath)
                else:
                    success_msg = t("backend.download_success_mp4", filepath=filepath)

                self.status_callback(success_msg)
                return {
                    "success": True,
                    "message": success_msg,
                    "filepath": filepath,
                }

        except yt_dlp.utils.DownloadCancelled:
            log.info("Download cancelled by user")
            self.status_callback(t("backend.download_cancelled"))
            return {
                "success": False,
                "message": t("backend.download_cancelled"),
                "filepath": "",
            }
        except yt_dlp.utils.DownloadError as e:
            log.error(f"yt-dlp DownloadError: {e}", exc_info=True)
            msg = t("backend.download_error_private")
            self.status_callback(f"Erreur : {msg}")
            return {"success": False, "message": msg, "filepath": ""}
        except OSError as e:
            log.error(f"OSError: {e}", exc_info=True)
            msg = t("backend.download_error_disk", error=str(e))
            self.status_callback(f"Erreur : {msg}")
            return {"success": False, "message": msg, "filepath": ""}
        except Exception as e:
            log.critical(f"Unexpected error: {e}", exc_info=True)
            msg = t("backend.download_error_generic", error=str(e))
            self.status_callback(f"Erreur : {msg}")
            return {"success": False, "message": msg, "filepath": ""}
