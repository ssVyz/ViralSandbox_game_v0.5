# Virus Sandbox - PySide6 UI Rework

## Overview
This is the modernized version of Virus Sandbox with a complete UI rework using PySide6.

## Installation

### Requirements
- Python 3.10+
- PySide6

### Install Dependencies
```bash
pip install PySide6
```

## Running the Application
```bash
python main.py
```

## Current Status

### ✅ Completed
- **Main Menu**: Modern, animated main menu with clean design
  - Animated title with fade-in effect
  - Primary action buttons (New Game, Continue, Database Editor)
  - Quick actions section (Create Sample DB, Exit)
  - Responsive layout with proper spacing

### 🚧 In Progress
- **Builder Module**: Virus building interface (coming next)
- **Play Module**: Simulation visualization (coming next)

### 📋 Planned
- Database Editor module
- Save/Load game functionality
- Additional UI polish and animations

## Architecture

### File Structure
```
main.py                 # Application entry point and controller
ui_menu.py             # Main menu module
ui_styles.py           # Centralized styling and theming
constants.py           # Game constants
data_models.py         # Data management (unchanged)
game_state.py          # Game state management (unchanged)
simulation.py          # Simulation logic (unchanged)
```

### Deleted Files (Old Tkinter UI)
- `ui_menu_builder.py` - Old menu and builder
- `ui_play.py` - Old play module
- `ui_base.py` - Old base UI classes

### Design System
The new UI follows a modern design system with:
- Clean, card-based layouts
- Consistent color palette
- Smooth animations
- Responsive spacing
- Proper typography hierarchy

## Next Steps
1. Implement Builder module with PySide6
2. Implement Play module with PySide6
3. Add database editor
4. Implement save/load functionality
5. Add more polish and animations
