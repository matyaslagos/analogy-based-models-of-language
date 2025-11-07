from collections import defaultdict
from collections import Counter
from string import ascii_lowercase
from operator import itemgetter
import custom_io as cio
import csv
import math

#-----------------------------#
# MorphModel class definition #
#-----------------------------#

class MorphModel():
    def __init__(self):
        self.tagtries = defaultdict(lambda: TagTrie())
        self.lemmas = defaultdict(Counter)

    def setup(self):
        morph_triples = import_training_data()
        for tag, word_form, lemma in morph_triples:
            self.tagtries[tag]._insert(word_form, lemma)
            self.lemmas[lemma][tag] += 1

#--------------------------#
# TagTrie class definition #
#--------------------------#

class TagNode:
    def __init__(self, char):
        self.children = {}
        self.freq = 0
        self.lemmas = {}
        self.label = char
    
    def _increment_or_make_branch(self, word_form, lemma):
        """Record branch of word_form and lemma.
        """
        current_node = self
        current_node.freq += 1
        for char in reversed(word_form):
            current_node = current_node._get_or_make_child(char, lemma)
            current_node.freq += 1
    
    def _get_or_make_child(self, char, lemma):
        """Return child labeled by char or make new child.
        """
        if char not in self.children:
            self.children[char] = TagNode(char)
        if lemma not in self.lemmas:
            self.lemmas[lemma] = self.children[char]
        return self.children[char]

class TagTrie:
    def __init__(self):
        self.root = TagNode('')

    def _insert(self, word_form, lemma):
        self.root._increment_or_make_branch(word_form, lemma)

#---------------------------#
# Analogy-finding functions #
#---------------------------#

def anl_bases(model, target_lemma, target_tag):
    encoded_lemma = cio.hun_encode(target_lemma)
    lemma_entry = model.lemmas.get(encoded_lemma)
    # Get "analogical tags" (tags that target lemma is attested with)
    if lemma_entry:
        if len(lemma_entry) == 1 and next(iter(lemma_entry)) == target_tag:
            anl_tags = Counter({frozenset({'Nom'}): 1})
        else:
            anl_tags = model.lemmas[encoded_lemma].copy()
    else:
        anl_tags = Counter({frozenset({'Nom'}): 1})
    # Pretend we haven't seen target lemma
    if target_tag in anl_tags:
        del anl_tags[target_tag]
    # Get "analogical lemmas" (lemmas that are attested with target tag)
    anl_lemmas = model.tagtries[target_tag].root.lemmas.keys()
    # Pretend we haven't seen target lemma
    anl_lemmas = anl_lemmas - {encoded_lemma}
    # For each analogical tag, collect analogical lemmas attested with it
    anl_tag_dict = defaultdict(set)
    for anl_lemma in anl_lemmas:
        for anl_tag in anl_tags & model.lemmas[anl_lemma]:
            anl_tag_dict[anl_tag].add(anl_lemma)
    return dict(anl_tag_dict)

def produce_word(model, lemma, target_tag):
    try:
        word_forms = inflect(model, lemma, target_tag)
        # If word forms are tied for first place, consider it a failure
        if len(word_forms) > 1 and word_forms[0][1] == word_forms[1][1]:
            return ''
        else:
            return word_forms[0][0]
    except:
        return ''

def inflect(model, lemma, target_tag_set):
    target_tag = frozenset(target_tag_set)
    encoded_lemma = cio.hun_encode(lemma)
    bases = anl_bases(model, lemma, target_tag)
    new_wordforms = defaultdict(float)
    for anl_tag, anl_lemmas in bases.items():
        transform_dict = defaultdict(Counter)
        tag_trie = model.tagtries[anl_tag]
        # Find wordform of target lemma for analogical tag
        lemma_wordform = wordform(model, encoded_lemma, anl_tag)
        for anl_lemma in anl_lemmas:
            # Record all common suffixes for analogical wordforms
            # of target lemma and analogical lemma for current analogical tag
            anl_lemma_wordform = wordform(model, anl_lemma, anl_tag)
            base_suffixes = common_suffixes(lemma_wordform, anl_lemma_wordform)
            # For each common suffix, find and record the suffix substitution
            # that transforms analogical lemma's word form for analogical tag
            # into analogical lemma's word form for target tag
            anl_lemma_target_wordform = wordform(model, anl_lemma, target_tag)
            for base_suffix in base_suffixes:
                anl_prefix = anl_lemma_wordform.removesuffix(base_suffix)
                if not anl_lemma_target_wordform.startswith(anl_prefix):
                    continue
                new_suffix = anl_lemma_target_wordform.removeprefix(anl_prefix)
                transform_dict[base_suffix][new_suffix] += 1
        # Normalize homogeneities to get weights, compute weighted word form probabilities
        for original_suffix, new_suffixes in transform_dict.items():
            stem = lemma_wordform.removesuffix(original_suffix)
            total_transformation_count = sum(new_suffixes.values())
            for new_suffix, new_suffix_count in new_suffixes.items():
                new_wordform = stem + new_suffix
                prob = new_suffix_count / total_transformation_count
                new_wordforms[new_wordform] += prob
    best_wordforms = sorted(new_wordforms.items(), key=itemgetter(1), reverse=True)
    return best_wordforms

