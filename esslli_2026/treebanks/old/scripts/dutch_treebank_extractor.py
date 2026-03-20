import xml.etree.ElementTree as ET
import re
import pickle
from pathlib import Path
from collections import Counter
from dutch_treefile_extractor import extract_contiguous_noun_phrases as source_seqs_from_file
from dutch_treefile_extractor import extract_pronouns_and_proper_nouns as target_seqs_from_file
from dutch_treefile_extractor import extract_contiguous_sequences as seqs_from_file

treebank_root_folder = Path("../treebank")

def get_all_xml_filepaths():
    return list(treebank_root_folder.rglob("*.xml"))

def all_source_sequences(xml_filepaths):
    return Counter(
        seq for path in xml_filepaths for seq in source_seqs_from_file(path)
    )

def all_target_sequences(xml_filepaths):
    return Counter(
        seq for path in xml_filepaths for seq in target_seqs_from_file(path)
    )

def all_sequences(xml_filepaths):
    return Counter(
        seq for path in xml_filepaths for seq in seqs_from_file(path)
    )

def main():
    filepaths = get_all_xml_filepaths()
    all_seqs = all_sequences(filepaths)
    source_seqs = all_source_sequences(filepaths)
    target_seqs = all_target_sequences(filepaths)
    for data, name in zip([all_seqs, source_seqs, target_seqs], ["all_sequences", "multiword_source_sequences", "singleword_target_sequences"]):
        pickle.dump(data, open("../extracted_sequence_files/" + name + ".pkl", "wb"))
    return all_seqs, source_seqs, target_seqs
