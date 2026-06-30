"""
theme.py - Single application theme (Midnight Neon)

The app uses one fixed theme. Colors are centralized here so every widget pulls
from the same source.
"""

# Midnight Neon - Dark blue with cyan accents
COLORS = {
    "bg": "#0B0E14",              # Ultra dark background
    "sidebar": "#151921",          # Slightly lighter sidebar
    "card": "#1C232E",             # Cards and fields
    "input_bg": "#0F172A",         # Input backgrounds
    "accent": "#38BDF8",           # Cyan neon accent
    "accent_hover": "#0EA5E9",     # Cyan neon hover
    "success": "#10B981",          # Emerald green
    "success_hover": "#059669",    # Emerald green hover
    "error": "#EF4444",            # Red error
    "error_hover": "#DC2626",      # Red error hover
    "warning": "#F59E0B",          # Amber warning
    "text_primary": "#E5E7EB",     # Primary text
    "text_secondary": "#9CA3AF",   # Secondary text
    "border": "#2D3748",           # Border color
}


def get_colors() -> dict:
    """Return a copy of the application's color palette."""
    return COLORS.copy()
