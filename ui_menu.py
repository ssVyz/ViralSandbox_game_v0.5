"""
Main Menu Module - PySide6

Modern main menu with animated title and clean design.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSpacerItem, QSizePolicy, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QFont

from ui_styles import ColorPalette, Fonts, Styles
from data_models import GeneDatabaseManager
from constants import FILE_TYPE_JSON, DEFAULT_SAMPLE_FILENAME


class AnimatedTitleLabel(QLabel):
    """Title label with fade-in animation."""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._opacity = 0.0
        self.setFont(Fonts.title())
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
    def get_opacity(self):
        return self._opacity
    
    def set_opacity(self, value):
        self._opacity = value
        self.setStyleSheet(f"""
            QLabel {{
                color: {ColorPalette.PRIMARY};
                background: transparent;
            }}
        """)
        self.setWindowOpacity(value)
    
    opacity = Property(float, get_opacity, set_opacity)
    
    def animate_in(self, delay=0):
        """Animate the title fading in."""
        self.animation = QPropertyAnimation(self, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        if delay > 0:
            QTimer.singleShot(delay, self.animation.start)
        else:
            self.animation.start()


class MenuButton(QPushButton):
    """Styled menu button."""
    
    def __init__(self, text, primary=True, parent=None):
        super().__init__(text, parent)
        self.setFont(Fonts.button())
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(50)
        
        if primary:
            self.setStyleSheet(Styles.PRIMARY_BUTTON)
        else:
            self.setStyleSheet(Styles.SECONDARY_BUTTON)


class QuickActionButton(QPushButton):
    """Small quick action button."""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(Fonts.small())
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {ColorPalette.TEXT_SECONDARY};
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 10px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {ColorPalette.BG_TERTIARY};
                color: {ColorPalette.TEXT_PRIMARY};
                border-color: {ColorPalette.BORDER_DEFAULT};
            }}
        """)


class MenuModule(QWidget):
    """Main menu module with modern design."""
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the menu UI."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        
        # Add spacer at top
        main_layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )
        
        # Title section
        title_layout = QVBoxLayout()
        title_layout.setSpacing(10)
        
        self.title_label = AnimatedTitleLabel("Virus Sandbox")
        title_layout.addWidget(self.title_label)
        
        subtitle = QLabel("Design and simulate your own virtual viruses")
        subtitle.setFont(Fonts.subtitle())
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY};")
        title_layout.addWidget(subtitle)
        
        main_layout.addLayout(title_layout)
        
        # Add spacer
        main_layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        )
        
        # Main buttons container
        buttons_container = QFrame()
        buttons_container.setMaximumWidth(400)
        buttons_container.setStyleSheet(Styles.CARD)
        
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(24, 24, 24, 24)
        buttons_layout.setSpacing(12)
        
        # New Game button
        self.new_game_btn = MenuButton("New Game", primary=True)
        self.new_game_btn.clicked.connect(self.start_new_game)
        buttons_layout.addWidget(self.new_game_btn)
        
        # Continue Game button (disabled for now)
        self.continue_btn = MenuButton("Continue Game", primary=False)
        self.continue_btn.setEnabled(False)
        self.continue_btn.clicked.connect(self.continue_game)
        buttons_layout.addWidget(self.continue_btn)
        
        # Database Editor button (placeholder)
        self.editor_btn = MenuButton("Database Editor", primary=False)
        self.editor_btn.setEnabled(False)
        self.editor_btn.setToolTip("Coming soon")
        buttons_layout.addWidget(self.editor_btn)
        
        # Center the buttons container
        button_container_layout = QHBoxLayout()
        button_container_layout.addStretch()
        button_container_layout.addWidget(buttons_container)
        button_container_layout.addStretch()
        
        main_layout.addLayout(button_container_layout)
        
        # Quick actions section
        quick_actions_layout = QHBoxLayout()
        quick_actions_layout.setSpacing(12)
        
        quick_actions_label = QLabel("Quick Actions:")
        quick_actions_label.setFont(Fonts.small())
        quick_actions_label.setStyleSheet(f"color: {ColorPalette.TEXT_TERTIARY};")
        quick_actions_layout.addWidget(quick_actions_label)
        
        # Create Sample Database button
        self.sample_db_btn = QuickActionButton("Create Sample DB")
        self.sample_db_btn.clicked.connect(self.create_sample_database)
        quick_actions_layout.addWidget(self.sample_db_btn)
        
        quick_actions_layout.addStretch()
        
        # Exit button
        self.exit_btn = QuickActionButton("Exit")
        self.exit_btn.clicked.connect(self.exit_application)
        quick_actions_layout.addWidget(self.exit_btn)
        
        main_layout.addLayout(quick_actions_layout)
        
        # Footer
        footer = QLabel("v1.0 | Made with ❤️ for viral biology")
        footer.setFont(Fonts.small())
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(f"color: {ColorPalette.TEXT_TERTIARY};")
        main_layout.addWidget(footer)
        
        # Add spacer at bottom
        main_layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )
        
        # Set the main layout
        self.setLayout(main_layout)
        
        # Apply window styling
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {ColorPalette.BG_SECONDARY};
            }}
        """)
    
    def show(self):
        """Show the menu and animate title."""
        super().show()
        # Animate title after a short delay
        QTimer.singleShot(100, lambda: self.title_label.animate_in(0))
    
    def hide(self):
        """Hide the menu."""
        super().hide()
    
    def start_new_game(self):
        """Start a new game - select database first."""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select Gene Database")
        file_dialog.setNameFilters(["JSON files (*.json)", "All files (*)"])
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setDirectory(os.getcwd())
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                file_path = file_paths[0]
                try:
                    db_manager = GeneDatabaseManager()
                    db_manager.load_database(file_path)
                    self.controller.start_new_game_with_database(db_manager)
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Failed to load database:\n{str(e)}"
                    )
    
    def continue_game(self):
        """Continue existing game - placeholder."""
        QMessageBox.information(
            self,
            "Not Implemented",
            "Continue game functionality will be added later"
        )
    
    def create_sample_database(self):
        """Create and save a sample database."""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Save Sample Database As")
        file_dialog.setNameFilters(["JSON files (*.json)", "All files (*)"])
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setDirectory(os.getcwd())
        file_dialog.selectFile(DEFAULT_SAMPLE_FILENAME)
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                file_path = file_paths[0]
                
                # Ensure .json extension
                if not file_path.endswith('.json'):
                    file_path += '.json'
                
                try:
                    db_manager = GeneDatabaseManager()
                    db_manager.create_sample_database()
                    db_manager.save_database(file_path)
                    
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Sample database created:\n{os.path.basename(file_path)}"
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Failed to create sample database:\n{str(e)}"
                    )
    
    def exit_application(self):
        """Exit the application with confirmation."""
        reply = QMessageBox.question(
            self,
            "Exit",
            "Are you sure you want to exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.controller.quit_application()
