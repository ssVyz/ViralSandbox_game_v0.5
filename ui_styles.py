"""
UI Styles and Themes - PySide6

Provides consistent styling across all UI modules.
"""

from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtCore import Qt


class ColorPalette:
    """Color definitions matching the design system."""
    
    # Primary colors
    PRIMARY = "#2563eb"
    PRIMARY_HOVER = "#1d4ed8"
    PRIMARY_ACTIVE = "#1e40af"
    
    # Background colors
    BG_PRIMARY = "#ffffff"
    BG_SECONDARY = "#f8fafc"
    BG_TERTIARY = "#f1f5f9"
    BG_DARK = "#1e293b"
    
    # Text colors
    TEXT_PRIMARY = "#0f172a"
    TEXT_SECONDARY = "#475569"
    TEXT_TERTIARY = "#94a3b8"
    TEXT_INVERSE = "#ffffff"
    
    # Border colors
    BORDER_LIGHT = "#e2e8f0"
    BORDER_DEFAULT = "#cbd5e1"
    BORDER_DARK = "#94a3b8"
    
    # Status colors
    SUCCESS = "#16a34a"
    SUCCESS_BG = "#dcfce7"
    WARNING = "#ea580c"
    WARNING_BG = "#fed7aa"
    DANGER = "#dc2626"
    DANGER_BG = "#fecaca"
    INFO = "#0284c7"
    INFO_BG = "#e0f2fe"
    
    # Special colors
    ACCENT = "#8b5cf6"
    ACCENT_HOVER = "#7c3aed"


class Fonts:
    """Font definitions."""
    
    @staticmethod
    def title():
        """Large title font."""
        font = QFont("Segoe UI", 32, QFont.Weight.Bold)
        return font
    
    @staticmethod
    def subtitle():
        """Subtitle font."""
        font = QFont("Segoe UI", 16)
        return font
    
    @staticmethod
    def header():
        """Section header font."""
        font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        return font
    
    @staticmethod
    def subheader():
        """Subsection header font."""
        font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        return font
    
    @staticmethod
    def body():
        """Body text font."""
        font = QFont("Segoe UI", 11)
        return font
    
    @staticmethod
    def small():
        """Small text font."""
        font = QFont("Segoe UI", 9)
        return font
    
    @staticmethod
    def button():
        """Button text font."""
        font = QFont("Segoe UI", 11, QFont.Weight.DemiBold)
        return font
    
    @staticmethod
    def mono():
        """Monospace font."""
        font = QFont("Consolas", 10)
        return font


class Styles:
    """Central stylesheet definitions."""
    
    MAIN_WINDOW = f"""
        QMainWindow {{
            background-color: {ColorPalette.BG_SECONDARY};
        }}
    """
    
    PRIMARY_BUTTON = f"""
        QPushButton {{
            background-color: {ColorPalette.PRIMARY};
            color: {ColorPalette.TEXT_INVERSE};
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: 600;
            min-width: 120px;
        }}
        QPushButton:hover {{
            background-color: {ColorPalette.PRIMARY_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {ColorPalette.PRIMARY_ACTIVE};
        }}
        QPushButton:disabled {{
            background-color: {ColorPalette.BORDER_DEFAULT};
            color: {ColorPalette.TEXT_TERTIARY};
        }}
    """
    
    SECONDARY_BUTTON = f"""
        QPushButton {{
            background-color: transparent;
            color: {ColorPalette.TEXT_PRIMARY};
            border: 2px solid {ColorPalette.BORDER_DEFAULT};
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: 600;
            min-width: 120px;
        }}
        QPushButton:hover {{
            border-color: {ColorPalette.PRIMARY};
            color: {ColorPalette.PRIMARY};
            background-color: {ColorPalette.BG_TERTIARY};
        }}
        QPushButton:pressed {{
            background-color: {ColorPalette.BORDER_LIGHT};
        }}
        QPushButton:disabled {{
            border-color: {ColorPalette.BORDER_LIGHT};
            color: {ColorPalette.TEXT_TERTIARY};
        }}
    """
    
    DANGER_BUTTON = f"""
        QPushButton {{
            background-color: {ColorPalette.DANGER};
            color: {ColorPalette.TEXT_INVERSE};
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: 600;
            min-width: 120px;
        }}
        QPushButton:hover {{
            background-color: #b91c1c;
        }}
        QPushButton:pressed {{
            background-color: #991b1b;
        }}
    """
    
    CARD = f"""
        QFrame {{
            background-color: {ColorPalette.BG_PRIMARY};
            border: 1px solid {ColorPalette.BORDER_LIGHT};
            border-radius: 12px;
            padding: 16px;
        }}
    """
    
    LABEL_PRIMARY = f"""
        QLabel {{
            color: {ColorPalette.TEXT_PRIMARY};
            font-size: 11pt;
        }}
    """
    
    LABEL_SECONDARY = f"""
        QLabel {{
            color: {ColorPalette.TEXT_SECONDARY};
            font-size: 10pt;
        }}
    """
    
    LABEL_TERTIARY = f"""
        QLabel {{
            color: {ColorPalette.TEXT_TERTIARY};
            font-size: 9pt;
        }}
    """


def apply_dark_palette(app):
    """Apply dark color palette to application (optional)."""
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(ColorPalette.BG_DARK))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(ColorPalette.TEXT_INVERSE))
    palette.setColor(QPalette.ColorRole.Base, QColor("#0f172a"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(ColorPalette.BG_DARK))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(ColorPalette.TEXT_INVERSE))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(ColorPalette.TEXT_INVERSE))
    palette.setColor(QPalette.ColorRole.Text, QColor(ColorPalette.TEXT_INVERSE))
    palette.setColor(QPalette.ColorRole.Button, QColor(ColorPalette.BG_DARK))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(ColorPalette.TEXT_INVERSE))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#ef4444"))
    palette.setColor(QPalette.ColorRole.Link, QColor(ColorPalette.PRIMARY))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(ColorPalette.PRIMARY))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(ColorPalette.TEXT_INVERSE))
    app.setPalette(palette)
