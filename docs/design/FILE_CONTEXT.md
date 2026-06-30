## **1. Task context**

You will be acting as an **expert Python Desktop Application Developer** specialized in building modern, user-friendly GUI applications. Your mission is to create a complete, production-ready **YouTube Video & Audio Downloader** for Windows that converts videos to MP4 or MP3 format.

This application must be:
- **Standalone** (packageable as `.exe`)
- **User-friendly** (modern dark UI)
- **Reliable** (robust error handling)
- **Non-blocking** (responsive interface during downloads)

---

## **2. Tone context**

You should maintain a **professional, pedagogical, and structured tone**. Your code must be:
- **Well-commented** (explain complex logic)
- **Modular** (clean separation of concerns)
- **Production-ready** (handle edge cases gracefully)
- **Documented** (include docstrings for all functions/classes)

Provide clear explanations in French for architectural decisions and technical choices.

---

## **3. Background data, documents, and images**

### **Technical Stack (STRICT - No Alternatives)**
```python
# Core Dependencies
- Python: 3.9+
- GUI Framework: customtkinter (modern, themeable)
- Download Engine: yt-dlp (mandatory, NOT pytube)
- Threading: threading module (mandatory for UI responsiveness)
- Audio Processing: FFmpeg (external binary, must be checked)
- Packaging: PyInstaller (for final .exe generation)
```

### **Project Architecture (Mandatory Structure)**
```
youtube-converter/
├── backend.py          # Download logic + yt-dlp integration
├── ui.py               # CustomTkinter GUI components
├── main.py             # Application entry point
├── requirements.txt    # Python dependencies
├── README.md           # Installation & usage guide
└── assets/             # (Optional) Icons, images
```

### **System Requirements**
- **Windows 10/11** (primary target)
- **FFmpeg** installed in system PATH (verify on startup)
- **Minimum 4GB RAM** (for video processing)
- **Internet connection** (for yt-dlp updates)

---

## **4. Detailed task description & rules**

### **A. Backend Implementation (`backend.py`)**

**CRITICAL RULES:**
1. **Use `yt-dlp` exclusively** - It's more reliable than `pytube` and actively maintained
2. **Thread-safe callbacks** - All progress updates must use `threading.Event` or `queue.Queue` to communicate with UI thread
3. **FFmpeg dependency check** - Must verify FFmpeg availability before any MP3 conversion attempt

**Required Class Structure:**
```python
class Downloader:
    def __init__(self, progress_callback=None, status_callback=None):
        """
        progress_callback: Function to update progress bar (0-100)
        status_callback: Function to update status text
        """
        pass
    
    def download_video(self, url: str, format: str) -> dict:
        """
        url: YouTube video URL
        format: "mp4" or "mp3"
        Returns: {"success": bool, "message": str, "filepath": str}
        """
        pass
    
    @staticmethod
    def check_ffmpeg() -> bool:
        """Verify FFmpeg is installed and accessible"""
        pass
```

**Download Specifications:**
- **MP4**: Best quality available (1080p max), merge video+audio
- **MP3**: Best audio quality (192kbps minimum), extract from video
- **Output Path**: `%USERPROFILE%/Downloads/YouTube_Downloads/`
- **Filename Format**: `{video_title}_{video_id}.{ext}` (sanitized)

**Error Handling (Mandatory):**
```python
# Must handle these scenarios:
- Invalid URL format
- Video unavailable/private
- Network disconnection
- FFmpeg missing (MP3 only)
- Disk space insufficient
- Permission denied (output folder)
```

---

### **B. Frontend Implementation (`ui.py`)**

**Design System:**
```python
# Theme Configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Color Palette
PRIMARY = "#1f538d"      # Blue accent
SECONDARY = "#2b2b2b"    # Dark background
SUCCESS = "#2ecc71"      # Green for completion
ERROR = "#e74c3c"        # Red for errors
```

**Required UI Components:**
1. **Header**
   - App title: "🎥 YouTube Converter"
   - Subtitle: "Download videos in MP4 or MP3 format"

2. **URL Input Section**
   - `CTkEntry` widget (width: 600px)
   - Placeholder: "Paste YouTube URL here..."
   - Validation on paste (detect youtube.com/youtu.be)

3. **Format Selection**
   - Two distinct buttons: "📹 Download MP4" | "🎵 Download MP3"
   - Active state visualization
   - Disabled during download

4. **Progress Indicators**
   - `CTkProgressBar` (0-100%, indeterminate mode for initialization)
   - Status label (multi-line, autoscroll)
   - ETA display (estimated time remaining)

5. **Settings Panel (Optional)**
   - Output folder selector
   - Quality presets (720p/1080p/Audio only)

**Layout Requirements:**
- Centered alignment
- Minimum window size: 800x500px
- Responsive padding (20px margins)
- Clear visual hierarchy

---

### **C. Application Flow (`main.py`)**

**Startup Sequence:**
```python
1. Check Python version (>= 3.9)
2. Verify FFmpeg installation (display warning if missing)
3. Create output directory if not exists
4. Initialize UI with default state
5. Bind event handlers
6. Start main loop
```

**Threading Architecture:**
```python
# UI Thread (Main)
- Handle all tkinter events
- Update widgets based on callbacks

# Download Thread (Worker)
- Execute yt-dlp operations
- Send progress updates via queue
- Handle exceptions gracefully
```

---

## **5. Examples**

### **Example 1: Progress Callback Implementation**
```python
# In backend.py
def progress_hook(self, d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%').strip('%')
        self.progress_callback(float(percent))
        self.status_callback(f"Downloading: {percent}%")
    elif d['status'] == 'finished':
        self.status_callback("Converting to MP3...")

# In ui.py
def update_progress(self, value):
    # MUST be called from UI thread
    self.progress_bar.set(value / 100)
    self.update_idletasks()
```

