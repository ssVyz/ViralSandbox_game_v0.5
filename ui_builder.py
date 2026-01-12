"""
Builder Module - PySide6

Virus building interface with gene deck, installed genes, blueprint graph, and milestones.
"""

from typing import List, Dict, Optional, Set
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy, QMessageBox, QComboBox,
    QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem,
    QGraphicsTextItem, QGraphicsRectItem, QGraphicsPathItem,
    QToolTip, QSplitter, QProgressBar, QGridLayout
)
from PySide6.QtCore import (
    Qt, Signal, QObject, QRectF, QPointF, QTimer, 
    QPropertyAnimation, QEasingCurve, Property
)
from PySide6.QtGui import (
    QFont, QColor, QPen, QBrush, QPainterPath, QPainter,
    QLinearGradient, QCursor
)

from ui_styles import ColorPalette, Fonts, Styles
from data_models import GeneDatabaseManager, GeneDatabase
from game_state import GameState
from simulation import VirusBuilder
from constants import (
    LOCATION_DISPLAY_ORDER, LOCATION_DISPLAY_LABELS,
    ENTITY_CLASS_VIRION, ENTITY_CLASS_RNA, ENTITY_CLASS_DNA,
    ENTITY_CLASS_PROTEIN, ENTITY_CLASS_COMPLEX
)


# Entity class colors
ENTITY_COLORS = {
    ENTITY_CLASS_VIRION: "#6b7280",   # Gray
    ENTITY_CLASS_RNA: "#22c55e",       # Green
    ENTITY_CLASS_DNA: "#3b82f6",       # Blue
    ENTITY_CLASS_PROTEIN: "#f97316",   # Orange
    ENTITY_CLASS_COMPLEX: "#8b5cf6",   # Purple
    "unknown": "#9ca3af"               # Light gray
}

# Location background colors
LOCATION_COLORS = {
    "extracellular": "#e0f2fe",  # Light blue
    "membrane": "#fef3c7",       # Light yellow
    "endosome": "#ffedd5",       # Light orange
    "cytoplasm": "#f3f4f6",      # Light gray
    "nucleus": "#ede9fe",        # Light purple
    "unknown": "#f9fafb"         # Very light gray
}


class BuildViewModel(QObject):
    """ViewModel bridging UI and game logic for the Build module."""
    
    deck_changed = Signal()
    installed_changed = Signal()
    blueprint_changed = Signal()
    ep_changed = Signal()
    milestones_changed = Signal()
    starter_entity_changed = Signal()
    
    def __init__(self, game_state: GameState, db_manager: GeneDatabaseManager):
        super().__init__()
        self._game_state = game_state
        self._db_manager = db_manager
        self._gene_database = GeneDatabase(db_manager)
        self._virus_builder = VirusBuilder(self._gene_database, game_state)
        
        # Initialize builder with deck genes
        for gene_name in game_state.deck:
            if self._virus_builder.can_add_gene(gene_name)[0]:
                self._virus_builder.add_gene(gene_name)
    
    @property
    def ep(self) -> int:
        return self._game_state.ep
    
    @property
    def deck(self) -> List[str]:
        return self._game_state.deck.copy()
    
    @property
    def installed_genes(self) -> List[str]:
        return [g["name"] for g in self._virus_builder.selected_genes]
    
    @property
    def available_starter_entities(self) -> List[str]:
        return self._game_state.get_available_starter_entities()
    
    @property
    def selected_starter_entity(self) -> str:
        return self._game_state.get_selected_starter_entity()
    
    @property
    def starting_entity_count(self) -> int:
        return self._game_state.get_starting_entity_count()
    
    def get_gene_data(self, gene_name: str) -> Optional[Dict]:
        """Get gene data from database."""
        return self._db_manager.get_gene(gene_name)
    
    def get_entity_data(self, entity_name: str) -> Optional[Dict]:
        """Get entity data from database."""
        return self._db_manager.get_entity(entity_name)
    
    def can_install_gene(self, gene_name: str) -> tuple[bool, str]:
        """Check if a gene can be installed."""
        # Check if already in builder
        if gene_name in self.installed_genes:
            return False, "already_installed"
        
        # Check prerequisites via builder
        can_add, reason = self._virus_builder.can_add_gene(gene_name)
        if not can_add:
            return False, reason
        
        # Check cost
        cost = self._game_state.get_gene_cost(gene_name)
        if self._game_state.ep < cost:
            return False, "insufficient_ep"
        
        return True, ""
    
    def install_gene(self, gene_name: str) -> bool:
        """Install a gene (spend EP and add to builder)."""
        can_install, reason = self.can_install_gene(gene_name)
        if not can_install:
            return False
        
        # Spend EP
        cost = self._game_state.get_gene_cost(gene_name)
        self._game_state.ep -= cost
        
        # Add to builder
        self._virus_builder.add_gene(gene_name)
        
        # Emit signals
        self.ep_changed.emit()
        self.installed_changed.emit()
        self.blueprint_changed.emit()
        
        return True
    
    def remove_gene(self, gene_name: str) -> bool:
        """Remove a gene (spend EP and remove from builder)."""
        if gene_name not in self.installed_genes:
            return False
        
        # Check removal cost
        cost = self._game_state.get_remove_cost(gene_name)
        if self._game_state.ep < cost:
            return False
        
        # Spend EP for removal
        self._game_state.ep -= cost
        
        # Remove from builder
        self._virus_builder.remove_gene(gene_name)
        
        # Emit signals
        self.ep_changed.emit()
        self.installed_changed.emit()
        self.blueprint_changed.emit()
        
        return True
    
    def set_starter_entity(self, entity_name: str) -> bool:
        """Set the starter entity."""
        if self._game_state.set_starter_entity(entity_name):
            self.starter_entity_changed.emit()
            self.blueprint_changed.emit()
            return True
        return False
    
    def get_virus_blueprint(self) -> Dict:
        """Get current virus capabilities."""
        return self._virus_builder.get_virus_capabilities()
    
    def get_milestone_progress(self) -> Dict:
        """Get milestone progress data."""
        return self._game_state.get_milestone_progress()
    
    def has_polymerase(self) -> bool:
        """Check if a polymerase gene is installed."""
        return self._virus_builder._has_polymerase_gene()
    
    def get_polymerase_gene(self) -> Optional[str]:
        """Get name of installed polymerase gene."""
        return self._virus_builder.get_selected_polymerase_gene()


