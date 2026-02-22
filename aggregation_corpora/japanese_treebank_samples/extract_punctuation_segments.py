#!/usr/bin/env python3
"""Build a pickle corpus of within-boundary-punctuation word sequences."""

from __future__ import annotations

import argparse
import pickle
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

TOKEN_RE = re.compile(r"\(|\)|[^\s()]+")
NULL_TOKEN_RE = re.compile(r"^\*.*\*$")

# Phrase-boundary punctuation delimiters.
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
    """Parse one full line with an unlabeled outer wrapper."""
    if not tokens or tokens[0] != "(":
        raise ParseError("Line does not start with '('")

    pos = 1
    children: list[Node | str] = []

    while pos < len(tokens) and tokens[pos] != ")":
        if tokens[pos] == "(":
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
                nested = parse_wrapper(nested_tokens)
                children.extend(nested.children)
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


def iter_terminals(node: Node) -> Iterator[str]:
    for child in node.children:
        if isinstance(child, Node):
            yield from iter_terminals(child)
        else:
            yield child


def is_null_token(token: str) -> bool:
    return token == "*" or bool(NULL_TOKEN_RE.match(token))


def split_on_boundary_punct(tokens: list[str]) -> list[list[str]]:
    segments: list[list[str]] = []
    current: list[str] = []

    for tok in tokens:
        if tok in BOUNDARY_PUNCT_TOKENS:
            if current:
                segments.append(current)
                current = []
            continue
        current.append(tok)

    if current:
        segments.append(current)

    return segments


def terminals_without_id(root: Node) -> list[str]:
    tokens: list[str] = []
    for child in root.children:
        if isinstance(child, Node) and child.label == "ID":
            continue
        if isinstance(child, Node):
            tokens.extend(iter_terminals(child))
        else:
            tokens.append(child)
    return tokens


def build_corpus(treebank_dir: Path) -> list[list[str]]:
    corpus: list[list[str]] = []

    for path in sorted(treebank_dir.iterdir()):
        if not path.is_file():
            continue

        with path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue

                try:
                    root = parse_wrapper(TOKEN_RE.findall(line))
                except ParseError as exc:
                    raise ParseError(f"{path}:{line_no}: {exc}") from exc

                terminals = terminals_without_id(root)
                words = [tok for tok in terminals if not is_null_token(tok)]
                segments = split_on_boundary_punct(words)
                corpus.extend(seg for seg in segments if seg)

    return corpus


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract all within-boundary-punctuation word sequences from Kainoki treebank "
            "files and save as pickle (list[list[str]])."
        )
    )
    parser.add_argument(
        "--treebank-dir",
        type=Path,
        default=Path("treebank_files"),
        help="Directory containing treebank files (default: treebank_files)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("within_phrase_boundary_sequences.pkl"),
        help="Output pickle path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    corpus = build_corpus(args.treebank_dir)

    with args.output.open("wb") as f:
        pickle.dump(corpus, f)

    print(f"Saved {len(corpus)} sequences to {args.output}")


if __name__ == "__main__":
    main()
