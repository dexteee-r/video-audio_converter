# Architecture

YouTube Converter is a desktop app that downloads media (MP4/MP3 and more) from
YouTube and 1000+ sites. The UI is rendered with web technologies (HTML/CSS/JS)
inside a native window via **pywebview**, while all business logic stays in Python.

## Layered design (separation of concerns)

```
┌─────────────────────────────────────────────┐
│  Frontend  (resources/web/*.html,.css,.js)   │  presentation only
└───────────────▲──────────────────────────────┘
                │  pywebview bridge (JSON)
┌───────────────┴──────────────────────────────┐
│  app.py  — Api class                          │  glue: exposes methods to JS,
│                                               │  pushes live events to JS
└───────────────▲──────────────────────────────┘
                │
┌───────────────┴──────────────────────────────┐
│  core/   backend · queue_manager · history    │  business logic (no UI)
│  config/ settings · constants · theme · paths │  configuration
│  utils/  logger · i18n                         │  cross-cutting helpers
└────────────────────────────────────────────────┘
```

The **frontend never talks to `core/` directly** — it goes through `app.py`'s
`Api` object. That keeps presentation and logic fully decoupled: the same backend
could drive any other UI.

## Package layout

```
src/youtube_converter/
├── __main__.py        # `python -m youtube_converter`
├── app.py             # pywebview window + Python<->JS bridge (Api)
├── core/              # backend (yt-dlp), download queue, history
├── config/            # settings, constants, single theme, path resolution
├── utils/             # logging, i18n
└── resources/
    ├── web/           # index.html, style.css, app.js (Terminal Neon Mauve)
    └── translations/  # fr / en / es / de
```

## Key conventions

- **Paths** are resolved through `config/paths.py`:
  - `resource_path(...)` → read-only bundled assets (works in source *and* in the
    frozen `.exe` via `sys._MEIPASS`).
  - `user_data_dir()` → writable per-user data in `%APPDATA%/YouTubeConverter`
    (settings, history, logs). Nothing is written next to the executable.
- **Threading**: downloads run in a worker thread (`DownloadQueue`); the bridge
  marshals progress/status back to the JS UI via `window.evaluate_js`.
- **i18n**: UI strings live in `resources/translations/*.json` and are applied to
  the DOM live (no restart needed) via `data-i18n` attributes.
- **Single theme**: Terminal Neon Mauve. Colors centralized in `config/theme.py`
  and `resources/web/style.css`.

## Build

Packaging lives in `packaging/` (PyInstaller spec, build script, icon). See
[BUILD.md](BUILD.md).
