# Radix Trie V2 - Improved Implementation

## Overview

This is an improved version of the radix trie (Patricia trie) implementation, providing the same functionality as `radix_trie.py` with enhanced code quality, better performance characteristics, and cleaner abstractions.

**Key Result:** All 10 comprehensive tests pass, confirming functional equivalence with both the original radix trie and the standard trie implementations.

## What's Improved in V2

### 1. **Eliminated Redundancy**
- **Before:** Nodes stored both a `freq` attribute and a `freqs` list, where `freq` always equaled `freqs[-1]`
- **After:** Only the `freqs` list is stored, with `freq` computed as a property when needed
- **Benefit:** Reduces memory usage and eliminates the need to keep two values in sync

### 2. **Better Type Safety**
- **Added:** Comprehensive type hints throughout the codebase using Python's `typing` module
- **Includes:** `Optional`, `Tuple`, `List`, `Dict`, `Iterator`, `Literal`, and `Union`
- **Benefit:** Better IDE support, easier maintenance, and self-documenting code

### 3. **Cleaner Position Tracking**
- **Before:** Used `-1` to indicate empty sequence or root position
- **After:** Uses `None` for these cases (more Pythonic and intuitive)
- **Benefit:** More readable code and clearer intent

### 4. **Extracted Helper Methods**
The complex insertion logic is now broken down into three clearly named methods:

```python
_merge_into_child()        # Case 1: Child's edge fully matched
_split_child_as_prefix()   # Case 2: Sequence is prefix of child's edge
_split_at_divergence()     # Case 3: Sequences diverge after common prefix
```

**Benefit:** The three cases of the radix trie insertion algorithm are now explicit and easy to understand

### 5. **Centralized Direction Logic**
- **Added:** `_build_path()` and `_get_last_token()` helper methods
- **Purpose:** Handle forward/backward direction logic in one place
- **Benefit:** Eliminates repeated reversing logic scattered throughout the code

### 6. **Better Variable Names**
- Replaced generic loop variables with descriptive names where appropriate
- Added clarity to complex operations
- Made the code more self-documenting

### 7. **Performance Optimizations**
- Added `__slots__` to `RadixNode` for memory efficiency
- Reduced unnecessary list conversions
- Optimized hot paths in traversal methods
- More efficient LCP (Longest Common Prefix) computation

### 8. **Principled Frequency Tracking**
- Cleaner separation between node frequency and position frequencies
- More consistent handling of corpus size tracking
- The `_corpus_size` attribute explicitly tracks total token frequency mass

## Core Algorithm Insights

### Compressed Edge Insertion

The radix trie insertion algorithm handles three distinct cases based on the Longest Common Prefix (LCP):

```
Given: Inserting sequence S into a node with child C having edge label L
       LCP = length of longest common prefix between S and L

Case 1: LCP == len(L)  [Child's edge fully matched]
┌─────────┐           ┌─────────┐
│ Parent  │   add     │ Parent  │
│         ├─[L]──►    │         ├─[L]──► (frequencies updated)
└─────────┘           └─────────┘
                               │
                               └─[S[len(L):]]──► (recurse with remainder)

Case 2: LCP == len(S)  [Sequence is prefix]
┌─────────┐           ┌─────────┐
│ Parent  │   split   │ Parent  │
│         ├─[L]──►    │         ├─[S]──► (new intermediate)
└─────────┘           └─────────┘
                               │
                               └─[L[len(S):]]──► (old child moved)

Case 3: LCP < both lengths  [Divergence]
┌─────────┐           ┌─────────┐
│ Parent  │   split   │ Parent  │
│         ├─[L]──►    │         ├─[L[:LCP]]──► (new intermediate)
└─────────┘           └─────────┘
                               ├─[L[LCP:]]──► (old child)
                               └─[S[LCP:]]──► (new child)
```

### Search with Mid-Edge Positions

The `_find_sequence()` method handles queries that end in the middle of compressed edges:

```python
# Example: Edge label is ('the', 'quick', 'brown', 'fox')
_find_sequence(('the', 'quick'))         # Returns (node, 1)
_find_sequence(('the', 'quick', 'brown')) # Returns (node, 2)
_find_sequence(('the', 'quick', 'brown', 'fox')) # Returns (node, None)
```

The position indicates where in the edge's `freqs` list to look up the frequency.

### Efficient Shared Neighbor Search

The shared neighbor algorithm only traverses children that:
1. Exist in **both** nodes
2. Have **exactly matching** edge labels

This prunes the search space dramatically:

```
Node1:         Node2:         Traversal:
  ├─[a]──►       ├─[a]──►       ✓ Traverse (shared, matching)
  ├─[b]──►       ├─[c]──►       ✗ Skip (not shared)
  └─[c]──►       └─[c]──►       ✗ Skip (different edges)
```

