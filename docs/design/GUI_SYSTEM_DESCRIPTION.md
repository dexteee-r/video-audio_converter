# 🎨 Documentation du Système Graphique - YouTube Converter

## 📚 Stack Technique

### Framework GUI
- **customtkinter** (CTk) - Framework moderne basé sur tkinter
- Widgets personnalisables avec thèmes dark/light
- Animations et coins arrondis natifs
- Support multi-plateforme (Windows, macOS, Linux)

### Dépendances visuelles
```python
import customtkinter as ctk
from theme import Theme
from i18n import t  # Système de traduction
```

---

## 🏗️ Architecture de l'Interface

### Classe principale: `YouTubeConverterUI`

```python
class YouTubeConverterUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Video & Audio Converter")
        self.geometry("900x800")
        self.minsize(850, 750)
```

### Hiérarchie des composants
```
YouTubeConverterUI (fenêtre principale)
│
├── main_container (scrollable frame)
│   │
│   ├── Header Section
│   │   ├── Titre principal
│   │   ├── Sous-titre
│   │   └── Sélecteur de langue
│   │
│   ├── URL Section
│   │   ├── Label "URL"
│   │   ├── Entry (saisie URL)
│   │   └── Bouton "Fetch Info"
│   │
│   ├── Quality Section
│   │   ├── Sélecteur de format (Video/Audio)
│   │   ├── Sélecteur de qualité vidéo (720p/1080p/4K)
│   │   ├── Sélecteur de format audio (MP3/FLAC/WAV/etc.)
│   │   ├── Sélecteur de bitrate audio
│   │   ├── Sélecteur de template de nom de fichier
│   │   ├── Sélecteur de format vidéo (MP4/MKV/WEBM/AVI/MOV)
│   │   ├── Sélecteur de compression (High/Medium/Low)
│   │   ├── Sélecteur de profil d'appareil (iPhone/Android/TV/Web/Custom)
│   │   └── Bouton "Add to Queue"
│   │
│   ├── Queue Section
│   │   ├── Label "Download Queue"
│   │   ├── Scrollable frame (liste des tâches)
│   │   │   └── Task cards (pour chaque tâche)
│   │   │       ├── Icône (📹 ou 🎵)
│   │   │       ├── Titre de la vidéo
│   │   │       ├── Qualité/Format
│   │   │       ├── Statut (En attente/Téléchargement/Terminé/Erreur)
│   │   │       └── Bouton "Remove"
│   │   └── Boutons de contrôle (Start Queue/Pause/Clear)
│   │
│   ├── Progress Section
│   │   ├── Label "Current Download"
│   │   ├── Progress bar (0-100%)
│   │   ├── Label de progression (pourcentage/vitesse)
│   │   └── Label de statut
│   │
│   └── History Section
│       ├── Label "Download History"
│       └── Scrollable frame (liste des téléchargements terminés)
│           └── History cards
│               ├── Titre
│               ├── Format/Qualité
│               ├── Date
│               └── Chemin du fichier
```

---

## 🎨 Système de Thèmes

### Fichier: `theme.py`

```python
class Theme:
    THEMES = {
        "dark": {
            "bg": "#1a1a1a",           # Fond principal
            "fg": "#ffffff",           # Texte principal
            "primary": "#1f538d",      # Couleur primaire (bleu)
            "secondary": "#2b2b2b",    # Fond secondaire
            "accent": "#3d85c6",       # Accent (bleu clair)
            "success": "#2ecc71",      # Vert (succès)
            "error": "#e74c3c",        # Rouge (erreur)
            "warning": "#f39c12",      # Orange (avertissement)
            "info": "#3498db",         # Bleu clair (info)
            "border": "#3d3d3d",       # Bordures
            "hover": "#363636",        # Survol
            "disabled": "#4a4a4a",     # Désactivé
        },
        "light": {
            "bg": "#f0f0f0",
            "fg": "#000000",
            "primary": "#1f538d",
            "secondary": "#e0e0e0",
            "accent": "#3d85c6",
            "success": "#27ae60",
            "error": "#c0392b",
            "warning": "#d68910",
            "info": "#2980b9",
            "border": "#cccccc",
            "hover": "#d6d6d6",
            "disabled": "#b0b0b0",
        }
    }
```

### Couleurs sémantiques
- **primary**: Actions principales, en-têtes
- **success**: Messages de succès, téléchargements terminés
- **error**: Messages d'erreur, échecs
- **warning**: Avertissements (FFmpeg manquant, etc.)
- **info**: Informations générales
- **accent**: Éléments interactifs (boutons, liens)

---

## 📐 Dimensions et Espacements

### Fenêtre principale
```python
window_size = "900x800"
min_size = (850, 750)
padding = 20  # Marges extérieures
```

