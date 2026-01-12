"""
Main Application Entry Point - PySide6 Version

Coordinates all game modules and manages application flow.
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from constants import WINDOW_WIDTH, WINDOW_HEIGHT
from data_models import GeneDatabaseManager
from game_state import GameState


class VirusSandboxApplication:
    """Main application controller for PySide6."""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Virus Sandbox")
        self.app.setOrganizationName("Virus Sandbox")

        # Enable high DPI scaling
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        # Initialize modules (will be populated as we build them)
        self.modules = {}
        self.current_module = None
        self.current_database_manager = None
        self.game_state = None

        # Setup modules
        self.setup_modules()

        # Show main menu
        self.switch_to_module("menu")

    def setup_modules(self):
        """Initialize all game modules."""
        from ui_menu import MenuModule

        self.modules["menu"] = MenuModule(self)
        # Builder and Play modules will be added later

    def switch_to_module(self, module_name: str):
        """Switch to a different module."""
        # Hide current module
        if self.current_module and self.current_module in self.modules:
            self.modules[self.current_module].hide()

        if module_name not in self.modules:
            raise ValueError(f"Unknown module: {module_name}")

        self.current_module = module_name
        self.modules[module_name].show()

    def start_new_game_with_database(self, database_manager: GeneDatabaseManager):
        """Start new game with a loaded database."""
        self.current_database_manager = database_manager

        # Initialize game state
        self.game_state = GameState()
        self.game_state.set_database_manager(database_manager)
        self.game_state.ep = 100  # Default starting EP
        self.game_state.reset_for_new_game()
        self.game_state.reset_starting_entity_count()

        # Seed deck with random genes
        import random
        all_genes = database_manager.get_all_genes()
        initial_deck_size = min(10, len(all_genes))
        self.game_state.deck = random.sample(all_genes, initial_deck_size)

        # TODO: Wire builder and play modules when they're implemented
        print("Game started with database - Builder module not yet implemented")
        # self.switch_to_module("builder")

    def quit_application(self):
        """Exit the application."""
        self.app.quit()

    def run(self):
        """Start the application."""
        return self.app.exec()


def main():
    """Application entry point."""
    app = VirusSandboxApplication()
    sys.exit(app.run())


if __name__ == "__main__":
    main()