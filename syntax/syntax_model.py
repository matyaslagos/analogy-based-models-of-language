#!/usr/bin/env python3
# ---------------------------------- #
# Trie data structure implementation #
# ---------------------------------- #

# --------------- #
# Setup functions #
# --------------- #

# Import some text as corpus
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

# --------------------------------------- #
# FreqNode and FreqTrie class definitions #
# --------------------------------------- #

class FreqNode:
    def __init__(self):
        self.children = {}
        self.freq = 0

    def _increment_or_make_branch(self, sequence, freq=1):
        """Increment the frequency of sequence or make a new branch for it.
        """
        current_node = self
        for token in sequence:
            current_node = current_node._get_or_make_child(token)
            current_node.freq += freq

    def _get_or_make_child(self, token):
        """Return the child called token or make a new child called token.
        """
        if token not in self.children:
            self.children[token] = FreqNode()
        return self.children[token]

class FreqTrie:
    def __init__(self):
        self.fw_root = FreqNode()
        self.bw_root = FreqNode()
    
    # Insert a sequence
    def _insert(self, sequence, freq=1):
        """Record distributions of prefixes and suffixes of sequence.

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
        prefix_suffix_pairs = (
            (sequence[:i], sequence[i:])
            for i in range(len(sequence) + 1)
        )
        for prefix, suffix in prefix_suffix_pairs:
            self.fw_root._increment_or_make_branch(suffix, freq)
            self.bw_root._increment_or_make_branch(reversed(prefix), freq)
    
    # Set up model with training corpus
    def setup(self, training_corpus_path='corpora/norvig_corpus.txt'):
        corpus = txt_to_list(training_corpus_path)
        for sequence in corpus:
            self._insert(sequence)
    
    # Get node of sequence
    def sequence_node(self, sequence, direction='fw'):
        """Return the node that represents sequence.

        Arguments:
            sequence (tuple of strings): of the form ('this', 'is')
            direction (string): 'fw' or 'bw', indicating whether we are looking
                for forward neighbors or backward neighbors

        Returns:
            FreqNode representing sequence.
        """
        # If looking for right neighbors, start in root of forward trie
        if direction == 'fw':
            current_node = self.fw_root
        # If looking for left neighbors, start in root of backward trie and reverse sequence
        else:
            current_node = self.bw_root
            sequence = reversed(sequence)
        # Go to node of sequence
        for token in sequence:
            try:
                current_node = current_node.children[token]
            except KeyError:
                return None
        return current_node

    # Get frequency of sequence
    def freq(self, sequence=''):
        """Return the frequency of sequence.
        """
        seq_node = self.sequence_node(sequence)
        return seq_node.freq if seq_node else 0
    
    # Get right neighbors (with frequencies) of sequence
    def right_neighbors(self, sequence, max_length=float('inf'),
                        min_length=0, only_completions=False):
        """Return generator of (right_neighbor, joint_freq) pairs for sequence.
        """
        return self._neighbors(sequence, 'fw',
                               max_length, min_length, only_completions)
    
    # Get left neighbors (with frequencies) of sequence
    def left_neighbors(self, sequence, max_length=float('inf'),
                       min_length=0, only_completions=False):
        """Return generator of (left_neighbor, joint_freq) pairs for sequence.
        """
        return self._neighbors(sequence, 'bw',
                               max_length, min_length, only_completions)
    
    # Get neighbors of sequence (with frequencies) in direction
    def _neighbors(self, sequence, direction='fw',
                   max_length=float('inf'), min_length=0, only_completions=False):
        """Return generator of (neighbor, joint_freq) pairs for sequence in direction.
        """
        seq_node = self.sequence_node(sequence, direction)
        if not seq_node:
            return iter(())
        return self._neighbors_aux(seq_node, direction, max_length, min_length,
                                   only_completions, path=[])
    
    # Auxiliary recursive function for _neighbors()
    def _neighbors_aux(self, seq_node, direction,
                       max_length, min_length, only_completions, path):
        """Yield each neighbor of sequence with their joint frequency.
        """
        if len(path) >= max_length:
            return
        for child in seq_node.children:
            new_path = path + [child] if direction == 'fw' else [child] + path
            child_node = seq_node.children[child]
            freq = child_node.freq
            if len(new_path) >= min_length:
                if (not only_completions) or (child in {'<','>'}):
                    yield (tuple(new_path), freq)
            yield from self._neighbors_aux(child_node, direction,
                                           max_length, min_length,
                                           only_completions, new_path)
    
    # Get shared right neighbors (with frequencies) of sequence_1 and sequence_2
    def shared_right_neighbors(self, sequence_1, sequence_2, max_length=float('inf'),
                               min_length=0, only_completions=False):
        """Return generator of (shared_neighbor, joint_freq_1, joint_freq_2) pairs.
        """
        return self._shared_neighbors(sequence_1, sequence_2, 'fw',
                                      max_length, min_length, only_completions)
    
    # Get shared left neighbors (with frequencies) of sequence_1 and sequence_2
    def shared_left_neighbors(self, sequence_1, sequence_2, max_length=float('inf'),
                              min_length=0, only_completions=False):
        """Return generator of (shared_neighbor, joint_freq_1, joint_freq_2) pairs.
        """
        return self._shared_neighbors(sequence_1, sequence_2, 'bw',
                                      max_length, min_length, only_completions)
    
    # Get shared neighbors (with frequencies) of sequence_1 and sequence_2 in direction
    def _shared_neighbors(self, sequence_1, sequence_2, direction='fw',
                          max_length=float('inf'), min_length=0, only_completions=False):
        """Return generator of shared neighbors of sequence_1 and sequence_2.

        Arguments:
            sequence_1 (tuple of strings): e.g. ('is', 'good')
            sequence_2 (tuple of strings): e.g. ('was', 'here')

        Returns:
            generator of (neighbor, freq_1, freq_2) tuples:
                if direction is 'bw' and the tuple (('this',), 23, 10) is yielded:
                - 'this' occurred before 'is good' 23 times, and
                - 'this' occurred before 'was here' 10 times.
        """
        seq_node_1 = self.sequence_node(sequence_1, direction)
        seq_node_2 = self.sequence_node(sequence_2, direction)
        if not seq_node_1 or not seq_node_2:
            return iter(())
        return self._shared_neighbors_aux(seq_node_1, seq_node_2, direction,
                                          max_length, min_length, only_completions, path=[])
    
    # Auxiliary function for _shared_neighbors()
    def _shared_neighbors_aux(self, seq_node_1, seq_node_2, direction,
                              max_length, min_length, only_completions, path):
        """Yield shared neighbors of seq_node_1 and seq_node_2.
        """
        if len(path) >= max_length:
            return
        for child in seq_node_1.children:
            if child in seq_node_2.children:
                new_path = path + [child] if direction == 'fw' else [child] + path
                child_node_1 = seq_node_1.children[child]
                child_node_2 = seq_node_2.children[child]
                freq_1 = child_node_1.freq
                freq_2 = child_node_2.freq
                if len(new_path) >= min_length:
                    if (not only_completions) or (child in {'<','>'}):
                        yield (tuple(new_path), freq_1, freq_2)
                yield from self._shared_neighbors_aux(child_node_1, child_node_2,
                                                      direction, max_length, min_length,
                                                      only_completions, new_path)