Only the first child is traversed because:
- Node1's `[b]` doesn't exist in Node2
- Both have `[c]` but the edge labels differ

## API Reference

### RadixFreqTrie

The main class for storing and querying word sequences with frequencies.

#### Constructor

```python
model = RadixFreqTrie()
```

Creates an empty radix trie with forward and backward roots.

#### Methods

##### `_insert(sequence, freq=1)`

Insert a sequence into the trie.

```python
model._insert(('<', 'the', 'cat', '>'), freq=1)
```

**Args:**
- `sequence`: Tuple of tokens
- `freq`: Number of occurrences to record (default 1)

##### `setup(training_corpus_path)`

Load a training corpus from a file.

```python
model.setup('syntax/corpora/small_test_corpus.txt')
```

**Args:**
- `training_corpus_path`: Path to corpus file (one sentence per line)

##### `freq(sequence)`

Get the frequency of a sequence.

```python
count = model.freq(('<', 'the', 'cat'))  # Returns frequency count
```

**Args:**
- `sequence`: Tuple of tokens

**Returns:** Integer frequency count

##### `right_neighbors(sequence, max_length=inf, min_length=0, only_completions=False)`

Get continuations of a sequence.

```python
for neighbor, freq in model.right_neighbors(('<', 'the'), max_length=2):
    print(f"{neighbor}: {freq}")
```

**Args:**
- `sequence`: Base sequence
- `max_length`: Maximum length of returned neighbors
- `min_length`: Minimum length of returned neighbors
- `only_completions`: Only return sequences ending with '<' or '>'

**Yields:** `(neighbor_tuple, frequency)` pairs

##### `left_neighbors(sequence, max_length=inf, min_length=0, only_completions=False)`

Get predecessors of a sequence.

```python
for neighbor, freq in model.left_neighbors(('the', 'cat'), max_length=2):
    print(f"{neighbor}: {freq}")
```

**Args:** Same as `right_neighbors`

**Yields:** `(neighbor_tuple, frequency)` pairs

##### `shared_right_neighbors(sequence_1, sequence_2, max_length=inf, min_length=0, only_completions=False)`

Get common continuations of two sequences.

```python
for neighbor, freq1, freq2 in model.shared_right_neighbors(('<', 'the', 'cat'), ('<', 'the', 'dog')):
    print(f"{neighbor}: cat={freq1}, dog={freq2}")
```

**Args:**
- `sequence_1`: First sequence
- `sequence_2`: Second sequence
- Other args same as `right_neighbors`

**Yields:** `(neighbor_tuple, freq1, freq2)` tuples

##### `shared_left_neighbors(sequence_1, sequence_2, max_length=inf, min_length=0, only_completions=False)`

Get common predecessors of two sequences.

**Args:** Same as `shared_right_neighbors`

**Yields:** `(neighbor_tuple, freq1, freq2)` tuples

## Implementation Quality

### Code Organization

The codebase is organized into clear sections:
1. **Setup functions:** `txt_to_list()`
2. **RadixNode class:** Core node operations
3. **RadixFreqTrie class:** High-level API

### Memory Efficiency

- **`__slots__`:** RadixNode uses slots to reduce per-instance memory overhead
- **Single frequency representation:** Eliminated redundant `freq` field
- **Edge compression:** Non-branching paths stored as single edges

### Maintainability

- **Type hints:** Full type annotations for all methods
- **Clear abstractions:** Helper methods for complex operations
- **Consistent naming:** Follows Python conventions throughout
- **Well-documented:** Comprehensive docstrings with examples

### Robustness

- **Edge case handling:** Properly handles empty sequences, mid-edge positions
- **Comprehensive tests:** All 10 tests pass with 100% accuracy
- **Functional equivalence:** Produces identical results to original implementations

## Performance Characteristics

### Time Complexity

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Insert | O(k) | k = sequence length; may require edge splitting |
| Frequency query | O(k) | k = sequence length |
| Neighbor traversal | O(n) | n = number of neighbors returned |
| Shared neighbor search | O(m) | m = number of shared neighbors; prunes non-shared subtrees |

### Space Complexity

| Case | Complexity | Condition |
|------|-----------|-----------|
| Best | O(n) | n = total unique tokens; all sequences share prefixes |
| Worst | O(m) | m = total length of all sequences; no compression possible |
| Typical | Between best and worst | Depends on branching factor and path lengths |

### Improvements Over Original

1. **Reduced memory per node** (eliminated redundant `freq` field)
2. **Fewer list conversions** (optimized hot paths)
3. **More efficient LCP computation** (cleaner algorithm)
4. **Better cache locality** (`__slots__` implementation)