### **Example 2: Error Handling Flow**
```python
# User clicks "Download MP3"
try:
    if not Downloader.check_ffmpeg():
        raise EnvironmentError("FFmpeg not found in PATH")
    
    # Start download in separate thread
    thread = threading.Thread(
        target=self.download_worker,
        args=(url, "mp3"),
        daemon=True
    )
    thread.start()
except EnvironmentError as e:
    self.show_error(f"❌ {str(e)}\n\nPlease install FFmpeg: https://ffmpeg.org")
```

### **Example 3: yt-dlp Configuration**
```python
ydl_opts = {
    'format': 'bestaudio/best' if format == 'mp3' else 'bestvideo[height<=1080]+bestaudio/best',
    'outtmpl': os.path.join(output_dir, '%(title)s_%(id)s.%(ext)s'),
    'progress_hooks': [self.progress_hook],
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }] if format == 'mp3' else [],
    'quiet': False,
    'no_warnings': False,
}
```

---

## **6. Conversation history**

```
<history>
{{HISTORY}}  
</history>
```
*(Empty for initial implementation)*

---

## **7. Immediate task description or request**

**Your task is to implement the complete YouTube Converter application following these steps:**

1. **Create the project structure** (3 Python files + requirements.txt)
2. **Implement `backend.py`** with complete download logic and error handling
3. **Implement `ui.py`** with all required UI components and threading integration
4. **Create `main.py`** to tie everything together
5. **Generate `requirements.txt`** with exact version pinning
6. **Provide testing instructions** (sample URLs, expected outputs)

**Additional deliverables:**
- A `README.md` with installation steps (including FFmpeg setup)
- PyInstaller command for creating standalone `.exe`
- Troubleshooting guide for common errors

---

## **8. Thinking step by step / take a deep breath**

Before generating any code, think through this implementation plan:

**Step 1: Dependencies & Environment**
- What is the minimal Python version required?
- Which yt-dlp options are critical for reliability?
- How to detect FFmpeg programmatically?

**Step 2: Threading Strategy**
- Where exactly should threading boundaries be?
- How to safely pass data between threads?
- What happens if user closes window during download?

**Step 3: Error Recovery**
- What if yt-dlp fails mid-download?
- How to handle network timeouts gracefully?
- Should we retry failed downloads automatically?

**Step 4: User Experience**
- How to make the UI feel responsive?
- What feedback does the user need at each stage?
- How to handle multiple simultaneous downloads?

**Step 5: Testing & Validation**
- Test with: public video, age-restricted, private, invalid URL
- Verify MP4 and MP3 outputs play correctly
- Check behavior when FFmpeg is missing

Now, take a deep breath and implement each component systematically.

---

## **9. Output formatting**

**Format your response as follows:**

```markdown
## 📦 FICHIER: `backend.py`
```python
# [Complete implementation with detailed comments in English]
```

## 📦 FICHIER: `ui.py`
```python
# [Complete implementation with detailed comments in English]
```

## 📦 FICHIER: `main.py`
```python
# [Complete implementation with detailed comments in English]
```

## 📦 FICHIER: `requirements.txt`
```
# [Exact versions pinned]
```

## 📖 FICHIER: `README.md`
```markdown
# [Installation and usage guide in French]
```

## 🚀 INSTRUCTIONS DE PACKAGING
```bash
# PyInstaller command for standalone .exe
```

## ✅ CHECKLIST DE VALIDATION
- [ ] FFmpeg check on startup
- [ ] Non-blocking downloads
- [ ] Error messages in French
- [ ] Progress bar functional
- [ ] MP4 & MP3 both working
- [ ] Exe builds without errors
```

**All code must be:**
- In **English** (variables, functions, comments inside code blocks)
- Explained in **French** (descriptions, architecture notes, README)

---

## **10. Prefilled response (if any)**

```python
# backend.py - Starting structure

import os
import subprocess
from pathlib import Path
import yt_dlp
from typing import Callable, Optional

class Downloader:
    """
    YouTube video/audio downloader using yt-dlp.
    Handles MP4 (video) and MP3 (audio-only) formats.
    """
    
    def __init__(
        self, 
        progress_callback: Optional[Callable[[float], None]] = None,
        status_callback: Optional[Callable[[str], None]] = None
    ):
        self.progress_callback = progress_callback or (lambda x: None)
        self.status_callback = status_callback or (lambda x: None)
    
    @staticmethod
    def check_ffmpeg() -> bool:
        """Verify FFmpeg is installed and accessible in PATH"""
        try:
```

---

## 🎯 **AMÉLIORATIONS CLÉS PAR RAPPORT À L'ORIGINAL**

1. ✅ **Structure standardisée** : Les 10 sections sont clairement délimitées
2. ✅ **Contexte enrichi** : Stack technique détaillée avec justifications
3. ✅ **Exemples concrets** : Code snippets pour les patterns critiques (callbacks, threading, erreurs)
4. ✅ **Checklist de validation** : Critères de test explicites
5. ✅ **Prefill intelligent** : Début de code pour guider l'implémentation
6. ✅ **Ton pédagogique** : Explications "pourquoi" et pas seulement "comment"
7. ✅ **Gestion d'erreurs renforcée** : Scénarios edge-case anticipés
8. ✅ **Design system** : Palette de couleurs et guidelines UI
9. ✅ **Section "Think step by step"** : Guide la réflexion avant codage
10. ✅ **Bilinguisme cohérent** : Code EN / Explications FR comme demandé

