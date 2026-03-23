#!/usr/bin/env python3
"""Extract terminal sequences for a target constituent label from Kainoki treebank files."""

from __future__ import annotations

import argparse
import pickle
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

TOKEN_RE = re.compile(r"\(|\)|[^\s()]+")
NULL_TOKEN_RE = re.compile(r"^\*.*\*$")

# Phrase-boundary punctuation markers to exclude from extracted sequences.
BOUNDARY_PUNCT_TOKENS = {
    ",",
    "，",
    ";",
    "；",
    ":",
    "：",
    ".",
    "．",
    "。",
    "、",
}


@dataclass
class Node:
    label: str
    children: list[Node | str]


class ParseError(RuntimeError):
    pass


def parse_tree(tokens: list[str], pos: int = 0) -> tuple[Node, int]:
    if pos >= len(tokens) or tokens[pos] != "(":
        raise ParseError(f"Expected '(' at token index {pos}")

    pos += 1
    if pos >= len(tokens):
        raise ParseError("Unexpected end after '('")

    label = tokens[pos]
    if label in {"(", ")"}:
        raise ParseError(f"Expected label at token index {pos}, got {label!r}")

    pos += 1
    children: list[Node | str] = []

    while pos < len(tokens) and tokens[pos] != ")":
        if tokens[pos] == "(":
            child, pos = parse_tree(tokens, pos)
            children.append(child)
        else:
            children.append(tokens[pos])
            pos += 1

    if pos >= len(tokens) or tokens[pos] != ")":
        raise ParseError(f"Expected ')' for label {label!r}")

    return Node(label=label, children=children), pos + 1


def parse_wrapper(tokens: list[str]) -> Node:
    """Parse one full treebank line with an unlabeled outer wrapper."""
    if not tokens or tokens[0] != "(":
        raise ParseError("Line does not start with '('")

    pos = 1
    children: list[Node | str] = []

    while pos < len(tokens) and tokens[pos] != ")":
        if tokens[pos] == "(":
            # Wrapper can contain either labeled subtrees or nested wrappers.
            if pos + 1 < len(tokens) and tokens[pos + 1] == "(":
                nested_tokens: list[str] = []
                depth = 0
                while pos < len(tokens):
                    tok = tokens[pos]
                    nested_tokens.append(tok)
                    if tok == "(":
                        depth += 1
                    elif tok == ")":
                        depth -= 1
                        if depth == 0:
                            pos += 1
                            break
                    pos += 1
                child = parse_wrapper(nested_tokens)
                children.extend(child.children)
            else:
                child, pos = parse_tree(tokens, pos)
                children.append(child)
        else:
            children.append(tokens[pos])
            pos += 1

    if pos >= len(tokens) or tokens[pos] != ")":
        raise ParseError("Missing closing ')' for outer wrapper")
    if pos + 1 != len(tokens):
        raise ParseError("Extra tokens after outer wrapper")

    return Node(label="__ROOT__", children=children)


def iter_nodes(node: Node) -> Iterator[Node]:
    yield node
    for child in node.children:
        if isinstance(child, Node):
            yield from iter_nodes(child)


def iter_terminals(node: Node) -> Iterator[str]:
    for child in node.children:
        if isinstance(child, Node):
            yield from iter_terminals(child)
        else:
            yield child


def is_leaf_node(node: Node) -> bool:
    return all(not isinstance(child, Node) for child in node.children)


def is_unary_phrase(node: Node) -> bool:
    return len(node.children) == 1 and isinstance(node.children[0], Node)


def is_null_token(token: str) -> bool:
    return token == "*" or bool(NULL_TOKEN_RE.match(token))


def has_boundary_punctuation(tokens: list[str]) -> bool:
    for tok in tokens:
        if tok in BOUNDARY_PUNCT_TOKENS:
            return True
    return False


def base_label(label: str) -> str:
    # Strip sort/reference suffix first, then function/index suffixes.
    return label.split(";", 1)[0].split("-", 1)[0]


def label_matches(node_label: str, target: str, mode: str) -> bool:
    if mode == "exact":
        return node_label == target
    if mode == "base":
        return base_label(node_label) == target
    raise ValueError(f"Unsupported mode: {mode}")


def category_specific_match_allowed(node: Node, target_label: str, match_mode: str) -> bool:
    # NP-specific rule:
    # keep NP-category constituents if they are non-unary, or unary with child label != PRO.
    target_is_np = (
        target_label == "NP" if match_mode == "exact" else base_label(target_label) == "NP"
    )
    if target_is_np and base_label(node.label) == "NP":
        if not is_unary_phrase(node):
            return True
        child = node.children[0]
        return not (isinstance(child, Node) and child.label == "PRO")

    return True


def extract_sequences_from_line(
    line: str, target_label: str, match_mode: str
) -> list[list[str]]:
    tokens = TOKEN_RE.findall(line)
    if not tokens:
        return []

    root = parse_wrapper(tokens)

    matches: list[list[str]] = []
    for node in iter_nodes(root):
        if not label_matches(node.label, target_label, match_mode):
            continue
        if not category_specific_match_allowed(node, target_label, match_mode):
            continue

        raw_tokens = list(iter_terminals(node))
        if has_boundary_punctuation(raw_tokens):
            continue

        words = [tok for tok in raw_tokens if not is_null_token(tok)]
        if not words:
            continue

        matches.append(words)

    return matches


def extract_sequences(
    treebank_dir: Path, target_label: str, match_mode: str
) -> list[list[str]]:
    all_sequences: list[list[str]] = []

    for path in sorted(treebank_dir.iterdir()):
        if not path.is_file():
            continue

        with path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    seqs = extract_sequences_from_line(line, target_label, match_mode)
                except ParseError as exc:
                    raise ParseError(f"{path}:{line_no}: {exc}") from exc
                all_sequences.extend(seqs)

    return all_sequences


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract word sequences for a constituent label from Kainoki treebank files "
            "and save them as a pickle (list[list[str]])."
        )
    )
    parser.add_argument("label", help="Target constituent label (e.g., NP or NP-SBJ)")
    parser.add_argument(
        "--treebank-dir",
        type=Path,
        default=Path("treebank_files"),
        help="Directory containing treebank files (default: treebank_files)",
    )
    parser.add_argument(
        "--match-mode",
        choices=["base", "exact"],
        default="base",
        help=(
            "Label matching mode: base matches by category before '-' and ';' "
            "(NP matches NP-SBJ, NP;...), exact matches full label."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output pickle file path (default: <label>_sequences.pkl)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = args.output or Path(f"{args.label}_sequences.pkl")

    sequences = extract_sequences(args.treebank_dir, args.label, args.match_mode)

    with output_path.open("wb") as f:
        pickle.dump(sequences, f)

    print(f"Saved {len(sequences)} sequences to {output_path}")


if __name__ == "__main__":
    main()
