"""Tests for the i18n translation layer."""

from youtube_converter.utils import i18n


def test_set_language_and_lookup():
    i18n.set_language("fr")
    assert i18n.t("ui.start") == "Démarrer"
    i18n.set_language("en")
    assert i18n.t("ui.start") == "Start"


def test_missing_key_returns_key():
    i18n.set_language("fr")
    assert i18n.t("ui.does.not.exist") == "ui.does.not.exist"


def test_interpolation():
    i18n.set_language("fr")
    out = i18n.t("messages.added_to_queue", url="URL_X", quality="1080p")
    assert "URL_X" in out and "1080p" in out


def test_interpolation_missing_var_does_not_crash():
    i18n.set_language("fr")
    # Missing kwargs must not raise; returns the raw template.
    out = i18n.t("messages.added_to_queue")
    assert isinstance(out, str)


def test_unknown_language_falls_back_to_french():
    data = i18n.load_translations("xx")
    assert data.get("ui", {}).get("start") == "Démarrer"
