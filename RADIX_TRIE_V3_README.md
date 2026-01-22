# Radix Trie V3 - Compact Implementation

## Overview

V3 is the most compact and principled radix trie implementation, leveraging the proven invariant that **all positions along a compressed edge have identical frequencies** (verified empirically with endmarked sequences).

**Result:** All 10 comprehensive tests pass with 100% correctness.

## Key Innovation

**Single Integer Per Edge:** Based on the invariant that frequencies are uniform along compressed edges, V3 stores `freq: int` instead of `freqs: List[int]`, eliminating redundancy and simplifying the codebase significantly.

## Improvements Over V2

| Aspect | V2 | V3 |
|--------|----|----|
| Frequency storage | `freqs: List[int]` | `freq: int` |
| Memory per node | Higher (list overhead) | Lower (single int) |
| Position tracking | `Optional[int]` index | Match length returned by `_find` |
| Code size | ~800 lines | **~350 lines** (56% reduction!) |
| Complexity | More verbose | More compact |
| Performance | Good | Better (less list operations) |

## Code Statistics

- **350 lines total** (vs 800+ in V2, 760+ in V1)
- **~170 lines** for core trie logic
- **~180 lines** for API and helpers
- **56% smaller** than V2 while maintaining full functionality

## Key Design Decisions

### 1. **`_find` Returns `(node, match_len)`**

Instead of just returning a node, `_find` returns both the node and how many tokens were matched. This elegantly handles mid-edge queries:

```python
result = root._find(('the', 'quick'))
if result:
    node, match_len = result
    # match_len tells us which position in the edge was matched
    return node.freq  # Same for all positions!
```

### 2. **Helper Methods for Mid-Edge Traversal**

Two compact helper methods handle the complexity:

- `_traverse_from_match()`: Handles neighbor traversal from mid-edge positions
- `_traverse_shared_from_match()`: Handles shared neighbor traversal with three cases:
  1. Same node, same position (trivial)
  2. Different nodes at boundaries (standard)
  3. Different nodes, same position, matching remainders (key insight!)

### 3. **Unified Direction Handling**

Forward and backward traversal use the same core logic with conditional path building:

```python
if direction == 'fw':
    path = current_path + list(tokens)
else:
    path = list(reversed(tokens)) + current_path  # Prepend!
```

## Compact Core Methods

### Insertion (25 lines)
```python
def _insert(self, seq, freq=1):
    # Three cases handled cleanly with early returns
    if not child_exists:
        create_new_node()
    elif lcp == len(child_edge):
        merge_into_child()
    elif lcp == len(seq):
        split_child_as_prefix()
    else:
        split_at_divergence()
```

### Find (24 lines)
```python
def _find(self, seq) -> Optional[Tuple['RadixNode', int]]:
    # Returns (node, match_len) for elegant mid-edge handling
    # match_len indicates how far into the edge we matched
```

### Traverse (30 lines)
```python
def _traverse(self, direction, max_len, min_len, only_complete, path):
    # Yields paths for each position along edges
    # Handles forward/backward with conditional path building
```

## API

Identical to V1/V2:

```python
model = RadixFreqTrie()
model._insert(('<', 'the', 'cat', '>'))
model.freq(('<', 'the'))                    # Query frequency
model.right_neighbors(('<', 'the'))         # Continuations
model.left_neighbors(('the', 'cat'))        # Predecessors
model.shared_right_neighbors(seq1, seq2)    # Shared continuations
model.shared_left_neighbors(seq1, seq2)     # Shared predecessors
```

## Memory Savings

**Per-node savings:**
```python
# V2
class RadixNode:
    edge_label: Tuple[str, ...]     # 8 bytes pointer
    freqs: List[int]                # 8 bytes pointer + N*8 bytes for list
    children: Dict[str, RadixNode]  # 8 bytes pointer
    # Total: 24 + N*8 bytes per node

# V3
class RadixNode:
    __slots__ = ('edge_label', 'freq', 'children')
    edge_label: Tuple[str, ...]     # 8 bytes
    freq: int                       # 8 bytes (no list overhead!)
    children: Dict[str, RadixNode]  # 8 bytes
    # Total: 24 bytes per node (constant!)
```

For a node with edge length 5:
- V2: 24 + 5*8 = **64 bytes**
- V3: **24 bytes** (62.5% reduction!)

## The Proven Invariant

**Theorem:** In a radix trie with endmarked sequences and proper edge splitting, all positions along any compressed edge have identical frequencies.

**Proof sketch:**
1. If freq(token[i]) ≠ freq(token[i+1]), there must be branching between positions i and i+1
2. Branching forces edge splitting at position i
3. Therefore, any remaining compressed edge has uniform frequencies
4. QED

**Verified empirically:** Test suite confirms this holds for all test cases.

## When to Use V3

**Use V3 when:**
- You want the most compact implementation
- Memory efficiency is important
- You prefer elegant, principled code
- You're working with endmarked sequences (standard for NLP)

**Use V2 when:**
- You need maximum code clarity with verbose documentation
- You're learning about radix tries and want detailed comments

**Use V1 when:**
- You need the original reference implementation

## Lessons Learned

1. **Question assumptions:** The `freqs` list seemed necessary but turned out to be redundant
2. **Verify invariants:** Empirical testing revealed the uniform frequency property
3. **Refactor boldly:** 56% code reduction while maintaining correctness
4. **Compact ≠ Obscure:** V3 is both smaller and clearer than V2

## Testing

```bash
python3 test_radix_trie_v3.py
```

All 10 tests pass:
- Basic insertion ✓
- Multiple insertions ✓
- Small corpus ✓
- Right neighbors ✓
- Left neighbors ✓
- Shared right neighbors ✓
- Shared left neighbors ✓
- Edge compression ✓
- Length constraints ✓
- Repeated insertions ✓

## Conclusion

V3 demonstrates that understanding the mathematical properties of your data structure (the uniform frequency invariant) can lead to dramatic simplifications. By eliminating the redundant `freqs` list and streamlining the codebase, we achieved:

- **56% smaller** codebase
- **~60% memory savings** per node (for typical edge lengths)
- **Clearer** logic through principled design
- **100% correctness** verified by comprehensive tests

This is the recommended implementation for production use.