### Widgets courants
```python
# Labels
label_width = 120
label_font = ctk.CTkFont(size=13)

# Entrées
entry_width = 600
entry_height = 40
entry_font = ctk.CTkFont(size=14)

# Boutons
button_height = 40
button_corner_radius = 8
button_font = ctk.CTkFont(size=14, weight="bold")

# Option menus (dropdowns)
optionmenu_width = 100-150 (selon le contenu)
optionmenu_height = 30

# Progress bars
progressbar_height = 20
progressbar_corner_radius = 10

# Spacing
section_pady = 15  # Espacement entre sections
widget_pady = 5    # Espacement entre widgets
```

---

## 🧩 Composants Détaillés

### 1. Header Section
```python
# Titre
title_font = ctk.CTkFont(size=24, weight="bold")
title_text = "🎥 YouTube Video & Audio Converter"

# Sous-titre
subtitle_font = ctk.CTkFont(size=13)
subtitle_text = t("ui.subtitle")  # Traduit selon la langue

# Sélecteur de langue
languages = ["🇫🇷 Français", "🇬🇧 English", "🇪🇸 Español", "🇩🇪 Deutsch"]
language_selector_width = 150
```

### 2. URL Section
```python
# Label
url_label = t("ui.url_label")  # "URL YouTube"

# Entry
placeholder = t("ui.url_placeholder")  # "Paste YouTube URL here..."
url_entry_width = 600

# Bouton Fetch Info
button_text = t("ui.fetch_info")  # "Fetch Info"
button_width = 150
```

### 3. Quality Section (Sélecteurs)

**Rangée 1: Type de format**
```python
label = t("ui.format_label")  # "Format"
options = ["Video", "Audio"]
optionmenu_width = 100
```

**Rangée 2: Qualité vidéo** (visible si format = Video)
```python
label = t("ui.video_quality_label")  # "Video Quality"
options = ["720p", "1080p", "2160p (4K)"]
default = "1080p"
```

**Rangée 3: Format audio** (visible si format = Audio)
```python
label = t("ui.audio_format_label")  # "Audio Format"
options = ["mp3", "flac", "wav", "m4a", "opus", "aac"]
default = "mp3"
```

**Rangée 4: Bitrate audio** (visible si format = Audio et format ≠ lossless)
```python
label = t("ui.audio_bitrate_label")  # "Bitrate"
options = ["128", "192", "256", "320"]
default = "192"
```

**Rangée 5: Template de nom de fichier**
```python
label = t("ui.filename_template_label")  # "Filename Template"
options = [
    "%(title)s_%(id)s.%(ext)s",
    "%(title)s.%(ext)s",
    "%(uploader)s_%(title)s.%(ext)s"
]
```

**Rangée 6: Format vidéo** (visible si format = Video)
```python
label = t("ui.video_format_label")  # "Container"
options = ["MP4", "MKV", "WEBM", "AVI", "MOV"]
default = "MP4"
```

**Rangée 7: Compression** (visible si format = Video)
```python
label = t("ui.compression_label")  # "Compression"
options = ["High", "Medium", "Low"]
default = "Medium"
```

**Rangée 8: Profil d'appareil** (visible si format = Video)
```python
label = t("ui.profile_label")  # "Device Profile"
options = ["iPhone", "Android", "TV", "Web", "Custom"]
default = "Custom"
```

**Bouton Add to Queue**
```python
button_text = t("ui.add_to_queue")  # "Add to Queue"
button_width = 200
button_fg_color = theme.get_color("primary")
```

### 4. Queue Section

**En-tête**
```python
section_title = t("ui.queue_title")  # "Download Queue"
title_font = ctk.CTkFont(size=16, weight="bold")
```

**Task Card** (pour chaque tâche)
```python
# Structure d'une carte de tâche
card_height = 80
card_padding = 10
card_border_width = 2

# Icône format
icon = "📹" if format_type == "video" else "🎵"

# Titre vidéo
title_font = ctk.CTkFont(size=13, weight="bold")
title_max_length = 50  # Tronqué si plus long

# Qualité/Format
quality_text = f"{format} {quality}"  # Ex: "MP4 1080p"
quality_font = ctk.CTkFont(size=11)

# Statut
status_colors = {
    "pending": theme.get_color("info"),      # Bleu
    "downloading": theme.get_color("warning"),  # Orange
    "completed": theme.get_color("success"),    # Vert
    "error": theme.get_color("error")          # Rouge
}

# Bouton Remove
remove_button_width = 80
remove_button_height = 28
```

**Boutons de contrôle**
```python
# Start Queue
start_button_text = t("ui.start_queue")  # "Start Queue"
start_button_width = 120

# Pause
pause_button_text = t("ui.pause_queue")  # "Pause"
pause_button_width = 100

# Clear Completed
clear_button_text = t("ui.clear_completed")  # "Clear Completed"
clear_button_width = 150
```

