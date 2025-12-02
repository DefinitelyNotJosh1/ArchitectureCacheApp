"""
Cache Simulator for Cache Learning Application
Supports direct-mapped and N-way set-associative caches
"""

import math
from typing import Tuple, List, Optional


class CacheEntry:
    """Represents a single cache entry"""
    
    def __init__(self, block_size_words=1):
        self.valid = False
        self.tag = 0
        self.data = [0] * block_size_words  # List of words in block
        self.dirty = False  # For write-back policy
        self.use_bit = 0  # For LRU in set-associative caches
        self.block_start_address = 0  # Track original block address for write-back
    
    def __repr__(self):
        return f"CacheEntry(valid={self.valid}, tag={self.tag}, data={self.data}, dirty={self.dirty}, use_bit={self.use_bit})"


class CacheSimulator:
    """Simulates cache memory with configurable parameters"""
    
    def __init__(self, cache_size_slots=256, block_size_words=1, associativity=1, 
                 write_policy='write-through', memory_simulator=None):
        """
        Initialize cache simulator
        
        Args:
            cache_size_slots: Number of cache slots (sets)
            block_size_words: Number of words per block
            associativity: Number of ways (1 = direct-mapped, >1 = set-associative)
            write_policy: 'write-through' or 'write-back'
            memory_simulator: Reference to MemorySimulator instance
        """
        self.cache_size_slots = cache_size_slots
        self.block_size_words = block_size_words
        self.associativity = associativity
        self.write_policy = write_policy
        self.memory = memory_simulator
        
        # Calculate address bit breakdown
        self.total_address_bits = 16  # 64K memory = 16 bits
        self.bytes_per_word = 4
        self.byte_offset_bits = int(math.log2(self.bytes_per_word))  # 2 bits
        self.block_offset_bits = int(math.log2(block_size_words))  # log2(block_size_words)
        self.block_index_bits = int(math.log2(cache_size_slots))  # log2(cache_size_slots)
        self.tag_bits = (self.total_address_bits - 
                        self.block_index_bits - 
                        self.block_offset_bits - 
                        self.byte_offset_bits)
        
        # Initialize cache structure
        # For direct-mapped: cache[set_index] = CacheEntry
        # For set-associative: cache[set_index] = [CacheEntry, ...] (list of ways)
        self.cache = {}
        self._initialize_cache()
        
        # Statistics
        self.hits = 0
        self.misses = 0
    
    def _initialize_cache(self):
        """Initialize cache structure"""
        if self.associativity == 1:
            # Direct-mapped: one entry per set
            for i in range(self.cache_size_slots):
                self.cache[i] = CacheEntry(self.block_size_words)
        else:
            # Set-associative: multiple entries per set
            for i in range(self.cache_size_slots):
                self.cache[i] = [CacheEntry(self.block_size_words) 
                                for _ in range(self.associativity)]
    
    def calculate_address_components(self, address: int) -> Tuple[int, int, int, int]:
        """
        Decompose address into components
        
        Args:
            address: Memory address
        
        Returns:
            Tuple of (tag, block_index, block_offset, byte_offset)
        """
        # Extract components using bit masks
        byte_offset = address & ((1 << self.byte_offset_bits) - 1)
        address >>= self.byte_offset_bits
        
        block_offset = address & ((1 << self.block_offset_bits) - 1)
        address >>= self.block_offset_bits
        
        block_index = address & ((1 << self.block_index_bits) - 1)
        address >>= self.block_index_bits
        
        tag = address & ((1 << self.tag_bits) - 1)
        
        return tag, block_index, block_offset, byte_offset
    
    def _get_block_start_address(self, address: int) -> int:
        """Get the starting address of the block containing the given address"""
        # Clear byte offset and block offset bits
        block_start = (address >> (self.byte_offset_bits + self.block_offset_bits)) << (self.byte_offset_bits + self.block_offset_bits)
        return block_start
    
    def _find_entry_in_set(self, set_index: int, tag: int) -> Optional[CacheEntry]:
        """Find cache entry with matching tag in a set (for set-associative)"""
        if self.associativity == 1:
            entry = self.cache[set_index]
            if entry.valid and entry.tag == tag:
                return entry
        else:
            for entry in self.cache[set_index]:
                if entry.valid and entry.tag == tag:
                    return entry
        return None
    
    def _select_victim_entry(self, set_index: int) -> CacheEntry:
        """Select which entry to evict in a set (LRU for set-associative)"""
        if self.associativity == 1:
            return self.cache[set_index]
        else:
            # Find entry with lowest use_bit (LRU)
            entries = self.cache[set_index]
            victim = entries[0]
            for entry in entries:
                if not entry.valid:
                    return entry
                if entry.use_bit < victim.use_bit:
                    victim = entry
            return victim
    
    def _update_lru(self, set_index: int, accessed_entry: CacheEntry):
        """Update LRU counters after accessing an entry"""
        if self.associativity > 1:
            max_use_bit = max(entry.use_bit for entry in self.cache[set_index] if entry.valid)
            accessed_entry.use_bit = max_use_bit + 1
    
    def _load_block_from_memory(self, block_start_address: int) -> List[int]:
        """Load a block from memory"""
        if self.memory:
            return self.memory.read_block(block_start_address, self.block_size_words)
        else:
            # Return zeros if no memory simulator
            return [0] * self.block_size_words
    
    def _write_back_if_needed(self, entry: CacheEntry, block_start_address: int):
        """Write back dirty block to memory if needed (for write-back policy)"""
        if self.write_policy == 'write-back' and entry.dirty and self.memory:
            self.memory.write_block(block_start_address, entry.data)
            entry.dirty = False
    
    def read(self, address: int) -> Tuple[bool, int, dict]:
        """
        Read from cache
        
        Args:
            address: Memory address to read
        
        Returns:
            Tuple of (hit/miss, value, updated_cache_state)
            - hit/miss: True for hit, False for miss
            - value: The value read
            - updated_cache_state: Dict with cache state info
        """
        tag, block_index, block_offset, byte_offset = self.calculate_address_components(address)
        block_start_address = self._get_block_start_address(address)
        
        # Check for hit
        entry = self._find_entry_in_set(block_index, tag)
        
        if entry:
            # Cache hit
            self.hits += 1
            value = entry.data[block_offset]
            self._update_lru(block_index, entry)
            
            return True, value, {
                'hit': True,
                'set_index': block_index,
                'way': self._get_way_index(block_index, entry) if self.associativity > 1 else 0,
                'tag': tag,
                'block_offset': block_offset
            }
        else:
            # Cache miss - load block from memory
            self.misses += 1
            block_data = self._load_block_from_memory(block_start_address)
            
            # Select victim entry
            victim = self._select_victim_entry(block_index)
            
            # Write back if needed
            if victim.valid:
                victim_block_start = self._get_block_start_address_from_entry(victim)
                self._write_back_if_needed(victim, victim_block_start)
            
            # Load new block
            victim.valid = True
            victim.tag = tag
            victim.data = block_data.copy()
            victim.dirty = False
            victim.block_start_address = block_start_address
            self._update_lru(block_index, victim)
            
            value = block_data[block_offset]
            
            return False, value, {
                'hit': False,
                'set_index': block_index,
                'way': self._get_way_index(block_index, victim) if self.associativity > 1 else 0,
                'tag': tag,
                'block_offset': block_offset,
                'evicted': victim.valid if victim != self.cache[block_index] else False
            }
    
    def _get_block_start_address_from_entry(self, entry: CacheEntry) -> int:
        """Get block start address from cache entry"""
        return entry.block_start_address
    
    def _get_way_index(self, set_index: int, entry: CacheEntry) -> int:
        """Get the way index of an entry in a set"""
        if self.associativity == 1:
            return 0
        for i, e in enumerate(self.cache[set_index]):
            if e is entry:
                return i
        return 0
    
    def write(self, address: int, value: int) -> Tuple[bool, dict]:
        """
        Write to cache
        
        Args:
            address: Memory address to write
            value: Value to write
        
        Returns:
            Tuple of (hit/miss, updated_cache_state)
        """
        tag, block_index, block_offset, byte_offset = self.calculate_address_components(address)
        block_start_address = self._get_block_start_address(address)
        
        # Check for hit
        entry = self._find_entry_in_set(block_index, tag)
        
        if entry:
            # Cache hit
            self.hits += 1
            entry.data[block_offset] = value
            if self.write_policy == 'write-back':
                entry.dirty = True
            else:  # write-through
                if self.memory:
                    self.memory.write(address, value)
            self._update_lru(block_index, entry)
            
            return True, {
                'hit': True,
                'set_index': block_index,
                'way': self._get_way_index(block_index, entry) if self.associativity > 1 else 0,
                'tag': tag,
                'block_offset': block_offset
            }
        else:
            # Cache miss
            self.misses += 1
            
            if self.write_policy == 'write-through':
                # Write-through: update memory directly
                if self.memory:
                    self.memory.write(address, value)
            else:
                # Write-back: load block, modify, mark dirty
                block_data = self._load_block_from_memory(block_start_address)
                block_data[block_offset] = value
                
                victim = self._select_victim_entry(block_index)
                if victim.valid:
                    victim_block_start = self._get_block_start_address_from_entry(victim)
                    self._write_back_if_needed(victim, victim_block_start)
                
                victim.valid = True
                victim.tag = tag
                victim.data = block_data
                victim.dirty = True
                victim.block_start_address = block_start_address
                self._update_lru(block_index, victim)
            
            return False, {
                'hit': False,
                'set_index': block_index,
                'way': self._get_way_index(block_index, self._select_victim_entry(block_index)) if self.associativity > 1 else 0,
                'tag': tag,
                'block_offset': block_offset
            }
    
    def get_cache_state(self) -> dict:
        """Get current cache state for display"""
        state = {}
        for set_idx in range(self.cache_size_slots):
            if self.associativity == 1:
                entry = self.cache[set_idx]
                state[set_idx] = {
                    'ways': [{
                        'valid': entry.valid,
                        'tag': entry.tag,
                        'data': entry.data.copy(),
                        'dirty': entry.dirty,
                        'use_bit': entry.use_bit
                    }]
                }
            else:
                ways = []
                for entry in self.cache[set_idx]:
                    ways.append({
                        'valid': entry.valid,
                        'tag': entry.tag,
                        'data': entry.data.copy(),
                        'dirty': entry.dirty,
                        'use_bit': entry.use_bit
                    })
                state[set_idx] = {'ways': ways}
        return state
    
    def reset(self):
        """Reset cache to initial state"""
        self._initialize_cache()
        self.hits = 0
        self.misses = 0
    
    def get_statistics(self) -> dict:
        """Get cache statistics"""
        total_accesses = self.hits + self.misses
        hit_rate = (self.hits / total_accesses * 100) if total_accesses > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'total': total_accesses,
            'hit_rate': hit_rate
        }

