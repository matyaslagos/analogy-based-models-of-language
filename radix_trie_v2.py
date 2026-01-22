#!/usr/bin/env python3
# ------------------------------------------------ #
# Improved Radix Trie Implementation (Version 2)  #
# ------------------------------------------------ #

"""
An optimized radix trie (Patricia trie) for storing word sequences with frequencies.

This is an improved version of the original radix_trie.py with:
- Cleaner abstractions and better separation of concerns
- Eliminated redundancy (single frequency representation)
- Type hints for better documentation and IDE support
- Performance optimizations (reduced list conversions, optimized hot paths)
- More intuitive position tracking (None for root instead of -1)
- Centralized direction-aware logic for forward/backward traversal
"""

from typing import Optional, Tuple, List, Dict, Iterator, Literal, Union

Direction = Literal['fw', 'bw']

# --------------- #
# Setup functions #
# --------------- #

def txt_to_list(filename: str) -> List[Tuple[str, ...]]:
    """Import a txt list of sentences as a list of tuples of words.

    Args:
        filename: Path to txt file with one sentence per line

    Returns:
        List of tuples of strings, each sentence endmarked with '<' and '>'
        Example: [('<', 'this', 'is', 'good', '>'), ...]
    """
    with open(filename, mode='r', encoding='utf-8-sig') as file:
        lines = file.readlines()
    return [('<',) + tuple(line.strip().split()) + ('>',) for line in lines]


# ------------------------------------------------- #
# RadixNode and RadixFreqTrie class definitions     #
# ------------------------------------------------- #