### 5. Progress Section

```python
# Titre de la section
section_title = t("ui.current_download")  # "Current Download"

# Progress bar
progressbar_width = 600
progressbar_height = 20
progressbar_mode = "determinate"  # 0-100%

# Label progression
# Format: "45.3% of 125.4MB at 2.3MB/s ETA 00:45"
progress_font = ctk.CTkFont(size=12)

# Label statut
# Format: "Downloading video..." / "Converting to MP3..." / etc.
status_font = ctk.CTkFont(size=12)
status_color = theme.get_color("info")
```

### 6. History Section

**En-tête**
```python
section_title = t("ui.history_title")  # "Download History"
title_font = ctk.CTkFont(size=16, weight="bold")
```

**History Card** (pour chaque téléchargement terminé)
```python
# Titre
title_font = ctk.CTkFont(size=12, weight="bold")

# Format/Qualité
info_font = ctk.CTkFont(size=11)
info_text = f"{format} {quality}"  # Ex: "MP3 320kbps"

# Date
date_font = ctk.CTkFont(size=10)
date_format = "%Y-%m-%d %H:%M"

# Chemin fichier
path_font = ctk.CTkFont(size=10)
path_color = theme.get_color("accent")
path_clickable = True  # Ouvre le fichier au clic
```

---

## 🔄 États Visuels

### Boutons
```python
# Normal
fg_color = theme.get_color("primary")
text_color = "#ffffff"

# Hover
hover_color = theme.get_color("accent")

# Disabled
fg_color = theme.get_color("disabled")
text_color = "#888888"
cursor = "arrow"  # Au lieu de "hand2"
```

### Entrées (Entry)
```python
# Normal
border_color = theme.get_color("border")
border_width = 2

# Focus
border_color = theme.get_color("primary")

# Error (URL invalide)
border_color = theme.get_color("error")
```

### Progress Bar
```python
# En cours
progress_color = theme.get_color("primary")
bg_color = theme.get_color("secondary")

# Terminé
progress_color = theme.get_color("success")

# Erreur
progress_color = theme.get_color("error")
```

---

## 🌍 Système i18n

### Structure des traductions
```python
# Fichier: translations/{lang}.json
{
    "ui": {
        "title": "YouTube Video & Audio Converter",
        "subtitle": "Download videos in MP4 or extract audio in MP3/FLAC/WAV",
        "url_label": "YouTube URL",
        "url_placeholder": "Paste YouTube URL here...",
        "fetch_info": "Fetch Info",
        "format_label": "Format",
        "video_quality_label": "Video Quality",
        "audio_format_label": "Audio Format",
        "audio_bitrate_label": "Bitrate",
        "filename_template_label": "Filename Template",
        "video_format_label": "Container",
        "compression_label": "Compression",
        "profile_label": "Device Profile",
        "add_to_queue": "Add to Queue",
        "queue_title": "Download Queue",
        "start_queue": "Start Queue",
        "pause_queue": "Pause",
        "clear_completed": "Clear Completed",
        "current_download": "Current Download",
        "history_title": "Download History",
        "language": "Language"
    },
    "messages": {
        "added_to_queue": "Added {url} to queue with quality {quality}",
        "download_complete": "Download complete: {filepath}",
        "download_error": "Error downloading: {error}",
        "profile_applied": "Profile {profile} applied.",
        "language_changed": "Language changed to {language}. Restart to apply."
    },
    "backend": {
        "fetching_info": "Fetching video information...",
        "downloading": "Downloading...",
        "converting": "Converting...",
        "finished": "Finished!",
        "invalid_url": "Invalid YouTube URL",
        "ffmpeg_missing_audio": "FFmpeg is required for audio conversion",
        "ffmpeg_warning_video": "FFmpeg not found - video merge may fail"
    }
}
```

### Fonction de traduction
```python
from i18n import t

# Utilisation simple
text = t("ui.title")

# Avec variables
text = t("messages.added_to_queue", url="https://...", quality="1080p")
```

---

## 🎯 Interactions Utilisateur

### Flux de téléchargement
```
1. Utilisateur colle une URL YouTube
2. Clic sur "Fetch Info" → Récupère titre/thumbnail
3. Sélection format (Video/Audio)
4. Sélection qualité/format/compression
5. Optionnel: Choix d'un profil d'appareil (applique les réglages)
6. Clic "Add to Queue" → Ajoute à la file d'attente
7. Clic "Start Queue" → Lance les téléchargements
8. Progress bar mise à jour en temps réel
9. À la fin: Carte ajoutée à l'historique
```

