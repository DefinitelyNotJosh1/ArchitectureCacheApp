"""
Operation Panel for Cache Learning Application
Displays current operation and allows student input
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGroupBox, QRadioButton, QButtonGroup, QPushButton,
                             QSpinBox, QLineEdit, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal


class OperationPanel(QWidget):
    """Panel for displaying current operation and collecting student answers"""
    
    check_answer = pyqtSignal()
    next_operation = pyqtSignal()
    previous_operation = pyqtSignal()
    reset_exercise = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Current Operation Display
        op_group = QGroupBox("Current Operation")
        op_layout = QVBoxLayout()
        self.operation_label = QLabel("No operation")
        self.operation_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        op_layout.addWidget(self.operation_label)
        self.address_label = QLabel("Address: -")
        op_layout.addWidget(self.address_label)
        self.value_label = QLabel("Value: -")
        op_layout.addWidget(self.value_label)
        op_group.setLayout(op_layout)
        layout.addWidget(op_group)
        
        # Hit/Miss Selection
        hit_miss_group = QGroupBox("Hit or Miss?")
        hit_miss_layout = QVBoxLayout()
        self.hit_miss_group = QButtonGroup()
        self.hit_radio = QRadioButton("Hit")
        self.miss_radio = QRadioButton("Miss")
        self.hit_miss_group.addButton(self.hit_radio, 0)
        self.hit_miss_group.addButton(self.miss_radio, 1)
        hit_miss_layout.addWidget(self.hit_radio)
        hit_miss_layout.addWidget(self.miss_radio)
        hit_miss_group.setLayout(hit_miss_layout)
        layout.addWidget(hit_miss_group)
        
        # Address Decomposition
        decomp_group = QGroupBox("Address Decomposition")
        decomp_layout = QVBoxLayout()
        
        # Tag
        tag_layout = QHBoxLayout()
        tag_layout.addWidget(QLabel("Tag:"))
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Enter tag (binary)")
        tag_layout.addWidget(self.tag_input)
        decomp_layout.addLayout(tag_layout)
        
        # Block Index
        block_idx_layout = QHBoxLayout()
        block_idx_layout.addWidget(QLabel("Block Index:"))
        self.block_idx_input = QLineEdit()
        self.block_idx_input.setPlaceholderText("Enter block index (binary)")
        block_idx_layout.addWidget(self.block_idx_input)
        decomp_layout.addLayout(block_idx_layout)
        
        # Block Offset
        block_off_layout = QHBoxLayout()
        block_off_layout.addWidget(QLabel("Block Offset:"))
        self.block_off_input = QLineEdit()
        self.block_off_input.setPlaceholderText("Enter block offset (binary)")
        block_off_layout.addWidget(self.block_off_input)
        decomp_layout.addLayout(block_off_layout)
        
        # Byte Offset
        byte_off_layout = QHBoxLayout()
        byte_off_layout.addWidget(QLabel("Byte Offset:"))
        self.byte_off_input = QLineEdit()
        self.byte_off_input.setPlaceholderText("Enter byte offset (binary)")
        byte_off_layout.addWidget(self.byte_off_input)
        decomp_layout.addLayout(byte_off_layout)
        
        decomp_group.setLayout(decomp_layout)
        layout.addWidget(decomp_group)
        
        # Feedback Area
        feedback_group = QGroupBox("Feedback")
        feedback_layout = QVBoxLayout()
        self.feedback_text = QTextEdit()
        self.feedback_text.setReadOnly(True)
        self.feedback_text.setMaximumHeight(100)
        feedback_layout.addWidget(self.feedback_text)
        feedback_group.setLayout(feedback_layout)
        layout.addWidget(feedback_group)
        
        # Navigation Buttons
        button_layout = QHBoxLayout()
        self.check_button = QPushButton("Check Answer")
        self.check_button.clicked.connect(self.check_answer.emit)
        self.previous_button = QPushButton("Previous")
        self.previous_button.clicked.connect(self.previous_operation.emit)
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_operation.emit)
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_exercise.emit)
        
        button_layout.addWidget(self.check_button)
        button_layout.addWidget(self.previous_button)
        button_layout.addWidget(self.next_button)
        button_layout.addWidget(self.reset_button)
        layout.addLayout(button_layout)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def update_operation(self, operation_type: str, address: int, value: int = None):
        """Update operation display"""
        if operation_type == 'read':
            self.operation_label.setText(f"Read Operation")
            self.address_label.setText(f"Address: {hex(address)}")
            self.value_label.setText("Value: (to be read)")
        else:
            self.operation_label.setText(f"Write Operation")
            self.address_label.setText(f"Address: {hex(address)}")
            self.value_label.setText(f"Value: {value}")
        
        # Clear inputs
        self.hit_radio.setChecked(False)
        self.miss_radio.setChecked(False)
        self.tag_input.clear()
        self.block_idx_input.clear()
        self.block_off_input.clear()
        self.byte_off_input.clear()
        self.feedback_text.clear()
    
    def get_hit_miss_answer(self) -> bool:
        """Get student's hit/miss answer (True = hit, False = miss)"""
        return self.hit_radio.isChecked()
    
    def get_address_decomposition(self) -> tuple:
        """Get student's address decomposition"""
        try:
            tag = int(self.tag_input.text(), 2) if self.tag_input.text() else 0
            block_idx = int(self.block_idx_input.text(), 2) if self.block_idx_input.text() else 0
            block_off = int(self.block_off_input.text(), 2) if self.block_off_input.text() else 0
            byte_off = int(self.byte_off_input.text(), 2) if self.byte_off_input.text() else 0
            return tag, block_idx, block_off, byte_off
        except ValueError:
            return 0, 0, 0, 0
    
    def set_feedback(self, message: str, is_correct: bool = None):
        """Set feedback message"""
        self.feedback_text.clear()
        if message:
            self.feedback_text.append(message)
            if is_correct is True:
                self.feedback_text.setStyleSheet("color: green;")
            elif is_correct is False:
                self.feedback_text.setStyleSheet("color: red;")
            else:
                self.feedback_text.setStyleSheet("")
    
    def clear_feedback(self):
        """Clear feedback"""
        self.feedback_text.clear()
        self.feedback_text.setStyleSheet("")