class RadixNode:
    """A node in the radix trie.

    Attributes:
        edge_label: Tuple of tokens on the edge leading to this node. Empty for root.
        freqs: List of frequency counts, one per token in edge_label.
               freqs[i] = frequency after consuming edge_label[0:i+1].
        children: Mapping from first token of child edge to child RadixNode.
    """

    __slots__ = ('edge_label', 'freqs', 'children')

    def __init__(self, edge_label: Tuple[str, ...] = (), freqs: Optional[List[int]] = None):
        """Initialize a radix trie node.

        Args:
            edge_label: Sequence of tokens for this edge (empty for root).
            freqs: Frequency list for each position. If None, initialized to zeros.
        """
        self.edge_label: Tuple[str, ...] = edge_label
        self.children: Dict[str, RadixNode] = {}
        self.freqs: List[int] = freqs if freqs is not None else [0] * len(edge_label)

    @property
    def freq(self) -> int:
        """Frequency at this node (after all tokens in edge_label)."""
        return self.freqs[-1] if self.freqs else 0

    def _compute_lcp_length(self, sequence: Tuple[str, ...],
                           child_label: Tuple[str, ...]) -> int:
        """Compute length of longest common prefix between sequence and child label.

        Args:
            sequence: Input sequence to compare.
            child_label: Edge label to compare against.

        Returns:
            Length of longest common prefix.
        """
        max_len = min(len(sequence), len(child_label))
        lcp_len = 0
        while lcp_len < max_len and sequence[lcp_len] == child_label[lcp_len]:
            lcp_len += 1
        return lcp_len

    def _merge_into_child(self, child: 'RadixNode', sequence: Tuple[str, ...],
                         freq: int) -> None:
        """Case 1: Child's edge is fully matched by sequence prefix.

        Increment frequencies along child's edge and recurse with remainder.

        Args:
            child: Child node whose edge is being traversed.
            sequence: Full input sequence.
            freq: Frequency to add.
        """
        # Increment all positions along child's edge
        for i in range(len(child.freqs)):
            child.freqs[i] += freq

        # Continue with remaining sequence
        remaining = sequence[len(child.edge_label):]
        child._insert_sequence(remaining, freq)

    def _split_child_as_prefix(self, child: 'RadixNode', sequence: Tuple[str, ...],
                              freq: int, first_token: str) -> None:
        """Case 2: Sequence is a complete prefix of child's edge.

        Split child's edge: create intermediate node with sequence,
        make child's remainder a child of intermediate.

        Args:
            child: Child node to split.
            sequence: Input sequence (prefix of child's edge).
            freq: Frequency to add.
            first_token: First token of sequence (key in parent's children dict).
        """
        common_len = len(sequence)

        # Create intermediate node with sequence as its edge
        intermediate_freqs = [child.freqs[i] + freq for i in range(common_len)]
        intermediate = RadixNode(edge_label=sequence, freqs=intermediate_freqs)

        # Update child to have only the remaining portion
        remaining_label = child.edge_label[common_len:]
        remaining_freqs = child.freqs[common_len:]
        child.edge_label = remaining_label
        child.freqs = remaining_freqs

        # Insert child under intermediate
        intermediate.children[remaining_label[0]] = child

        # Replace child with intermediate in parent
        self.children[first_token] = intermediate

    def _split_at_divergence(self, child: 'RadixNode', sequence: Tuple[str, ...],
                           freq: int, lcp_len: int, first_token: str) -> None:
        """Case 3: Sequence and child's edge diverge after common prefix.

        Create intermediate node with common prefix, make both remainders children.

        Args:
            child: Existing child node.
            sequence: Input sequence.
            freq: Frequency to add.
            lcp_len: Length of longest common prefix.
            first_token: First token (key in parent's children dict).
        """
        # Create intermediate node with common prefix
        common_prefix = sequence[:lcp_len]
        common_freqs = [child.freqs[i] + freq for i in range(lcp_len)]
        intermediate = RadixNode(edge_label=common_prefix, freqs=common_freqs)

        # Update existing child to have remaining portion
        child_remaining = child.edge_label[lcp_len:]
        child_remaining_freqs = child.freqs[lcp_len:]
        child.edge_label = child_remaining
        child.freqs = child_remaining_freqs
        intermediate.children[child_remaining[0]] = child

        # Create new child for our diverging sequence
        our_remaining = sequence[lcp_len:]
        if our_remaining:  # Should always be true in this case
            new_freqs = [freq] * len(our_remaining)
            new_node = RadixNode(edge_label=our_remaining, freqs=new_freqs)
            intermediate.children[our_remaining[0]] = new_node

        # Replace old child with intermediate
        self.children[first_token] = intermediate

    def _insert_sequence(self, sequence: Tuple[str, ...], freq: int = 1) -> None:
        """Insert a sequence into the radix trie starting from this node.

        Core radix trie algorithm: find common prefixes, split edges when necessary,
        and maintain frequency information at each token position.

        Args:
            sequence: Tuple of tokens to insert.
            freq: Frequency increment for this sequence.
        """
        if not sequence:
            return

        first_token = sequence[0]

        # Case: No existing child with this first token
        if first_token not in self.children:
            new_freqs = [freq] * len(sequence)
            new_node = RadixNode(edge_label=sequence, freqs=new_freqs)
            self.children[first_token] = new_node
            return

        # Case: Existing child - need to handle common prefix
        child = self.children[first_token]
        lcp_len = self._compute_lcp_length(sequence, child.edge_label)

        if lcp_len == len(child.edge_label):
            # Case 1: Child's edge is fully matched
            self._merge_into_child(child, sequence, freq)
        elif lcp_len == len(sequence):
            # Case 2: Sequence is prefix of child's edge
            self._split_child_as_prefix(child, sequence, freq, first_token)
        else:
            # Case 3: Divergence after common prefix
            self._split_at_divergence(child, sequence, freq, lcp_len, first_token)

    def _find_sequence(self, sequence: Tuple[str, ...]) -> Optional[Tuple['RadixNode', Optional[int]]]:
        """Find the node and position corresponding to a sequence.

        Handles cases where sequence ends mid-edge.

        Args:
            sequence: Sequence of tokens to find.

        Returns:
            (node, position) tuple where:
                - node: RadixNode containing the sequence endpoint
                - position: Index in node.edge_label where sequence ends
                           None if sequence is empty or ends exactly at node
            Returns None if sequence not found.
        """
        if not sequence:
            return (self, None)

        first_token = sequence[0]
        if first_token not in self.children:
            return None

        child = self.children[first_token]

        # Find how much of sequence matches child's edge
        match_len = self._compute_lcp_length(sequence, child.edge_label)

        if match_len == 0:
            return None

        # Sequence ends partway through this edge
        if match_len < len(child.edge_label):
            if match_len == len(sequence):
                # Exact match up to this point
                return (child, match_len - 1)
            else:
                # Sequence diverges - not found
                return None

        # Match covers entire edge label
        if len(sequence) == len(child.edge_label):
            # Exact match at end of edge
            return (child, None)

        # Continue search with remaining sequence
        remaining = sequence[len(child.edge_label):]
        return child._find_sequence(remaining)

    def _build_path(self, edge_slice: Tuple[str, ...], current_path: List[str],
                   direction: Direction) -> List[str]:
        """Build path by adding edge tokens according to direction.

        Args:
            edge_slice: Slice of edge_label to add.
            current_path: Current path being built.
            direction: 'fw' for forward, 'bw' for backward.

        Returns:
            New path with edge_slice incorporated.
        """
        if direction == 'fw':
            return current_path + list(edge_slice)
        else:
            # Backward: reverse tokens and prepend
            return list(reversed(edge_slice)) + current_path

    def _get_last_token(self, edge_slice: Tuple[str, ...],
                       direction: Direction) -> str:
        """Get the last token in edge_slice according to direction.

        Args:
            edge_slice: Slice of edge_label.
            direction: 'fw' or 'bw'.

        Returns:
            Last token in forward order.
        """
        if direction == 'fw':
            return edge_slice[-1]
        else:
            return edge_slice[0]  # First in reversed order

    def _traverse_paths(self, direction: Direction, max_length: Union[int, float],
                       min_length: int, only_completions: bool,
                       current_path: List[str]) -> Iterator[Tuple[Tuple[str, ...], int]]:
        """Yield all paths from this node with their frequencies.

        Traverses the trie and yields (path, freq) tuples for every token position.

        Args:
            direction: 'fw' for forward, 'bw' for backward.
            max_length: Maximum path length to return.
            min_length: Minimum path length to return.
            only_completions: Only yield paths ending with '<' or '>'.
            current_path: Current path being built.

        Yields:
            (path_tuple, frequency) pairs.
        """
        if len(current_path) >= max_length:
            return

        for child in self.children.values():
            edge_len = len(child.edge_label)

            # Yield paths for each position along this edge
            for i in range(edge_len):
                if len(current_path) + i + 1 > max_length:
                    break

                edge_slice = child.edge_label[:i+1]
                path_to_i = self._build_path(edge_slice, current_path, direction)
                last_token = self._get_last_token(edge_slice, direction)

                # Check if we should yield this path
                if len(path_to_i) >= min_length:
                    if not only_completions or last_token in {'<', '>'}:
                        yield (tuple(path_to_i), child.freqs[i])

            # Continue recursion from end of this edge
            new_path = self._build_path(child.edge_label, current_path, direction)

            if len(new_path) < max_length:
                yield from child._traverse_paths(direction, max_length, min_length,
                                                only_completions, new_path)

    def _traverse_shared_paths(self, other: 'RadixNode', direction: Direction,
                              max_length: Union[int, float], min_length: int,
                              only_completions: bool,
                              current_path: List[str]) -> Iterator[Tuple[Tuple[str, ...], int, int]]:
        """Yield all shared paths between this node and another node.

        Only traverses children that exist in both nodes with matching edge labels.

        Args:
            other: The other node to compare with.
            direction: 'fw' or 'bw'.
            max_length: Maximum path length.
            min_length: Minimum path length.
            only_completions: Only yield complete sequences.
            current_path: Current path being built.

        Yields:
            (path_tuple, freq1, freq2) for shared paths.
        """
        if len(current_path) >= max_length:
            return

        # Find children that exist in both nodes with matching edges
        for first_token in self.children:
            if first_token not in other.children:
                continue

            child1 = self.children[first_token]
            child2 = other.children[first_token]

            # Edge labels must match exactly for shared paths
            if child1.edge_label != child2.edge_label:
                continue

            edge_len = len(child1.edge_label)

            # Yield shared paths for each position along this edge
            for i in range(edge_len):
                if len(current_path) + i + 1 > max_length:
                    break

                edge_slice = child1.edge_label[:i+1]
                path_to_i = self._build_path(edge_slice, current_path, direction)
                last_token = self._get_last_token(edge_slice, direction)

                if len(path_to_i) >= min_length:
                    if not only_completions or last_token in {'<', '>'}:
                        yield (tuple(path_to_i), child1.freqs[i], child2.freqs[i])

            # Continue recursion from end of edges
            new_path = self._build_path(child1.edge_label, current_path, direction)

            if len(new_path) < max_length:
                yield from child1._traverse_shared_paths(child2, direction, max_length,
                                                        min_length, only_completions, new_path)


