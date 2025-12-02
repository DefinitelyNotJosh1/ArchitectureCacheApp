"""
Memory View for Cache Learning Application
Displays memory contents
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QLabel, QCheckBox, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal


class MemoryView(QWidget):
    """Widget for displaying memory contents"""
    
    go_to_address = pyqtSignal(int)  # Signal to scroll to address
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.recent_addresses = set()
        self.all_addresses_mode = False
    
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
        
        # Store memory contents for refresh
        self.memory_contents = {}
        
        self.setLayout(layout)
    
    def update_memory(self, memory_contents: dict, recent_addresses: set = None):
        """
        Update memory display
        
        Args:
            memory_contents: Dict of {address: value}
            recent_addresses: Set of recently accessed addresses to highlight
        """
        # Store for refresh
        self.memory_contents = memory_contents.copy()
        
        if recent_addresses:
            self.recent_addresses = recent_addresses.copy()
        else:
            self.recent_addresses = set()
        
        self._refresh_display()
    
    def _refresh_display(self):
        """Refresh the memory display based on current filter settings"""
        # Filter addresses if not showing all
        if not self.show_all_checkbox.isChecked():
            # Only show modified/recent addresses
            addresses_to_show = set(self.memory_contents.keys()) | self.recent_addresses
        else:
            # Show all addresses in memory (0 to 64K-1, word-aligned)
            addresses_to_show = set(range(0, 65536, 4))
        
        # Sort addresses in descending order (highest at top)
        sorted_addresses = sorted(addresses_to_show, reverse=True)
        
        self.table.setRowCount(len(sorted_addresses))
        
        for row, addr in enumerate(sorted_addresses):
            # Address
            addr_item = QTableWidgetItem(hex(addr))
            addr_item.setFlags(addr_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, addr_item)
            
            # Value
            value = self.memory_contents.get(addr, 0)
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
        self._refresh_display()
    
    def scroll_to_address(self, address: int):
        """Scroll table to show the given address"""
        # Find the row with this address
        for row in range(self.table.rowCount()):
            addr_item = self.table.item(row, 0)
            if addr_item:
                try:
                    addr_text = addr_item.text()
                    addr_value = int(addr_text, 16)
                    if addr_value == address:
                        self.table.scrollToItem(addr_item)
                        # Highlight it
                        for col in range(2):
                            item = self.table.item(row, col)
                            if item:
                                item.setBackground(Qt.GlobalColor.cyan)
                        return
                except ValueError:
                    continue