class GeneCard(QFrame):
    """A card widget displaying a single gene."""
    
    clicked = Signal(str)  # gene_name
    hovered = Signal(str)  # gene_name
    unhovered = Signal()
    
    def __init__(self, gene_name: str, gene_data: Dict, parent=None):
        super().__init__(parent)
        self.gene_name = gene_name
        self.gene_data = gene_data
        self._is_available = True
        self._is_installed = False
        self._is_hovered = False
        self._unavailable_reason = ""
        
        self.setup_ui()
        self.update_style()
        
    def setup_ui(self):
        """Setup the card UI."""
        self.setFixedSize(140, 100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)
        
        # Gene name
        self.name_label = QLabel(self.gene_name)
        self.name_label.setFont(Fonts.small())
        self.name_label.setWordWrap(True)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label)
        
        layout.addStretch()
        
        # Bottom row: cost and badges
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(4)
        
        # Cost
        cost = self.gene_data.get("cost", 0)
        self.cost_label = QLabel(f"{cost} EP")
        self.cost_label.setFont(Fonts.small())
        bottom_layout.addWidget(self.cost_label)
        
        bottom_layout.addStretch()
        
        # Polymerase badge
        if self.gene_data.get("is_polymerase", False):
            poly_badge = QLabel("▶ Poly")
            poly_badge.setFont(Fonts.small())
            poly_badge.setStyleSheet(f"""
                QLabel {{
                    background-color: {ColorPalette.ACCENT};
                    color: white;
                    border-radius: 3px;
                    padding: 2px 4px;
                    font-size: 8px;
                }}
            """)
            bottom_layout.addWidget(poly_badge)
        
        layout.addLayout(bottom_layout)
    
    def set_available(self, available: bool, reason: str = ""):
        """Set whether the gene can be installed."""
        self._is_available = available
        self._unavailable_reason = reason
        self.update_style()
    
    def set_installed(self, installed: bool):
        """Set whether the gene is installed."""
        self._is_installed = installed
        self.update_style()
    
    def update_style(self):
        """Update card style based on state."""
        if self._is_installed:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {ColorPalette.SUCCESS_BG};
                    border: 2px solid {ColorPalette.SUCCESS};
                    border-radius: 8px;
                }}
            """)
            self.name_label.setStyleSheet(f"color: {ColorPalette.SUCCESS};")
            self.cost_label.setStyleSheet(f"color: {ColorPalette.SUCCESS};")
        elif not self._is_available:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {ColorPalette.BG_TERTIARY};
                    border: 1px solid {ColorPalette.BORDER_LIGHT};
                    border-radius: 8px;
                }}
            """)
            self.name_label.setStyleSheet(f"color: {ColorPalette.TEXT_TERTIARY};")
            self.cost_label.setStyleSheet(f"color: {ColorPalette.TEXT_TERTIARY};")
            self.setCursor(Qt.CursorShape.ForbiddenCursor)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {ColorPalette.BG_PRIMARY};
                    border: 1px solid {ColorPalette.BORDER_DEFAULT};
                    border-radius: 8px;
                }}
                QFrame:hover {{
                    border: 2px solid {ColorPalette.PRIMARY};
                    background-color: {ColorPalette.INFO_BG};
                }}
            """)
            self.name_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY};")
            self.cost_label.setStyleSheet(f"color: {ColorPalette.PRIMARY};")
            self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def enterEvent(self, event):
        """Handle mouse enter."""
        self._is_hovered = True
        self.hovered.emit(self.gene_name)
        
        # Show tooltip with gene details
        tooltip_text = self._build_tooltip()
        QToolTip.showText(QCursor.pos(), tooltip_text, self)
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave."""
        self._is_hovered = False
        self.unhovered.emit()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle click."""
        if event.button() == Qt.MouseButton.LeftButton and self._is_available:
            self.clicked.emit(self.gene_name)
        super().mousePressEvent(event)
    
    def _build_tooltip(self) -> str:
        """Build tooltip text for the gene."""
        lines = [f"<b>{self.gene_name}</b>"]
        
        # Description
        desc = self.gene_data.get("description", "")
        if desc:
            lines.append(f"<br/>{desc}")
        
        # Cost
        cost = self.gene_data.get("cost", 0)
        lines.append(f"<br/><b>Cost:</b> {cost} EP")
        
        # Prerequisites
        requires = self.gene_data.get("requires", [])
        if requires:
            lines.append(f"<br/><b>Requires:</b> {', '.join(requires)}")
        
        # Effects summary
        effects = self.gene_data.get("effects", [])
        if effects:
            lines.append("<br/><b>Effects:</b>")
            for effect in effects[:3]:  # Show first 3 effects
                if effect["type"] == "add_transition":
                    rule = effect.get("rule", {})
                    rule_name = rule.get("name", "Unknown")
                    prob = rule.get("probability", 0) * 100
                    lines.append(f"<br/>  • {rule_name} ({prob:.0f}%)")
                elif effect["type"] == "modify_transition":
                    rule_name = effect.get("rule_name", "Unknown")
                    lines.append(f"<br/>  • Modifies: {rule_name}")
            if len(effects) > 3:
                lines.append(f"<br/>  • ... and {len(effects) - 3} more")
        
        # Unavailable reason
        if not self._is_available and self._unavailable_reason:
            reason_text = {
                "already_installed": "Already installed",
                "missing_prerequisites": "Missing prerequisites",
                "polymerase_limit": "Polymerase limit (1 max)",
                "insufficient_ep": "Not enough EP"
            }.get(self._unavailable_reason, self._unavailable_reason)
            lines.append(f"<br/><span style='color: {ColorPalette.DANGER};'><b>⚠ {reason_text}</b></span>")
        
        return "".join(lines)


class InstalledGeneCard(QFrame):
    """A compact card for installed genes."""
    
    clicked = Signal(str)  # gene_name
    remove_clicked = Signal(str)  # gene_name
    
    def __init__(self, gene_name: str, gene_data: Dict, parent=None):
        super().__init__(parent)
        self.gene_name = gene_name
        self.gene_data = gene_data
        self._is_selected = False
        
        self.setup_ui()
        self.update_style()
    
    def setup_ui(self):
        """Setup the card UI."""
        self.setFixedSize(120, 70)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)
        
        # Gene name
        self.name_label = QLabel(self.gene_name)
        self.name_label.setFont(Fonts.small())
        self.name_label.setWordWrap(True)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label)
        
        layout.addStretch()
        
        # Active indicator
        active_label = QLabel("★ Active")
        active_label.setFont(Fonts.small())
        active_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        active_label.setStyleSheet(f"color: {ColorPalette.SUCCESS};")
        layout.addWidget(active_label)
    
    def set_selected(self, selected: bool):
        """Set selection state."""
        self._is_selected = selected
        self.update_style()
    
    def update_style(self):
        """Update card style."""
        if self._is_selected:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {ColorPalette.WARNING_BG};
                    border: 2px solid {ColorPalette.WARNING};
                    border-radius: 6px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {ColorPalette.SUCCESS_BG};
                    border: 1px solid {ColorPalette.SUCCESS};
                    border-radius: 6px;
                }}
                QFrame:hover {{
                    border: 2px solid {ColorPalette.WARNING};
                }}
            """)
    
    def mousePressEvent(self, event):
        """Handle click."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.gene_name)
        super().mousePressEvent(event)


class BlueprintGraphView(QGraphicsView):
    """Interactive visualization of virus transitions."""
    
    entity_hovered = Signal(str)  # entity_name
    transition_hovered = Signal(str)  # transition_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        
        # Setup view properties
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setMinimumHeight(300)
        
        self._db_manager = None
        self._entity_items = {}
        self._transition_items = []
        
        self.setStyleSheet(f"""
            QGraphicsView {{
                background-color: {ColorPalette.BG_PRIMARY};
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: 8px;
            }}
        """)
    
    def set_database_manager(self, db_manager: GeneDatabaseManager):
        """Set database manager for entity lookups."""
        self._db_manager = db_manager
    
    def update_blueprint(self, blueprint: Dict):
        """Update the graph with new blueprint data."""
        self._scene.clear()
        self._entity_items = {}
        self._transition_items = []
        
        if not blueprint:
            return
        
        # Get all entities and organize by location
        entities_by_location = self._organize_entities_by_location(blueprint)
        
        # Calculate layout
        y_offset = 20
        location_y_positions = {}
        entity_positions = {}
        
        scene_width = max(400, self.width() - 40)
        
        for location in LOCATION_DISPLAY_ORDER:
            if location not in entities_by_location:
                continue
            
            entities = entities_by_location[location]
            if not entities:
                continue
            
            # Draw location background
            location_height = max(60, len(entities) * 30 + 40)
            bg_color = QColor(LOCATION_COLORS.get(location, "#f9fafb"))
            bg_rect = self._scene.addRect(
                10, y_offset, scene_width - 20, location_height,
                QPen(QColor(ColorPalette.BORDER_LIGHT)),
                QBrush(bg_color)
            )
            bg_rect.setZValue(-1)
            
            # Location label
            label_text = LOCATION_DISPLAY_LABELS.get(location, location.upper())
            label = self._scene.addText(label_text)
            label.setFont(Fonts.small())
            label.setDefaultTextColor(QColor(ColorPalette.TEXT_SECONDARY))
            label.setPos(15, y_offset + 5)
            
            location_y_positions[location] = y_offset + location_height / 2
            
            # Place entities
            x_spacing = (scene_width - 60) / max(1, len(entities))
            for i, entity_name in enumerate(sorted(entities)):
                x_pos = 30 + i * x_spacing + x_spacing / 2
                y_pos = y_offset + location_height / 2
                
                entity_positions[entity_name] = (x_pos, y_pos)
                self._draw_entity(entity_name, x_pos, y_pos)
            
            y_offset += location_height + 10
        
        # Draw transitions
        transition_rules = blueprint.get("transition_rules", [])
        for rule in transition_rules:
            self._draw_transition(rule, entity_positions)
        
        # Adjust scene size
        self._scene.setSceneRect(0, 0, scene_width, y_offset + 20)
    
    def _organize_entities_by_location(self, blueprint: Dict) -> Dict[str, List[str]]:
        """Organize entities by their location."""
        entities_by_location = {}
        
        for entity_name in blueprint.get("possible_entities", []):
            location = "unknown"
            if self._db_manager:
                entity_data = self._db_manager.get_entity(entity_name)
                if entity_data:
                    location = entity_data.get("location", "unknown")
            
            if location not in entities_by_location:
                entities_by_location[location] = []
            entities_by_location[location].append(entity_name)
        
        return entities_by_location
    
    def _draw_entity(self, entity_name: str, x: float, y: float):
        """Draw an entity node."""
        # Get entity class for color
        entity_class = "unknown"
        if self._db_manager:
            entity_data = self._db_manager.get_entity(entity_name)
            if entity_data:
                entity_class = entity_data.get("entity_class", "unknown")
        
        color = QColor(ENTITY_COLORS.get(entity_class, "#9ca3af"))
        
        # Draw circle
        radius = 12
        ellipse = self._scene.addEllipse(
            x - radius, y - radius, radius * 2, radius * 2,
            QPen(color.darker(120), 2),
            QBrush(color)
        )
        ellipse.setToolTip(entity_name)
        ellipse.setZValue(10)
        
        # Draw label
        # Truncate long names
        display_name = entity_name
        if len(display_name) > 20:
            display_name = display_name[:18] + "..."
        
        label = self._scene.addText(display_name)
        label.setFont(QFont("Segoe UI", 7))
        label.setDefaultTextColor(QColor(ColorPalette.TEXT_PRIMARY))
        label_rect = label.boundingRect()
        label.setPos(x - label_rect.width() / 2, y + radius + 2)
        label.setZValue(10)
        
        self._entity_items[entity_name] = (ellipse, label)
    
    def _draw_transition(self, rule: Dict, entity_positions: Dict):
        """Draw a transition arrow."""
        inputs = rule.get("inputs", [])
        outputs = rule.get("outputs", [])
        
        if not inputs or not outputs:
            return
        
        # Get source and target positions
        source_entities = [i["entity"] for i in inputs]
        target_entities = [o["entity"] for o in outputs]
        
        # Calculate average positions
        source_positions = [entity_positions.get(e) for e in source_entities if e in entity_positions]
        target_positions = [entity_positions.get(e) for e in target_entities if e in entity_positions]
        
        if not source_positions or not target_positions:
            return
        
        src_x = sum(p[0] for p in source_positions) / len(source_positions)
        src_y = sum(p[1] for p in source_positions) / len(source_positions)
        tgt_x = sum(p[0] for p in target_positions) / len(target_positions)
        tgt_y = sum(p[1] for p in target_positions) / len(target_positions)
        
        # Draw arrow line
        path = QPainterPath()
        path.moveTo(src_x, src_y + 12)  # Start below source entity
        
        # Add some curve for visual appeal
        mid_y = (src_y + tgt_y) / 2
        ctrl_x = (src_x + tgt_x) / 2
        
        path.quadTo(ctrl_x, mid_y, tgt_x, tgt_y - 12)  # End above target entity
        
        arrow = self._scene.addPath(
            path,
            QPen(QColor(ColorPalette.TEXT_SECONDARY), 1.5)
        )
        
        # Draw arrowhead
        self._draw_arrowhead(tgt_x, tgt_y - 12, src_x, src_y)
        
        # Add probability label
        prob = rule.get("probability", 0) * 100
        rule_name = rule.get("name", "")
        label_text = f"{prob:.0f}%"
        
        prob_label = self._scene.addText(label_text)
        prob_label.setFont(QFont("Segoe UI", 7))
        prob_label.setDefaultTextColor(QColor(ColorPalette.TEXT_SECONDARY))
        prob_label.setPos(ctrl_x - 10, mid_y - 8)
        
        # Store tooltip on arrow
        tooltip = f"<b>{rule_name}</b><br/>Probability: {prob:.0f}%"
        if rule.get("interferon_amount"):
            tooltip += f"<br/>Interferon: +{rule['interferon_amount']}"
        arrow.setToolTip(tooltip)
        
        self._transition_items.append((arrow, prob_label))
    
    def _draw_arrowhead(self, x: float, y: float, from_x: float, from_y: float):
        """Draw an arrowhead at the end of a line."""
        import math
        
        angle = math.atan2(y - from_y, x - from_x)
        arrow_size = 8
        
        p1_x = x - arrow_size * math.cos(angle - math.pi / 6)
        p1_y = y - arrow_size * math.sin(angle - math.pi / 6)
        p2_x = x - arrow_size * math.cos(angle + math.pi / 6)
        p2_y = y - arrow_size * math.sin(angle + math.pi / 6)
        
        path = QPainterPath()
        path.moveTo(x, y)
        path.lineTo(p1_x, p1_y)
        path.lineTo(p2_x, p2_y)
        path.closeSubpath()
        
        self._scene.addPath(
            path,
            QPen(QColor(ColorPalette.TEXT_SECONDARY)),
            QBrush(QColor(ColorPalette.TEXT_SECONDARY))
        )


class MilestoneCard(QFrame):
    """A card showing milestone progress."""
    
    def __init__(self, milestone_data: Dict, parent=None):
        super().__init__(parent)
        self.milestone_data = milestone_data
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the milestone card UI."""
        self.setFixedSize(180, 70)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)
        
        # Header with status icon and name
        header_layout = QHBoxLayout()
        header_layout.setSpacing(4)
        
        # Status icon
        is_achieved = self.milestone_data.get("achieved", False)
        if is_achieved:
            icon = "✓"
            icon_color = ColorPalette.SUCCESS
        else:
            icon = "▶"
            icon_color = ColorPalette.PRIMARY
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"color: {icon_color}; font-size: 12px;")
        header_layout.addWidget(icon_label)
        
        # Milestone name
        name = self.milestone_data.get("name", "Unknown")
        name_label = QLabel(name)
        name_label.setFont(Fonts.small())
        name_label.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY};")
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Progress or reward
        if is_achieved:
            reward = self.milestone_data.get("reward_ep", 0)
            progress_text = f"+{reward} EP EARNED"
            progress_color = ColorPalette.SUCCESS
        else:
            progress_desc = self.milestone_data.get("progress_description", "")
            progress_text = progress_desc
            progress_color = ColorPalette.TEXT_SECONDARY
        
        progress_label = QLabel(progress_text)
        progress_label.setFont(Fonts.small())
        progress_label.setStyleSheet(f"color: {progress_color};")
        layout.addWidget(progress_label)
        
        # Progress bar if not achieved
        if not is_achieved:
            current = self.milestone_data.get("current_progress", 0)
            target = self.milestone_data.get("target_progress", 1)
            
            progress_bar = QProgressBar()
            progress_bar.setRange(0, target)
            progress_bar.setValue(min(current, target))
            progress_bar.setTextVisible(False)
            progress_bar.setFixedHeight(4)
            progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: {ColorPalette.BG_TERTIARY};
                    border: none;
                    border-radius: 2px;
                }}
                QProgressBar::chunk {{
                    background-color: {ColorPalette.PRIMARY};
                    border-radius: 2px;
                }}
            """)
            layout.addWidget(progress_bar)
        
        # Style the card
        bg_color = ColorPalette.SUCCESS_BG if is_achieved else ColorPalette.BG_PRIMARY
        border_color = ColorPalette.SUCCESS if is_achieved else ColorPalette.BORDER_LIGHT
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
        """)
        
        # Tooltip
        desc = self.milestone_data.get("description", "")
        self.setToolTip(desc)


