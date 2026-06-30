# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec — YouTube Converter (Terminal Neon Mauve, pywebview).
Builds dist/YouTubeConverter.exe.

Run from the PROJECT ROOT:
    pyinstaller --clean --noconfirm packaging/youtube_converter.spec
"""

import os
from PyInstaller.utils.hooks import collect_all, collect_submodules

# Spec paths are resolved relative to the spec file's directory, so anchor
# everything to the project root (parent of packaging/).
ROOT = os.path.abspath(os.path.join(SPECPATH, os.pardir))

app_name = 'YouTubeConverter'
main_script = os.path.join(ROOT, 'src', 'youtube_converter', '__main__.py')

# Bundle pywebview + its native bridges (WebView2 / pythonnet / clr_loader).
datas, binaries, hiddenimports = [], [], []
for pkg in ('webview', 'clr_loader', 'pythonnet', 'proxy_tools'):
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

# Bundle package resources (frontend + translations) preserving structure so
# config.paths.resource_path() resolves them under youtube_converter/resources.
datas += [(os.path.join(ROOT, 'src', 'youtube_converter', 'resources'), 'youtube_converter/resources')]

hiddenimports += [
    'webview.platforms.edgechromium',
    'webview.platforms.winforms',
    'clr',
    'yt_dlp',
]
hiddenimports += collect_submodules('youtube_converter')

a = Analysis(
    [main_script],
    pathex=[os.path.join(ROOT, 'src')],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'pytest', 'IPython', 'customtkinter', 'tkinter'],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(ROOT, 'packaging', 'icon', 'icon.ico'),
)
