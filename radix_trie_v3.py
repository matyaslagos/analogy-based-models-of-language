#!/usr/bin/env python3
"""
Python implementation of the Radix Trie data structure, with efficient
shared-neighbor search.
"""

from typing import Optional, Tuple, List, Dict, Iterator, Literal, Union

Direction = Literal['fw', 'bw']


def txt_to_list(filename: str) -> List[Tuple[str, ...]]:
    """Load sentences from file as endmarked tuples."""
    with open(filename, mode='r', encoding='utf-8-sig') as f:
        return [('<',) + tuple(line.strip().split()) + ('>',) for line in f]


class RadixNode:
    """Node in radix trie with compressed edge."""

    __slots__ = ('edge_label', 'freq', 'children')

    def __init__(self, edge_label: Tuple[str, ...] = (), freq: int = 0):
        self.edge_label = edge_label
        self.freq = freq
        self.children: Dict[str, RadixNode] = {}

    def _lcp_len(self, seq: Tuple[str, ...]) -> int:
        """Compute longest common prefix length of edge label and sequence.
        """
        n = min(len(seq), len(self.edge_label))
        i = 0
        while i < n and seq[i] == self.edge_label[i]:
            i += 1
        return i

    def _insert(self, seq: Tuple[str, ...], freq: int = 1) -> None:
        """Insert sequence starting from this node.
        """
        if not seq:
            return

        first = seq[0]

        if first not in self.children:
            # No child: create new node with full sequence
            self.children[first] = RadixNode(seq, freq)
            return

        child = self.children[first]
        lcp = child._lcp_len(seq)

        if lcp == len(child.edge_label):
            # Case 1: Child's edge fully matched - traverse and recurse
            child.freq += freq
            child._insert(seq[lcp:], freq)

        elif lcp == len(seq):
            # Case 2: Sequence is prefix of child's edge - split child
            intermediate = RadixNode(seq, child.freq + freq)
            child.edge_label = child.edge_label[lcp:]
            intermediate.children[child.edge_label[0]] = child
            self.children[first] = intermediate

        else:
            # Case 3: Divergence - create intermediate with common prefix
            intermediate = RadixNode(seq[:lcp], child.freq + freq)

            # Update existing child
            child.edge_label = child.edge_label[lcp:]
            intermediate.children[child.edge_label[0]] = child

            # Add new child for our sequence
            remaining = seq[lcp:]
            if remaining:
                intermediate.children[remaining[0]] = RadixNode(remaining, freq)

            self.children[first] = intermediate

    def _find(self, seq: Tuple[str, ...]) -> Optional[Tuple['RadixNode', int]]:
        """Find node containing sequence. Returns (node, match_len) where match_len
        is how many tokens of the node's edge were matched."""
        if not seq:
            return (self, 0)

        first = seq[0]
        if first not in self.children:
            return None

        child = self.children[first]
        lcp = child._lcp_len(seq)

        if lcp == 0:
            return None
        elif lcp < len(child.edge_label):
            # Sequence ends mid-edge
            return (child, lcp) if lcp == len(seq) else None
        elif len(seq) == len(child.edge_label):
            # Exact match at node boundary
            return (child, len(child.edge_label))
        else:
            # Continue search
            return child._find(seq[lcp:])

    def _traverse(self, direction: Direction, max_len: Union[int, float], min_len: int,
                  only_complete: bool, path: List[str]) -> Iterator[Tuple[Tuple[str, ...], int]]:
        """Yield (path, freq) for all continuations."""
        if len(path) >= max_len:
            return

        for child in self.children.values():
            # Yield path for each token position along edge
            for i in range(len(child.edge_label)):
                if direction == 'fw':
                    # Forward: append tokens in order
                    new_path = path + list(child.edge_label[:i+1])
                    last_token = child.edge_label[i]
                else:
                    # Backward: reverse slice and prepend
                    reversed_slice = list(reversed(child.edge_label[:i+1]))
                    new_path = reversed_slice + path
                    last_token = reversed_slice[-1]

                if len(new_path) > max_len:
                    break
                if len(new_path) >= min_len:
                    if not only_complete or last_token in {'<', '>'}:
                        yield (tuple(new_path), child.freq)

            # Recurse to children
            if direction == 'fw':
                full_path = path + list(child.edge_label)
            else:
                full_path = list(reversed(child.edge_label)) + path

            if len(full_path) < max_len:
                yield from child._traverse(direction, max_len, min_len, only_complete, full_path)

    def _traverse_shared(self, other: 'RadixNode', direction: Direction,
                        max_len: Union[int, float], min_len: int, only_complete: bool,
                        path: List[str]) -> Iterator[Tuple[Tuple[str, ...], int, int]]:
        """Yield (path, freq1, freq2) for shared continuations."""
        if len(path) >= max_len:
            return

        # Only traverse children present in both nodes with matching edges
        for token in self.children:
            if token not in other.children:
                continue

            child1 = self.children[token]
            child2 = other.children[token]

            if child1.edge_label != child2.edge_label:
                continue

            # Yield shared paths for each position along edge
            for i in range(len(child1.edge_label)):
                if direction == 'fw':
                    new_path = path + list(child1.edge_label[:i+1])
                    last_token = child1.edge_label[i]
                else:
                    reversed_slice = list(reversed(child1.edge_label[:i+1]))
                    new_path = reversed_slice + path
                    last_token = reversed_slice[-1]

                if len(new_path) > max_len:
                    break
                if len(new_path) >= min_len:
                    if not only_complete or last_token in {'<', '>'}:
                        yield (tuple(new_path), child1.freq, child2.freq)

            # Recurse
            if direction == 'fw':
                full_path = path + list(child1.edge_label)
            else:
                full_path = list(reversed(child1.edge_label)) + path

            if len(full_path) < max_len:
                yield from child1._traverse_shared(child2, direction, max_len, min_len,
                                                   only_complete, full_path)


