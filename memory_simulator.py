"""
Memory Simulator for Cache Learning Application
Simulates a 64K byte memory with 16-bit addresses, word-addressable (4 bytes per word)
"""


class MemorySimulator:
    """Simulates main memory with 64K bytes (16-bit addresses)"""
    
    def __init__(self, size_kb=64):
        """
        Initialize memory simulator
        
        Args:
            size_kb: Memory size in KB (default 64KB)
        """
        self.size_bytes = size_kb * 1024
        self.words_per_address = 4  # 4 bytes per word
        self.num_words = self.size_bytes // self.words_per_address
        
        # Memory storage: address -> value (word)
        self.memory = {}
        self.modified_addresses = set()
        
        # Initialize with default values (0) or can be customized
        self._initialize_default()
    
    def _initialize_default(self):
        """Initialize memory with default values"""
        # Initialize all addresses to 0
        for addr in range(0, self.size_bytes, self.words_per_address):
            self.memory[addr] = 0
    
    def initialize_custom(self, address_value_pairs):
        """
        Initialize memory with custom values
        
        Args:
            address_value_pairs: List of tuples (address, value) or dict {address: value}
        """
        if isinstance(address_value_pairs, dict):
            for addr, value in address_value_pairs.items():
                self.write(addr, value)
        else:
            for addr, value in address_value_pairs:
                self.write(addr, value)
    
    def read(self, address):
        """
        Read a word from memory
        
        Args:
            address: Memory address (must be word-aligned, i.e., multiple of 4)
        
        Returns:
            int: Value at the address
        """
        # Ensure address is word-aligned
        address = (address // self.words_per_address) * self.words_per_address
        
        if address < 0 or address >= self.size_bytes:
            raise ValueError(f"Address {hex(address)} out of range")
        
        return self.memory.get(address, 0)
    
    def read_block(self, start_address, block_size_words):
        """
        Read a block of words from memory
        
        Args:
            start_address: Starting address (word-aligned)
            block_size_words: Number of words to read
        
        Returns:
            list: List of word values
        """
        start_address = (start_address // self.words_per_address) * self.words_per_address
        block = []
        for i in range(block_size_words):
            addr = start_address + (i * self.words_per_address)
            block.append(self.read(addr))
        return block
    
    def write(self, address, value):
        """
        Write a word to memory
        
        Args:
            address: Memory address (must be word-aligned)
            value: Value to write
        """
        # Ensure address is word-aligned
        address = (address // self.words_per_address) * self.words_per_address
        
        if address < 0 or address >= self.size_bytes:
            raise ValueError(f"Address {hex(address)} out of range")
        
        self.memory[address] = value
        self.modified_addresses.add(address)
    
    def write_block(self, start_address, block_data):
        """
        Write a block of words to memory
        
        Args:
            start_address: Starting address (word-aligned)
            block_data: List of word values to write
        """
        start_address = (start_address // self.words_per_address) * self.words_per_address
        for i, value in enumerate(block_data):
            addr = start_address + (i * self.words_per_address)
            self.write(addr, value)
    
    def get_modified_addresses(self):
        """Get set of addresses that have been modified"""
        return self.modified_addresses.copy()
    
    def reset(self):
        """Reset memory to default state"""
        self.memory.clear()
        self.modified_addresses.clear()
        self._initialize_default()
    
    def get_all_addresses(self):
        """Get all addresses that have been written to"""
        return sorted(self.memory.keys())
    
    def get_address_range(self, start_addr, end_addr):
        """
        Get memory contents in a range
        
        Args:
            start_addr: Start address
            end_addr: End address (exclusive)
        
        Returns:
            dict: {address: value} for the range
        """
        result = {}
        start_addr = (start_addr // self.words_per_address) * self.words_per_address
        end_addr = (end_addr // self.words_per_address) * self.words_per_address
        
        for addr in range(start_addr, end_addr, self.words_per_address):
            if addr in self.memory:
                result[addr] = self.memory[addr]
        return result