class HeaderBar(QFrame):
    """Header bar showing game status and actions."""
    
    start_simulation_clicked = Signal()
    back_to_menu_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the header bar UI."""
        self.setFixedHeight(60)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {ColorPalette.BG_PRIMARY};
                border-bottom: 1px solid {ColorPalette.BORDER_LIGHT};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(20)
        
        # Back button
        self.back_btn = QPushButton("← Menu")
        self.back_btn.setFont(Fonts.small())
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {ColorPalette.TEXT_SECONDARY};
                border: none;
                padding: 5px 10px;
            }}
            QPushButton:hover {{
                color: {ColorPalette.PRIMARY};
            }}
        """)
        self.back_btn.clicked.connect(self.back_to_menu_clicked.emit)
        layout.addWidget(self.back_btn)
        
        # EP display
        self.ep_label = QLabel("EP: 0")
        self.ep_label.setFont(Fonts.subheader())
        self.ep_label.setStyleSheet(f"color: {ColorPalette.PRIMARY};")
        layout.addWidget(self.ep_label)
        
        # Separator
        sep1 = QLabel("|")
        sep1.setStyleSheet(f"color: {ColorPalette.BORDER_DEFAULT};")
        layout.addWidget(sep1)
        
        # Starter entity selector
        starter_layout = QHBoxLayout()
        starter_layout.setSpacing(5)
        
        starter_label = QLabel("Starter:")
        starter_label.setFont(Fonts.small())
        starter_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY};")
        starter_layout.addWidget(starter_label)
        
        self.starter_combo = QComboBox()
        self.starter_combo.setFont(Fonts.small())
        self.starter_combo.setMinimumWidth(150)
        self.starter_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {ColorPalette.BG_TERTIARY};
                border: 1px solid {ColorPalette.BORDER_DEFAULT};
                border-radius: 4px;
                padding: 4px 8px;
            }}
        """)
        starter_layout.addWidget(self.starter_combo)
        
        self.starter_count_label = QLabel("(×10)")
        self.starter_count_label.setFont(Fonts.small())
        self.starter_count_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY};")
        starter_layout.addWidget(self.starter_count_label)
        
        layout.addLayout(starter_layout)
        
        layout.addStretch()
        
        # Milestone summary
        self.milestone_label = QLabel("Milestones: 0/0")
        self.milestone_label.setFont(Fonts.small())
        self.milestone_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY};")
        layout.addWidget(self.milestone_label)
        
        # Separator
        sep2 = QLabel("|")
        sep2.setStyleSheet(f"color: {ColorPalette.BORDER_DEFAULT};")
        layout.addWidget(sep2)
        
        # Polymerase status
        self.polymerase_label = QLabel("Polymerase: None")
        self.polymerase_label.setFont(Fonts.small())
        self.polymerase_label.setStyleSheet(f"color: {ColorPalette.WARNING};")
        layout.addWidget(self.polymerase_label)
        
        # Start simulation button
        self.start_btn = QPushButton("Start Simulation ▶")
        self.start_btn.setFont(Fonts.button())
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.setStyleSheet(Styles.PRIMARY_BUTTON)
        self.start_btn.clicked.connect(self.start_simulation_clicked.emit)
        layout.addWidget(self.start_btn)
    
    def update_ep(self, ep: int):
        """Update EP display."""
        self.ep_label.setText(f"EP: {ep}")
    
    def update_starter_entities(self, entities: List[str], selected: str, count: int):
        """Update starter entity selector."""
        self.starter_combo.blockSignals(True)
        self.starter_combo.clear()
        for entity in entities:
            self.starter_combo.addItem(entity)
        
        index = self.starter_combo.findText(selected)
        if index >= 0:
            self.starter_combo.setCurrentIndex(index)
        
        self.starter_combo.blockSignals(False)
        self.starter_count_label.setText(f"(×{count})")
    
    def update_milestones(self, achieved: int, total: int):
        """Update milestone display."""
        self.milestone_label.setText(f"Milestones: {achieved}/{total}")
    
    def update_polymerase(self, gene_name: Optional[str]):
        """Update polymerase status."""
        if gene_name:
            self.polymerase_label.setText(f"Polymerase: ✓")
            self.polymerase_label.setStyleSheet(f"color: {ColorPalette.SUCCESS};")
            self.polymerase_label.setToolTip(gene_name)
        else:
            self.polymerase_label.setText("Polymerase: None")
            self.polymerase_label.setStyleSheet(f"color: {ColorPalette.WARNING};")
            self.polymerase_label.setToolTip("Install a polymerase gene!")


class GeneDeckPanel(QFrame):
    """Panel showing the gene deck with scrollable cards."""
    
    gene_clicked = Signal(str)
    gene_hovered = Signal(str)
    gene_unhovered = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._cards = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the deck panel UI."""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {ColorPalette.BG_PRIMARY};
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: 8px;
            }}
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)
        
        # Header
        header = QLabel("Gene Deck")
        header.setFont(Fonts.subheader())
        header.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY};")
        main_layout.addWidget(header)
        
        # Scroll area for cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFixedHeight(130)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)
        
        # Container widget
        self.cards_container = QWidget()
        self.cards_layout = QHBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        scroll.setWidget(self.cards_container)
        main_layout.addWidget(scroll)
    
    def update_genes(self, deck: List[str], installed: List[str], 
                     gene_data_func, can_install_func):
        """Update displayed genes."""
        # Clear existing cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._cards.clear()
        
        # Add cards for each gene in deck
        for gene_name in deck:
            gene_data = gene_data_func(gene_name)
            if not gene_data:
                continue
            
            card = GeneCard(gene_name, gene_data)
            
            # Check if installed
            is_installed = gene_name in installed
            card.set_installed(is_installed)
            
            # Check availability
            if not is_installed:
                can_install, reason = can_install_func(gene_name)
                card.set_available(can_install, reason)
            
            # Connect signals
            card.clicked.connect(self.gene_clicked.emit)
            card.hovered.connect(self.gene_hovered.emit)
            card.unhovered.connect(self.gene_unhovered.emit)
            
            self.cards_layout.addWidget(card)
            self._cards[gene_name] = card
        
        # Add stretch at end
        self.cards_layout.addStretch()


