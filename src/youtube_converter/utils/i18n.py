"""
i18n.py - Internationalization module

Provides translation support for multiple languages.
Translations are loaded from JSON files in the translations/ directory.
"""

import json
import os

from youtube_converter.config.paths import resource_path

_current_language = "fr"
_translations = {}


def load_translations(lang: str, _is_fallback: bool = False) -> dict:
    """
    Load translation file for the given language code.

    Args:
        lang: Language code (fr, en, es, de).
        _is_fallback: Internal flag to prevent infinite recursion.

    Returns:
        Dictionary containing all translations for the language.
    """
    filepath = resource_path(os.path.join("translations", f"{lang}.json"))
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Translation file not found: {filepath}")
        # Fallback to French if file not found (but only once)
        if lang != "fr" and not _is_fallback:
            return load_translations("fr", _is_fallback=True)
        # If French also missing or already in fallback, return empty dict
        return {}


def set_language(lang: str):
    """
    Change the active language.

    Args:
        lang: Language code (fr, en, es, de).
    """
    global _current_language, _translations
    _current_language = lang
    _translations = load_translations(lang)


def t(key: str, **kwargs) -> str:
    """
    Get translated string by key path using dot notation.

    Args:
        key: Translation key path (e.g., "ui.url_label").
        **kwargs: Variables for string interpolation.

    Returns:
        Translated string with variables substituted.

    Examples:
        t("ui.url_label") → "URL de la vidéo :"
        t("messages.added_to_queue", url="...", quality="1080p")
    """
    keys = key.split(".")
    value = _translations

    # Navigate through nested dict
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k, key)
        else:
            return key

    # Variable substitution
    if isinstance(value, str) and kwargs:
        try:
            return value.format(**kwargs)
        except KeyError:
            return value

    return value if isinstance(value, str) else key


# Initialize default language
set_language("fr")
