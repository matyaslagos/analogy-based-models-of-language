from __future__ import annotations

import argparse
from collections import Counter
import pickle
from pathlib import Path
from typing import Iterable
import xml.etree.ElementTree as ET


WordSequence = tuple[str, ...]

# These relations typically mark material internal to larger phrases rather than
# stand-alone nominal constituents, so they are excluded from the implicit
# single-word NP heuristic.
_EXCLUDED_IMPLICIT_NP_RELS = {"--", "cmp", "crd", "det", "hd", "mod", "mwp"}
_SUBJECT_OR_OBJECT_RELS = {"su", "obj1", "obj2", "pobj1"}


def parse_alpino_file(path: str | Path) -> ET.Element:
    """Parse a sentence-level Alpino XML file and return the document root."""
    return ET.parse(path).getroot()


def iter_nodes(node: ET.Element) -> Iterable[ET.Element]:
    """Yield a node and all descendant nodes in document order."""
    yield node
    for child in child_nodes(node):
        yield from iter_nodes(child)


def child_nodes(node: ET.Element) -> list[ET.Element]:
    return [child for child in node if child.tag == "node"]


def is_terminal(node: ET.Element) -> bool:
    return not child_nodes(node)


def is_punctuation(node: ET.Element) -> bool:
    return node.get("pt") == "let" or node.get("pos") == "punct"


def token_index(node: ET.Element) -> int:
    return int(node.attrib["begin"])


def token_word(node: ET.Element) -> str:
    return node.attrib["word"].lower()


def terminal_descendants(node: ET.Element) -> list[ET.Element]:
    leaves = [desc for desc in iter_nodes(node) if is_terminal(desc) and "word" in desc.attrib]
    return sorted(leaves, key=token_index)


def non_punct_terminal_descendants(node: ET.Element) -> list[ET.Element]:
    return [leaf for leaf in terminal_descendants(node) if not is_punctuation(leaf)]


def words_from_terminals(terminals: list[ET.Element]) -> WordSequence:
    return tuple(token_word(terminal) for terminal in terminals)


def is_contiguous_terminal_sequence(terminals: list[ET.Element]) -> bool:
    if not terminals:
        return False
    indices = [token_index(terminal) for terminal in terminals]
    start = indices[0]
    return indices == list(range(start, start + len(indices)))


def contiguous_non_punct_words(node: ET.Element) -> WordSequence | None:
    terminals = terminal_descendants(node)
    if not terminals or any(is_punctuation(terminal) for terminal in terminals):
        return None
    if not is_contiguous_terminal_sequence(terminals):
        return None
    return words_from_terminals(terminals)


def terminal_runs_without_punctuation(root: ET.Element) -> list[list[ET.Element]]:
    runs: list[list[ET.Element]] = []
    current_run: list[ET.Element] = []

    for terminal in terminal_descendants(root):
        # Punctuation acts as a hard boundary for the "contiguous" sequences the
        # user asked for, so each run is built only from neighboring non-punct tokens.
        if is_punctuation(terminal):
            if current_run:
                runs.append(current_run)
                current_run = []
            continue
        current_run.append(terminal)

    if current_run:
        runs.append(current_run)

    return runs


def extract_all_contiguous_sequences_from_file(path: str | Path) -> Counter[WordSequence]:
    root = parse_alpino_file(path)
    sequences: Counter[WordSequence] = Counter()

    for run in terminal_runs_without_punctuation(root):
        # "All contiguous sequences" means the maximal punctuation-free stretches
        # of surface words, not every substring inside those stretches.
        sequences[words_from_terminals(run)] += 1

    return sequences


def extract_multiword_np_sequences_from_file(path: str | Path) -> Counter[WordSequence]:
    root = parse_alpino_file(path)
    sequences: Counter[WordSequence] = Counter()

    for node in iter_nodes(root):
        if node.get("cat") != "np":
            continue
        # We only want true contiguous NP yields, excluding any span whose terminal
        # yield contains punctuation or gaps in token order.
        words = contiguous_non_punct_words(node)
        if words is None or len(words) <= 1:
            continue
        sequences[words] += 1

    return sequences


def parent_map(root: ET.Element) -> dict[ET.Element, ET.Element]:
    mapping: dict[ET.Element, ET.Element] = {}
    for node in iter_nodes(root):
        for child in child_nodes(node):
            mapping[child] = node
    return mapping


def has_np_ancestor(node: ET.Element, parents: dict[ET.Element, ET.Element]) -> bool:
    current = parents.get(node)
    while current is not None:
        if current.get("cat") == "np":
            return True
        current = parents.get(current)
    return False


