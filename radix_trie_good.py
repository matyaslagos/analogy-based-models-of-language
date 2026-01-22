#!/usr/bin/env python3

from typing import Optional, Tuple, List, Dict, Iterator, Literal, Union

Direction = Literal["fw", "bw"]

class RadixNode:
    def __init__(
            self,
            sequence_label: Tuple[str, ...] = (),
            sequence_freq: int = 0,
            sequence_children: Optional[Dict[str, "RadixNode"]] = None
        ):
        self.label = sequence_label
        self.freq = sequence_freq
        self.children = {} if sequence_children is None else sequence_children

    def _insert(self, sequence: Tuple[str, ...], freq: int = 1) -> None:
        """Insert sequence and increment freq at node.
        """
        if not sequence:
            return
        label = self.label
        # Find index of disagreeing token (if any) and update node
        split_point = -1
        for i, (seq_token, label_token) in enumerate(zip(sequence, label)):
            split_point = i
            # If disagreement, split node at disagreeing token and rearrange children
            if seq_token != label_token:
                # Get distinct suffixes
                rem_sequence, rem_label = sequence[split_point:], label[split_point:]
                # Relabel node to common prefix
                self.label = label[:split_point]
                # Make child node for original label's suffix, copy original children
                rem_label_child_node = RadixNode(rem_label, self.freq, self.children.copy())
                # Make child node for sequence's suffix
                rem_seq_child_node = RadixNode(rem_sequence, freq)
                # Assign new children
                self.children = {
                        rem_sequence[0]: rem_seq_child_node,
                        rem_label[0]: rem_label_child_node
                    }
                self.freq += freq
                return
        # Sequence and label don't disagree: increment frequency and update children 
        self.freq += freq
        # Get remaining suffixes
        rem_sequence, rem_label = sequence[split_point + 1:], label[split_point + 1:]
        # If sequence is prefix of label, then they are identical (due to endmarking)
        if not rem_sequence:
            return
        # If label is proper prefix of sequence, then check if node has child headed by
        # the head of remaining sequence, and insert or create new node accordingly
        if rem_sequence[0] in self.children:
            self.children[rem_sequence[0]]._insert(rem_sequence, freq)
        else:
            self.children[rem_sequence[0]] = RadixNode(rem_sequence, freq)

class RadixTrie:
    def __init__(self):
        self.fw_root = RadixNode()
        self.bw_root = RadixNode()

    def setup(self, corpus: List[Tuple[str, ...]]) -> None:
        for sequence in corpus:
            self._insert(sequence)

    def _insert(self, sequence: Tuple[str, ...], freq: int = 1) -> None:
        reversed_sequence = tuple(reversed(sequence))
        for i in range(len(sequence) + 1):
            self.fw_root._insert(sequence[i:], freq)
            self.bw_root._insert(reversed_sequence[i:], freq)

test_corpus = [
        tuple("< some dog was barking in the street >".split()),
        tuple("< i was walking around the street >".split()),
        tuple("< some dog was running around the table >".split()),
        tuple("< some parrot was here >".split())
    ]

