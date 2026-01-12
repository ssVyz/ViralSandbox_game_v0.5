# Virus Sandbox Game - UI Rework Context

## Project Overview

**Virus Sandbox** is a Python-based strategy game where players build custom viruses by selecting genes, then simulate viral replication cycles. The game has working mechanics but requires a complete UI overhaul for clarity and usability.

### Core Game Loop
1. **Build Phase:** Player selects genes from their deck to install in their virus
2. **Play Phase:** Simulation runs turn-by-turn showing viral replication
3. **Repeat:** After simulation ends, player returns to build phase with gene rewards

### Key Game Concepts

| Concept | Description |
|---------|-------------|
| **Genes** | Cards that add capabilities (transitions) to the virus. Cost EP to install. |
| **Entities** | Viral components (virions, RNA, proteins, DNA) that exist in locations |
| **Locations** | Where entities exist: extracellular, membrane, endosome, cytoplasm, nucleus |
| **Transitions** | Rules that convert inputs → outputs with probability (e.g., RNA → Protein) |
| **EP (Evolution Points)** | Currency for installing/removing genes |
| **Milestones** | Achievement goals that reward EP (survive N turns, reach N entities, etc.) |
| **Interferon** | Host immune response that increases entity degradation |

---

## Technical Decisions

### UI Framework: **PySide6 (Qt6)**

**Rationale:**
- Professional appearance with minimal styling effort
- `QGraphicsScene`/`QGraphicsView` for card layouts and transition diagrams
- Built-in animation framework for card interactions
- Native hover events and tooltips
- Strong Model-View separation

### Architecture Pattern

```
┌─────────────────────────────────────┐
│         PRESENTATION LAYER          │
│   (PySide6 Views - NEW CODE)        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         VIEWMODEL LAYER             │
│   (Bridges UI ↔ Logic - NEW CODE)   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         GAME LOGIC LAYER            │
│   (EXISTING - DO NOT MODIFY)        │
│   - game_state.py                   │
│   - simulation.py                   │
│   - data_models.py                  │
│   - constants.py                    │
└─────────────────────────────────────┘
```

**Critical Rule:** The existing game logic files contain working mechanics. The UI layer must only call their public methods and read their state—never modify internal logic.

### Files to Preserve (Game Logic)
- `game_state.py` - EP, deck, milestones, round tracking
- `simulation.py` - `VirusBuilder`, `ViralSimulation` classes
- `data_models.py` - `GeneDatabaseManager`, `GeneDatabase` classes
- `constants.py` - All game constants

### Files to Remove
- `ui_editor.py` - Editor will be a separate application
- `ui_base.py` - Will be replaced
- `ui_menu_builder.py` - Will be replaced
- `ui_play.py` - Will be replaced

---

## Design Goals

### Primary Goals
1. **Clarity:** Players must always understand what's happening and why
2. **Progressive Disclosure:** Show summaries first, details on demand
3. **Visual Feedback:** Every action should have clear visual response
4. **Information Architecture:** Right information in right place at right time

### What Players Must Always Know
- Current EP and round count
- What genes are available and what they do
- How their virus currently works (all transitions)
- Milestone progress
- During simulation: entity populations and what's changing

---

## Build Module Design

### Layout Structure

