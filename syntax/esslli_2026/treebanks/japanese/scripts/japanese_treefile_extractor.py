from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


PUNCTUATION_LABELS = {
    "FS",
    "PUL",
    "PULB",
    "PULQ",
    "PUNC",
    "PUR",
    "PURB",
    "PURQ",
    "PUQ",
    "SYM",
}
NP_LABEL_PATTERN = re.compile(r"^NP(?:$|[-;])")
EXCLUDED_MULTIWORD_NP_BASE_LABELS = {
    "NP-ADV",
    "NP-DOB1",
    "NP-LGS",
    "NP-PRP",
}


@dataclass
class Node:
    label: str | None
    children: list["Node | str"]


@dataclass(frozen=True)
class Terminal:
    label: str
    word: str


def tokenize_tree(tree_string: str) -> list[str]:
    return re.findall(r"\(|\)|[^\s()]+", tree_string)


def parse_tree(tokens: list[str], start_index: int = 0) -> tuple[Node, int]:
    if tokens[start_index] != "(":
        raise ValueError(f"Expected '(' at token {start_index}, got {tokens[start_index]!r}")

    index = start_index + 1
    label: str | None = None
    if tokens[index] != "(":
        label = tokens[index]
        index += 1

    children: list[Node | str] = []
    while tokens[index] != ")":
        if tokens[index] == "(":
            child, index = parse_tree(tokens, index)
            children.append(child)
        else:
            children.append(tokens[index])
            index += 1

    return Node(label=label, children=children), index + 1


def parse_tree_line(tree_line: str) -> Node:
    tokens = tokenize_tree(tree_line.strip())
    tree, next_index = parse_tree(tokens)
    if next_index != len(tokens):
        raise ValueError("Unexpected tokens after complete parse")
    return tree


def is_preterminal(node: Node) -> bool:
    return node.label is not None and len(node.children) == 1 and isinstance(node.children[0], str)


def is_punctuation_label(label: str) -> bool:
    return label in PUNCTUATION_LABELS or label.startswith("PU")


def is_np_label(label: str | None) -> bool:
    return bool(label and NP_LABEL_PATTERN.match(label))


def np_base_label(label: str | None) -> str | None:
    if label is None:
        return None
    return label.split(";", 1)[0]


def is_excluded_multiword_np_label(label: str | None) -> bool:
    base_label = np_base_label(label)
    return base_label in EXCLUDED_MULTIWORD_NP_BASE_LABELS


def is_null_terminal(word: str) -> bool:
    return word.startswith("*")


def iter_terminals(node: Node) -> list[Terminal]:
    terminals: list[Terminal] = []
    if node.label == "ID":
        return terminals
    if is_preterminal(node):
        terminals.append(Terminal(node.label, node.children[0]))
        return terminals
    for child in node.children:
        if isinstance(child, Node):
            terminals.extend(iter_terminals(child))
    return terminals


def tree_to_contiguous_sequences(tree: Node) -> list[tuple[str, ...]]:
    sequences: list[tuple[str, ...]] = []
    current_sequence: list[str] = []
    for terminal in iter_terminals(tree):
        if is_punctuation_label(terminal.label):
            if current_sequence:
                sequences.append(tuple(current_sequence))
                current_sequence = []
            continue
        if is_null_terminal(terminal.word):
            continue
        current_sequence.append(terminal.word)
    if current_sequence:
        sequences.append(tuple(current_sequence))
    return sequences


def np_sequence_from_node(node: Node) -> tuple[str, ...] | None:
    terminals = iter_terminals(node)
    if any(is_punctuation_label(terminal.label) for terminal in terminals):
        return None
    words = tuple(terminal.word for terminal in terminals if not is_null_terminal(terminal.word))
    return words or None


def find_np_sequences(tree: Node) -> list[tuple[str, ...]]:
    sequences: list[tuple[str, ...]] = []
    if is_np_label(tree.label):
        sequence = np_sequence_from_node(tree)
        if sequence is not None:
            sequences.append(sequence)
    for child in tree.children:
        if isinstance(child, Node):
            sequences.extend(find_np_sequences(child))
    return sequences


def walk_nodes(tree: Node) -> list[Node]:
    nodes = [tree]
    for child in tree.children:
        if isinstance(child, Node):
            nodes.extend(walk_nodes(child))
    return nodes


def iter_trees_in_file(tree_filepath: str | Path) -> list[Node]:
    filepath = Path(tree_filepath)
    return [
        parse_tree_line(line)
        for line in filepath.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def extract_contiguous_sequences(tree_filepath: str | Path) -> list[tuple[str, ...]]:
    sequences: list[tuple[str, ...]] = []
    for tree in iter_trees_in_file(tree_filepath):
        sequences.extend(tree_to_contiguous_sequences(tree))
    return sequences


def extract_multiword_noun_phrases(tree_filepath: str | Path) -> list[tuple[str, ...]]:
    noun_phrases: list[tuple[str, ...]] = []
    for tree in iter_trees_in_file(tree_filepath):
        noun_phrases.extend(
            sequence
            for node in walk_nodes(tree)
            if is_np_label(node.label) and not is_excluded_multiword_np_label(node.label)
            for sequence in [np_sequence_from_node(node)]
            if sequence is not None
            if len(sequence) > 1
        )
    return noun_phrases


def extract_singleword_noun_phrases(tree_filepath: str | Path) -> list[tuple[str, ...]]:
    noun_phrases: list[tuple[str, ...]] = []
    for tree in iter_trees_in_file(tree_filepath):
        noun_phrases.extend(sequence for sequence in find_np_sequences(tree) if len(sequence) == 1)
    return noun_phrases


def main():
    sample_tree_filepath = Path("../treebank/news_kahoku39")
    all_sequences = extract_contiguous_sequences(sample_tree_filepath)
    multiword_nps = extract_multiword_noun_phrases(sample_tree_filepath)
    singleword_nps = extract_singleword_noun_phrases(sample_tree_filepath)
    return all_sequences, multiword_nps, singleword_nps
