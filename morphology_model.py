from collections import defaultdict
from collections import Counter
from string import ascii_lowercase
import custom_io as cio
import csv

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

def anl_bases(self, lemma, target_tag):
    encoded_lemma = cio.hun_encode(lemma)
    starting_tags = self.lemmas[encoded_lemma]
    shared_tag_dict = defaultdict(set)
    candidate_lemmas = self.tagtries[target_tag].root.lemmas.keys()
    for candidate_lemma in candidate_lemmas:
        for shared_tag in starting_tags & self.lemmas[candidate_lemma]:
            shared_tag_dict[shared_tag].add(candidate_lemma)
    return dict(shared_tag_dict)

def produce_word(model, lemma, target_tag):
    try:
        return most_similar_bases(model, lemma, target_tag)[0][0]
    except:
        return ''

def produce_word_list(model, lemma, target_tag):
    try:
        return most_similar_bases(model, lemma, target_tag)
    except:
        return ''

def most_similar_bases(self, lemma, target_tag):
    encoded_lemma = cio.hun_encode(lemma)
    tag_dict = {}
    bases = anl_bases(self, encoded_lemma, target_tag)
    tag_wordforms = defaultdict(lambda: defaultdict(float))
    for tag, anl_lemmas in bases.items():
        transform_dict = defaultdict(Counter)
        tag_trie = self.tagtries[tag]
        lemma_wordform = wordform(self, encoded_lemma, tag)
        for anl_lemma in anl_lemmas:
            # Record all common suffixes for tagged wordforms of lemma and anl_lemma
            common_suffixes = set()
            common_suffix = ''
            anl_lemma_node = None
            current_node = tag_trie.root
            while anl_lemma in current_node.lemmas and encoded_lemma in current_node.lemmas:
                common_suffix = current_node.label + common_suffix
                common_suffixes.add(common_suffix)
                anl_lemma_node = current_node
                current_node = current_node.lemmas[encoded_lemma]
            # Find tagged wordform of anl_lemma
            anl_lemma_wordform = common_suffix
            while anl_lemma in anl_lemma_node.lemmas:
                anl_lemma_node = anl_lemma_node.lemmas[anl_lemma]
                anl_lemma_wordform = anl_lemma_node.label + anl_lemma_wordform
            # Find wordform of anl_lemma for target tag
            target_anl_lemma_wordform = wordform(self, anl_lemma, target_tag)
            # For each common suffix, find and record transformation pair
            for original_suffix in common_suffixes:
                anl_prefix = anl_lemma_wordform.removesuffix(original_suffix)
                if not target_anl_lemma_wordform.startswith(anl_prefix):
                    continue
                new_suffix = target_anl_lemma_wordform.removeprefix(anl_prefix)
                transform_dict[original_suffix][new_suffix] += 1
        # Compute homogeneity for each original suffix
        suffix_homogeneities = {}
        total_suffix_homogeneity = 0
        for original_suffix, new_suffixes in transform_dict.items():
            homogeneity = simpson_index(new_suffixes.values())
            suffix_homogeneities[original_suffix] = homogeneity
            total_suffix_homogeneity += homogeneity
            """original scoring
            stem = lemma_wordform.removesuffix(original_suffix)
            type_count = len(new_suffixes)
            total_transformation_count = sum(new_suffixes.values())
            for new_suffix, new_suffix_count in new_suffixes.items():
                new_wordform = stem + new_suffix
                weight = (new_suffix_count / type_count)
                new_wordforms[new_wordform] += weight
            """
        # Normalize homogeneities to get weights and compute weighted word form probabilities
        for original_suffix, new_suffixes in transform_dict.items():
            weight = suffix_homogeneities[original_suffix] / total_suffix_homogeneity
            # If defectivity is allowed
            #weight = suffix_homogeneities[original_suffix] / len(suffix_homogeneities)
            stem = lemma_wordform.removesuffix(original_suffix)
            total_transformation_count = sum(new_suffixes.values())
            for new_suffix, new_suffix_count in new_suffixes.items():
                new_wordform = stem + new_suffix
                prob = new_suffix_count / total_transformation_count
                tag_wordforms[tag][new_wordform] += prob * weight
    # Compute homogeneity for each tag
    tag_homogeneities = {}
    total_tag_homogeneity = 0
    for tag, wordforms in tag_wordforms.items():
        homogeneity = simpson_index(wordforms.values())
        tag_homogeneities[tag] = homogeneity
        total_tag_homogeneity += homogeneity
    new_wordforms = defaultdict(float)
    for tag, wordforms in tag_wordforms.items():
        weight = tag_homogeneities[tag] / total_tag_homogeneity
        # If defectivity is allowed
        #weight = tag_homogeneities[tag] / len(tag_homogeneities)
        for new_wordform, wordform_prob in wordforms.items():
            prob = wordform_prob
            new_wordforms[new_wordform] += prob * weight
    # If defectivity is allowed
    #new_wordforms['*'] += 1 - sum(new_wordforms.values())
    return sorted(new_wordforms.items(), key=lambda x: x[1], reverse=True)

def wordform(model, lemma, target_tag):
    word = ''
    tag_trie = model.tagtries[target_tag]
    current_node = tag_trie.root
    while lemma in current_node.lemmas:
        word = current_node.label + word
        current_node = current_node.lemmas[lemma]
    word = current_node.label + word
    return word

def simpson_index(counts):
    norm_const = sum(counts)
    return sum((count / norm_const) ** 2 for count in counts)

def testing(model, test_corpus):
    results = {True: set(), False: set()}
    for tag, target_word, lemma in test_corpus:
        # Get token frequency of lemma in training corpus
        lemmafreq = sum(model.lemmas[lemma].values())
        # If lemma is unattested or target word form is attested, skip
        if (lemmafreq == 0) or (tag in model.lemmas[lemma]):
            continue
        # Compare target word form with word form produced by the model
        # and record outcome of guess
        produced_word = produce_word(model, lemma, tag)
        guess_outcome = produced_word == target_word
        results[guess_outcome].add((target_word, produced_word, tuple(tag), lemma, lemmafreq))
    return results


def import_training_data():
    sztaki_corpus_path = 'corpora/sztaki_corpus_2017_2018_0001_clean.tsv'
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
                yield (tag, word_form, lemma)

def import_test_data():
    sztaki_corpus_path = 'corpora/sztaki_corpus_2017_2018_0002_clean.tsv'
    morph_triples = []
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
                morph_triples.append((tag, word_form, lemma))
    return morph_triples