```
┌─────────────────────────────────────────────────────────────────────────┐
│  HEADER BAR                                                              │
│  EP: 127  │  Round 3/10  │  Milestones: 4/12 ████░░  │ [Start Simulation]│
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  GENE DECK (horizontal scrollable card row)                             │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐     │
│  │  Gene  │ │  Gene  │ │  Gene  │ │  Gene  │ │  Gene  │ │  Gene  │     │
│  │   A    │ │   B    │ │   C    │ │   D    │ │   E    │ │   F    │     │
│  │        │ │        │ │        │ │        │ │        │ │        │     │
│  │ 25 EP  │ │ 40 EP  │ │ 15 EP  │ │ 50 EP  │ │ 30 EP  │ │ 20 EP  │     │
│  │ ▶ Poly │ │        │ │        │ │ ▶ Poly │ │        │ │        │     │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘     │
│                                                                          │
├──────────────────────────────┬──────────────────────────────────────────┤
│  INSTALLED GENES             │  VIRUS BLUEPRINT (Interactive Graph)     │
│  (2 genes installed)         │                                          │
│                              │  ┌─────────────────────────────────────┐ │
│  ┌────────┐ ┌────────┐      │  │                                     │ │
│  │ Capsid │ │  RdRp  │      │  │  [EXTRACELLULAR]                    │ │
│  │   ★    │ │   ★    │      │  │       ○ Virion                      │ │
│  │ Active │ │ Active │      │  │           │                         │ │
│  └────────┘ └────────┘      │  │           │ 40% receptor binding    │ │
│                              │  │           ▼                         │ │
│  ┌──────────────────┐       │  │  [MEMBRANE]                         │ │
│  │ Polymerase: 1/1  │       │  │       ○ Bound Virion                │ │
│  │ ██████████ FULL  │       │  │           │                         │ │
│  └──────────────────┘       │  │           │ 70% endocytosis         │ │
│                              │  │           ▼                         │ │
│  [Remove Selected: 10 EP]   │  │  [CYTOPLASM]                        │ │
│                              │  │       ○ RNA ◄───┐                   │ │
│                              │  │           │     │ 80% replication   │ │
│                              │  │           │     │                   │ │
│                              │  │           ▼     │                   │ │
│                              │  │       ○ Polymerase ─────────────┘   │ │
│                              │  │                                     │ │
│                              │  └─────────────────────────────────────┘ │
│                              │                                          │
│                              │  Legend: ○ Entity  │ Transition         │
│                              │  Color = Entity Class (RNA/Protein/etc) │
├──────────────────────────────┴──────────────────────────────────────────┤
│  MILESTONES                                                              │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────────────┐ │
│  │ ✓ Survive 5 turns│ │ ▶ 10 RNA peak    │ │ ○ 100 total virions      │ │
│  │   +25 EP EARNED  │ │   Progress: 3/10 │ │   Progress: 0/100        │ │
│  └──────────────────┘ └──────────────────┘ └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### Card Component Behavior

**Default State:**
- Compact card showing: Gene name, EP cost, type indicator (polymerase badge if applicable)
- Grayed out if prerequisites not met or polymerase limit reached

**Hover State:**
- Card expands slightly (scale 1.05)
- Tooltip panel appears showing:
  - Full description
  - All effects (transitions added/modified)
  - Prerequisites status
  - **Preview highlight on blueprint graph** showing what would change

**Click Action:**
- Confirmation dialog if cost > 20 EP
- Immediate install if affordable
- Card animates from deck to installed area
- Blueprint graph updates with new transitions

### Virus Blueprint Graph

**Purpose:** Visual representation of all transitions the virus can perform

**Layout Algorithm:**
- Group entities by location (vertical sections)
- Entities are nodes (circles/icons)
- Transitions are arrows connecting nodes
- Arrow labels show: probability, interferon cost

**Interactions:**
- Hover entity: Highlight all transitions involving it
- Hover transition arrow: Show detailed tooltip (inputs, outputs, consumed status)
- Click entity: Show entity details panel

**Visual Encoding:**
```
Entity Classes (node colors):
- Virion: Gray (#6b7280)
- RNA: Green (#22c55e)
- DNA: Blue (#3b82f6)
- Protein: Orange (#f97316)
- Complex: Purple (#8b5cf6)

Location Sections (background bands):
- Extracellular: Light blue
- Membrane: Light yellow
- Endosome: Light orange
- Cytoplasm: Light gray
- Nucleus: Light purple
```

### Starter Entity Selector
- Dropdown in header or near "Start Simulation" button
- Shows only entities marked as `is_starter: true`
- Preview starting count (including any bonuses)

---

## Play Module Design

### Layout Structure

```
┌─────────────────────────────────────────────────────────────────────────┐
│  HEADER BAR                                                              │
│  Turn: 47  │  Interferon: ████░░░░ 42/100  │  [+1] [+10] [+50] [◄ End]  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────┐  ┌────────────────────────────────┐│
│  │  ENTITY POPULATIONS             │  │  LOCATION VIEW                 ││
│  │                                 │  │                                ││
│  │  RNA      ████████████████ 847  │  │  ┌─────────────────────────┐  ││
│  │  Protein  ██████████░░░░░ 523   │  │  │ EXTRACELLULAR           │  ││
│  │  Virion   ████░░░░░░░░░░░ 189   │  │  │  ○○○○ Virion (42)       │  ││
│  │  DNA      ░░░░░░░░░░░░░░░   0   │  │  │  ○○ Exported (18)       │  ││
│  │                                 │  │  └─────────────────────────┘  ││
│  │  Total: 1,559 entities          │  │  ┌─────────────────────────┐  ││
│  │                                 │  │  │ MEMBRANE                │  ││
│  └─────────────────────────────────┘  │  │  ○○ Bound (8)           │  ││
│                                        │  └─────────────────────────┘  ││
│  ┌─────────────────────────────────┐  │  ┌─────────────────────────┐  ││
│  │  POPULATION HISTORY             │  │  │ CYTOPLASM               │  ││
│  │                                 │  │  │  ●●●● RNA (847)         │  ││
│  │  1000┤         ╱╲               │  │  │  ■■■ Protein (523)      │  ││
│  │      │        ╱  ╲    RNA       │  │  │  ◆◆ Polymerase (12)     │  ││
│  │   500┤    ╱──╱    ╲             │  │  │  ▲ Immature (89)        │  ││
│  │      │   ╱         ╲ Protein    │  │  └─────────────────────────┘  ││
│  │     0┼───────────────────────   │  │  ┌─────────────────────────┐  ││
│  │      0    20    40    Turn      │  │  │ NUCLEUS                 │  ││
│  │                                 │  │  │  (empty)                │  ││
│  └─────────────────────────────────┘  │  └─────────────────────────┘  ││
│                                        │                                ││
│                                        └────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────────────┤
│  THIS TURN                                                               │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌───────────┐ │
│  │ ▲ +24 RNA      │ │ ▲ +18 Protein  │ │ ▼ -34 Degraded │ │ ⚡ +2.4 IFN│ │
│  │ (replication)  │ │ (translation)  │ │ (natural)      │ │           │ │
│  └────────────────┘ └────────────────┘ └────────────────┘ └───────────┘ │
│                                                     [Show Detailed Log ▼]│
├─────────────────────────────────────────────────────────────────────────┤
│  MILESTONE PROGRESS                                                      │
│  ┌──────────────────────────┐ ┌──────────────────────────┐              │
│  │ ▶ 1000 RNA peak          │ │ ▶ Survive 100 turns      │              │
│  │   ████████░░ 847/1000    │ │   ████░░░░░░ 47/100      │              │
│  └──────────────────────────┘ └──────────────────────────┘              │
└─────────────────────────────────────────────────────────────────────────┘
```

### Entity Population Bars

**Design:**
- Horizontal bars, sorted by count (highest first)
- Color matches entity class
- Show exact count at end of bar
- Max bar width = highest current count (dynamic scaling)

**Interactions:**
- Hover: Show breakdown by specific entity type within class
- Click: Filter location view to show only that class

### Population History Graph

**Design:**
- Line graph showing last 50 turns
- One line per entity class (RNA, Protein, Virion, DNA)
- Y-axis auto-scales to max value
- X-axis shows turn numbers
- Legend with toggleable lines

**Data Source:** Extend existing `entity_type_history` tracking in simulation

### Location View

**Purpose:** Show WHERE entities are (critical for understanding viral lifecycle)

**Design:**
- Stacked panels, one per location
- Each panel shows entities in that location with counts
- Visual density (number of dots/icons) indicates quantity
- Empty locations shown but grayed

**Color Coding:** Same as entity classes

### This Turn Summary

**Purpose:** Quick scan of what just happened

**Design:**
- Horizontal card row showing major events
- Categories: Produced (+green), Consumed (-red), Degraded (-orange), Interferon (yellow)
- Click any card to expand to full transition details
- "Show Detailed Log" expands full console output (hidden by default)

### Turn Controls

**Buttons:**
- `[+1]` - Single turn with dramatic display
- `[+10]` - Fast forward 10 turns
- `[+50]` - Fast forward 50 turns (or to extinction/victory)
- `[◄ End]` - End simulation and return to builder

**Fast Forward Behavior:**
- Disable buttons during execution
- Update UI every 5 turns (not every turn)
- Show progress indicator
- Stop immediately on extinction or victory

### Victory/Extinction States

**Victory (10,000 entities):**
- Celebration overlay with stats
- Disable all controls
- Show milestone rewards earned
- "Return to Menu" button

**Extinction (0 entities):**
- Somber overlay with stats
- Show what went wrong (peak counts, turn of extinction)
- "Return to Builder" to try again

---

## Milestone Display Guidelines

### States
1. **Completed (✓):** Green checkmark, shows EP earned
2. **In Progress (▶):** Progress bar, shows current/target
3. **Locked (○):** Grayed out, shows requirements

### Always Visible
- Build Module: Horizontal row at bottom, show 3-5 most relevant
- Play Module: Show in-progress milestones with live-updating progress bars

### Milestone Types to Display
```
survive_turns: "Survive N turns" - show turn counter
peak_entity_count: "Have N [class] at once" - show current peak
cumulative_entity_count: "Create N total [class]" - show running total
```

---

## Interaction Patterns

### Hover = Preview
Anywhere the player can make a decision, hovering should preview the result:
- Hover gene card → Preview on blueprint graph
- Hover transition arrow → Show probability and effects
- Hover entity → Highlight related transitions

### Click = Commit
Clicking executes the action:
- Click gene card → Install gene (with confirmation if expensive)
- Click installed gene → Select for removal
- Click turn button → Execute turns

### Visual Feedback Timing
- Hover response: < 50ms
- Click feedback: < 100ms
- Transition animations: 200-300ms
- Turn simulation update: < 16ms per turn (60fps capable)

---

## Color Palette

```
Primary Colors:
- Background: #f8fafc (very light gray)
- Card Background: #ffffff
- Text Primary: #1e293b
- Text Secondary: #64748b

Entity Classes:
- Virion: #6b7280 (gray)
- RNA: #22c55e (green)
- DNA: #3b82f6 (blue)
- Protein: #f97316 (orange)
- Complex: #8b5cf6 (purple)

Status Colors:
- Success: #16a34a
- Warning: #ea580c
- Danger: #dc2626
- Info: #2563eb

Interferon Levels:
- None (0): #6b7280
- Low (1-25): #22c55e
- Medium (26-50): #eab308
- High (51-75): #f97316
- Critical (76-100): #dc2626
```

---

## Implementation Notes

### Gene Card Widget
Create a reusable `GeneCard` widget with:
- Properties: `gene_data`, `is_available`, `is_installed`, `is_hovered`
- Signals: `clicked`, `hovered`, `unhovered`
- Methods: `set_preview_mode(bool)`, `animate_install()`

### Blueprint Graph Widget
Use `QGraphicsScene` with:
- `EntityNode` items (circles with labels)
- `TransitionArrow` items (curved arrows with labels)
- Auto-layout algorithm based on entity locations
- Hover highlighting system

### Population Chart Widget
Use `QChartView` or custom `QPainter` drawing:
- Efficient line rendering for 50+ data points
- Smooth scrolling for history
- Legend with toggle buttons

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

---

## Success Criteria

The UI rework is successful when:

1. **New players understand the game in < 5 minutes** without external explanation
2. **Gene effects are immediately clear** from visual inspection
3. **Players can predict simulation outcomes** based on blueprint view
4. **No critical information requires scrolling** in primary views
5. **The app feels responsive** (no lag during simulation)
6. **Players always know their next goal** (milestone visibility)
