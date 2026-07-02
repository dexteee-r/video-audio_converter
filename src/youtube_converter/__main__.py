"""Entry point so the app can be launched with `python -m youtube_converter`.

The yt-dlp override is installed in youtube_converter/__init__.py (which Python
runs before this module), so nothing extra is needed here.
"""

from youtube_converter.app import main

if __name__ == "__main__":
    main()
