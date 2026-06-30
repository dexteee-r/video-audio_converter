# Guide de compilation (.exe)

Crée un exécutable Windows autonome `dist/YouTubeConverter.exe` à partir de la
version pywebview (Terminal Neon Mauve).

## Prérequis

1. **Python 3.9+**
2. Dépendances + outils de build installés :
   ```bash
   pip install -e ".[build]"
   ```
3. **WebView2 Runtime** sur la machine cible (préinstallé sur Win 10/11).
4. **FFmpeg** sur la machine cible (audio + fusion vidéo), dans le PATH.

## Build

Depuis la **racine du projet** :

```bash
pyinstaller --clean --noconfirm packaging/youtube_converter.spec
```

ou via le script (qui se place tout seul à la racine) :

```bash
python packaging/build.py
```

Résultat : `dist/YouTubeConverter.exe`.

> ⚠️ Fermez l'application avant de recompiler, sinon PyInstaller renvoie
> « Accès refusé » (l'exe est verrouillé).

## L'icône

L'icône (`packaging/icon/icon.ico`) est générée par script :

```bash
python packaging/icon/make_icon.py
```

Modifiez `make_icon.py` pour changer le motif/les couleurs, régénérez, puis
recompilez (la spec référence `packaging/icon/icon.ico`).

## Ce qui est embarqué automatiquement

- Runtime Python + pywebview + bridges WebView2 (pythonnet / clr_loader)
- Le package `youtube_converter` (compilé)
- Les resources : `resources/web/` (frontend) et `resources/translations/`
- yt-dlp et ses extracteurs

## Ce qui est créé au premier lancement (dans %APPDATA%)

- `%APPDATA%\YouTubeConverter\settings.json`
- `%APPDATA%\YouTubeConverter\download_history.json`
- `%APPDATA%\YouTubeConverter\logs\youtube_converter.log`

## Dépannage

| Erreur | Cause / solution |
|--------|------------------|
| `Accès refusé` sur `YouTubeConverter.exe` | L'app tourne encore — fermez-la |
| `script ... __main__.py not found` | Lancer depuis la racine (la spec s'auto-ancre via `SPECPATH`) |
| La fenêtre ne s'ouvre pas sur la cible | Installer le WebView2 Runtime (Microsoft) |
| Audio/fusion KO sur la cible | Installer FFmpeg dans le PATH |

## Taille / mémoire indicatives

- Exécutable : ~20 Mo
- RAM au lancement : process hôte léger + processus `msedgewebview2` (rendu)
