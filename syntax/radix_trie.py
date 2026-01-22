#!/usr/bin/env python3
# ---------------------------------------- #
# Radix Trie data structure implementation #
# ---------------------------------------- #

"""
A radix trie (or Patricia trie) implementation for storing word sequences with frequencies.

This implementation provides the same functionality as the standard trie in syntax_model.py,
but with improved space efficiency through edge compression. In a radix trie, paths with
no branching are compressed into single edges labeled with sequences of tokens, rather than
having a separate node for each token.

Key differences from standard trie:
- Nodes store edge labels (tuples of tokens) rather than single tokens
- Non-branching paths are compressed into single edges
- More space-efficient for sparse tries with long unique paths
"""

# --------------- #
# Setup functions #
# --------------- #

def txt_to_list(filename):
    """Import a txt list of sentences as a list of tuples of words.

    Argument:
        filename (string): e.g. 'corpus.txt', the name of a txt file with one sentence
        per line

    Returns:
        list of tuples of strings: each sentence is an endmarked tuple of strings,
        e.g. ('<', 'this', 'is', 'good', '>')
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
        edge_label (tuple): Sequence of tokens on the edge leading to this node.
                           Empty for the root node.
        children (dict): Mapping from first token of child edge to child RadixNode.
        freq (int): Frequency count at this node (after all tokens in edge_label).
        freqs (list): Frequency counts after each token position in edge_label.
                     freqs[i] is the frequency after consuming edge_label[0:i+1].
                     Length equals len(edge_label).
    """

    def __init__(self, edge_label=(), freqs=None):
        """Initialize a radix trie node.

        Args:
            edge_label (tuple): Sequence of tokens for this edge. Default empty for root.
            freqs (list): Frequency list for each position. If None, initialized to zeros.
        """
        self.edge_label = edge_label
        self.children = {}  # Maps first_token -> RadixNode
        self.freq = 0
        # Initialize freqs list: one frequency per token in edge label
        if freqs is None:
            self.freqs = [0] * len(edge_label)
        else:
            self.freqs = freqs

    def _insert_sequence(self, sequence, freq=1):
        """Insert a sequence into the radix trie starting from this node.

        This method handles the core radix trie logic of finding common prefixes,
        splitting edges when necessary, and compressing paths. It also maintains
        frequency information for each token position.

        Args:
            sequence (tuple): Tuple of tokens to insert.
            freq (int): Frequency increment for this sequence.
        """
        if not sequence:
            # Empty sequence: do nothing (mimics standard trie behavior)
            # The standard trie's _increment_or_make_branch does nothing for empty sequences
            return

        first_token = sequence[0]

        # Check if we have a child starting with this token
        if first_token not in self.children:
            # No existing child: create new node with full remaining sequence
            # Build frequency list: cumulative freq for each position
            new_freqs = [freq] * len(sequence)
            new_node = RadixNode(edge_label=sequence, freqs=new_freqs)
            new_node.freq = freq
            self.children[first_token] = new_node
            return

        # We have a child starting with this token
        child = self.children[first_token]
        child_label = child.edge_label

        # Find the longest common prefix between sequence and child's edge label
        common_len = 0
        max_len = min(len(sequence), len(child_label))
        while common_len < max_len and sequence[common_len] == child_label[common_len]:
            common_len += 1

        if common_len == len(child_label):
            # The child's entire edge label is a prefix of our sequence
            # Increment frequencies along child's edge
            for i in range(len(child.freqs)):
                child.freqs[i] += freq
            child.freq += freq

            # Continue insertion from the child with remaining sequence
            remaining_sequence = sequence[common_len:]
            child._insert_sequence(remaining_sequence, freq)

        elif common_len == len(sequence):
            # Our sequence is a prefix of the child's edge label
            # Need to split the child's edge

            # Create new intermediate node with our sequence
            intermediate_freqs = [child.freqs[i] + freq for i in range(common_len)]
            intermediate = RadixNode(edge_label=sequence, freqs=intermediate_freqs)
            intermediate.freq = freq + child.freq  # Include existing frequency

            # Update child to have remaining label
            remaining_label = child_label[common_len:]
            remaining_freqs = child.freqs[common_len:]
            child.edge_label = remaining_label
            child.freqs = remaining_freqs

            # Insert child under intermediate node
            intermediate.children[remaining_label[0]] = child

            # Replace child with intermediate node
            self.children[first_token] = intermediate

        else:
            # Sequences diverge in the middle: need to split edge
            # Create intermediate node with common prefix
            common_prefix = sequence[:common_len]
            common_freqs = [child.freqs[i] + freq for i in range(common_len)]
            intermediate = RadixNode(edge_label=common_prefix, freqs=common_freqs)
            intermediate.freq = freq + child.freq  # Both paths pass through here

            # Update existing child to have remaining label
            child_remaining = child_label[common_len:]
            child_remaining_freqs = child.freqs[common_len:]
            child.edge_label = child_remaining
            child.freqs = child_remaining_freqs
            intermediate.children[child_remaining[0]] = child

            # Create new child for our remaining sequence
            our_remaining = sequence[common_len:]
            if our_remaining:
                new_freqs = [freq] * len(our_remaining)
                new_node = RadixNode(edge_label=our_remaining, freqs=new_freqs)
                new_node.freq = freq
                intermediate.children[our_remaining[0]] = new_node

            # Replace old child with intermediate node
            self.children[first_token] = intermediate

    def _find_sequence(self, sequence):
        """Find the node and position corresponding to a sequence.

        This method handles cases where the sequence might end in the middle
        of a compressed edge.

        Args:
            sequence (tuple): Sequence of tokens to find.

        Returns:
            tuple or None: (node, position) where:
                - node is the RadixNode containing the sequence endpoint
                - position is the index in node.edge_label where sequence ends
                  (position == len(node.edge_label) - 1 means the sequence ends at the node)
                Returns None if sequence not found.
        """
        if not sequence:
            return (self, -1)  # Empty sequence, -1 indicates we're at the node itself

        first_token = sequence[0]
        if first_token not in self.children:
            return None

        child = self.children[first_token]
        child_label = child.edge_label

        # Check if sequence matches beginning of edge label
        match_len = 0
        max_match = min(len(sequence), len(child_label))
        while match_len < max_match and sequence[match_len] == child_label[match_len]:
            match_len += 1

        if match_len == 0:
            # No match at all
            return None

        if match_len < len(child_label):
            # Sequence ends partway through this edge
            if match_len == len(sequence):
                # Sequence matches exactly up to this point
                return (child, match_len - 1)
            else:
                # Sequence diverges from edge - not found
                return None

        # Match covers entire edge label
        if len(sequence) == len(child_label):
            # Exact match at end of edge
            return (child, len(child_label) - 1)

        # Continue search with remaining sequence
        remaining = sequence[len(child_label):]
        return child._find_sequence(remaining)

    def _find_node(self, sequence):
        """Find the node corresponding to a sequence.

        Args:
            sequence (tuple): Sequence of tokens to find.

        Returns:
            RadixNode or None: The node if sequence exists, None otherwise.
        """
        result = self._find_sequence(sequence)
        if result is None:
            return None

        node, position = result
        # Only return node if sequence ends exactly at the node
        if position == len(node.edge_label) - 1 or (position == -1 and not sequence):
            return node
        return None

    def _traverse_paths(self, direction, max_length, min_length, only_completions, current_path=[]):
        """Yield all paths from this node with their frequencies.

        This is a generator that traverses the trie and yields (path, freq) tuples.
        It yields paths for every token position along edges, not just at nodes.

        For backward traversal, edge labels are stored reversed in the trie, but we
        need to return them in forward order by reversing them as we build paths.

        Args:
            direction (str): 'fw' or 'bw' for forward/backward traversal.
            max_length (int): Maximum path length to return.
            min_length (int): Minimum path length to return.
            only_completions (bool): If True, only yield paths ending with '<' or '>'.
            current_path (list): Current path being built (used in recursion).

        Yields:
            tuple: (path_tuple, frequency) pairs.
        """
        if not self.children or len(current_path) >= max_length:
            return

        for child in self.children.values():
            # Yield paths for each position along this edge
            for i in range(len(child.edge_label)):
                if len(current_path) + i + 1 > max_length:
                    break

                # Build path up to position i
                if direction == 'fw':
                    # Forward: append tokens in order
                    path_to_i = current_path + list(child.edge_label[:i+1])
                    last_token = child.edge_label[i]
                else:
                    # Backward: tokens are stored reversed, so reverse them back
                    # and prepend to build path in forward order
                    reversed_slice = list(reversed(child.edge_label[:i+1]))
                    path_to_i = reversed_slice + current_path
                    last_token = reversed_slice[-1]  # Last token in forward order

                # Check if we should yield this path
                if len(path_to_i) >= min_length:
                    # Check completion requirement
                    if (not only_completions) or (last_token in {'<', '>'}):
                        yield (tuple(path_to_i), child.freqs[i])

            # Continue recursion from end of this edge
            if direction == 'fw':
                new_path = current_path + list(child.edge_label)
            else:
                new_path = list(reversed(child.edge_label)) + current_path

            if len(new_path) < max_length:
                yield from child._traverse_paths(direction, max_length, min_length,
                                                only_completions, new_path)

    def _traverse_shared_paths(self, other_node, direction, max_length, min_length,
                              only_completions, current_path=[]):
        """Yield all shared paths between this node and another node.

        This yields shared paths at every token position along matching edges.
        For backward traversal, reverses edge labels to return paths in forward order.

        Args:
            other_node (RadixNode): The other node to compare with.
            direction (str): 'fw' or 'bw' for forward/backward traversal.
            max_length (int): Maximum path length.
            min_length (int): Minimum path length.
            only_completions (bool): Only yield complete sequences.
            current_path (list): Current path being built.

        Yields:
            tuple: (path_tuple, freq1, freq2) for shared paths.
        """
        if len(current_path) >= max_length:
            return

        # Find children that exist in both nodes
        for first_token in self.children:
            if first_token not in other_node.children:
                continue

            child1 = self.children[first_token]
            child2 = other_node.children[first_token]

            # For shared paths, edge labels must match exactly
            if child1.edge_label != child2.edge_label:
                continue

            # Yield paths for each position along this edge
            for i in range(len(child1.edge_label)):
                if len(current_path) + i + 1 > max_length:
                    break

                # Build path up to position i
                if direction == 'fw':
                    path_to_i = current_path + list(child1.edge_label[:i+1])
                    last_token = child1.edge_label[i]
                else:
                    # Backward: reverse tokens to get forward order
                    reversed_slice = list(reversed(child1.edge_label[:i+1]))
                    path_to_i = reversed_slice + current_path
                    last_token = reversed_slice[-1]

                # Yield if within length bounds
                if len(path_to_i) >= min_length:
                    if (not only_completions) or (last_token in {'<', '>'}):
                        yield (tuple(path_to_i), child1.freqs[i], child2.freqs[i])

            # Continue recursion from end of edges
            if direction == 'fw':
                new_path = current_path + list(child1.edge_label)
            else:
                new_path = list(reversed(child1.edge_label)) + current_path

            if len(new_path) < max_length:
                yield from child1._traverse_shared_paths(child2, direction, max_length,
                                                        min_length, only_completions, new_path)


