"""
Exercise Manager for Cache Learning Application
Manages questions, attempts, and progression
"""

from typing import List, Dict, Tuple, Optional
from cache_simulator import CacheSimulator
from memory_simulator import MemorySimulator


class ExerciseOperation:
    """Represents a single operation in an exercise"""
    
    def __init__(self, operation_type: str, address: int, value: Optional[int] = None):
        """
        Initialize operation
        
        Args:
            operation_type: 'read' or 'write'
            address: Memory address
            value: Value to write (for write operations)
        """
        self.operation_type = operation_type
        self.address = address
        self.value = value
    
    def __repr__(self):
        if self.operation_type == 'read':
            return f"Read @ {hex(self.address)}"
        else:
            return f"Write @ {hex(self.address)} = {self.value}"


class ExerciseManager:
    """Manages exercise sequences and student progress"""
    
    def __init__(self, cache_simulator: CacheSimulator, memory_simulator: MemorySimulator):
        """
        Initialize exercise manager
        
        Args:
            cache_simulator: CacheSimulator instance
            memory_simulator: MemorySimulator instance
        """
        self.cache = cache_simulator
        self.memory = memory_simulator
        self.operations: List[ExerciseOperation] = []
        self.current_operation_index = 0
        self.attempts_per_question = {}  # Track attempts for each question
        self.max_attempts = 2
    
    def load_exercise(self, operations: List[ExerciseOperation], reset_cache=True):
        """
        Load an exercise sequence
        
        Args:
            operations: List of ExerciseOperation objects
            reset_cache: Whether to reset cache and memory before starting
        """
        self.operations = operations
        self.current_operation_index = 0
        self.attempts_per_question = {}
        
        if reset_cache:
            self.cache.reset()
            self.memory.reset()
    
    def get_current_operation(self) -> Optional[ExerciseOperation]:
        """Get the current operation"""
        if 0 <= self.current_operation_index < len(self.operations):
            return self.operations[self.current_operation_index]
        return None
    
    def get_operation_number(self) -> int:
        """Get current operation number (1-indexed)"""
        return self.current_operation_index + 1
    
    def get_total_operations(self) -> int:
        """Get total number of operations"""
        return len(self.operations)
    
    def has_next(self) -> bool:
        """Check if there are more operations"""
        return self.current_operation_index < len(self.operations) - 1
    
    def has_previous(self) -> bool:
        """Check if there are previous operations"""
        return self.current_operation_index > 0
    
    def next_operation(self):
        """Move to next operation"""
        if self.has_next():
            self.current_operation_index += 1
    
    def previous_operation(self):
        """Move to previous operation"""
        if self.has_previous():
            self.current_operation_index -= 1
    
    def go_to_operation(self, index: int):
        """Go to a specific operation index"""
        if 0 <= index < len(self.operations):
            self.current_operation_index = index
    
    def get_attempts_for_current(self) -> int:
        """Get number of attempts for current question"""
        return self.attempts_per_question.get(self.current_operation_index, 0)
    
    def validate_hit_miss(self, student_answer: bool, actual_hit: bool = None) -> Tuple[bool, bool, Optional[str]]:
        """
        Validate student's hit/miss answer
        
        Args:
            student_answer: True for hit, False for miss
            actual_hit: Pre-computed hit/miss result (if None, will compute)
        
        Returns:
            Tuple of (is_correct, should_auto_advance, feedback_message)
        """
        op = self.get_current_operation()
        if not op:
            return False, False, "No current operation"
        
        # Get actual result (use provided or compute)
        if actual_hit is None:
            # Perform the operation to get actual result
            if op.operation_type == 'read':
                hit, value, state = self.cache.read(op.address)
            else:
                hit, state = self.cache.write(op.address, op.value)
            actual_hit = hit
        
        is_correct = (actual_hit == student_answer)
        attempts = self.get_attempts_for_current()
        
        if is_correct:
            self.attempts_per_question[self.current_operation_index] = 0  # Reset attempts
            return True, True, "Correct!"
        else:
            attempts += 1
            self.attempts_per_question[self.current_operation_index] = attempts
            
            if attempts >= self.max_attempts:
                # Auto-correct and advance
                return False, True, f"Incorrect. The correct answer is {'Hit' if actual_hit else 'Miss'}."
            else:
                return False, False, "Incorrect, try again."
    
    def validate_address_decomposition(self, tag: int, block_index: int, 
                                      byte_offset: int, block_offset: int) -> Tuple[bool, bool, Optional[str]]:
        """
        Validate student's address decomposition
        
        Args:
            tag: Student's tag value
            block_index: Student's block index value
            byte_offset: Student's byte offset value
            block_offset: Student's block offset value
        
        Returns:
            Tuple of (is_correct, should_auto_advance, feedback_message)
        """
        op = self.get_current_operation()
        if not op:
            return False, False, "No current operation"
        
        # Get correct decomposition
        correct_tag, correct_block_index, correct_block_offset, correct_byte_offset = \
            self.cache.calculate_address_components(op.address)
        
        # Compare (all must match)
        tag_correct = (tag == correct_tag)
        block_index_correct = (block_index == correct_block_index)
        byte_offset_correct = (byte_offset == correct_byte_offset)
        block_offset_correct = (block_offset == correct_block_offset)
        
        all_correct = tag_correct and block_index_correct and byte_offset_correct and block_offset_correct
        
        attempts = self.get_attempts_for_current()
        
        if all_correct:
            self.attempts_per_question[self.current_operation_index] = 0
            return True, True, "Correct!"
        else:
            attempts += 1
            self.attempts_per_question[self.current_operation_index] = attempts
            
            if attempts >= self.max_attempts:
                # Auto-correct and show correct answer
                feedback = f"Incorrect. Correct answer: Tag={correct_tag}, BlockIdx={correct_block_index}, "
                feedback += f"BlockOff={correct_block_offset}, ByteOff={correct_byte_offset}"
                return False, True, feedback
            else:
                errors = []
                if not tag_correct:
                    errors.append(f"Tag (correct: {correct_tag})")
                if not block_index_correct:
                    errors.append(f"Block Index (correct: {correct_block_index})")
                if not block_offset_correct:
                    errors.append(f"Block Offset (correct: {correct_block_offset})")
                if not byte_offset_correct:
                    errors.append(f"Byte Offset (correct: {correct_byte_offset})")
                return False, False, f"Incorrect: {', '.join(errors)}. Try again."
    
    def get_correct_address_decomposition(self) -> Tuple[int, int, int, int]:
        """Get correct address decomposition for current operation"""
        op = self.get_current_operation()
        if not op:
            return 0, 0, 0, 0
        return self.cache.calculate_address_components(op.address)
    
    def get_correct_hit_miss(self) -> bool:
        """Get correct hit/miss for current operation (without performing it)"""
        # This would require simulating up to current point
        # For now, we'll perform the operation
        op = self.get_current_operation()
        if not op:
            return False
        
        if op.operation_type == 'read':
            hit, value, state = self.cache.read(op.address)
        else:
            hit, state = self.cache.write(op.address, op.value)
        
        return hit
    
    def reset_to_beginning(self):
        """Reset exercise to beginning"""
        self.current_operation_index = 0
        self.attempts_per_question = {}
        self.cache.reset()
        self.memory.reset()
    
    def execute_current_operation(self) -> Tuple[bool, Optional[int], dict]:
        """
        Execute current operation and return result
        
        Returns:
            Tuple of (hit/miss, value (if read), state_info)
        """
        op = self.get_current_operation()
        if not op:
            return False, None, {}
        
        if op.operation_type == 'read':
            hit, value, state = self.cache.read(op.address)
            return hit, value, state
        else:
            hit, state = self.cache.write(op.address, op.value)
            return hit, None, state

