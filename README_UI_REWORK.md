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

#### Main Menu
- Modern, animated main menu with clean design
- Animated title with fade-in effect
- Primary action buttons (New Game, Continue, Database Editor)
- Quick actions section (Create Sample DB, Exit)
- Responsive layout with proper spacing

#### Builder Module
Complete virus building interface with all specified features:

**Core Components:**
- **BuildViewModel**: Bridges UI ↔ game logic (game_state.py, simulation.py, data_models.py)
- **GeneCard**: Compact card (140×100px) with hover tooltips showing effects, prerequisites, cost
- **InstalledGeneCard**: Smaller card (120×70px) for installed genes with selection state
- **BlueprintGraphView**: QGraphicsView showing virus capabilities organized by location
- **MilestoneCard**: Progress display (180×70px) with status icons (✓/▶/○) and progress bars
- **HeaderBar**: EP display, starter entity selector, milestone summary, polymerase indicator
- **GeneDeckPanel**: Horizontal scrollable gene card container
- **InstalledGenesPanel**: Grid layout for installed genes with removal functionality
- **MilestonesPanel**: Horizontal milestone card row
- **BuildModule**: Main widget coordinating all components

**Visual Design:**
- Entity class colors: Virion=#6b7280, RNA=#22c55e, DNA=#3b82f6, Protein=#f97316, Complex=#8b5cf6
- Location backgrounds: Extracellular=#e0f2fe, Membrane=#fef3c7, Endosome=#ffedd5, Cytoplasm=#f3f4f6, Nucleus=#ede9fe

**Interactions:**
- Hover gene card → tooltip with full details
- Click gene card → install (confirmation if cost >20 EP)
- Click installed gene → select for removal
- Blueprint graph shows entities as nodes, transitions as arrows with probability labels
- Starter entity dropdown with count display
- Polymerase status indicator (warns if missing)

### 🚧 In Progress
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
ui_builder.py          # Build/virus construction module (1500+ lines)
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
- `ui_editor.py` - Editor (will be separate application)

### Design System
The new UI follows a modern design system with:
- Clean, card-based layouts
- Consistent color palette
- Smooth animations
- Responsive spacing
- Proper typography hierarchy

### ViewModel Pattern
```python
class BuildViewModel(QObject):
    deck_changed = Signal()
    installed_changed = Signal()
    blueprint_changed = Signal()
    ep_changed = Signal()
    
    def __init__(self, game_state: GameState, db_manager: GeneDatabaseManager):
        self._game_state = game_state
        self._db_manager = db_manager
        self._virus_builder = VirusBuilder(GeneDatabase(db_manager), game_state)
    
    @property
    def available_genes(self) -> List[GeneCardData]:
        # Transform deck data for UI consumption
        ...
    
    def install_gene(self, gene_name: str) -> bool:
        # Validate, spend EP, update builder, emit signals
        ...
```

## Build Module Features

### Gene Deck Panel
- Horizontal scrollable row of gene cards
- Cards show: name, EP cost, polymerase badge (if applicable)
- Unavailable genes are grayed out with reason indicator
- Hover shows detailed tooltip with effects and prerequisites

### Installed Genes Panel
- Grid layout of active genes
- Click to select for removal
- Shows "★ Active" indicator
- Removal requires 10 EP (with confirmation)

### Blueprint Graph
- Visual representation of all transitions
- Entities organized by location (vertical sections)
- Color-coded by entity class
- Arrows show transitions with probability labels
- Hover for detailed tooltips

### Milestone Tracking
- Three states: Completed (✓), In Progress (▶), Locked (○)
- Progress bars for active milestones
- EP rewards displayed for completed

### Header Bar
- Current EP display
- Starter entity selector dropdown
- Milestone progress summary
- Polymerase status indicator
- "Start Simulation" button

## Next Steps
1. Implement Play module with simulation visualization
2. Add database editor as separate application
3. Implement save/load functionality
4. Add more polish and animations