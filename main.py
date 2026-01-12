"""
Main Application Entry Point - PySide6 Version

Coordinates all game modules and manages application flow.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PySide6.QtCore import Qt

from constants import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from data_models import GeneDatabaseManager
from game_state import GameState


class VirusSandboxWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Virus Sandbox")
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        # Central stacked widget for module switching
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)


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

        # Create main window
        self.window = VirusSandboxWindow()

        # Initialize modules (will be populated as we build them)
        self.modules = {}
        self.current_module = None
        self.current_database_manager = None
        self.game_state = None
        self.virus_builder = None

        # Setup modules
        self.setup_modules()

        # Show main menu
        self.switch_to_module("menu")
        self.window.show()

    def setup_modules(self):
        """Initialize all game modules."""
        from ui_menu import MenuModule
        from ui_builder import BuildModule

        # Create modules and add to stack
        self.modules["menu"] = MenuModule(self)
        self.modules["builder"] = BuildModule(self)

        self.window.stack.addWidget(self.modules["menu"])
        self.window.stack.addWidget(self.modules["builder"])

        # Play module will be added later
        # self.modules["play"] = PlayModule(self)

    def switch_to_module(self, module_name: str):
        """Switch to a different module."""
        if module_name not in self.modules:
            raise ValueError(f"Unknown module: {module_name}")

        self.current_module = module_name
        widget = self.modules[module_name]
        self.window.stack.setCurrentWidget(widget)

        # Call show method if it exists (for module-specific initialization)
        if hasattr(widget, 'show'):
            widget.show()

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

        # Set up the builder module with game context
        self.modules["builder"].set_game_context(self.game_state, database_manager)

        # Switch to builder
        self.switch_to_module("builder")

    def start_simulation(self, blueprint: dict, virus_builder):
        """Start the play/simulation module."""
        self.virus_builder = virus_builder

        # Play module not implemented yet
        QMessageBox.information(
            self.window,
            "Play Module",
            "Simulation started!\n\n"
            f"Starting entity: {list(blueprint['starting_entities'].keys())[0]}\n"
            f"Starting count: {list(blueprint['starting_entities'].values())[0]}\n"
            f"Installed genes: {len(blueprint['genes'])}\n"
            f"Transition rules: {len(blueprint['transition_rules'])}\n\n"
            "Play module will be implemented in the next phase."
        )

        # When play module is ready:
        # self.modules["play"].set_simulation(blueprint, virus_builder)
        # self.switch_to_module("play")

    def return_to_builder(self):
        """Return to builder from play module."""
        self.switch_to_module("builder")

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