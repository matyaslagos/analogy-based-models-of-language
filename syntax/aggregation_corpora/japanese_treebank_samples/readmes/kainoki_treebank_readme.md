# Kainoki Treebank README

This folder contains parsed Japanese treebank files from the Kainoki Treebank.

## 1. What is in this folder

Current files:

- `academic_fujimoto2008`
- `academic_fukuda2010`
- `academic_goto2012`
- `academic_hanawa2010`
- `academic_ihara2003`

Each file is plain text and contains one parsed tree per line.

## 2. Conceptual model of a file

Treat each line as a complete treebank record with:

1. A parsed tree in Penn-style labeled parentheses.
2. A final `ID` node identifying tree number and source file.

Canonical shape:

```text
( ( ...TREE... ) (ID <treeNumber>_<fileName>[;optional_metadata]) )
```

Example:

```text
( (FRAG (NP (NPR 藤本雅彦))) (ID 3_academic_fujimoto2008))
```

Important properties:

- One line = one tree.
- The outermost wrapper is unlabeled parentheses (CorpusSearch-style wrapper).
- The `ID` is required for search tools and traceability.
- Trees represent sentence-like units (full clauses, fragments, parentheticals, etc.).

## 3. Structural layers and design choices

Kainoki uses a Penn-Treebank-like scheme adapted for Japanese.

- Clause layer: `IP-*` / `CP-*` / `FRAG`
- Phrase layer: `NP`, `PP`, `ADVP`, `CONJP`, `PRN`, etc.
- Terminal/preterminal layer: word class tags like `N`, `VB`, `P-ROLE`, `AX`, ...

Key design decisions:

- Flat clause structure around `IP` (no explicit VP node).
- Rich function extensions on labels (`-SBJ`, `-OB1`, `-OB2`, `-TPC`, `-PRD`, etc.).
- Heavy use of null elements and sort info to represent omitted arguments and reference.

## 4. Label syntax and meaning

Labels can combine:

- Base category: `NP`, `PP`, `IP`, `CP`, ...
- Function extension(s): e.g. `NP-SBJ`, `PP-OB1`, `IP-ADV-SCON-CND`
- Sort annotation after semicolon: e.g. `NP;{PERSON}`, `NP;*SBJ*`, `IP-REL;*`

### Common clause tags

- `IP-MAT`: matrix clause
- `IP-SUB`: clause under CP
- `IP-REL`: relative clause
- `IP-EMB`: gapless adnominal clause
- `IP-ADV`: adverbial clause
- `IP-NMZ`: nominalized clause
- `IP-SMC`: small clause
- `CP-QUE`: question
- `CP-THT`: complementizer clause
- `CP-FINAL`: sentence-final particle projection
- `FRAG`: fragment

### Common phrase tags

- `NP`: noun phrase
- `PP`: particle phrase
- `ADVP`: adverb phrase
- `CONJP`: coordination phrase
- `PRN`: parenthetical
- `NUMCLP`: numeral-classifier phrase

### Common terminal tags

- Nounal: `N`, `NPR`, `PRO`, `Q`, `NUM`, `CL`
- Predicate-related: `VB`, `VB0`, `VB2`, `ADJI`, `ADJN`, `AX`, `AXD`, `NEG`, `MD`
- Particle-related: `P-ROLE`, `P-OPTR`, `P-CONN`, `P-COMP`, `P-FINAL`
- Punctuation-like: `PU`, `PUL`, `PUR`, `PUQ`

## 5. Null elements and gaps

Kainoki encodes omitted material explicitly with special terminals.

### Indexed null trace

- `*ICH*` ("interpret constituent here")
- Used for discontinuity/remote placement.
- Coindexed with an overt moved/postposed constituent (`...-1` etc.).

### Unindexed null elements

- `*` : semantically unspecified zero element
- `*exp*` : expletive subject
- `*arb*` : generic impersonal zero pronoun
- `*pro*` : discourse-referential zero pronoun
- `*speaker*`, `*hearer*`, and combined forms
- `*T*` : relative clause trace

Important:

- Controlled gaps and ATB extraction sites are often left as structural gaps (no extra node), unlike relative traces.

## 6. Sort information and reference linkage

Sort information appears after `;` in a node label.

Main uses:

- `;{X}` for sort/coreference classes (e.g., pronoun-antecedent linkage).
- `;*` and `;*X*` for quantifier-host relations (including floating quantifiers).

This metadata is crucial when recovering discourse reference beyond local syntax.

## 7. How to read a line quickly

Recommended reading order:

1. Find top node (`IP-MAT`, `CP-QUE`, `FRAG`, etc.).
2. Locate predicate spine (`VB/ADJI/ADJN/AX...`).
3. Identify core functions (`-SBJ`, `-OB1`, `-OB2`, `-PRD`).
4. Check for null elements (`*pro*`, `*T*`, `*ICH*`).
5. Check sort annotations (`;{...}` / quantifier markers).
6. Record `ID` for provenance.

## 8. Practical parsing tips (for scripts)

- Parse each line as a standalone bracketed tree with a wrapper.
- Do not split on spaces naively; tokens are structure-dependent.
- Treat `;...` as part of node label (not terminal text).
- Preserve UTF-8 (Japanese terminals).
- Keep null terminals intact; they carry grammatical information.
- Use `ID` as stable primary key.

## 9. Querying mindset (CorpusSearch/Tregex)

The corpus is intended for structure-aware search, not only string matching.

Typical query targets:

- Constituents by function (e.g., all `PP-OB1` in `IP-ADV`)
- Predicate-argument structure across null arguments
- Relative and adnominal clause behavior (`IP-REL`, `IP-EMB`)
- Coreference-linked zero pronouns via sort annotations

Example pattern style (from the guide):

```text
/^IP-ADV/ < /^PP-OB1/ < (/^PP/ < (/^P-ROLE/ < に)) !<3 __
```

## 10. Known limitations to keep in mind

- String search alone misses structural generalizations.
- Orthographic variants are distinct in raw string matching.
- Lemma-level equivalence is not guaranteed by string search.
- Some interpretations depend on null/sort annotations rather than overt words.

## 11. Minimal working glossary

- `IP`: inflectional phrase (clause)
- `CP`: complementizer layer
- `PP`: particle phrase
- `OB1`/`OB2`: primary/secondary object
- `SBJ`: subject
- `PRD`: predicate complement
- `TPC`: topic
- `LGS`: logical subject (e.g., passive-related)

## 12. Source documentation

Primary guides for this annotation scheme:

- Invitation/overview: <https://kainoki.github.io/invitation.html>
- Full parsing guide: <https://kainoki.github.io/guide.html>

The detailed operational conventions (tag inventory, special constructions, edge cases) are defined in the parsing guide chapters.
