# Japanese Extraction Scripts README

This folder documents the scripts in `../scripts` that extract word-sequence data from the Japanese Kainoki treebank in `../treebank`.

## Files

- `../scripts/japanese_treefile_extractor.py`
  Per-file extraction functions. This is the core parser/extractor module.
- `../scripts/japanese_treebank_extractor.py`
  Corpus-level runner. It applies the per-file functions to all treebank files and dumps pickle files.

## Outputs

Running `japanese_treebank_extractor.py` creates three pickle files in the `japanese/` directory:

- `all_contiguous_sequences.pkl`
- `all_multiword_np_sequences.pkl`
- `all_singleword_np_sequences.pkl`

Each pickle contains a Python `Counter` whose keys are tuples of strings.

Examples:

- `('私', 'は', '行く')`
- `('東日本大震災',)`
- `('ヨーロッパ', 'の', '中')`

## Conceptual Background

The source corpus is the Kainoki Treebank, a Penn-style Japanese treebank with one parsed tree per line. Each line has:

1. An unlabeled outer wrapper.
2. One full syntactic tree.
3. A final `ID` node.

Canonical shape:

```text
( ( ...TREE... ) (ID 3_news_kahoku39) )
```

Important properties of the annotation:

- Clause structure is centered on `IP-*`, `CP-*`, and `FRAG`.
- There is generally no explicit `VP`.
- Phrase and clause labels are compositional: for example `NP-SBJ`, `IP-ADV-SCON`, `CP-THT-OB1`.
- Sort and discourse metadata may be appended after `;`, for example `NP;{AUTHOR}`.
- Null elements such as `*pro*`, `*T*`, `*arb*`, `*speaker*` are syntactically important, but they are not overt words.

The scripts are therefore tree-structure-aware. They do not treat the files as plain sentences.

## Parsing Strategy

`japanese_treefile_extractor.py` parses each tree line directly from the bracket notation.

The parser:

- tokenizes parentheses and atoms,
- builds a recursive tree structure,
- ignores the final `ID` subtree during extraction,
- treats UTF-8 Japanese strings as ordinary terminal words,
- preserves compositional labels such as `NP-SBJ;{AUTHOR}`.

For extraction purposes, the relevant tree nodes are the overt terminals dominated by preterminal labels such as `N`, `NPR`, `PRO`, `VB`, `P-ROLE`, `AX`, and so on.

## What Counts As Punctuation

Contiguity is defined structurally, not by Unicode character class.

The scripts treat the following labels as punctuation-like boundaries:

- `PUNC`
- `SYM`
- `FS`
- `PUL`
- `PUR`
- `PUQ`
- `PULB`
- `PURB`
- `PULQ`
- `PURQ`
- any label beginning with `PU`

When one of these labels is reached, the current contiguous sequence is closed.

## Treatment of Null Elements

Null terminals such as:

- `*pro*`
- `*exp*`
- `*arb*`
- `*T*`
- `*ICH*`
- `*speaker*`
- `*hearer*`

are ignored in the extracted word sequences, because the task is about overt word strings rather than abstract syntactic positions.

## Extraction Type 1: All Contiguous Sequences

Function:

- `extract_contiguous_sequences(tree_filepath)`

This function:

1. parses every tree in one file,
2. reads off the overt terminals from left to right,
3. partitions the linear sequence at punctuation boundaries,
4. returns each resulting span as one tuple.

Important:

- These are maximal punctuation-delimited spans.
- The script does **not** generate all substrings or subspans.

Example:

If a tree yields:

```text
私 は 行く 。 そして 帰る 。
```

the extracted contiguous sequences are:

- `('私', 'は', '行く')`
- `('そして', '帰る')`

and not:

- `('私',)`
- `('は', '行く')`
- `('帰る',)`

unless such spans occur independently elsewhere.

## Extraction Type 2: Multiword NP Sequences

Function:

- `extract_multiword_noun_phrases(tree_filepath)`

This function finds NP-labeled nodes and extracts their overt terminal yield, but only when:

- the yield contains no punctuation labels,
- the resulting overt sequence has length greater than 1,
- the NP label is not in the excluded function set.

### Which NP labels are included

The script treats the full NP family as NP-labeled, including labels such as:

- `NP`
- `NP-SBJ`
- `NP-OB1`
- `NP-OB2`
- `NP-PRD`
- `NP-TMP`
- `NP-MSR`
- `NP-LOC`
- `NP-TPC`
- `NP-POS`
- `NP-VOC`
- `NP;{...}`
- `NP-SBJ;{...}`

### Which NP labels are excluded

For multiword NP extraction, the following base labels are excluded:

- `NP-ADV`
- `NP-DOB1`
- `NP-LGS`
- `NP-PRP`

Reason:

- `NP-ADV` is explicitly adverbial in the Kainoki label system.
- `NP-DOB1`, `NP-LGS`, and `NP-PRP` encode specialized argument or purposive functions that are not good matches for the intended “ordinary noun phrase” extraction target.

This means the multiword NP list is narrower than “all NP-family nodes in the corpus”.

## Extraction Type 3: Single-word NP Sequences

Function:

- `extract_singleword_noun_phrases(tree_filepath)`

This function finds NP-family nodes and returns their overt terminal yield when the yield length is exactly 1 and contains no punctuation.

Unlike multiword NP extraction, the single-word NP extraction currently keeps the NP family broadly, because the target of that list is simply single-word NP sequences.

## Corpus-level Script

`japanese_treebank_extractor.py` follows the same overall design as the Dutch example scripts:

- one module provides per-file extraction functions,
- a second module runs them over the full corpus.

The corpus-level script:

1. collects all files directly under `../treebank`,
2. runs all three extraction functions on every file,
3. aggregates the outputs with `collections.Counter`,
4. pickles the three counters.

Core functions:

- `get_all_tree_filepaths()`
- `all_sequences(...)`
- `all_multiword_noun_phrases(...)`
- `all_singleword_noun_phrases(...)`
- `dump_counter(...)`

## Data Format

All counters map tuple keys to integer frequencies.

Example conceptual shape:

```python
Counter({
    ('私',): 4013,
    ('ヨーロッパ', 'の', '中'): 165,
    ('彼女',): 1696,
})
```

Tuples are used rather than joined strings so that token boundaries are preserved exactly.

## Design Assumptions

The current scripts make the following assumptions:

- One line in a treebank file is one complete tree.
- `ID` nodes are metadata, not linguistic material to extract.
- Null elements are excluded from overt word-sequence data.
- Punctuation boundaries are determined by treebank labels, not just by surface characters.
- NP extraction is based on constituent labels, not on heuristics over word classes.

## Re-running the Extraction

From the `japanese/` directory:

```bash
python3 scripts/japanese_treebank_extractor.py
```

To verify the scripts compile:

```bash
python3 -m py_compile scripts/japanese_treefile_extractor.py scripts/japanese_treebank_extractor.py
```

## Relation to the Dutch Example Scripts

The Japanese scripts intentionally mirror the Dutch workflow:

- per-file extractors are kept separate from the full-corpus runner,
- the full-corpus runner only coordinates file discovery, counting, and pickling,
- the language-specific logic lives in the per-file extractor module.

The main difference is that the Dutch scripts read XML, whereas the Japanese scripts parse bracketed Kainoki trees directly.
