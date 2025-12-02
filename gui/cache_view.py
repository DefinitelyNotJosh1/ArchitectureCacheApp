"""
Cache View for Cache Learning Application
Displays cache table with entries
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class CacheView(QWidget):
    """Widget for displaying cache state"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.highlighted_set = None
        self.highlighted_way = None
        self.last_operation_hit = None
        self.tag_bits = 6  # Default, will be updated from cache
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        title = QLabel("Cache")
        title.setStyleSheet("font-weight: bold; font-size: 14pt;")
        layout.addWidget(title)
        
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(True)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def update_cache(self, cache_state: dict, associativity: int = 1, 
                    highlighted_set: int = None, highlighted_way: int = None,
                    is_hit: bool = None, tag_bits: int = 6):
        """
        Update cache display
        
        Args:
            cache_state: Dict from cache.get_cache_state()
            associativity: Number of ways
            highlighted_set: Set index to highlight
            highlighted_way: Way index to highlight (for set-associative)
            is_hit: Whether last operation was hit (for color coding)
            tag_bits: Number of tag bits for display
        """
        self.highlighted_set = highlighted_set
        self.highlighted_way = highlighted_way
        self.last_operation_hit = is_hit
        self.tag_bits = tag_bits
        
        if associativity == 1:
            # Direct-mapped cache
            self._update_direct_mapped(cache_state)
        else:
            # Set-associative cache
            self._update_set_associative(cache_state, associativity)
    
    def _update_direct_mapped(self, cache_state: dict):
        """Update display for direct-mapped cache"""
        num_sets = len(cache_state)
        
        # Set up table
        self.table.setRowCount(num_sets)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Valid", "Tag", "Data", ""])
        
        for set_idx in range(num_sets):
            entry = cache_state[set_idx]['ways'][0]
            
            # Valid bit
            valid_item = QTableWidgetItem("1" if entry['valid'] else "0")
            self.table.setItem(set_idx, 0, valid_item)
            
            # Tag
            if entry['valid']:
                tag_item = QTableWidgetItem(f"{entry['tag']:0{self._get_tag_bits()}b}")
            else:
                tag_item = QTableWidgetItem("-")
            self.table.setItem(set_idx, 1, tag_item)
            
            # Data
            if entry['valid']:
                data_str = ", ".join(str(word) for word in entry['data'])
            else:
                data_str = "-"
            data_item = QTableWidgetItem(data_str)
            self.table.setItem(set_idx, 2, data_item)
            
            # Empty column for spacing
            self.table.setItem(set_idx, 3, QTableWidgetItem(""))
            
            # Highlight if this is the target set
            if set_idx == self.highlighted_set:
                color = QColor(144, 238, 144) if self.last_operation_hit else QColor(255, 182, 193)
                for col in range(4):
                    item = self.table.item(set_idx, col)
                    if item:
                        item.setBackground(color)
        
        self.table.resizeColumnsToContents()
    
    def _update_set_associative(self, cache_state: dict, associativity: int):
        """Update display for set-associative cache"""
        num_sets = len(cache_state)
        
        # Set up table with columns for each way
        num_cols = 2 + associativity * 3  # Set, then (V, Tag, Data) for each way
        self.table.setRowCount(num_sets)
        self.table.setColumnCount(num_cols)
        
        # Create header
        headers = ["Set"]
        for way in range(associativity):
            headers.extend([f"V{way}", f"Tag{way}", f"Data{way}"])
        self.table.setHorizontalHeaderLabels(headers)
        
        for set_idx in range(num_sets):
            # Set index
            set_item = QTableWidgetItem(str(set_idx))
            self.table.setItem(set_idx, 0, set_item)
            
            col = 1
            for way_idx, way_entry in enumerate(cache_state[set_idx]['ways']):
                # Valid bit
                valid_item = QTableWidgetItem("1" if way_entry['valid'] else "0")
                self.table.setItem(set_idx, col, valid_item)
                col += 1
                
                # Tag
                if way_entry['valid']:
                    tag_item = QTableWidgetItem(f"{way_entry['tag']:0{self._get_tag_bits()}b}")
                else:
                    tag_item = QTableWidgetItem("-")
                self.table.setItem(set_idx, col, tag_item)
                col += 1
                
                # Data
                if way_entry['valid']:
                    data_str = ", ".join(str(word) for word in way_entry['data'])
                else:
                    data_str = "-"
                data_item = QTableWidgetItem(data_str)
                self.table.setItem(set_idx, col, data_item)
                col += 1
                
                # Highlight if this is the target set and way
                if (set_idx == self.highlighted_set and 
                    way_idx == self.highlighted_way):
                    color = QColor(144, 238, 144) if self.last_operation_hit else QColor(255, 182, 193)
                    for c in range(col - 3, col):
                        item = self.table.item(set_idx, c)
                        if item:
                            item.setBackground(color)
        
        self.table.resizeColumnsToContents()
    
    def _get_tag_bits(self) -> int:
        """Get number of tag bits for display"""
        return self.tag_bits

