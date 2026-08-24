from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

DARK_PALETTE = {
    "Window": QColor("#353535"),
    "WindowText": QColor("#f0f0f0"),
    "Base": QColor("#2b2b2b"),
    "AlternateBase": QColor("#353535"),
    "ToolTipBase": QColor("#2b2b2b"),
    "ToolTipText": QColor("#f0f0f0"),
    "Text": QColor("#f0f0f0"),
    "Button": QColor("#3c3c3c"),
    "ButtonText": QColor("#f0f0f0"),
    "BrightText": QColor("#ff6b6b"),
    "Link": QColor("#4a9eff"),
    "Highlight": QColor("#1677ff"),
    "HighlightedText": QColor("#ffffff"),
    "PlaceholderText": QColor("#9a9a9a"),
}

LIGHT_PALETTE = {
    "Window": QColor("#efefef"),
    "WindowText": QColor("#1a1a1a"),
    "Base": QColor("#ffffff"),
    "AlternateBase": QColor("#f4f4f4"),
    "ToolTipBase": QColor("#ffffff"),
    "ToolTipText": QColor("#1a1a1a"),
    "Text": QColor("#1a1a1a"),
    "Button": QColor("#efefef"),
    "ButtonText": QColor("#1a1a1a"),
    "BrightText": QColor("#b00020"),
    "Link": QColor("#1677ff"),
    "Highlight": QColor("#1677ff"),
    "HighlightedText": QColor("#ffffff"),
    "PlaceholderText": QColor("#8a8a8a"),
}


def apply_theme(application: QApplication, mode: str) -> None:
    """Apply a color palette for the requested theme mode.

    ``mode`` is one of ``"system"``, ``"dark"`` or ``"light"``. In ``system``
    mode the palette follows the platform color scheme.
    """
    if mode == "system":
        application.style().unpolish(application)
        application.setPalette(application.style().standardPalette())
        return

    colors = DARK_PALETTE if mode == "dark" else LIGHT_PALETTE
    palette = QPalette()
    for role_name, color in colors.items():
        role = getattr(QPalette.ColorRole, role_name)
        palette.setColor(role, color)
    for group in (
        QPalette.ColorGroup.Active,
        QPalette.ColorGroup.Inactive,
        QPalette.ColorGroup.Disabled,
    ):
        for role_name, color in colors.items():
            if group == QPalette.ColorGroup.Disabled and role_name in (
                "Text",
                "ButtonText",
                "WindowText",
            ):
                palette.setColor(group, getattr(QPalette.ColorRole, role_name), color.darker(140))
                continue
            palette.setColor(group, getattr(QPalette.ColorRole, role_name), color)
    application.setPalette(palette)


def system_prefers_dark(application: QApplication) -> bool:
    return application.styleHints().colorScheme() == Qt.ColorScheme.Dark
