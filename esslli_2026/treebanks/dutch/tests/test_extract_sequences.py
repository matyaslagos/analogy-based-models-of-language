from __future__ import annotations

import pickle
import tempfile
import unittest
from pathlib import Path

from extract_sequences import (
    extract_corpus_sequences,
    extract_all_contiguous_sequences_from_file,
    extract_multiword_np_sequences_from_file,
    extract_single_word_np_sequences_from_file,
    write_corpus_sequence_pickles,
)


ROOT = Path(__file__).resolve().parents[1]


class ExtractSequencesTest(unittest.TestCase):
    def test_all_contiguous_sequences_are_maximal_punctuation_free_runs(self) -> None:
        path = ROOT / "treebank/WR-P-P-I-0000000096/WR-P-P-I-0000000096.p.3.s.5.xml"
        sequences = extract_all_contiguous_sequences_from_file(path)

        self.assertIn(("hij", "zag", "een", "cruciaal", "boek", "over", "het", "hoofd"), sequences)
        self.assertIn(("het", "lijvige", "fin", "de", "la", "souveraineté", "belge", "au", "congo"), sequences)
        self.assertIn(("in", "1960", "minister", "voor", "algemene", "zaken", "in", "afrika"), sequences)
        self.assertNotIn(("hij",), sequences)
        self.assertNotIn(("het", "hoofd"), sequences)
        self.assertNotIn(("afrika",), sequences)

    def test_multiword_np_extraction_uses_only_contiguous_np_spans(self) -> None:
        path = ROOT / "treebank/dpc-bmm-001083-nl-sen/dpc-bmm-001083-nl-sen.p.2.s.1.xml"
        sequences = extract_multiword_np_sequences_from_file(path)

        self.assertIn(("de", "bmm"), sequences)
        self.assertIn(("wetenschappelijke", "duikactiviteiten"), sequences)
        self.assertIn(("de", "noordzee"), sequences)
        self.assertIn(("de", "belgische", "wateren", "van", "de", "noordzee"), sequences)
        self.assertNotIn(("bmm",), sequences)

    def test_single_word_np_extraction_captures_implicit_pronouns(self) -> None:
        path = ROOT / "treebank/WR-P-P-I-0000000096/WR-P-P-I-0000000096.p.3.s.5.xml"
        sequences = extract_single_word_np_sequences_from_file(path)

        self.assertIn(("hij",), sequences)
        self.assertNotIn(("afrika",), sequences)

    def test_single_word_np_extraction_keeps_pronoun_objects(self) -> None:
        path = ROOT / "treebank/WR-P-P-I-0000000096/WR-P-P-I-0000000096.p.1.s.5.xml"
        sequences = extract_single_word_np_sequences_from_file(path)

        self.assertIn(("niemand",), sequences)
        self.assertIn(("hem",), sequences)
        self.assertIn(("hij",), sequences)

    def test_single_word_np_extraction_excludes_non_argument_pronouns(self) -> None:
        path = ROOT / "treebank/dpc-bmm-001083-nl-sen/dpc-bmm-001083-nl-sen.p.5.s.1.xml"
        sequences = extract_single_word_np_sequences_from_file(path)

        self.assertNotIn(("dat",), sequences)
        self.assertNotIn(("die",), sequences)

    def test_single_word_np_extraction_captures_bare_nominals(self) -> None:
        path = ROOT / "treebank/WR-P-P-I-0000000096/WR-P-P-I-0000000096.p.1.s.1.xml"
        sequences = extract_single_word_np_sequences_from_file(path)

        self.assertNotIn(("journalisten",), sequences)
        self.assertNotIn(("geheimen",), sequences)
        self.assertNotIn(("meer",), sequences)

    def test_single_word_np_extraction_captures_bare_names(self) -> None:
        path = ROOT / "treebank/WR-P-P-I-0000000096/WR-P-P-I-0000000096.p.3.s.6.xml"
        sequences = extract_single_word_np_sequences_from_file(path)

        self.assertIn(("verlinden",), sequences)

    def test_corpus_pickles_are_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            treebank_dir = Path(tmp_dir) / "treebank"
            treebank_dir.mkdir()

            source = ROOT / "treebank/WR-P-P-I-0000000096/WR-P-P-I-0000000096.p.1.s.1.xml"
            target = treebank_dir / source.name
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

            output_dir = Path(tmp_dir) / "output"
            all_path, multiword_path, single_word_path = write_corpus_sequence_pickles(treebank_dir, output_dir)

            self.assertTrue(all_path.exists())
            self.assertTrue(multiword_path.exists())
            self.assertTrue(single_word_path.exists())

            with all_path.open("rb") as handle:
                all_sequences = pickle.load(handle)
            with multiword_path.open("rb") as handle:
                multiword_sequences = pickle.load(handle)
            with single_word_path.open("rb") as handle:
                single_word_sequences = pickle.load(handle)

            expected_all, expected_multiword, expected_single = extract_corpus_sequences(treebank_dir)
            self.assertEqual(all_sequences, expected_all)
            self.assertEqual(multiword_sequences, expected_multiword)
            self.assertEqual(single_word_sequences, expected_single)


if __name__ == "__main__":
    unittest.main()
