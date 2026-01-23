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
        """Node of a radix trie, containing compressed edge in label.
        """
        self.label = sequence_label
        self.freq = sequence_freq
        self.children = {} if sequence_children is None else sequence_children

    def _insert(self, sequence: Tuple[str, ...], freq: int = 1) -> None:
        """Insert sequence and increment freq at node.
        """
        if not sequence:
            return
        label = self.label
        # Find index of last agreeing token and update node accordingly
        split_point = -1
        for seq_token, label_token in zip(sequence, label):
            split_point += 1
            # Case 1: sequence and label disagree at some token. Split node at disagreeing
            # token and rearrange children
            if seq_token != label_token:
                # Get remaining suffixes
                rem_sequence, rem_label = sequence[split_point:], label[split_point:]
                # Relabel node to common prefix
                self.label = label[:split_point]
                # Make child node for remaining label, copy original label's children
                rem_label_child_node = RadixNode(rem_label, self.freq, self.children.copy())
                # Make child node for remaining sequence
                rem_sequence_child_node = RadixNode(rem_sequence, freq)
                # Assign new children and increment freq
                self.children = {
                        rem_sequence[0]: rem_sequence_child_node,
                        rem_label[0]: rem_label_child_node
                    }
                self.freq += freq
                return
        # Sequence and label don't disagree. Sequence is endmarked, so they are either
        # identical or label is proper prefix of sequence. Increment label's freq, then
        # check which case holds and handle it
        self.freq += freq
        rem_sequence, rem_label = sequence[split_point + 1:], label[split_point + 1:]
        # Case 2: sequence is prefix of label => they are identical. Do nothing.
        if not rem_sequence:
            return
        # Case 3: label is proper prefix of sequence. Check if node has child headed by
        # head of remaining sequence, and insert or create new node accordingly
        self._insert_or_make_child(rem_sequence, freq)

    def _insert_or_make_child(self, sequence, freq):
        sequence_head = sequence[0] 
        if sequence_head in self.children:
            self.children[sequence_head]._insert(sequence, freq)
        else:
            self.children[sequence_head] = RadixNode(sequence, freq)

    def _find(self, sequence) -> Optional[Tuple["RadixNode", int]]:
        label = self.label
        # Match sequence with label as long as possible
        position = -1
        for seq_token, label_token in zip(sequence, label):
            if seq_token != label_token:
                return None
            position += 1
        rem_sequence, rem_label = sequence[position + 1:], label[position + 1:]
        # Sequence ends inside label => return found node and position
        if not rem_sequence:
            return (self, position)
        # Sequence doesn't end inside label => recurse to child if possible
        try:
            return self.children[rem_sequence[0]]._find(rem_sequence)
        except KeyError:
            return None

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

    def _find(self, sequence, direction: Direction = "fw"):
        if direction == "fw":
            root, goal_sequence = self.fw_root, sequence
        else:
            root, goal_sequence = self.bw_root, tuple(reversed(sequence))
        return root._find(goal_sequence)

    def freq(self, sequence, direction: Direction = "fw"):
        return self._find(sequence, direction)[0].freq

test_corpus = [
        tuple("< some dog was barking in the street >".split()),
        tuple("< i was walking around the street >".split()),
        tuple("< some dog was running around the table >".split()),
        tuple("< some parrot was here >".split())
    ]

def main():
    model = RadixTrie()
    model.setup(test_corpus)
