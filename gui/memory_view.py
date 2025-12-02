"""
Memory View for Cache Learning Application
Displays memory contents
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QCheckBox)
from PyQt6.QtCore import Qt


class MemoryView(QWidget):
    """Widget for displaying memory contents"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.recent_addresses = set()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        
        title = QLabel("Main Memory")
        title.setStyleSheet("font-weight: bold; font-size: 14pt;")
        layout.addWidget(title)
        
        self.show_all_checkbox = QCheckBox("Show all addresses")
        self.show_all_checkbox.toggled.connect(self.on_show_all_toggled)
        layout.addWidget(self.show_all_checkbox)
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Address", "Value"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def update_memory(self, memory_contents: dict, recent_addresses: set = None):
        """
        Update memory display
        
        Args:
            memory_contents: Dict of {address: value}
            recent_addresses: Set of recently accessed addresses to highlight
        """
        if recent_addresses:
            self.recent_addresses = recent_addresses.copy()
        else:
            self.recent_addresses = set()
        
        # Filter addresses if not showing all
        if not self.show_all_checkbox.isChecked():
            # Only show modified/recent addresses
            addresses_to_show = set(memory_contents.keys()) | self.recent_addresses
        else:
            # Show all addresses in range
            if memory_contents:
                min_addr = min(memory_contents.keys())
                max_addr = max(memory_contents.keys())
                addresses_to_show = set(range(min_addr, max_addr + 4, 4))
            else:
                addresses_to_show = set()
        
        # Sort addresses
        sorted_addresses = sorted(addresses_to_show)
        
        self.table.setRowCount(len(sorted_addresses))
        
        for row, addr in enumerate(sorted_addresses):
            # Address
            addr_item = QTableWidgetItem(hex(addr))
            addr_item.setFlags(addr_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, addr_item)
            
            # Value
            value = memory_contents.get(addr, 0)
            value_item = QTableWidgetItem(str(value))
            value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, value_item)
            
            # Highlight recent addresses
            if addr in self.recent_addresses:
                addr_item.setBackground(Qt.GlobalColor.yellow)
                value_item.setBackground(Qt.GlobalColor.yellow)
        
        self.table.resizeColumnsToContents()
    
    def on_show_all_toggled(self, checked):
        """Handle show all checkbox toggle"""
        # This would trigger a refresh - for now just update display
        pass