class InstalledGenesPanel(QFrame):
    """Panel showing installed genes."""
    
    gene_selected = Signal(str)
    remove_clicked = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._cards = {}
        self._selected_gene = None
        self._remove_cost = 10
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the installed genes panel UI."""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {ColorPalette.BG_PRIMARY};
                border: 1px solid {ColorPalette.BORDER_LIGHT};
                border-radius: 8px;
            }}
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        
        header = QLabel("Installed Genes")
        header.setFont(Fonts.subheader())
        header.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY};")
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        self.count_label = QLabel("(0 installed)")
        self.count_label.setFont(Fonts.small())
        self.count_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY};")
        header_layout.addWidget(self.count_label)
        
        main_layout.addLayout(header_layout)
        
        # Cards container with flow layout
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(8)
        main_layout.addWidget(self.cards_container)
        
        main_layout.addStretch()
        
        # Remove button
        self.remove_btn = QPushButton(f"Remove Selected: {self._remove_cost} EP")
        self.remove_btn.setFont(Fonts.small())
        self.remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remove_btn.setEnabled(False)
        self.remove_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {ColorPalette.DANGER};
                border: 1px solid {ColorPalette.DANGER};
                border-radius: 4px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {ColorPalette.DANGER_BG};
            }}
            QPushButton:disabled {{
                color: {ColorPalette.TEXT_TERTIARY};
                border-color: {ColorPalette.BORDER_LIGHT};
            }}
        """)
        self.remove_btn.clicked.connect(self._on_remove_clicked)
        main_layout.addWidget(self.remove_btn)
    
    def update_genes(self, installed: List[str], gene_data_func):
        """Update displayed installed genes."""
        # Clear existing cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._cards.clear()
        self._selected_gene = None
        self.remove_btn.setEnabled(False)
        
        # Add cards
        row, col = 0, 0
        max_cols = 3
        
        for gene_name in installed:
            gene_data = gene_data_func(gene_name)
            if not gene_data:
                continue
            
            card = InstalledGeneCard(gene_name, gene_data)
            card.clicked.connect(self._on_card_clicked)
            
            self.cards_layout.addWidget(card, row, col)
            self._cards[gene_name] = card
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        self.count_label.setText(f"({len(installed)} installed)")
    
    def _on_card_clicked(self, gene_name: str):
        """Handle card selection."""
        # Deselect previous
        if self._selected_gene and self._selected_gene in self._cards:
            self._cards[self._selected_gene].set_selected(False)
        
        # Toggle selection
        if self._selected_gene == gene_name:
            self._selected_gene = None
            self.remove_btn.setEnabled(False)
        else:
            self._selected_gene = gene_name
            self._cards[gene_name].set_selected(True)
            self.remove_btn.setEnabled(True)
        
        self.gene_selected.emit(gene_name if self._selected_gene else "")
    
    def _on_remove_clicked(self):
        """Handle remove button click."""
        if self._selected_gene:
            self.remove_clicked.emit(self._selected_gene)