### Callbacks importants
```python
# Fetch Info
def _fetch_info(self):
    url = self.url_entry.get()
    # Valide URL + récupère métadonnées
    # Affiche titre dans status

# Format change
def _on_format_change(self, value):
    if value == "Video":
        # Affiche sélecteurs vidéo
        # Cache sélecteurs audio
    else:
        # Cache sélecteurs vidéo
        # Affiche sélecteurs audio

# Profile change
def _on_profile_change(self, profile):
    if profile == "iPhone":
        # Applique: MP4, 1080p, Medium
    # etc.

# Add to Queue
def _add_to_queue(self):
    task = DownloadTask(...)
    self.queue_manager.add_task(task)
    # Crée une carte visuelle dans la queue

# Start Queue
def _start_queue(self):
    threading.Thread(
        target=self.queue_manager.start,
        daemon=True
    ).start()
```

---

## 📱 Responsive Design

### Fenêtre redimensionnable
```python
# Taille minimale
min_width = 850
min_height = 750

# Composants qui s'adaptent
- URL Entry: width = container_width - 40
- Queue cards: width = container_width - 40
- Progress bar: width = container_width - 40
```

### Scrollable Sections
```python
# Main container
main_container = ctk.CTkScrollableFrame(...)

# Queue list
queue_list = ctk.CTkScrollableFrame(height=300)

# History list
history_list = ctk.CTkScrollableFrame(height=200)
```

---

## 🚀 Optimisations UI

### Threading
```python
# Téléchargement dans un thread séparé
download_thread = threading.Thread(
    target=self._download_worker,
    daemon=True
)

# Mise à jour UI dans le thread principal
def update_progress(self, value):
    self.after(0, lambda: self._update_progress_ui(value))
```

### Performance
- Utilisation de `CTkScrollableFrame` pour grandes listes
- Limitation du nombre d'éléments d'historique affichés (100 max)
- Callbacks thread-safe avec `after()`
- Désactivation des widgets pendant le téléchargement

---

## 📝 Notes pour génération de variantes

### Éléments modifiables
- ✅ **Couleurs**: Changer le thème via `theme.py`
- ✅ **Disposition**: Réorganiser les sections (ex: queue à droite)
- ✅ **Widgets**: Utiliser d'autres composants CTk
- ✅ **Animations**: Ajouter des transitions
- ✅ **Icônes**: Remplacer les emojis par des images

### Éléments à préserver
- ❌ **Hiérarchie de données**: Queue, Task, History
- ❌ **Callbacks**: Noms et signatures des méthodes
- ❌ **Threading**: Architecture de concurrence
- ❌ **i18n**: Système de traduction (clés JSON)
- ❌ **Backend interface**: Connexion avec `backend.py`, `queue_manager.py`

---

## 🔗 Dépendances entre fichiers

```
ui.py
├── importe → theme.py (couleurs, styles)
├── importe → i18n.py (traductions)
├── importe → settings.py (préférences utilisateur)
├── importe → queue_manager.py (gestion file d'attente)
├── importe → backend.py (téléchargement)
└── importe → history.py (historique)
```

### Contrats d'interface

**Queue Manager**
```python
# ui.py appelle:
queue_manager.add_task(task: DownloadTask)
queue_manager.start()
queue_manager.pause()
queue_manager.clear_completed()

# queue_manager appelle (callbacks):
progress_callback(percentage: float)
status_callback(message: str)
complete_callback(task: DownloadTask)
error_callback(task: DownloadTask, error: str)
```

**Backend**
```python
# ui.py appelle:
downloader.validate_url(url: str) -> bool
downloader.get_video_info(url: str) -> dict
downloader.download_video(url, format_type, ...) -> dict

# downloader appelle (callbacks):
progress_callback(d: dict)  # Informations de progression yt-dlp
status_callback(message: str)
```

---

## 🎨 Exemple de variante UI

### Layout alternatif: "Split View"
```
┌─────────────────────────────────────────────┐
│ Header + Language Selector                 │
├──────────────────┬──────────────────────────┤
│                  │                          │
│  Left Panel      │  Right Panel             │
│  ─────────       │  ──────────              │
│  • URL Input     │  • Queue (live)          │
│  • Format Select │  • Current Progress      │
│  • Quality       │  • History (recent 5)    │
│  • Add Button    │                          │
│                  │                          │
│  [Start Queue]   │  [Task cards...]         │
│  [Pause]         │                          │
│  [Clear]         │                          │
│                  │                          │
└──────────────────┴──────────────────────────┘
```

### Thème alternatif: "Neon Dark"
```python
NEON_THEME = {
    "bg": "#0a0a0a",
    "fg": "#e0e0e0",
    "primary": "#00ff9f",      # Vert néon
    "accent": "#ff006e",       # Rose néon
    "success": "#00ff9f",
    "error": "#ff006e",
    "border": "#1a1a1a",
    "glow": True,              # Effets de brillance
}
```

---

**Fin de la documentation** 📄
