# Spanish AnCora Sequence Extraction

This directory contains scripts for extracting word-sequence statistics from the Spanish AnCora treebank.

## Conceptual background

The treebank files in [`treebank/`](/Users/matyaslagos/Documents/GitHub/analogical-path-models/esslli_2026/treebanks/spanish/treebank) are XML files from the Spanish AnCora corpus. AnCora is a constituent-based treebank with additional morphosyntactic and semantic annotation. The documentation in [`info/ancora_corpus_information.pdf`](/Users/matyaslagos/Documents/GitHub/analogical-path-models/esslli_2026/treebanks/spanish/info/ancora_corpus_information.pdf) describes the general scheme.

For the present scripts, the most important structural facts are:

- Files are rooted in `<article>` and contain multiple `<sentence>` elements.
- Surface words are stored in terminal XML nodes with a `wd` attribute.
- Punctuation is also represented as terminal nodes, distinguished by a `punct` attribute.
- Adjectival material is represented with the tags `sa` and `s.a`.
- Nominal groups are represented with `grup.nom`, and noun heads are represented with `n`.

The extraction logic is intentionally shallow. It does not reconstruct dependencies or deeper semantic structure. Instead, it relies on terminal order inside XML subtrees.

## What is extracted

The scripts produce four `Counter` objects, each dumped as a pickle file under [`output/`](/Users/matyaslagos/Documents/GitHub/analogical-path-models/esslli_2026/treebanks/spanish/output):

- [`all_contiguous_sequences.pkl`](/Users/matyaslagos/Documents/GitHub/analogical-path-models/esslli_2026/treebanks/spanish/output/all_contiguous_sequences.pkl)
  All contiguous word sequences from sentences, where punctuation breaks the sequence.
- [`multiword_adjective_phrases.pkl`](/Users/matyaslagos/Documents/GitHub/analogical-path-models/esslli_2026/treebanks/spanish/output/multiword_adjective_phrases.pkl)
  All adjective-phrase subtrees whose terminal yield is longer than one word and contains no punctuation.
- [`single_word_adjective_phrases.pkl`](/Users/matyaslagos/Documents/GitHub/analogical-path-models/esslli_2026/treebanks/spanish/output/single_word_adjective_phrases.pkl)
  All adjective-phrase subtrees whose terminal yield is exactly one word.
- [`postnominal_single_word_adjective_phrases.pkl`](/Users/matyaslagos/Documents/GitHub/analogical-path-models/esslli_2026/treebanks/spanish/output/postnominal_single_word_adjective_phrases.pkl)
  A filtered version of the single-word adjective counter. An adjective is included if, among its uses as a single-adjective nominal modifier, at least 50% are postnominal. Its stored count is its overall frequency from `single_word_adjective_phrases.pkl`, not just its modifier frequency.

All keys are tuples of lowercase word forms, following the pattern used in the Dutch example scripts.

## Script structure

The code follows the same division of labor as the Dutch example scripts in [`scripts/`](/Users/matyaslagos/Documents/GitHub/analogical-path-models/esslli_2026/treebanks/spanish/scripts):

- [`scripts/spanish_treefile_extractor.py`](/Users/matyaslagos/Documents/GitHub/analogical-path-models/esslli_2026/treebanks/spanish/scripts/spanish_treefile_extractor.py)
  Contains functions that operate on a single XML treebank file.
- [`scripts/spanish_treebank_extractor.py`](/Users/matyaslagos/Documents/GitHub/analogical-path-models/esslli_2026/treebanks/spanish/scripts/spanish_treebank_extractor.py)
  Finds all XML files, applies the per-file functions across the whole treebank, aggregates the results into `Counter` objects, and dumps them to pickle files.

## How the per-file extraction works

### 1. Contiguous sequences

`extract_contiguous_sequences(xml_filepath)` walks through each sentence in document order and collects terminal words. Whenever a punctuation terminal is encountered, the current sequence is closed and a new one begins.

This means that:

- commas, periods, colons, and other punctuation split sequences,
- punctuation tokens themselves are excluded,
- word order is the surface order found in the XML,
- all forms are lowercased.

### 2. Adjective phrases

`extract_multiword_adjective_phrases(xml_filepath)` and `extract_single_word_adjective_phrases(xml_filepath)` search for all subtrees tagged `sa` or `s.a`.

For each such subtree, the script:

- collects all terminal descendants in XML order,
- discards the subtree if any terminal is punctuation,
- lowercases the remaining words,
- keeps the resulting tuple if its length matches the requested type.

The use of both `sa` and `s.a` is deliberate. In this treebank, both tags occur in adjectival phrase structure.

### 3. Postnominal adjective filter

`extract_single_word_adjective_nominal_modifiers_with_position(xml_filepath)` identifies cases where a single-word `s.a` child modifies a noun inside a `grup.nom` subtree.

The implementation only counts cases where:

- the `grup.nom` node has exactly one direct `n` child,
- the adjectival modifier is a direct `s.a` child,
- the adjectival subtree yields exactly one non-punctuation word.

For each such case, the function returns the adjective together with a Boolean saying whether the adjective appears to the right of the noun in the immediate child order of the `grup.nom`.

The treebank-level script then:

1. counts, for each adjective, how often it appears in these single-adjective nominal-modifier constructions,
2. counts how often those uses are postnominal,
3. keeps adjectives whose postnominal share is at least 50%,
4. assigns them their overall counts from `single_word_adjective_phrases.pkl`.

## Running the scripts

From this directory:

```bash
python3 scripts/spanish_treebank_extractor.py
```

This regenerates all pickle files in [`output/`](/Users/matyaslagos/Documents/GitHub/analogical-path-models/esslli_2026/treebanks/spanish/output).

To test only the per-file extractor on its built-in sample file:

```bash
python3 -c "from scripts.spanish_treefile_extractor import main; print(main())"
```

## Design choices and limitations

- The scripts are surface-oriented. They use subtree yields and immediate XML order rather than deeper grammatical reconstruction.
- Punctuation is detected by the presence of the `punct` attribute on terminal nodes.
- The postnominal filter is restricted to direct `grup.nom` configurations with one noun head and direct `s.a` children. It therefore ignores more complex nominal structures, coordinated adjective phrases, and cases where adjective-noun relations are mediated by deeper nesting.
- Words are lowercased exactly as they appear in the `wd` attribute. Underscores in multiword named entities remain unchanged.
- Because the counters store tuples, even single-word items appear as one-element tuples such as `('general',)`.

These choices were made to keep the extractor simple, deterministic, and parallel to the Dutch example scripts while still matching the main structural properties of the Spanish AnCora XML.