class MilestonesPanel(QFrame):
    """Panel showing milestone progress."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the milestones panel UI."""
        self.setFixedHeight(100)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {ColorPalette.BG_PRIMARY};
                border-top: 1px solid {ColorPalette.BORDER_LIGHT};
            }}
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 10, 20, 10)
        main_layout.setSpacing(8)
        
        # Header
        header = QLabel("Milestones")
        header.setFont(Fonts.subheader())
        header.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY};")
        main_layout.addWidget(header)
        
        # Scroll area for milestone cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        self.cards_container = QWidget()
        self.cards_layout = QHBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        scroll.setWidget(self.cards_container)
        main_layout.addWidget(scroll)
    
    def update_milestones(self, milestone_progress: Dict):
        """Update milestone display."""
        # Clear existing cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Show achieved milestones first, then open ones
        achieved = milestone_progress.get("achieved", [])
        open_milestones = milestone_progress.get("open", [])
        
        # Show first 2 achieved and first 3 open
        for milestone in achieved[:2]:
            card = MilestoneCard(milestone)
            self.cards_layout.addWidget(card)
        
        for milestone in open_milestones[:3]:
            card = MilestoneCard(milestone)
            self.cards_layout.addWidget(card)
        
        self.cards_layout.addStretch()


class BuildModule(QWidget):
    """Main builder module widget."""
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._view_model = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the builder UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header bar
        self.header = HeaderBar()
        self.header.start_simulation_clicked.connect(self._on_start_simulation)
        self.header.back_to_menu_clicked.connect(self._on_back_to_menu)
        main_layout.addWidget(self.header)
        
        # Gene deck panel
        self.deck_panel = GeneDeckPanel()
        self.deck_panel.gene_clicked.connect(self._on_gene_clicked)
        self.deck_panel.gene_hovered.connect(self._on_gene_hovered)
        self.deck_panel.gene_unhovered.connect(self._on_gene_unhovered)
        main_layout.addWidget(self.deck_panel)
        
        # Content area with splitter
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {ColorPalette.BORDER_LIGHT};
                width: 1px;
            }}
        """)
        
        # Left side: Installed genes
        self.installed_panel = InstalledGenesPanel()
        self.installed_panel.setMinimumWidth(250)
        self.installed_panel.setMaximumWidth(400)
        self.installed_panel.remove_clicked.connect(self._on_remove_gene)
        content_splitter.addWidget(self.installed_panel)
        
        # Right side: Blueprint graph
        blueprint_container = QFrame()
        blueprint_container.setStyleSheet(f"""
            QFrame {{
                background-color: {ColorPalette.BG_SECONDARY};
            }}
        """)
        blueprint_layout = QVBoxLayout(blueprint_container)
        blueprint_layout.setContentsMargins(12, 12, 12, 12)
        blueprint_layout.setSpacing(8)
        
        blueprint_header = QLabel("Virus Blueprint")
        blueprint_header.setFont(Fonts.subheader())
        blueprint_header.setStyleSheet(f"color: {ColorPalette.TEXT_PRIMARY};")
        blueprint_layout.addWidget(blueprint_header)
        
        self.blueprint_view = BlueprintGraphView()
        blueprint_layout.addWidget(self.blueprint_view)
        
        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(15)
        
        legend_label = QLabel("Entity Classes:")
        legend_label.setFont(Fonts.small())
        legend_label.setStyleSheet(f"color: {ColorPalette.TEXT_SECONDARY};")
        legend_layout.addWidget(legend_label)
        
        for entity_class, color in [
            ("Virion", ENTITY_COLORS[ENTITY_CLASS_VIRION]),
            ("RNA", ENTITY_COLORS[ENTITY_CLASS_RNA]),
            ("DNA", ENTITY_COLORS[ENTITY_CLASS_DNA]),
            ("Protein", ENTITY_COLORS[ENTITY_CLASS_PROTEIN]),
            ("Complex", ENTITY_COLORS[ENTITY_CLASS_COMPLEX])
        ]:
            legend_item = QLabel(f"● {entity_class}")
            legend_item.setFont(Fonts.small())
            legend_item.setStyleSheet(f"color: {color};")
            legend_layout.addWidget(legend_item)
        
        legend_layout.addStretch()
        blueprint_layout.addLayout(legend_layout)
        
        content_splitter.addWidget(blueprint_container)
        content_splitter.setStretchFactor(0, 1)
        content_splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(content_splitter, 1)
        
        # Milestones panel
        self.milestones_panel = MilestonesPanel()
        main_layout.addWidget(self.milestones_panel)
        
        # Set background
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {ColorPalette.BG_SECONDARY};
            }}
        """)
    
    def set_game_context(self, game_state: GameState, db_manager: GeneDatabaseManager):
        """Initialize with game context."""
        self._view_model = BuildViewModel(game_state, db_manager)
        
        # Connect signals
        self._view_model.ep_changed.connect(self._update_ep)
        self._view_model.installed_changed.connect(self._update_installed)
        self._view_model.blueprint_changed.connect(self._update_blueprint)
        self._view_model.milestones_changed.connect(self._update_milestones)
        self._view_model.starter_entity_changed.connect(self._update_starter)
        
        # Set database manager for blueprint view
        self.blueprint_view.set_database_manager(db_manager)
        
        # Connect starter entity combo
        self.header.starter_combo.currentTextChanged.connect(self._on_starter_changed)
        
        # Initial update
        self._refresh_all()
    
    def _refresh_all(self):
        """Refresh all UI components."""
        if not self._view_model:
            return
        
        self._update_ep()
        self._update_deck()
        self._update_installed()
        self._update_blueprint()
        self._update_milestones()
        self._update_starter()
        self._update_polymerase()
    
    def _update_ep(self):
        """Update EP display."""
        if self._view_model:
            self.header.update_ep(self._view_model.ep)
    
    def _update_deck(self):
        """Update gene deck display."""
        if not self._view_model:
            return
        
        self.deck_panel.update_genes(
            self._view_model.deck,
            self._view_model.installed_genes,
            self._view_model.get_gene_data,
            self._view_model.can_install_gene
        )
    
    def _update_installed(self):
        """Update installed genes display."""
        if not self._view_model:
            return
        
        self.installed_panel.update_genes(
            self._view_model.installed_genes,
            self._view_model.get_gene_data
        )
        
        # Also update deck (availability may have changed)
        self._update_deck()
        self._update_polymerase()
    
    def _update_blueprint(self):
        """Update blueprint graph."""
        if not self._view_model:
            return
        
        blueprint = self._view_model.get_virus_blueprint()
        self.blueprint_view.update_blueprint(blueprint)
    
    def _update_milestones(self):
        """Update milestones display."""
        if not self._view_model:
            return
        
        progress = self._view_model.get_milestone_progress()
        self.milestones_panel.update_milestones(progress)
        
        # Update header summary
        achieved = len(progress.get("achieved", []))
        total = achieved + len(progress.get("open", []))
        self.header.update_milestones(achieved, total)
    
    def _update_starter(self):
        """Update starter entity selector."""
        if not self._view_model:
            return
        
        self.header.update_starter_entities(
            self._view_model.available_starter_entities,
            self._view_model.selected_starter_entity,
            self._view_model.starting_entity_count
        )
    
    def _update_polymerase(self):
        """Update polymerase status."""
        if not self._view_model:
            return
        
        self.header.update_polymerase(self._view_model.get_polymerase_gene())
    
    def _on_gene_clicked(self, gene_name: str):
        """Handle gene card click."""
        if not self._view_model:
            return
        
        gene_data = self._view_model.get_gene_data(gene_name)
        if not gene_data:
            return
        
        cost = gene_data.get("cost", 0)
        
        # Confirm if expensive
        if cost > 20:
            reply = QMessageBox.question(
                self,
                "Install Gene",
                f"Install '{gene_name}' for {cost} EP?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Try to install
        if not self._view_model.install_gene(gene_name):
            can_install, reason = self._view_model.can_install_gene(gene_name)
            reason_text = {
                "already_installed": "Gene is already installed",
                "missing_prerequisites": "Missing required prerequisite genes",
                "polymerase_limit": "Only one polymerase gene allowed",
                "insufficient_ep": "Not enough EP"
            }.get(reason, reason)
            
            QMessageBox.warning(
                self,
                "Cannot Install",
                f"Cannot install '{gene_name}':\n{reason_text}"
            )
    
    def _on_gene_hovered(self, gene_name: str):
        """Handle gene hover - could preview on blueprint."""
        # Future: highlight what this gene would add to blueprint
        pass
    
    def _on_gene_unhovered(self):
        """Handle gene unhover."""
        pass
    
    def _on_remove_gene(self, gene_name: str):
        """Handle gene removal request."""
        if not self._view_model:
            return
        
        reply = QMessageBox.question(
            self,
            "Remove Gene",
            f"Remove '{gene_name}' for 10 EP?\n\nNote: This will also remove any genes that depend on it.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if not self._view_model.remove_gene(gene_name):
                QMessageBox.warning(
                    self,
                    "Cannot Remove",
                    "Not enough EP to remove this gene."
                )
    
    def _on_starter_changed(self, entity_name: str):
        """Handle starter entity selection change."""
        if self._view_model and entity_name:
            self._view_model.set_starter_entity(entity_name)
    
    def _on_start_simulation(self):
        """Handle start simulation click."""
        if not self._view_model:
            return
        
        # Check if we have a polymerase
        if not self._view_model.has_polymerase():
            reply = QMessageBox.question(
                self,
                "No Polymerase",
                "You haven't installed a polymerase gene!\n\n"
                "Without a polymerase, your virus cannot replicate its genome.\n\n"
                "Start simulation anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Get the blueprint and start simulation
        blueprint = self._view_model.get_virus_blueprint()
        
        # Notify controller to start play module
        self.controller.start_simulation(blueprint, self._view_model._virus_builder)
    
    def _on_back_to_menu(self):
        """Handle back to menu click."""
        reply = QMessageBox.question(
            self,
            "Return to Menu",
            "Return to main menu?\n\nYour current progress will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.controller.switch_to_module("menu")
    
    def show(self):
        """Show the builder module."""
        super().show()
        self._refresh_all()
    
    def hide(self):
        """Hide the builder module."""
        super().hide()