def wordform(model, lemma, target_tag):
    if target_tag == frozenset({'Nom'}):
        return lemma
    word = ''
    tag_trie = model.tagtries[target_tag]
    current_node = tag_trie.root
    while lemma in current_node.lemmas:
        word = current_node.label + word
        current_node = current_node.lemmas[lemma]
    word = current_node.label + word
    return word

def common_suffixes(s1: str, s2: str, include_empty=True):
    common_suffix_list = [''] if include_empty else []
    common_suffix = ''
    for c1, c2 in zip(reversed(s1), reversed(s2)):
        if c1 != c2:
            break
        common_suffix = c1 + common_suffix
        common_suffix_list.append(common_suffix)
    return common_suffix_list

def testing(model, test_corpus):
    results = {True: set(), False: set(), 'UNK': set()}
    for tag, target_word, lemma in test_corpus:
        # Get token frequency of lemma in training corpus
        lemma_entry = model.lemmas.get(lemma)
        lemmafreq = 0 if (not lemma_entry) else sum(lemma_entry.values())
        # Don't try to guess Nom word forms of unattested lemmas or Nom word forms
        # of lemmas that are only attested with their Nom word forms
        unattested = (lemmafreq == 0)
        only_nom_attested = lemmafreq > 0 \
                            and len(lemma_entry) == 1 \
                            and next(iter(lemma_entry)) == frozenset({'Nom'})
        if tag == frozenset({'Nom'}) and (unattested or only_nom_attested):
                results['UNK'].add((target_word, 'UNK', tuple(sorted(tag)), lemma, 0))
                continue
        # Compare target word form with word form produced by the model
        # and record outcome of guess
        produced_word = produce_word(model, lemma, tag)
        guess_outcome = produced_word == target_word
        results[guess_outcome].add(
            (target_word, produced_word, tuple(sorted(tag)), lemma, lemmafreq)
        )
    output_results = {}
    for outcome, result_set in results.items():
        output_set = [
            {'target word': cio.hun_decode(tw),
             'produced word': cio.hun_decode(pw),
             'tag': set(tag),
             'lemma': cio.hun_decode(lemma),
             'lemmafreq': lf}
            for tw, pw, tag, lemma, lf in result_set]
        output_results[outcome] = output_set
    return output_results

def import_training_data():
    sztaki_corpus_paths = ['corpora/sztaki_corpus_2017_2018_0001_clean.tsv']
    for sztaki_corpus_path in sztaki_corpus_paths:
        with open(sztaki_corpus_path, newline='') as f:
            reader = csv.reader(
                (row for row in f if row.strip() and not row.startswith('#')),
                delimiter='\t'
            )
            next(reader, None) # skip first line
            is_hun_char = lambda x: x.lower() in ascii_lowercase + 'áéíóúöőüű'
            is_hun_string = lambda x: all(map(is_hun_char, x))
            for row in reader:
                if len(row) >= 4 and row[3].startswith('[/N]') and is_hun_string(row[0]):
                    word_form = cio.hun_encode(row[0].lower())
                    lemma = cio.hun_encode(row[2].lower())
                    tag = cio.xpostag_set(row[3])
                    if word_form and lemma and tag:
                        yield (tag, word_form, lemma)

def import_test_data():
    sztaki_corpus_path = 'corpora/sztaki_corpus_2017_2018_0002_clean.tsv'
    morph_triples = set()
    with open(sztaki_corpus_path, newline='') as f:
        reader = csv.reader(
            (row for row in f if row.strip() and not row.startswith('#')),
            delimiter='\t'
        )
        next(reader, None) # skip first line
        is_hun_char = lambda x: x.lower() in ascii_lowercase + 'áéíóúöőüű'
        is_hun_string = lambda x: all(map(is_hun_char, x))
        for row in reader:
            if len(row) >= 4 and row[3].startswith('[/N]') and is_hun_string(row[0]):
                word_form = cio.hun_encode(row[0].lower())
                lemma = cio.hun_encode(row[2].lower())
                tag = cio.xpostag_set(row[3])
                if word_form and lemma and tag:
                    morph_triples.add((tag, word_form, lemma))
    return list(morph_triples)