import pickle
from collections import Counter
from pathlib import Path

from spanish_treefile_extractor import extract_contiguous_sequences as all_seqs_from_file
from spanish_treefile_extractor import (
    extract_multiword_adjective_phrases as multiword_adj_phrases_from_file,
)
from spanish_treefile_extractor import (
    extract_single_word_adjective_phrases as single_word_adj_phrases_from_file,
)
from spanish_treefile_extractor import (
    extract_single_word_adjective_nominal_modifiers_with_position
    as adj_nominal_modifiers_with_position_from_file,
)


script_dir = Path(__file__).resolve().parent
treebank_root_folder = script_dir.parent / "treebank"
output_folder = script_dir.parent / "output"

all_sequences_pickle_filepath = output_folder / "all_contiguous_sequences.pkl"
multiword_adjective_phrases_pickle_filepath = (
    output_folder / "multiword_adjective_phrases.pkl"
)
single_word_adjective_phrases_pickle_filepath = (
    output_folder / "single_word_adjective_phrases.pkl"
)
postnominal_single_word_adjective_phrases_pickle_filepath = (
    output_folder / "postnominal_single_word_adjective_phrases.pkl"
)


def get_all_xml_filepaths():
    return sorted(treebank_root_folder.rglob("*.xml"))


def all_sequences(xml_filepaths) -> Counter:
    return Counter(seq for path in xml_filepaths for seq in all_seqs_from_file(path))


def all_multiword_adjective_phrases(xml_filepaths) -> Counter:
    return Counter(
        seq for path in xml_filepaths for seq in multiword_adj_phrases_from_file(path)
    )


def all_single_word_adjective_phrases(xml_filepaths) -> Counter:
    return Counter(
        seq for path in xml_filepaths for seq in single_word_adj_phrases_from_file(path)
    )


def all_postnominal_single_word_adjective_phrases(
    xml_filepaths, single_word_adjective_phrase_counts: Counter
) -> Counter:
    total_counts = Counter()
    postnominal_counts = Counter()

    for path in xml_filepaths:
        for adjective, is_postnominal in adj_nominal_modifiers_with_position_from_file(path):
            total_counts[adjective] += 1
            if is_postnominal:
                postnominal_counts[adjective] += 1

    return Counter(
        {
            adjective: single_word_adjective_phrase_counts[adjective]
            for adjective in total_counts
            if postnominal_counts[adjective] / total_counts[adjective] >= 0.5
        }
    )


def dump_pickle_file(counter: Counter, filepath: Path) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with filepath.open("wb") as file:
        pickle.dump(counter, file)


def main():
    filepaths = get_all_xml_filepaths()
    all_seqs = all_sequences(filepaths)
    multiword_adj_phrases = all_multiword_adjective_phrases(filepaths)
    single_word_adj_phrases = all_single_word_adjective_phrases(filepaths)
    postnominal_single_word_adj_phrases = (
        all_postnominal_single_word_adjective_phrases(filepaths, single_word_adj_phrases)
    )

    dump_pickle_file(all_seqs, all_sequences_pickle_filepath)
    dump_pickle_file(
        multiword_adj_phrases, multiword_adjective_phrases_pickle_filepath
    )
    dump_pickle_file(
        single_word_adj_phrases, single_word_adjective_phrases_pickle_filepath
    )
    dump_pickle_file(
        postnominal_single_word_adj_phrases,
        postnominal_single_word_adjective_phrases_pickle_filepath,
    )

    return (
        all_seqs,
        multiword_adj_phrases,
        single_word_adj_phrases,
        postnominal_single_word_adj_phrases,
    )


if __name__ == "__main__":
    main()
