"""
Main Window for Cache Learning Application
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QSplitter, QMenuBar, QMenu, QMessageBox)
from PyQt6.QtCore import Qt
from gui.config_panel import ConfigPanel
from gui.cache_view import CacheView
from gui.memory_view import MemoryView
from gui.operation_panel import OperationPanel
from gui.stats_panel import StatsPanel
from cache_simulator import CacheSimulator
from memory_simulator import MemorySimulator
from exercise_manager import ExerciseManager, ExerciseOperation
from predefined_exercises import get_exercise_names, load_exercise


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.cache = None
        self.memory = None
        self.exercise_manager = None
        self.init_ui()
        self.setup_default_config()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Cache Learning Application")
        self.setGeometry(100, 100, 1400, 800)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Create panels
        self.config_panel = ConfigPanel()
        self.cache_view = CacheView()
        self.memory_view = MemoryView()
        self.operation_panel = OperationPanel()
        self.stats_panel = StatsPanel()
        
        # Connect signals
        self.config_panel.config_changed.connect(self.on_config_changed)
        self.operation_panel.check_answer.connect(self.on_check_answer)
        self.operation_panel.next_operation.connect(self.on_next_operation)
        self.operation_panel.previous_operation.connect(self.on_previous_operation)
        self.operation_panel.reset_exercise.connect(self.on_reset_exercise)
        
        # Left side: Config panel
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.config_panel)
        left_widget.setLayout(left_layout)
        left_widget.setMaximumWidth(250)
        
        # Center: Cache and Memory views
        center_splitter = QSplitter(Qt.Orientation.Vertical)
        center_splitter.addWidget(self.cache_view)
        center_splitter.addWidget(self.memory_view)
        center_splitter.setSizes([400, 300])
        
        # Right side: Operation and Stats panels
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.operation_panel)
        right_layout.addWidget(self.stats_panel)
        right_widget.setLayout(right_layout)
        right_widget.setMaximumWidth(400)
        
        # Main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(center_splitter)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([250, 800, 400])
        
        main_layout.addWidget(main_splitter)
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        reset_action = file_menu.addAction("Reset")
        reset_action.triggered.connect(self.on_reset_exercise)
        load_exercise_action = file_menu.addAction("Load Exercise")
        load_exercise_action.triggered.connect(self.on_load_exercise)
        file_menu.addSeparator()
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.on_about)
    
    def setup_default_config(self):
        """Set up default configuration"""
        self.config_panel.apply_config()
    
    def on_config_changed(self, config: dict):
        """Handle configuration change"""
        # Create new cache and memory simulators
        self.memory = MemorySimulator()
        
        self.cache = CacheSimulator(
            cache_size_slots=config['cache_size_slots'],
            block_size_words=config['block_size_words'],
            associativity=config['associativity'],
            write_policy=config['write_policy'],
            memory_simulator=self.memory
        )
        
        # Create exercise manager
        self.exercise_manager = ExerciseManager(self.cache, self.memory)
        
        # Update displays
        self.update_all_displays()
    
    def on_check_answer(self):
        """Handle check answer button click"""
        if not self.exercise_manager:
            self.operation_panel.set_feedback("Please configure cache first.", False)
            return
        
        op = self.exercise_manager.get_current_operation()
        if not op:
            self.operation_panel.set_feedback("No current operation.", False)
            return
        
        # Execute operation once to get actual result
        hit, value, state = self.exercise_manager.execute_current_operation()
        actual_hit = hit
        
        # Validate hit/miss using the actual result
        hit_miss_answer = self.operation_panel.get_hit_miss_answer()
        is_correct_hm, should_advance_hm, feedback_hm = \
            self.exercise_manager.validate_hit_miss(hit_miss_answer, actual_hit)
        
        # Validate address decomposition
        tag, block_idx, block_off, byte_off = self.operation_panel.get_address_decomposition()
        is_correct_decomp, should_advance_decomp, feedback_decomp = \
            self.exercise_manager.validate_address_decomposition(tag, block_idx, byte_off, block_off)
        
        # Combine feedback
        all_correct = is_correct_hm and is_correct_decomp
        should_advance = should_advance_hm or should_advance_decomp
        
        if all_correct:
            feedback = "Correct! Both hit/miss and address decomposition are correct."
            self.operation_panel.set_feedback(feedback, True)
            if should_advance and self.exercise_manager.has_next():
                self.exercise_manager.next_operation()
                self.update_operation_display()
        else:
            feedback_parts = []
            if not is_correct_hm:
                feedback_parts.append(feedback_hm)
            if not is_correct_decomp:
                feedback_parts.append(feedback_decomp)
            feedback = "\n".join(feedback_parts)
            self.operation_panel.set_feedback(feedback, False)
            
            if should_advance:
                # Auto-correct: show correct answer and advance
                correct_tag, correct_bi, correct_bo, correct_byo = \
                    self.exercise_manager.get_correct_address_decomposition()
                
                # Update UI with correct answers
                if actual_hit:
                    self.operation_panel.hit_radio.setChecked(True)
                else:
                    self.operation_panel.miss_radio.setChecked(True)
                
                # Convert to binary strings
                tag_bits = self.cache.tag_bits
                bi_bits = self.cache.block_index_bits
                bo_bits = self.cache.block_offset_bits
                byo_bits = self.cache.byte_offset_bits
                
                self.operation_panel.tag_input.setText(f"{correct_tag:0{tag_bits}b}")
                self.operation_panel.block_idx_input.setText(f"{correct_bi:0{bi_bits}b}")
                self.operation_panel.block_off_input.setText(f"{correct_bo:0{bo_bits}b}")
                self.operation_panel.byte_off_input.setText(f"{correct_byo:0{byo_bits}b}")
                
                if self.exercise_manager.has_next():
                    self.exercise_manager.next_operation()
                    self.update_operation_display()
        
        # Update displays with hit/miss info
        self.update_all_displays_with_hit_miss(actual_hit)
    
    def on_next_operation(self):
        """Handle next operation button"""
        if self.exercise_manager and self.exercise_manager.has_next():
            self.exercise_manager.next_operation()
            self.update_operation_display()
            self.update_all_displays()
    
    def on_previous_operation(self):
        """Handle previous operation button"""
        if self.exercise_manager and self.exercise_manager.has_previous():
            self.exercise_manager.previous_operation()
            self.update_operation_display()
            self.update_all_displays()
    
    def on_reset_exercise(self):
        """Handle reset exercise"""
        if self.exercise_manager:
            self.exercise_manager.reset_to_beginning()
            self.update_operation_display()
            self.update_all_displays()
    
    def on_load_exercise(self):
        """Handle load exercise menu action"""
        if not self.exercise_manager:
            QMessageBox.warning(self, "Warning", "Please configure cache first.")
            return
        
        # Show exercise selection dialog
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Load Exercise")
        layout = QVBoxLayout()
        
        exercise_list = QListWidget()
        exercise_names = get_exercise_names()
        exercise_list.addItems(exercise_names)
        if exercise_names:
            exercise_list.setCurrentRow(0)
        layout.addWidget(exercise_list)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_items = exercise_list.selectedItems()
            if selected_items:
                exercise_name = selected_items[0].text()
                try:
                    operations = load_exercise(exercise_name, self.memory)
                    self.exercise_manager.load_exercise(operations, reset_cache=True)
                    self.update_operation_display()
                    self.update_all_displays()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to load exercise: {str(e)}")
    
    def on_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About", 
                         "Cache Learning Application\n\n"
                         "A tool for learning cache memory concepts.")
    
    def update_operation_display(self):
        """Update operation panel display"""
        if not self.exercise_manager:
            return
        
        op = self.exercise_manager.get_current_operation()
        if op:
            self.operation_panel.update_operation(op.operation_type, op.address, op.value)
        else:
            self.operation_panel.update_operation('read', 0, None)
    
    def update_all_displays(self, is_hit: bool = None):
        """Update all display panels"""
        self.update_all_displays_with_hit_miss(is_hit)
    
    def update_all_displays_with_hit_miss(self, is_hit: bool = None):
        """Update all display panels with hit/miss information"""
        if not self.cache or not self.memory:
            return
        
        # Update cache view
        cache_state = self.cache.get_cache_state()
        op = self.exercise_manager.get_current_operation() if self.exercise_manager else None
        
        highlighted_set = None
        highlighted_way = None
        
        if op:
            tag, block_idx, block_off, byte_off = self.cache.calculate_address_components(op.address)
            highlighted_set = block_idx
            # Try to find which way contains this tag
            highlighted_way = 0
            if self.cache.associativity > 1:
                set_entries = cache_state[block_idx]['ways']
                for way_idx, way_entry in enumerate(set_entries):
                    if way_entry['valid'] and way_entry['tag'] == tag:
                        highlighted_way = way_idx
                        break
        
        self.cache_view.update_cache(
            cache_state, 
            self.cache.associativity,
            highlighted_set,
            highlighted_way,
            is_hit,
            self.cache.tag_bits
        )
        
        # Update memory view
        memory_contents = {}
        for addr in self.memory.get_all_addresses():
            memory_contents[addr] = self.memory.read(addr)
        
        recent_addresses = set()
        if op:
            recent_addresses.add(op.address)
        
        self.memory_view.update_memory(memory_contents, recent_addresses)
        
        # Update stats panel
        stats = self.cache.get_statistics()
        current_op = self.exercise_manager.get_operation_number() if self.exercise_manager else 0
        total_ops = self.exercise_manager.get_total_operations() if self.exercise_manager else 0
        self.stats_panel.update_stats(stats['hits'], stats['misses'], current_op, total_ops)