class RadixFreqTrie:
    """A radix trie for storing word sequences with frequencies.

    This data structure maintains two radix tries:
    - fw_root: Forward trie for storing suffixes (right contexts)
    - bw_root: Backward trie for storing reversed prefixes (left contexts)

    The radix trie compresses non-branching paths into single edges, making it
    more space-efficient than a standard trie while maintaining the same functionality.
    """

    def __init__(self):
        """Initialize an empty radix trie with forward and backward roots."""
        self.fw_root = RadixNode()
        self.bw_root = RadixNode()

    def _insert(self, sequence, freq=1):
        """Record distributions of prefixes and suffixes of sequence.

        This method inserts all prefix-suffix splits of the sequence into the trie,
        storing suffixes in the forward trie and reversed prefixes in the backward trie.

        Arguments:
            sequence (iterable of strings): e.g. ('<', 'this', 'is', 'good', '>')
            freq (int): how many occurrences of sequence should be recorded

        Effect:
            For each prefix--suffix split of sequence, record the occurrences of
            prefix and suffix. (Prefix is reversed to make shared-neighbor search more
            efficient.)
        """
        # Add token frequency mass of sequence to root nodes (to record corpus size)
        token_freq_mass = len(sequence) * freq
        self.fw_root.freq += token_freq_mass
        self.bw_root.freq += token_freq_mass

        # Record each suffix in fw_trie and each reversed prefix in bw_trie
        # For each position i, we insert:
        # - suffix starting at position i into forward trie
        # - reversed prefix ending at position i into backward trie
        for i in range(len(sequence) + 1):
            suffix = sequence[i:]
            prefix = sequence[:i]

            self.fw_root._insert_sequence(suffix, freq)
            self.bw_root._insert_sequence(tuple(reversed(prefix)), freq)

    def setup(self, training_corpus_path='corpora/norvig_corpus.txt'):
        """Set up model with training corpus.

        Args:
            training_corpus_path (str): Path to corpus file with one sentence per line.
        """
        corpus = txt_to_list(training_corpus_path)
        for sequence in corpus:
            self._insert(sequence)

    def sequence_node(self, sequence, direction='fw'):
        """Return the node that represents sequence.

        Arguments:
            sequence (tuple of strings): of the form ('this', 'is')
            direction (string): 'fw' or 'bw', indicating whether we are looking
                for forward neighbors or backward neighbors

        Returns:
            RadixNode representing sequence, or None if not found.
        """
        if direction == 'fw':
            return self.fw_root._find_node(sequence)
        else:
            return self.bw_root._find_node(tuple(reversed(sequence)))

    def freq(self, sequence=''):
        """Return the frequency of sequence.

        Args:
            sequence (tuple): Sequence of tokens.

        Returns:
            int: Frequency count for this sequence.
        """
        if not sequence:
            return self.fw_root.freq if hasattr(self.fw_root, 'freq') else 0

        # Use _find_sequence to handle sequences that end mid-edge
        result = self.fw_root._find_sequence(sequence)
        if result is None:
            return 0

        node, position = result
        if position == -1:
            # Empty sequence, at root
            return self.fw_root.freq
        else:
            # Return frequency at the specified position
            return node.freqs[position]

    def right_neighbors(self, sequence, max_length=float('inf'),
                        min_length=0, only_completions=False):
        """Return generator of (right_neighbor, joint_freq) pairs for sequence.

        Args:
            sequence (tuple): Base sequence to find neighbors for.
            max_length (int): Maximum length of neighbor sequences.
            min_length (int): Minimum length of neighbor sequences.
            only_completions (bool): Only return sequences ending with '<' or '>'.

        Yields:
            tuple: (neighbor_sequence, frequency) pairs.
        """
        return self._neighbors(sequence, 'fw', max_length, min_length, only_completions)

    def left_neighbors(self, sequence, max_length=float('inf'),
                      min_length=0, only_completions=False):
        """Return generator of (left_neighbor, joint_freq) pairs for sequence.

        Args:
            sequence (tuple): Base sequence to find neighbors for.
            max_length (int): Maximum length of neighbor sequences.
            min_length (int): Minimum length of neighbor sequences.
            only_completions (bool): Only return sequences ending with '<' or '>'.

        Yields:
            tuple: (neighbor_sequence, frequency) pairs.
        """
        return self._neighbors(sequence, 'bw', max_length, min_length, only_completions)

    def _neighbors(self, sequence, direction='fw',
                  max_length=float('inf'), min_length=0, only_completions=False):
        """Return generator of (neighbor, joint_freq) pairs for sequence in direction.

        Args:
            sequence (tuple): Base sequence.
            direction (str): 'fw' for right neighbors, 'bw' for left neighbors.
            max_length (int): Maximum neighbor length.
            min_length (int): Minimum neighbor length.
            only_completions (bool): Only return complete sequences.

        Yields:
            tuple: (neighbor_sequence, frequency) pairs.
        """
        # Find the sequence, which might end mid-edge
        root = self.fw_root if direction == 'fw' else self.bw_root

        if direction == 'bw':
            # For backward trie, reverse the sequence
            search_seq = tuple(reversed(sequence))
        else:
            search_seq = sequence

        result = root._find_sequence(search_seq)
        if result is None:
            return iter(())

        seq_node, position = result

        # If sequence ends exactly at a node, traverse from there
        if position == len(seq_node.edge_label) - 1 or position == -1:
            return seq_node._traverse_paths(direction, max_length, min_length,
                                           only_completions, current_path=[])

        # Sequence ends mid-edge: need to yield continuations from within the edge
        # and then traverse children
        return self._neighbors_from_mid_edge(seq_node, position, direction,
                                            max_length, min_length, only_completions)

    def _neighbors_from_mid_edge(self, node, position, direction,
                                max_length, min_length, only_completions):
        """Yield neighbors when starting from middle of an edge.

        Args:
            node (RadixNode): The node containing the edge.
            position (int): Position within the edge where sequence ends.
            direction (str): 'fw' or 'bw'.
            max_length (int): Maximum neighbor length.
            min_length (int): Minimum neighbor length.
            only_completions (bool): Only yield complete sequences.

        Yields:
            tuple: (neighbor_sequence, frequency) pairs.
        """
        # Yield continuations from the rest of this edge
        for i in range(position + 1, len(node.edge_label)):
            if i - position > max_length:
                break

            # Build neighbor from position+1 to i
            if direction == 'fw':
                neighbor = tuple(node.edge_label[position+1:i+1])
                last_token = node.edge_label[i]
            else:
                # Backward: reverse the slice
                neighbor = tuple(reversed(node.edge_label[position+1:i+1]))
                last_token = node.edge_label[position+1]  # First in reversed order

            if len(neighbor) >= min_length:
                if (not only_completions) or (last_token in {'<', '>'}):
                    yield (neighbor, node.freqs[i])

        # Now traverse children from this node
        if len(node.edge_label) - position - 1 < max_length:
            # Build current path up to end of this edge (from start of neighbor perspective)
            if direction == 'fw':
                current_path = list(node.edge_label[position+1:])
            else:
                current_path = list(reversed(node.edge_label[position+1:]))

            yield from node._traverse_paths(direction, max_length, min_length,
                                           only_completions, current_path)

    def shared_right_neighbors(self, sequence_1, sequence_2, max_length=float('inf'),
                               min_length=0, only_completions=False):
        """Return generator of (shared_neighbor, joint_freq_1, joint_freq_2) pairs.

        Args:
            sequence_1 (tuple): First sequence.
            sequence_2 (tuple): Second sequence.
            max_length (int): Maximum neighbor length.
            min_length (int): Minimum neighbor length.
            only_completions (bool): Only return complete sequences.

        Yields:
            tuple: (neighbor, freq1, freq2) for shared right neighbors.
        """
        return self._shared_neighbors(sequence_1, sequence_2, 'fw',
                                     max_length, min_length, only_completions)

    def shared_left_neighbors(self, sequence_1, sequence_2, max_length=float('inf'),
                              min_length=0, only_completions=False):
        """Return generator of (shared_neighbor, joint_freq_1, joint_freq_2) pairs.

        Args:
            sequence_1 (tuple): First sequence.
            sequence_2 (tuple): Second sequence.
            max_length (int): Maximum neighbor length.
            min_length (int): Minimum neighbor length.
            only_completions (bool): Only return complete sequences.

        Yields:
            tuple: (neighbor, freq1, freq2) for shared left neighbors.
        """
        return self._shared_neighbors(sequence_1, sequence_2, 'bw',
                                     max_length, min_length, only_completions)

    def _shared_neighbors(self, sequence_1, sequence_2, direction='fw',
                          max_length=float('inf'), min_length=0, only_completions=False):
        """Return generator of shared neighbors of sequence_1 and sequence_2.

        Arguments:
            sequence_1 (tuple of strings): e.g. ('is', 'good')
            sequence_2 (tuple of strings): e.g. ('was', 'here')
            direction (str): 'fw' for right neighbors, 'bw' for left neighbors.
            max_length (int): Maximum neighbor length.
            min_length (int): Minimum neighbor length.
            only_completions (bool): Only return complete sequences.

        Returns:
            generator of (neighbor, freq_1, freq_2) tuples:
                if direction is 'bw' and the tuple (('this',), 23, 10) is yielded:
                - 'this' occurred before 'is good' 23 times, and
                - 'this' occurred before 'was here' 10 times.
        """
        # Find both sequences, which might end mid-edge
        root = self.fw_root if direction == 'fw' else self.bw_root

        if direction == 'bw':
            search_seq_1 = tuple(reversed(sequence_1))
            search_seq_2 = tuple(reversed(sequence_2))
        else:
            search_seq_1 = sequence_1
            search_seq_2 = sequence_2

        result_1 = root._find_sequence(search_seq_1)
        result_2 = root._find_sequence(search_seq_2)

        if result_1 is None or result_2 is None:
            return iter(())

        seq_node_1, position_1 = result_1
        seq_node_2, position_2 = result_2

        # Both sequences must end at nodes (not mid-edge) for standard traversal
        at_node_1 = (position_1 == len(seq_node_1.edge_label) - 1 or position_1 == -1)
        at_node_2 = (position_2 == len(seq_node_2.edge_label) - 1 or position_2 == -1)

        if at_node_1 and at_node_2:
            # Both at nodes: use standard shared traversal
            return seq_node_1._traverse_shared_paths(seq_node_2, direction, max_length,
                                                     min_length, only_completions, current_path=[])

        # Handle mid-edge cases
        if seq_node_1 is seq_node_2 and position_1 == position_2:
            # Both sequences end at the same position in the same edge: they share neighbors
            return self._shared_neighbors_from_mid_edge(seq_node_1, position_1, direction,
                                                       max_length, min_length, only_completions)

        # Check if they're at different nodes but with matching continuations
        if (seq_node_1 is not seq_node_2 and position_1 == position_2 and
            position_1 < len(seq_node_1.edge_label) - 1 and
            position_2 < len(seq_node_2.edge_label) - 1):
            # Check if the remaining parts of the edges match
            remaining_1 = seq_node_1.edge_label[position_1+1:]
            remaining_2 = seq_node_2.edge_label[position_2+1:]
            if remaining_1 == remaining_2:
                # The continuations match: yield shared neighbors from here
                return self._shared_neighbors_from_matching_edges(
                    seq_node_1, seq_node_2, position_1, direction,
                    max_length, min_length, only_completions)

        # Sequences end at different positions or incompatible edges: no shared neighbors
        return iter(())

    def _shared_neighbors_from_mid_edge(self, node, position, direction,
                                        max_length, min_length, only_completions):
        """Yield shared neighbors when both sequences end at same mid-edge position.

        Args:
            node (RadixNode): The node containing the shared edge.
            position (int): Position within the edge where both sequences end.
            direction (str): 'fw' or 'bw'.
            max_length (int): Maximum neighbor length.
            min_length (int): Minimum neighbor length.
            only_completions (bool): Only yield complete sequences.

        Yields:
            tuple: (neighbor_sequence, freq, freq) tuples (freq is same for both).
        """
        # Yield continuations from the rest of this edge
        for i in range(position + 1, len(node.edge_label)):
            if i - position > max_length:
                break

            # Build neighbor from position+1 to i
            if direction == 'fw':
                neighbor = tuple(node.edge_label[position+1:i+1])
                last_token = node.edge_label[i]
            else:
                # Backward: reverse the slice
                neighbor = tuple(reversed(node.edge_label[position+1:i+1]))
                last_token = node.edge_label[position+1]

            if len(neighbor) >= min_length:
                if (not only_completions) or (last_token in {'<', '>'}):
                    freq = node.freqs[i]
                    yield (neighbor, freq, freq)

        # Now traverse children from this node (they share the same subtree)
        if len(node.edge_label) - position - 1 < max_length:
            # Build current path up to end of this edge
            if direction == 'fw':
                current_path = list(node.edge_label[position+1:])
            else:
                current_path = list(reversed(node.edge_label[position+1:]))

            # For shared traversal from same node, pass it as both arguments
            yield from node._traverse_shared_paths(node, direction, max_length, min_length,
                                                   only_completions, current_path)

    def _shared_neighbors_from_matching_edges(self, node1, node2, position, direction,
                                              max_length, min_length, only_completions):
        """Yield shared neighbors when sequences end at same position in different nodes with matching continuations.

        Args:
            node1, node2 (RadixNode): The two nodes with matching edge suffixes.
            position (int): Position within edges where both sequences end.
            direction (str): 'fw' or 'bw'.
            max_length (int): Maximum neighbor length.
            min_length (int): Minimum neighbor length.
            only_completions (bool): Only yield complete sequences.

        Yields:
            tuple: (neighbor_sequence, freq1, freq2) tuples.
        """
        # The edges match from position+1 onward, so yield those tokens
        for i in range(position + 1, len(node1.edge_label)):
            if i - position > max_length:
                break

            # Build neighbor from position+1 to i
            if direction == 'fw':
                neighbor = tuple(node1.edge_label[position+1:i+1])
                last_token = node1.edge_label[i]
            else:
                # Backward: reverse the slice
                neighbor = tuple(reversed(node1.edge_label[position+1:i+1]))
                last_token = node1.edge_label[position+1]

            if len(neighbor) >= min_length:
                if (not only_completions) or (last_token in {'<', '>'}):
                    yield (neighbor, node1.freqs[i], node2.freqs[i])

        # Now traverse children - they share structure from here on
        if len(node1.edge_label) - position - 1 < max_length:
            # Build current path up to end of edges
            if direction == 'fw':
                current_path = list(node1.edge_label[position+1:])
            else:
                current_path = list(reversed(node1.edge_label[position+1:]))

            yield from node1._traverse_shared_paths(node2, direction, max_length, min_length,
                                                   only_completions, current_path)