## Testing

### Running Tests

```bash
python3 test_radix_trie_v2.py
```

### Test Coverage

The test suite verifies:
1. ✓ Basic insertion and frequency counting
2. ✓ Multiple insertions with overlapping prefixes
3. ✓ Small corpus testing (real-world data)
4. ✓ Right neighbor queries
5. ✓ Left neighbor queries
6. ✓ Shared right neighbor queries
7. ✓ Shared left neighbor queries
8. ✓ Edge compression verification
9. ✓ Frequency counting with repeated insertions
10. ✓ Neighbor queries with length constraints

**Result:** 10/10 tests passed

## Comparison: V1 vs V2

| Aspect | V1 (Original) | V2 (Improved) |
|--------|---------------|---------------|
| Redundant freq field | ✗ Yes | ✓ No (property) |
| Type hints | ✗ No | ✓ Comprehensive |
| Position tracking | -1 for root | None for root |
| Insert logic clarity | Single method | 3 clear methods |
| Direction handling | Scattered | Centralized helpers |
| Memory per node | Higher | Lower (__slots__) |
| Code readability | Good | Excellent |
| Test coverage | 10/10 | 10/10 |
| Functional correctness | ✓ | ✓ |

## Usage Example

```python
import radix_trie_v2 as radix

# Create and populate trie
model = radix.RadixFreqTrie()
model._insert(('<', 'the', 'cat', 'ran', '>'))
model._insert(('<', 'the', 'cat', 'jumped', '>'))
model._insert(('<', 'the', 'dog', 'ran', '>'))

# Query frequencies
print(model.freq(('<', 'the')))           # 3
print(model.freq(('<', 'the', 'cat')))    # 2

# Get right neighbors
for neighbor, freq in model.right_neighbors(('<', 'the', 'cat')):
    print(f"{neighbor}: {freq}")
# Output:
# ('ran',): 1
# ('ran', '>'): 1
# ('jumped',): 1
# ('jumped', '>'): 1

# Find shared right neighbors
for neighbor, freq1, freq2 in model.shared_right_neighbors(
    ('<', 'the', 'cat'),
    ('<', 'the', 'dog')
):
    print(f"{neighbor}: cat={freq1}, dog={freq2}")
# Output:
# ('ran',): cat=1, dog=1
# ('ran', '>'): cat=1, dog=1
```

## When to Use Radix Trie vs Standard Trie

### Use Radix Trie When:
- You have long unique paths (sparse branching)
- Memory efficiency is important
- You're working with n-gram language models
- You need to track frequencies at every position

### Use Standard Trie When:
- Maximum simplicity is desired
- Branching factor is high throughout
- Implementation complexity is a concern

## Future Enhancement Ideas

While the current implementation is robust and efficient, potential improvements include:

1. **Lazy edge splitting:** Delay splitting until necessary for insert-heavy workloads
2. **Serialization support:** Save/load trie to/from disk
3. **Memory profiling:** Detailed analysis with real-world corpora
4. **Parallel traversal:** Multi-threaded neighbor queries for large tries
5. **Custom allocator:** Pool allocation for nodes to improve cache behavior

## Technical Details

### Node Structure

```python
class RadixNode:
    __slots__ = ('edge_label', 'freqs', 'children')

    edge_label: Tuple[str, ...]    # Tokens on this edge
    freqs: List[int]               # Frequency after each token
    children: Dict[str, RadixNode] # First token -> child node
```

### Frequency Semantics

For an edge with label `('the', 'quick', 'brown')`:
- `freqs[0]` = frequency after "the"
- `freqs[1]` = frequency after "the quick"
- `freqs[2]` = frequency after "the quick brown"

### Direction Handling

- **Forward (fw):** Tokens stored and returned in original order
- **Backward (bw):** Tokens stored reversed in trie, but returned in forward order

This symmetry allows efficient left/right neighbor searches with identical logic.

## References

- **Original implementation:** `radix_trie.py`
- **Standard trie:** `syntax_model.py`
- **Test suite:** `test_radix_trie_v2.py`
- **Wikipedia:** [Radix tree](https://en.wikipedia.org/wiki/Radix_tree)

## Author Notes

This implementation represents a thorough refactoring focused on:
- **Clarity:** Making the algorithm structure explicit
- **Efficiency:** Reducing redundancy and optimizing hot paths
- **Maintainability:** Adding type hints and better abstractions
- **Correctness:** Comprehensive testing ensures functional equivalence

The V2 implementation maintains 100% functional compatibility while providing a more elegant, efficient, and maintainable codebase for future development.
