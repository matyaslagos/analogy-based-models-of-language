# Dutch Lassy Small Treebank Notes

This directory contains working notes about the Dutch Lassy Small treebank files in `treebank/`.

## Format

The files are sentence-level XML files in Alpino's `alpino_ds` format. Each sentence has a tree of `node` elements.

- Internal nodes usually represent syntactic constituents and carry:
  - `cat`: constituent/category label
  - `rel`: grammatical relation to the parent
  - `begin`, `end`: token span boundaries
- Leaf nodes are terminals and usually carry lexical and morphosyntactic information instead of `cat`, such as:
  - `word`, `lemma`, `root`
  - `pt`: coarse POS code
  - `pos`: readable POS name
  - `postag`: detailed morphological/syntactic tag

This is best treated as an Alpino phrasal dependency representation rather than a plain constituency treebank.

## Non-terminal Labels (`cat`)

Common constituent labels found in the corpus:

- `top`
- `smain`, `ssub`, `sv1`
- `inf`, `ppart`, `ppres`
- `np`, `pp`, `ap`, `advp`
- `cp`, `conj`, `mwu`
- `rel`, `ti`, `oti`, `du`
- `whsub`, `whrel`, `whq`
- `detp`

There are also a few rarer labels and some parenthesized variants such as `p(smain)`.

## Relation Labels (`rel`)

Common grammatical relation labels:

- `hd`: head
- `su`: subject
- `obj1`, `obj2`: objects
- `mod`: modifier
- `det`: determiner
- `predc`, `predm`: predicative complement / predicative modifier
- `pc`: prepositional complement
- `vc`: verbal complement
- `cnj`, `crd`: conjunct / coordinator
- `cmp`: complementizer
- `mwp`: part of a multi-word unit
- `app`: apposition
- `svp`: separable verb particle
- `ld`: locative/directional complement
- `rhd`, `whd`: relative/wh head
- `body`, `dp`, `nucl`, `dlink`, `sat`
- `se`, `me`, `sup`, `tag`, `obcomp`, `pobj1`, `hdf`
- `top`, `--`

For extraction work, `cat` usually identifies the constituent type of interest, while `rel` identifies the constituent's syntactic function.

## Terminal Labels

### Coarse terminal code (`pt`)

Frequent `pt` values:

- `n`: noun/name
- `ww`: verb
- `adj`: adjective
- `bw`: adverb
- `vnw`: pronoun
- `lid`: determiner/article
- `vz`: preposition
- `vg`: conjunction
- `tw`: numeral
- `spec`: special token class
- `let`: punctuation
- `tsw`: interjection

### Readable POS label (`pos`)

Frequent `pos` values:

- `noun`, `name`, `verb`, `adj`, `adv`, `pron`, `det`, `prep`
- `vg`, `num`, `punct`
- `part`, `pp`, `fixed`, `comparative`

### Rich tag (`postag`)

`postag` provides detailed morphological/syntactic annotation, for example:

- `N(soort,ev,basis,zijd,stan)`
- `N(eigen,ev,basis,onz,stan)`
- `WW(pv,tgw,ev)`
- `WW(inf,vrij,zonder)`
- `ADJ(prenom,basis,met-e,stan)`
- `VNW(...)`
- `LID(...)`
- `VZ(init)`
- `LET()`

These tags encode distinctions such as common vs. proper noun, number, tense, verbal form, adjective position, inflection, pronoun subtype, and more.

## Parsing Implication

If the goal is to extract word sequences for particular syntactic categories, the natural strategy is:

1. Find internal `node`s with the target `cat`.
2. Collect the terminal descendants in token order, usually by `begin`/`end`.
3. Use `rel` when the extraction should be restricted by grammatical function.
4. Use `pt`, `pos`, or `postag` only when filtering by lexical or morphosyntactic type.

## Sources Consulted

- Local inspection of sample files in `treebank/`
- Alpino User Guide: <https://www.let.rug.nl/vannoord/alp/Alpino/AlpinoUserGuide.html>
- D-Coi / Alpino annotation materials: <https://www.let.rug.nl/vannoord/DCOI/>
