# Kainoki Treebank Script README

This directory contains three utility scripts for working with the sample Kainoki treebank files in `treebank_files/`.

## Requirements

- Python 3.9+
- No third-party packages required (standard library only)

## 1) `extract_kainoki_labels.py`

Extracts all node labels used in the treebank files, including leaf-level labels, and compares them against tags listed in `kainoki_treebank_annotation_overview.md`.

### Usage

```bash
python3 extract_kainoki_labels.py
```

### Optional arguments

- `--treebank-dir` (default: `treebank_files`)
- `--overview` (default: `kainoki_treebank_annotation_overview.md`)
- `--output` (default: `kainoki_treebank_labels.md`)

### Output

- Markdown report (default): `kainoki_treebank_labels.md`

## 2) `extract_constituent_sequences.py`

Given a constituent label, extracts all matching constituent terminal sequences as `list[list[str]]`.

Extraction behavior:
- Sequences containing phrase-boundary punctuation are excluded.
- Null/empty elements (e.g. `*`, `*pro*`, `*T*`) are removed.
- Empty results after filtering are discarded.

### Usage

```bash
python3 extract_constituent_sequences.py NP --match-mode base --output NP_sequences.pkl
```

### Positional argument

- `label`: target constituent label (for example `NP`, `PP`, `IP-MAT`)

### Optional arguments

- `--treebank-dir` (default: `treebank_files`)
- `--match-mode`:
  - `base` (default): matches by base category before `-` and `;`.
    - Example: `NP` matches `NP`, `NP-SBJ`, `NP;*SBJ*`, etc.
  - `exact`: exact full-label match only.
- `--allow-leaves`:
  - `yes` (default): allow leaf-node and unary phrase matches.
  - `no`: skip both leaf-node matches and unary phrase-level matches (single-child constituents).
- `--output` (default: `<label>_sequences.pkl`)

### Output

- Pickle file containing `list[list[str]]`

## 3) `extract_punctuation_segments.py`

Builds a corpus of all within-boundary-punctuation word sequences from each tree line.

Segmentation behavior:
- Token stream is split on boundary punctuation (comma/semicolon/colon/period, including Japanese `、` and `。` and fullwidth variants).
- `ID` metadata nodes are ignored.
- Null/empty elements are removed.

### Usage

```bash
python3 extract_punctuation_segments.py
```

### Optional arguments

- `--treebank-dir` (default: `treebank_files`)
- `--output` (default: `within_phrase_boundary_sequences.pkl`)

### Output

- Pickle file containing `list[list[str]]`

## Current generated files in this directory

- `kainoki_treebank_labels.md`
- `NP_sequences.pkl` (may appear as `np_sequences.pkl` on case-insensitive filesystems)
- `within_phrase_boundary_sequences.pkl`

## Quick examples

Extract all PP sequences:

```bash
python3 extract_constituent_sequences.py PP --match-mode base --output PP_sequences.pkl
```

Extract exact `NP-SBJ` only:

```bash
python3 extract_constituent_sequences.py NP-SBJ --match-mode exact --output NP-SBJ_sequences.pkl
```

Write a custom punctuation-segment corpus path:

```bash
python3 extract_punctuation_segments.py --output all_segments.pkl
```
