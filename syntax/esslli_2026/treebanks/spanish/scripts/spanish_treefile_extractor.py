import xml.etree.ElementTree as ET
from pathlib import Path


sample_xml_filepath = Path(__file__).resolve().parent.parent / "treebank" / "1_20020901.tbf.xml"
adjective_phrase_tags = {"sa", "s.a"}


def is_punctuation_node(node: ET.Element) -> bool:
    return "punct" in node.attrib


def is_terminal_word_node(node: ET.Element) -> bool:
    return "wd" in node.attrib and len(node) == 0


def normalize_word(word: str) -> str:
    return word.lower()


def iter_terminal_nodes_in_order(node: ET.Element):
    for descendant in node.iter():
        if is_terminal_word_node(descendant):
            yield descendant


def extract_words_from_subtree(node: ET.Element) -> tuple[str, ...]:
    terminals = list(iter_terminal_nodes_in_order(node))
    if not terminals:
        return ()
    if any(is_punctuation_node(terminal) for terminal in terminals):
        return ()
    return tuple(normalize_word(terminal.attrib["wd"]) for terminal in terminals)


def extract_contiguous_sequences(xml_filepath) -> list[tuple[str, ...]]:
    tree = ET.parse(xml_filepath)
    root = tree.getroot()
    sequences = []
    current_sequence = []

    for sentence in root.findall(".//sentence"):
        current_sequence = []
        for terminal in iter_terminal_nodes_in_order(sentence):
            if is_punctuation_node(terminal):
                if current_sequence:
                    sequences.append(tuple(current_sequence))
                    current_sequence = []
                continue
            current_sequence.append(normalize_word(terminal.attrib["wd"]))
        if current_sequence:
            sequences.append(tuple(current_sequence))

    return sequences


def extract_multiword_adjective_phrases(xml_filepath) -> list[tuple[str, ...]]:
    tree = ET.parse(xml_filepath)
    root = tree.getroot()
    adjective_phrases = []

    for node in root.iter():
        if node.tag not in adjective_phrase_tags:
            continue
        phrase = extract_words_from_subtree(node)
        if len(phrase) > 1:
            adjective_phrases.append(phrase)

    return adjective_phrases


def extract_single_word_adjective_phrases(xml_filepath) -> list[tuple[str, ...]]:
    tree = ET.parse(xml_filepath)
    root = tree.getroot()
    adjective_phrases = []

    for node in root.iter():
        if node.tag not in adjective_phrase_tags:
            continue
        phrase = extract_words_from_subtree(node)
        if len(phrase) == 1:
            adjective_phrases.append(phrase)

    return adjective_phrases


def extract_single_word_adjective_nominal_modifiers_with_position(
    xml_filepath,
) -> list[tuple[tuple[str, ...], bool]]:
    tree = ET.parse(xml_filepath)
    root = tree.getroot()
    adjective_modifiers = []

    for noun_group in root.iter("grup.nom"):
        children = list(noun_group)
        noun_indices = [
            index for index, child in enumerate(children) if child.tag == "n"
        ]
        if len(noun_indices) != 1:
            continue

        noun_index = noun_indices[0]
        for index, child in enumerate(children):
            if child.tag != "s.a":
                continue
            phrase = extract_words_from_subtree(child)
            if len(phrase) != 1:
                continue
            adjective_modifiers.append((phrase, index > noun_index))

    return adjective_modifiers


def main():
    all_sequences = extract_contiguous_sequences(sample_xml_filepath)
    multiword_adjective_phrases = extract_multiword_adjective_phrases(sample_xml_filepath)
    single_word_adjective_phrases = extract_single_word_adjective_phrases(sample_xml_filepath)
    return all_sequences, multiword_adjective_phrases, single_word_adjective_phrases
