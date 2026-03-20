import xml.etree.ElementTree as ET
from collections import Counter

sample_xml_filepath = f"../treebank/dpc-bmm-001073-nl-sen/dpc-bmm-001073-nl-sen.p.6.s.1.xml"
punctuation_chars =  ".,:;!?()"
punctuation_tokens = set(punctuation_chars + "\"'")

def get_leaf_words(root) -> list[str]:
    leaf_nodes = sorted(
        [node for node in root.iter("node")
         if node.get("word") is not None
         and node.get("begin") is not None
         and node.get("end") is not None
         and int(node.get("begin")) == int(node.get("end")) - 1],
        key=lambda node: int(node.get("begin"))
    )
    return [node.get("word").lower() for node in leaf_nodes]

def extract_contiguous_noun_phrases(xml_filepath) -> list[tuple[str, ...]]:
    tree = ET.parse(xml_filepath)
    root = tree.getroot()
    noun_phrases = []
    leaf_words = get_leaf_words(root)
    np_nodes = root.findall(".//node[@cat='np']")
    for node in np_nodes:
        begin = int(node.get("begin"))
        end = int(node.get("end"))
        span = tuple(leaf_words[begin:end])
        if span and all(token not in punctuation_tokens for token in span):
            noun_phrases.append(span)
    return noun_phrases

def extract_pronouns_and_proper_nouns(xml_filepath) -> list[tuple[str, ...]]:
    tree = ET.parse(xml_filepath)
    root = tree.getroot()
    words = []
    word_nodes = [node for node in root.iter()
                  if ((node.get("pt") == "vnw"
                       and node.get("pdtype") == "pron"
                       and node.get("positie") != "prenom")
                      or node.get("ntype") == "eigen")
                  and int(node.get("begin")) == int(node.get("end")) - 1]
    for node in word_nodes:
        surface_word = node.get("word")
        word = (surface_word.lower(),) if surface_word else ()
        if word and word[0] not in "\"' " + punctuation_chars:
            words.append(word)
    return words

def extract_contiguous_sequences(xml_filepath) -> list[tuple[str, ...]]:
    tree = ET.parse(xml_filepath)
    root = tree.getroot()
    leaf_words = get_leaf_words(root)
    sequences = []
    current_sequence = []
    for word in leaf_words:
        if word in punctuation_tokens:
            if current_sequence:
                sequences.append(tuple(current_sequence))
                current_sequence = []
        else:
            current_sequence.append(word)
    if current_sequence:
        sequences.append(tuple(current_sequence))
    return sequences


def main():
    mixed_sequences = extract_contiguous_noun_phrases(sample_xml_filepath)
    good_analogical_words = extract_pronouns_and_proper_nouns(sample_xml_filepath)
    all_sequences = extract_contiguous_sequences(sample_xml_filepath)
    return all_sequences
