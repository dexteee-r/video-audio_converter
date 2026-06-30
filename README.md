# YouTube Converter

Application desktop Windows pour télécharger des vidéos en **MP4** (vidéo) ou
**MP3 / M4A / FLAC / WAV / OGG** (audio), depuis YouTube, TikTok, Instagram,
Vimeo, Twitch et 1000+ sites — interface **Terminal Neon Mauve**.

Le moteur de téléchargement est [yt-dlp](https://github.com/yt-dlp/yt-dlp) ;
l'interface est rendue en HTML/CSS/JS dans une fenêtre native via
[pywebview](https://pywebview.flowrl.com/) (WebView2).

## Prérequis

- **Python 3.9+**
- **FFmpeg** dans le PATH (requis pour l'audio et la fusion vidéo)
  - Téléchargement : https://ffmpeg.org/download.html
- **WebView2 Runtime** (préinstallé sur Windows 10/11)

## Installation (développement)

```bash
python -m venv venv
venv\Scripts\activate
pip install -e .
```

## Lancer

```bash
python -m youtube_converter
```

## Fonctionnalités

- Vidéo (MP4/MKV/WEBM/AVI/MOV) ou audio (MP3/M4A/FLAC/WAV/OGG)
- Choix qualité, conteneur, bitrate, template de nom de fichier
- Profils d'appareil (iPhone / Android / TV / Web)
- Compression optionnelle (désactivée par défaut → téléchargement direct, sans perte)
- File d'attente séquentielle, progression temps réel
- Historique persistant + export CSV
- Multilingue **live** : FR / EN / ES / DE (sans redémarrage)

## Données utilisateur

Réglages, historique et logs sont stockés dans
`%APPDATA%\YouTubeConverter\` (rien n'est écrit à côté de l'exécutable).

## Créer l'exécutable (.exe)

Voir [docs/BUILD.md](docs/BUILD.md). En bref, depuis la racine :

```bash
pip install -e ".[build]"
pyinstaller --clean --noconfirm packaging/youtube_converter.spec
# -> dist/YouTubeConverter.exe
```

## Architecture

Voir [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

```
src/youtube_converter/   core (logique) · config · utils · app.py (UI bridge) · resources/ (web + i18n)
packaging/               spec PyInstaller · build.py · icon/
docs/                    BUILD.md · ARCHITECTURE.md · design/
tests/                   tests
```

## Dépannage

| Problème | Solution |
|----------|----------|
| « FFmpeg non détecté » | Installez FFmpeg et ajoutez-le au PATH |
| La fenêtre ne s'ouvre pas | Installez le WebView2 Runtime (Microsoft) |
| « Vidéo non disponible » | Vidéo privée, supprimée ou géo-restreinte |
| Permission refusée | Changez le dossier de destination |