def is_nominal_or_pronominal_terminal(node: ET.Element) -> bool:
    pt = node.get("pt")
    pos = node.get("pos")
    pdtype = node.get("pdtype")
    ntype = node.get("ntype")

    # Bare common nouns are excluded from the implicit single-word NP heuristic.
    # They are only counted when the treebank explicitly wraps them in `cat="np"`.
    if pt == "n":
        return ntype == "eigen" or pos == "name"
    if pt == "vnw":
        if pdtype == "adv-pron":
            return False
        return True
    if pt == "tw" and pos == "noun":
        return True
    if pos in {"noun", "name", "pron"}:
        return True
    return pos == "det" and pdtype == "pron"


def is_pronominal_terminal(node: ET.Element) -> bool:
    pdtype = node.get("pdtype")
    return node.get("pt") == "vnw" and pdtype != "adv-pron"


def extract_single_word_np_sequences_from_file(path: str | Path) -> Counter[WordSequence]:
    root = parse_alpino_file(path)
    parents = parent_map(root)
    sequences: Counter[WordSequence] = Counter()
    counted_indices: set[int] = set()

    for node in iter_nodes(root):
        if node.get("cat") != "np":
            continue
        # Some single-word noun phrases are explicitly represented as unary NP nodes.
        words = contiguous_non_punct_words(node)
        if words is None or len(words) != 1:
            continue
        terminal = non_punct_terminal_descendants(node)[0]
        index = token_index(terminal)
        if index in counted_indices:
            continue
        sequences[words] += 1
        counted_indices.add(index)

    for node in iter_nodes(root):
        if not is_terminal(node) or "word" not in node.attrib:
            continue
        if is_punctuation(node) or not is_nominal_or_pronominal_terminal(node):
            continue
        if node.get("rel") in _EXCLUDED_IMPLICIT_NP_RELS:
            continue
        # Bare pronouns, nouns, names, and nominal numerals can function as
        # one-word noun phrases even when the tree does not wrap them in `cat="np"`.
        # We therefore keep only stand-alone nominal terminals outside larger NPs.
        if has_np_ancestor(node, parents):
            continue
        # For pronouns, keep only bare subject/object uses rather than every
        # pronominal function in the treebank.
        if is_pronominal_terminal(node) and node.get("rel") not in _SUBJECT_OR_OBJECT_RELS:
            continue

        index = token_index(node)
        if index in counted_indices:
            continue

        sequences[(token_word(node),)] += 1
        counted_indices.add(index)

    return sequences


def iter_treebank_files(treebank_dir: str | Path) -> Iterable[Path]:
    treebank_path = Path(treebank_dir)
    yield from sorted(treebank_path.rglob("*.xml"))


def update_counters_from_file(
    path: str | Path,
    all_sequences: Counter[WordSequence],
    multiword_np_sequences: Counter[WordSequence],
    single_word_np_sequences: Counter[WordSequence],
) -> None:
    all_sequences.update(extract_all_contiguous_sequences_from_file(path))
    multiword_np_sequences.update(extract_multiword_np_sequences_from_file(path))
    single_word_np_sequences.update(extract_single_word_np_sequences_from_file(path))


def extract_corpus_sequences(
    treebank_dir: str | Path,
) -> tuple[Counter[WordSequence], Counter[WordSequence], Counter[WordSequence]]:
    all_sequences: Counter[WordSequence] = Counter()
    multiword_np_sequences: Counter[WordSequence] = Counter()
    single_word_np_sequences: Counter[WordSequence] = Counter()

    for path in iter_treebank_files(treebank_dir):
        update_counters_from_file(
            path,
            all_sequences,
            multiword_np_sequences,
            single_word_np_sequences,
        )

    return all_sequences, multiword_np_sequences, single_word_np_sequences


def dump_pickle(obj: object, path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as handle:
        pickle.dump(obj, handle)


def write_corpus_sequence_pickles(
    treebank_dir: str | Path,
    output_dir: str | Path,
) -> tuple[Path, Path, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    all_sequences, multiword_np_sequences, single_word_np_sequences = extract_corpus_sequences(treebank_dir)

    all_sequences_path = output_path / "all_contiguous_sequences.pkl"
    multiword_np_path = output_path / "multiword_np_sequences.pkl"
    single_word_np_path = output_path / "single_word_np_sequences.pkl"

    dump_pickle(all_sequences, all_sequences_path)
    dump_pickle(multiword_np_sequences, multiword_np_path)
    dump_pickle(single_word_np_sequences, single_word_np_path)

    return all_sequences_path, multiword_np_path, single_word_np_path


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract contiguous word sequences and noun-phrase sequences from the Dutch treebank.",
    )
    parser.add_argument(
        "--treebank-dir",
        default="treebank",
        help="Directory containing the sentence-level Alpino XML files.",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory where the pickle files will be written.",
    )
    return parser


def main() -> None:
    args = build_argument_parser().parse_args()
    all_path, multiword_path, single_word_path = write_corpus_sequence_pickles(
        args.treebank_dir,
        args.output_dir,
    )

    print(f"Wrote {all_path}")
    print(f"Wrote {multiword_path}")
    print(f"Wrote {single_word_path}")


if __name__ == "__main__":
    main()
