# Cache Learning Application

An interactive educational tool for learning cache memory concepts, including direct-mapped and set-associative caches.

## Features

- **Cache Simulation**: Supports both direct-mapped and N-way set-associative caches
- **Configurable Parameters**: 
  - Cache size (number of slots)
  - Block size (1, 2, 4, or 8 words)
  - Associativity (direct-mapped or 2/4/8-way set-associative)
  - Write policy (write-through or write-back)
- **Interactive Exercises**: Predefined exercises based on worksheets
- **Procedural Mode**: Practice mode without exercise limits
- **Address Decomposition**: Learn how addresses are broken down into tag, block index, block offset, and byte offset
- **Hit/Miss Detection**: Practice identifying cache hits and misses
- **Visual Feedback**: Color-coded cache entries (green for hits, red for misses)
- **Statistics Tracking**: Monitor hit rate and cache performance

## Installation

1. Install Python 3.7 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

### Basic Workflow

1. **Configure Cache**: Use the left panel to set cache parameters
   - Select cache type (Direct-Mapped or Set-Associative)
   - Choose cache size, block size, and write policy
   - Click "Apply" to initialize

2. **Load Exercise** (optional):
   - Go to File → Load Exercise
   - Select a predefined exercise from the list
   - The exercise will initialize memory and provide a sequence of operations

3. **Procedural Mode** (alternative):
   - Go to File → Clear Exercise (Procedural Mode)
   - Use File → Randomize Memory to populate memory with random values
   - Perform operations without a fixed sequence

4. **Answer Questions**:
   - For each operation, determine if it's a hit or miss
   - Decompose the address into its components (Tag, Block Index, Block Offset, Byte Offset)
   - Click "Check Answer" to validate
   - Use "Go to Address" button to locate addresses in memory view

5. **Navigate**:
   - Use Previous/Next buttons to move between operations
   - Use Reset to start over

### Understanding the Display

- **Cache View**: Shows cache entries with valid bits, tags, and data
  - Entries are displayed from highest to lowest address (bottom-up)
  - Highlighted entries indicate the current operation's target
  - Green highlight = hit, Red highlight = miss

- **Memory View**: Shows main memory contents
  - Toggle "Show all addresses" to view entire memory or just modified addresses
  - Recent addresses are highlighted in yellow
  - Addresses are displayed from highest to lowest

- **Operation Panel**: Current operation and input fields
  - Block Offset field only appears when block size > 1 word
  - "Go to Address" button scrolls memory view to the address

- **Statistics Panel**: Displays hit/miss counts and hit rate

## Exercises

The application includes several predefined exercises:

- **Part 2 - Direct-Mapped (4-word blocks)**: Exercises with direct-mapped cache and multi-word blocks
- **Part 3 - 2-Way Set-Associative (LRU)**: Exercises with set-associative cache and LRU replacement
- **Simple Direct-Mapped**: Basic exercises for beginners
- **Write Operations**: Exercises involving write operations

## Address Decomposition

A 16-bit address is decomposed as follows:
- **Tag**: Upper bits identifying the memory block
- **Block Index**: Bits selecting which cache set/slot
- **Block Offset**: Bits selecting word within block (only when block size > 1)
- **Byte Offset**: Lower bits for byte selection within word (always 2 bits)

The number of bits for each component depends on:
- Cache size (determines block index bits)
- Block size (determines block offset bits)
- Total address bits (16 for 64K memory)

## Tips

- Start with simple exercises to understand basic concepts
- Pay attention to block boundaries when determining hits/misses
- In set-associative caches, multiple blocks can map to the same set
- Use the "Go to Address" feature to visualize memory layout
- ize memory in procedural mode to create custom practice scenarios

## Technical Details

- **Memory**: 64KB (16-bit addresses), word-addressable (4 bytes per word)
- **Cache**: Configurable size, block size, and associativity
- **Replacement Policy**: LRU (Least Recently Used) for set-associative caches
- **Write Policies**: Write-through and write-back supported

## License

This is an educational tool for learning cache memory concepts.