class RadixFreqTrie:
    """Radix trie for n-gram frequency tracking."""

    def __init__(self):
        self.fw_root = RadixNode()
        self.bw_root = RadixNode()
        self._corpus_size = 0

    def _insert(self, seq: Tuple[str, ...], freq: int = 1) -> None:
        """Insert all prefix-suffix splits of sequence."""
        self._corpus_size += len(seq) * freq

        for i in range(len(seq) + 1):
            self.fw_root._insert(seq[i:], freq)
            self.bw_root._insert(tuple(reversed(seq[:i])), freq)

    def setup(self, corpus_path: str = 'corpora/small_test_corpus.txt') -> None:
        """Load corpus from file."""
        for seq in txt_to_list(corpus_path):
            self._insert(seq)

    def freq(self, seq: Tuple[str, ...] = ()) -> int:
        """Get frequency of sequence."""
        if not seq:
            return self._corpus_size
        result = self.fw_root._find(seq)
        return result[0].freq if result else 0

    def _traverse_from_match(self, node: RadixNode, match_len: int, direction: Direction,
                            max_length: Union[int, float], min_length: int,
                            only_completions: bool) -> Iterator[Tuple[Tuple[str, ...], int]]:
        """Traverse from a node that may have been matched mid-edge."""
        if match_len < len(node.edge_label):
            # Mid-edge match: yield remaining edge positions first
            for i in range(match_len, len(node.edge_label)):
                if direction == 'fw':
                    path = list(node.edge_label[match_len:i+1])
                    last_token = node.edge_label[i]
                else:
                    reversed_slice = list(reversed(node.edge_label[match_len:i+1]))
                    path = reversed_slice
                    last_token = reversed_slice[-1]

                if len(path) > max_length:
                    break
                if len(path) >= min_length:
                    if not only_completions or last_token in {'<', '>'}:
                        yield (tuple(path), node.freq)

            # Continue to children if within length bound
            if direction == 'fw':
                initial_path = list(node.edge_label[match_len:])
            else:
                initial_path = list(reversed(node.edge_label[match_len:]))

            if len(initial_path) < max_length:
                yield from node._traverse(direction, max_length, min_length, only_completions, initial_path)
        else:
            # Exact node boundary match: traverse normally
            yield from node._traverse(direction, max_length, min_length, only_completions, [])

    def right_neighbors(self, seq: Tuple[str, ...], max_length: Union[int, float] = float('inf'),
                       min_length: int = 0, only_completions: bool = False
                       ) -> Iterator[Tuple[Tuple[str, ...], int]]:
        """Yield (continuation, freq) for sequence."""
        result = self.fw_root._find(seq)
        if not result:
            return iter(())
        node, match_len = result
        return self._traverse_from_match(node, match_len, 'fw', max_length, min_length, only_completions)

    def left_neighbors(self, seq: Tuple[str, ...], max_length: Union[int, float] = float('inf'),
                      min_length: int = 0, only_completions: bool = False
                      ) -> Iterator[Tuple[Tuple[str, ...], int]]:
        """Yield (predecessor, freq) for sequence."""
        result = self.bw_root._find(tuple(reversed(seq)))
        if not result:
            return iter(())
        node, match_len = result
        return self._traverse_from_match(node, match_len, 'bw', max_length, min_length, only_completions)

    def _traverse_shared_from_match(self, node1: RadixNode, match_len1: int,
                                    node2: RadixNode, match_len2: int,
                                    direction: Direction, max_length: Union[int, float],
                                    min_length: int, only_completions: bool
                                    ) -> Iterator[Tuple[Tuple[str, ...], int, int]]:
        """Traverse shared paths from nodes that may have been matched mid-edge."""
        # Handle case where both match mid-edge in same node
        print(node1.edge_label, node2.edge_label)
        if node1 is node2 and match_len1 == match_len2 and match_len1 < len(node1.edge_label):
            print(1)
            # Both end at same mid-edge position: yield remaining edge then traverse
            for i in range(match_len1, len(node1.edge_label)):
                if direction == 'fw':
                    path = list(node1.edge_label[match_len1:i+1])
                    last_token = node1.edge_label[i]
                else:
                    reversed_slice = list(reversed(node1.edge_label[match_len1:i+1]))
                    path = reversed_slice
                    last_token = reversed_slice[-1]

                if len(path) > max_length:
                    break
                if len(path) >= min_length:
                    if not only_completions or last_token in {'<', '>'}:
                        yield (tuple(path), node1.freq, node1.freq)

            # Continue to shared children
            if direction == 'fw':
                initial_path = list(node1.edge_label[match_len1:])
            else:
                initial_path = list(reversed(node1.edge_label[match_len1:]))

            if len(initial_path) < max_length:
                yield from node1._traverse_shared(node1, direction, max_length, min_length,
                                                  only_completions, initial_path)
        elif match_len1 == len(node1.edge_label) and match_len2 == len(node2.edge_label):
            print(2)
            # Both at node boundaries: traverse normally
            yield from node1._traverse_shared(node2, direction, max_length, min_length,
                                             only_completions, [])
        elif (node1 is not node2 and match_len1 == match_len2 and
              match_len1 < len(node1.edge_label) and match_len2 < len(node2.edge_label)):
            print(3)
            # Different nodes, same mid-edge position: check if remainders match
            remaining1 = node1.edge_label[match_len1:]
            remaining2 = node2.edge_label[match_len2:]
            print(remaining1, remaining2)
            if remaining1 == remaining2:
                # Remainders match: yield them and traverse shared children
                for i in range(len(remaining1)):
                    if direction == 'fw':
                        path = list(remaining1[:i+1])
                        last_token = remaining1[i]
                    else:
                        reversed_slice = list(reversed(remaining1[:i+1]))
                        path = reversed_slice
                        last_token = reversed_slice[-1]

                    if len(path) > max_length:
                        break
                    if len(path) >= min_length:
                        if not only_completions or last_token in {'<', '>'}:
                            yield (tuple(path), node1.freq, node2.freq)

                # Continue to shared children
                if direction == 'fw':
                    initial_path = list(remaining1)
                else:
                    initial_path = list(reversed(remaining1))

                if len(initial_path) < max_length:
                    yield from node1._traverse_shared(node2, direction, max_length, min_length,
                                                      only_completions, initial_path)
        # else: No shared neighbors (different positions or incompatible edges)

    def shared_right_neighbors(self, seq1: Tuple[str, ...], seq2: Tuple[str, ...],
                               max_length: Union[int, float] = float('inf'), min_length: int = 0,
                               only_completions: bool = False
                               ) -> Iterator[Tuple[Tuple[str, ...], int, int]]:
        """Yield (continuation, freq1, freq2) shared by both sequences."""
        result1 = self.fw_root._find(seq1)
        result2 = self.fw_root._find(seq2)
        if not result1 or not result2:
            return iter(())
        node1, match_len1 = result1
        node2, match_len2 = result2
        return self._traverse_shared_from_match(node1, match_len1, node2, match_len2,
                                                'fw', max_length, min_length, only_completions)

    def shared_left_neighbors(self, seq1: Tuple[str, ...], seq2: Tuple[str, ...],
                              max_length: Union[int, float] = float('inf'), min_length: int = 0,
                              only_completions: bool = False
                              ) -> Iterator[Tuple[Tuple[str, ...], int, int]]:
        """Yield (predecessor, freq1, freq2) shared by both sequences."""
        result1 = self.bw_root._find(tuple(reversed(seq1)))
        result2 = self.bw_root._find(tuple(reversed(seq2)))
        if not result1 or not result2:
            return iter(())
        node1, match_len1 = result1
        node2, match_len2 = result2
        return self._traverse_shared_from_match(node1, match_len1, node2, match_len2,
                                                'bw', max_length, min_length, only_completions)
