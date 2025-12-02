"""
Predefined Exercise Sequences for Cache Learning Application
Based on the worksheet examples
"""

from exercise_manager import ExerciseOperation
from memory_simulator import MemorySimulator


def get_part2_exercise(memory: MemorySimulator) -> list:
    """
    Part 2 Exercise: Direct-mapped cache with 4-word blocks
    Based on the first worksheet image
    """
    # Initialize memory with values from the worksheet
    memory.initialize_custom({
        0x26C0: 22,
        0x26C4: 33,
        0x26C8: 44,
        0x26CC: 55,
        0x3520: 66,
        0x3524: 77,
        0x3528: 88,
        0x352C: 99,
    })
    
    operations = [
        ExerciseOperation('read', 0xBD28),  # Should be miss, read 6666
        ExerciseOperation('read', 0xBD24),  # Should be hit, read 5555
        ExerciseOperation('read', 0x8128),  # Should be miss, read 777
    ]
    
    return operations


def get_part3_exercise(memory: MemorySimulator) -> list:
    """
    Part 3 Exercise: 2-way set-associative cache with LRU
    Based on the second worksheet image
    """
    # Initialize memory with values from the worksheet
    memory.initialize_custom({
        0x3238: 123,
        0x3748: 234,
        0x9238: 345,
        0x92A8: 456,
        0xF038: 567,
        0xF0A8: 678,
    })
    
    operations = [
        ExerciseOperation('read', 0x3738),  # Miss, read 123
        ExerciseOperation('read', 0xF0A8),  # Miss, read 678
        ExerciseOperation('read', 0x92A8),  # Miss, read 456
    ]
    
    return operations


def get_simple_direct_mapped_exercise(memory: MemorySimulator) -> list:
    """
    Simple direct-mapped cache exercise for beginners
    """
    # Initialize some memory values
    memory.initialize_custom({
        0x1000: 100,
        0x1004: 200,
        0x1008: 300,
        0x100C: 400,
        0x2000: 500,
        0x2004: 600,
    })
    
    operations = [
        ExerciseOperation('read', 0x1000),  # Miss
        ExerciseOperation('read', 0x1004),  # Hit (same block)
        ExerciseOperation('read', 0x2000),  # Miss (different block)
        ExerciseOperation('read', 0x1000),  # Hit (cached)
    ]
    
    return operations


def get_write_exercise(memory: MemorySimulator) -> list:
    """
    Exercise with write operations
    """
    memory.initialize_custom({
        0x3000: 1000,
        0x3004: 2000,
        0x4000: 3000,
    })
    
    operations = [
        ExerciseOperation('read', 0x3000),   # Miss
        ExerciseOperation('write', 0x3004, 2500),  # Hit (same block)
        ExerciseOperation('read', 0x4000),   # Miss
        ExerciseOperation('read', 0x3004),   # Hit (should read 2500)
    ]
    
    return operations


# Exercise registry
EXERCISE_REGISTRY = {
    "Part 2 - Direct-Mapped (4-word blocks)": get_part2_exercise,
    "Part 3 - 2-Way Set-Associative (LRU)": get_part3_exercise,
    "Simple Direct-Mapped": get_simple_direct_mapped_exercise,
    "Write Operations": get_write_exercise,
}


def get_exercise_names() -> list:
    """Get list of available exercise names"""
    return list(EXERCISE_REGISTRY.keys())


def load_exercise(name: str, memory: MemorySimulator) -> list:
    """
    Load a predefined exercise by name
    
    Args:
        name: Exercise name
        memory: MemorySimulator instance to initialize
    
    Returns:
        List of ExerciseOperation objects
    """
    if name in EXERCISE_REGISTRY:
        return EXERCISE_REGISTRY[name](memory)
    else:
        raise ValueError(f"Unknown exercise: {name}")