class RadixFreqTrie:
    """A radix trie for storing word sequences with frequencies.

    Maintains two radix tries:
        fw_root: Forward trie for storing suffixes (right contexts).
        bw_root: Backward trie for storing reversed prefixes (left contexts).

    The radix trie compresses non-branching paths into single edges, making it
    more space-efficient than a standard trie.
    """

    def __init__(self):
        """Initialize an empty radix trie with forward and backward roots."""
        self.fw_root = RadixNode()
        self.bw_root = RadixNode()
        self._corpus_size = 0  # Total token frequency mass

    def _insert(self, sequence: Tuple[str, ...], freq: int = 1) -> None:
        """Record distributions of prefixes and suffixes of sequence.

        Inserts all prefix-suffix splits of the sequence into the trie.
        Suffixes go in forward trie, reversed prefixes in backward trie.

        Args:
            sequence: Tuple of tokens, e.g. ('<', 'this', 'is', 'good', '>').
            freq: Number of occurrences to record.
        """
        # Track total token frequency mass (for corpus size)
        token_freq_mass = len(sequence) * freq
        self._corpus_size += token_freq_mass

        # Record each suffix and reversed prefix
        for i in range(len(sequence) + 1):
            suffix = sequence[i:]
            prefix = sequence[:i]

            self.fw_root._insert_sequence(suffix, freq)
            self.bw_root._insert_sequence(tuple(reversed(prefix)), freq)

    def setup(self, training_corpus_path: str = 'corpora/small_test_corpus.txt') -> None:
        """Set up model with training corpus.

        Args:
            training_corpus_path: Path to corpus file with one sentence per line.
        """
        corpus = txt_to_list(training_corpus_path)
        for sequence in corpus:
            self._insert(sequence)

    def freq(self, sequence: Tuple[str, ...] = ()) -> int:
        """Return the frequency of sequence.

        Args:
            sequence: Sequence of tokens.

        Returns:
            Frequency count for this sequence.
        """
        if not sequence:
            return self._corpus_size

        result = self.fw_root._find_sequence(sequence)
        if result is None:
            return 0

        node, position = result
        if position is None:
            # Sequence ends at node
            return node.freq
        else:
            # Sequence ends mid-edge
            return node.freqs[position]

    def sequence_node(self, sequence: Tuple[str, ...],
                     direction: Direction = 'fw') -> Optional[RadixNode]:
        """Return the node that represents sequence.

        Only returns a node if sequence ends exactly at a node boundary.

        Args:
            sequence: Tuple of tokens.
            direction: 'fw' or 'bw'.

        Returns:
            RadixNode representing sequence, or None if not found or mid-edge.
        """
        root = self.fw_root if direction == 'fw' else self.bw_root
        search_seq = sequence if direction == 'fw' else tuple(reversed(sequence))

        result = root._find_sequence(search_seq)
        if result is None:
            return None

        node, position = result
        # Only return if at node boundary
        return node if position is None else None

    def right_neighbors(self, sequence: Tuple[str, ...],
                       max_length: Union[int, float] = float('inf'),
                       min_length: int = 0,
                       only_completions: bool = False) -> Iterator[Tuple[Tuple[str, ...], int]]:
        """Return generator of (right_neighbor, joint_freq) pairs for sequence.

        Args:
            sequence: Base sequence to find neighbors for.
            max_length: Maximum length of neighbor sequences.
            min_length: Minimum length of neighbor sequences.
            only_completions: Only return sequences ending with '<' or '>'.

        Yields:
            (neighbor_sequence, frequency) pairs.
        """
        return self._neighbors(sequence, 'fw', max_length, min_length, only_completions)

    def left_neighbors(self, sequence: Tuple[str, ...],
                      max_length: Union[int, float] = float('inf'),
                      min_length: int = 0,
                      only_completions: bool = False) -> Iterator[Tuple[Tuple[str, ...], int]]:
        """Return generator of (left_neighbor, joint_freq) pairs for sequence.

        Args:
            sequence: Base sequence to find neighbors for.
            max_length: Maximum length of neighbor sequences.
            min_length: Minimum length of neighbor sequences.
            only_completions: Only return sequences ending with '<' or '>'.

        Yields:
            (neighbor_sequence, frequency) pairs.
        """
        return self._neighbors(sequence, 'bw', max_length, min_length, only_completions)

    def _neighbors(self, sequence: Tuple[str, ...], direction: Direction,
                  max_length: Union[int, float], min_length: int,
                  only_completions: bool) -> Iterator[Tuple[Tuple[str, ...], int]]:
        """Return generator of (neighbor, joint_freq) pairs for sequence in direction.

        Args:
            sequence: Base sequence.
            direction: 'fw' for right neighbors, 'bw' for left neighbors.
            max_length: Maximum neighbor length.
            min_length: Minimum neighbor length.
            only_completions: Only return complete sequences.

        Yields:
            (neighbor_sequence, frequency) pairs.
        """
        root = self.fw_root if direction == 'fw' else self.bw_root
        search_seq = sequence if direction == 'fw' else tuple(reversed(sequence))

        result = root._find_sequence(search_seq)
        if result is None:
            return iter(())

        seq_node, position = result

        # If sequence ends at node boundary, traverse from there
        if position is None:
            return seq_node._traverse_paths(direction, max_length, min_length,
                                           only_completions, [])

        # Sequence ends mid-edge: yield continuations
        return self._neighbors_from_mid_edge(seq_node, position, direction,
                                            max_length, min_length, only_completions)

    def _neighbors_from_mid_edge(self, node: RadixNode, position: int,
                                direction: Direction, max_length: Union[int, float],
                                min_length: int,
                                only_completions: bool) -> Iterator[Tuple[Tuple[str, ...], int]]:
        """Yield neighbors when starting from middle of an edge.

        Args:
            node: The node containing the edge.
            position: Position within the edge where sequence ends.
            direction: 'fw' or 'bw'.
            max_length: Maximum neighbor length.
            min_length: Minimum neighbor length.
            only_completions: Only yield complete sequences.

        Yields:
            (neighbor_sequence, frequency) pairs.
        """
        edge_len = len(node.edge_label)

        # Yield continuations from rest of this edge
        for i in range(position + 1, edge_len):
            if i - position > max_length:
                break

            edge_slice = node.edge_label[position+1:i+1]
            if direction == 'fw':
                neighbor = edge_slice
                last_token = edge_slice[-1]
            else:
                neighbor = tuple(reversed(edge_slice))
                last_token = edge_slice[0]

            if len(neighbor) >= min_length:
                if not only_completions or last_token in {'<', '>'}:
                    yield (neighbor, node.freqs[i])

        # Traverse children from this node
        if edge_len - position - 1 < max_length:
            if direction == 'fw':
                current_path = list(node.edge_label[position+1:])
            else:
                current_path = list(reversed(node.edge_label[position+1:]))

            yield from node._traverse_paths(direction, max_length, min_length,
                                           only_completions, current_path)

    def shared_right_neighbors(self, sequence_1: Tuple[str, ...],
                               sequence_2: Tuple[str, ...],
                               max_length: Union[int, float] = float('inf'),
                               min_length: int = 0,
                               only_completions: bool = False) -> Iterator[Tuple[Tuple[str, ...], int, int]]:
        """Return generator of (shared_neighbor, joint_freq_1, joint_freq_2) pairs.

        Args:
            sequence_1: First sequence.
            sequence_2: Second sequence.
            max_length: Maximum neighbor length.
            min_length: Minimum neighbor length.
            only_completions: Only return complete sequences.

        Yields:
            (neighbor, freq1, freq2) for shared right neighbors.
        """
        return self._shared_neighbors(sequence_1, sequence_2, 'fw',
                                     max_length, min_length, only_completions)

    def shared_left_neighbors(self, sequence_1: Tuple[str, ...],
                              sequence_2: Tuple[str, ...],
                              max_length: Union[int, float] = float('inf'),
                              min_length: int = 0,
                              only_completions: bool = False) -> Iterator[Tuple[Tuple[str, ...], int, int]]:
        """Return generator of (shared_neighbor, joint_freq_1, joint_freq_2) pairs.

        Args:
            sequence_1: First sequence.
            sequence_2: Second sequence.
            max_length: Maximum neighbor length.
            min_length: Minimum neighbor length.
            only_completions: Only return complete sequences.

        Yields:
            (neighbor, freq1, freq2) for shared left neighbors.
        """
        return self._shared_neighbors(sequence_1, sequence_2, 'bw',
                                     max_length, min_length, only_completions)

    def _shared_neighbors(self, sequence_1: Tuple[str, ...],
                         sequence_2: Tuple[str, ...],
                         direction: Direction, max_length: Union[int, float],
                         min_length: int,
                         only_completions: bool) -> Iterator[Tuple[Tuple[str, ...], int, int]]:
        """Return generator of shared neighbors of sequence_1 and sequence_2.

        Args:
            sequence_1: First sequence.
            sequence_2: Second sequence.
            direction: 'fw' for right neighbors, 'bw' for left neighbors.
            max_length: Maximum neighbor length.
            min_length: Minimum neighbor length.
            only_completions: Only return complete sequences.

        Yields:
            (neighbor, freq_1, freq_2) tuples.
        """
        root = self.fw_root if direction == 'fw' else self.bw_root

        search_seq_1 = sequence_1 if direction == 'fw' else tuple(reversed(sequence_1))
        search_seq_2 = sequence_2 if direction == 'fw' else tuple(reversed(sequence_2))

        result_1 = root._find_sequence(search_seq_1)
        result_2 = root._find_sequence(search_seq_2)

        if result_1 is None or result_2 is None:
            return iter(())

        seq_node_1, position_1 = result_1
        seq_node_2, position_2 = result_2

        # Both sequences must end at nodes for standard traversal
        at_node_1 = (position_1 is None)
        at_node_2 = (position_2 is None)

        if at_node_1 and at_node_2:
            # Both at nodes: use standard shared traversal
            return seq_node_1._traverse_shared_paths(seq_node_2, direction, max_length,
                                                     min_length, only_completions, [])

        # Handle mid-edge cases
        if seq_node_1 is seq_node_2 and position_1 == position_2 and position_1 is not None:
            # Both sequences end at same position in same edge
            return self._shared_neighbors_from_mid_edge(seq_node_1, position_1, direction,
                                                       max_length, min_length, only_completions)

        # Check for different nodes with matching continuations
        if (seq_node_1 is not seq_node_2 and position_1 == position_2 and
            position_1 is not None and position_2 is not None):
            # Check if remaining parts of edges match
            remaining_1 = seq_node_1.edge_label[position_1+1:]
            remaining_2 = seq_node_2.edge_label[position_2+1:]
            if remaining_1 == remaining_2:
                return self._shared_neighbors_from_matching_edges(
                    seq_node_1, seq_node_2, position_1, direction,
                    max_length, min_length, only_completions)

        # No shared neighbors
        return iter(())

    def _shared_neighbors_from_mid_edge(self, node: RadixNode, position: int,
                                        direction: Direction, max_length: Union[int, float],
                                        min_length: int,
                                        only_completions: bool) -> Iterator[Tuple[Tuple[str, ...], int, int]]:
        """Yield shared neighbors when both sequences end at same mid-edge position.

        Args:
            node: The node containing the shared edge.
            position: Position within the edge where both sequences end.
            direction: 'fw' or 'bw'.
            max_length: Maximum neighbor length.
            min_length: Minimum neighbor length.
            only_completions: Only yield complete sequences.

        Yields:
            (neighbor_sequence, freq, freq) tuples (freq is same for both).
        """
        edge_len = len(node.edge_label)

        # Yield continuations from rest of this edge
        for i in range(position + 1, edge_len):
            if i - position > max_length:
                break

            edge_slice = node.edge_label[position+1:i+1]
            if direction == 'fw':
                neighbor = edge_slice
                last_token = edge_slice[-1]
            else:
                neighbor = tuple(reversed(edge_slice))
                last_token = edge_slice[0]

            if len(neighbor) >= min_length:
                if not only_completions or last_token in {'<', '>'}:
                    freq = node.freqs[i]
                    yield (neighbor, freq, freq)

        # Traverse children (they share the same subtree)
        if edge_len - position - 1 < max_length:
            if direction == 'fw':
                current_path = list(node.edge_label[position+1:])
            else:
                current_path = list(reversed(node.edge_label[position+1:]))

            yield from node._traverse_shared_paths(node, direction, max_length, min_length,
                                                   only_completions, current_path)

    def _shared_neighbors_from_matching_edges(self, node1: RadixNode, node2: RadixNode,
                                              position: int, direction: Direction,
                                              max_length: Union[int, float], min_length: int,
                                              only_completions: bool) -> Iterator[Tuple[Tuple[str, ...], int, int]]:
        """Yield shared neighbors when sequences end at same position in different nodes.

        The nodes must have matching edge suffixes from position onward.

        Args:
            node1, node2: The two nodes with matching edge suffixes.
            position: Position within edges where both sequences end.
            direction: 'fw' or 'bw'.
            max_length: Maximum neighbor length.
            min_length: Minimum neighbor length.
            only_completions: Only yield complete sequences.

        Yields:
            (neighbor_sequence, freq1, freq2) tuples.
        """
        edge_len = len(node1.edge_label)

        # Yield continuations from matching edge portions
        for i in range(position + 1, edge_len):
            if i - position > max_length:
                break

            edge_slice = node1.edge_label[position+1:i+1]
            if direction == 'fw':
                neighbor = edge_slice
                last_token = edge_slice[-1]
            else:
                neighbor = tuple(reversed(edge_slice))
                last_token = edge_slice[0]

            if len(neighbor) >= min_length:
                if not only_completions or last_token in {'<', '>'}:
                    yield (neighbor, node1.freqs[i], node2.freqs[i])

        # Traverse children - they share structure from here on
        if edge_len - position - 1 < max_length:
            if direction == 'fw':
                current_path = list(node1.edge_label[position+1:])
            else:
                current_path = list(reversed(node1.edge_label[position+1:]))

            yield from node1._traverse_shared_paths(node2, direction, max_length, min_length,
                                                   only_completions, current_path)
