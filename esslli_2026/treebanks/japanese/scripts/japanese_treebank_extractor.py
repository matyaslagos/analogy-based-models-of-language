from __future__ import annotations

import pickle
from collections import Counter
from pathlib import Path

from japanese_treefile_extractor import extract_contiguous_sequences as seqs_from_file
from japanese_treefile_extractor import extract_multiword_noun_phrases as multi_nps_from_file
from japanese_treefile_extractor import extract_singleword_noun_phrases as single_nps_from_file


TREEBANK_ROOT_FOLDER = Path(__file__).resolve().parents[1] / "treebank"
OUTPUT_FOLDER = Path(__file__).resolve().parents[1]
ALL_SEQUENCES_PICKLE = OUTPUT_FOLDER / "all_contiguous_sequences.pkl"
MULTIWORD_NPS_PICKLE = OUTPUT_FOLDER / "all_multiword_np_sequences.pkl"
SINGLEWORD_NPS_PICKLE = OUTPUT_FOLDER / "all_singleword_np_sequences.pkl"


def get_all_tree_filepaths() -> list[Path]:
    return sorted(path for path in TREEBANK_ROOT_FOLDER.iterdir() if path.is_file())


def all_sequences(tree_filepaths: list[Path]) -> Counter[tuple[str, ...]]:
    return Counter(seq for path in tree_filepaths for seq in seqs_from_file(path))


def all_multiword_noun_phrases(tree_filepaths: list[Path]) -> Counter[tuple[str, ...]]:
    return Counter(seq for path in tree_filepaths for seq in multi_nps_from_file(path))


def all_singleword_noun_phrases(tree_filepaths: list[Path]) -> Counter[tuple[str, ...]]:
    return Counter(seq for path in tree_filepaths for seq in single_nps_from_file(path))


def dump_counter(counter: Counter[tuple[str, ...]], output_filepath: Path) -> None:
    with output_filepath.open("wb") as output_file:
        pickle.dump(counter, output_file)


def main() -> tuple[Counter[tuple[str, ...]], Counter[tuple[str, ...]], Counter[tuple[str, ...]]]:
    filepaths = get_all_tree_filepaths()
    all_seqs = all_sequences(filepaths)
    multiword_nps = all_multiword_noun_phrases(filepaths)
    singleword_nps = all_singleword_noun_phrases(filepaths)

    dump_counter(all_seqs, ALL_SEQUENCES_PICKLE)
    dump_counter(multiword_nps, MULTIWORD_NPS_PICKLE)
    dump_counter(singleword_nps, SINGLEWORD_NPS_PICKLE)

    return all_seqs, multiword_nps, singleword_nps


if __name__ == "__main__":
    main()
