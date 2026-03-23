# Kainoki Treebank Labels (Extracted from `treebank_files`)

Extracted **105** unique labels from the five treebank files.
Overview tables list **91** unique tags (word/phrase/clause/function/other).

## Differences from `kainoki_treebank_annotation_overview.md`

- Labels present in treebank but not listed as exact tags in the overview: **52**
- Overview tags not attested in these five files: **38**
- Compositional combinations of documented tags/functions: **34**
- Sort/reference-annotated labels (`;...`): **10**
- Undocumented/non-compositional labels: **8**

### Compositional combinations (not listed as standalone rows)

`ADVP-CMPL`, `CP-THT-ADV`, `CP-THT-OB1`, `CP-THT-SBJ`, `IP-ADV-CONJ`, `IP-ADV-SCON`, `IP-ADV-SCON-CND`, `NP-ADV`, `NP-DOB1`, `NP-LGS`, `NP-LOC`, `NP-MSR`, `NP-OB1`, `NP-OB2`, `NP-PRD`, `NP-SBJ`, `NP-TMP`, `PP-1`, `PP-CMPL`, `PP-CONJ`, `PP-CZZ`, `PP-DSBJ`, `PP-LGS`, `PP-MSR`, `PP-OB1`, `PP-OB2`, `PP-PRD`, `PP-SBJ`, `PP-SBJ2`, `PP-SCON`, `PP-SCON-CND`, `PP-TMP`, `PP-TPC`, `PRN-1`

### Sort/reference-annotated labels

`IP-REL;*`, `NP-CZZ;{POSSIBILITY}`, `NP-OB1;{DREAM}`, `NP;*`, `NP;*OB1*`, `NP;*OB2*`, `NP;*SBJ*`, `NP;{DREAM}`, `NP;{POSSIBILITY}`, `PP;*OB1*`

### Undocumented/non-compositional labels

`ID`, `IP-ADV2-SCON`, `IP-SMC-CLR`, `PULB`, `PULQ`, `PUNC`, `PURB`, `PURQ`

### Overview tags not attested in this sample

`-ADV`, `-CMPL`, `-CND`, `-CNT`, `-CONJ`, `-CZZ`, `-DOB1`, `-DSBJ`, `-LGS`, `-LOC`, `-MSR`, `-OB1`, `-OB2`, `-POS`, `-PRD`, `-PRP`, `-SBJ`, `-SBJ2`, `-SCON`, `-TMP`, `-TPC`, `-VOC`, `ADJI-MD`, `ADJN-MD`, `CP-EXL`, `FS`, `INTJP`, `IP-NMZ`, `LS`, `META`, `P-INTJ`, `PASS2`, `PNLP`, `PU`, `PUL`, `PUQ`, `PUR`, `multi-sentence`

## Leaf-Level Labels

Labels that directly dominate token leaves at least once in the extracted files:

`ADJI`, `ADJN`, `ADV`, `AX`, `AXD`, `CL`, `CONJ`, `D`, `FN`, `FW`, `ID`, `INTJ`, `MD`, `N`, `N-MENTION`, `NEG`, `NP`, `NP-CZZ;{POSSIBILITY}`, `NP-DOB1`, `NP-LGS`, `NP-LOC`, `NP-OB1`, `NP-OB1;{DREAM}`, `NP-OB2`, `NP-SBJ`, `NPR`, `NUM`, `P-COMP`, `P-CONN`, `P-FINAL`, `P-OPTR`, `P-ROLE`, `PASS`, `PNL`, `PP-SCON`, `PRN`, `PRO`, `PULB`, `PULQ`, `PUNC`, `PURB`, `PURQ`, `Q`, `SYM`, `VB`, `VB0`, `VB2`, `WADV`, `WD`, `WNUM`, `WPRO`

## Extracted Labels and Meanings

| Label | Count | Leaf label count | Meaning | Notes |
|---|---:|---:|---|---|
| `ADJI` | 33 | 33 | イ-adjective | Documented in overview (Word class tags) |
| `ADJN` | 120 | 120 | ナ-adjective | Documented in overview (Word class tags) |
| `ADV` | 58 | 58 | adverb | Documented in overview (Word class tags) |
| `ADVP` | 102 | 0 | adverb phrase | Documented in overview (Phrase layer tags) |
| `ADVP-CMPL` | 3 | 0 | adverb phrase + used with complement function |  |
| `AX` | 379 | 379 | auxiliary verb (including copula) | Documented in overview (Word class tags) |
| `AXD` | 53 | 53 | auxiliary verb, past tense | Documented in overview (Word class tags) |
| `CL` | 47 | 47 | classifier | Documented in overview (Word class tags) |
| `CONJ` | 33 | 33 | coordinating conjunction | Documented in overview (Word class tags) |
| `CONJP` | 104 | 0 | conjunction phrase | Documented in overview (Phrase layer tags) |
| `CP-FINAL` | 1 | 0 | projection for sentence final particle)projection for sentence final particle | Documented in overview (Clause layer tags) |
| `CP-IMP` | 1 | 0 | imperative | Documented in overview (Clause layer tags) |
| `CP-QUE` | 13 | 0 | question (direct or indirect) | Documented in overview (Clause layer tags) |
| `CP-THT` | 17 | 0 | complementizer clause | Documented in overview (Clause layer tags) |
| `CP-THT-ADV` | 1 | 0 | complementizer clause + unspecified adverbial function |  |
| `CP-THT-OB1` | 14 | 0 | complementizer clause + used as primary object |  |
| `CP-THT-SBJ` | 10 | 0 | complementizer clause + used as subject |  |
| `D` | 35 | 35 | determiner | Documented in overview (Word class tags) |
| `FN` | 28 | 28 | formal noun | Documented in overview (Word class tags) |
| `FRAG` | 39 | 0 | fragment | Documented in overview (Clause layer tags) |
| `FW` | 4 | 4 | foreign word | Documented in overview (Word class tags) |
| `ID` | 179 | 179 | (not documented in overview) | No direct mapping in overview tables |
| `INTJ` | 1 | 1 | interjection | Documented in overview (Word class tags) |
| `IP-ADV` | 36 | 0 | adverbial clause | Documented in overview (Clause layer tags) |
| `IP-ADV-CONJ` | 78 | 0 | adverbial clause + conjunct of coordination |  |
| `IP-ADV-SCON` | 20 | 0 | adverbial clause + subordinate element of subordinate conjunction |  |
| `IP-ADV-SCON-CND` | 9 | 0 | adverbial clause + subordinate element of subordinate conjunction + used as conditional |  |
| `IP-ADV2-SCON` | 1 | 0 | (not documented in overview) | No direct mapping in overview tables |
| `IP-EMB` | 90 | 0 | gapless noun-modifying clause | Documented in overview (Clause layer tags) |
| `IP-MAT` | 138 | 0 | matrix clause | Documented in overview (Clause layer tags) |
| `IP-REL` | 203 | 0 | relative clause | Documented in overview (Clause layer tags) |
| `IP-REL;*` | 15 | 0 | relative clause | Sort/reference annotation `;*` |
| `IP-SMC` | 5 | 0 | small clause | Documented in overview (Clause layer tags) |
| `IP-SMC-CLR` | 23 | 0 | small clause | Undocumented extension part(s): `-CLR` |
| `IP-SUB` | 47 | 0 | clause under CP layer | Documented in overview (Clause layer tags) |
| `LST` | 14 | 0 | list | Documented in overview (Other tags) |
| `MD` | 11 | 11 | modal element | Documented in overview (Word class tags) |
| `N` | 1069 | 1069 | noun | Documented in overview (Word class tags) |
| `N-MENTION` | 6 | 6 | mentioned expression | Documented in overview (Word class tags) |
| `NEG` | 51 | 51 | negation | Documented in overview (Word class tags) |
| `NLYR` | 19 | 0 | noun phrase intermediate layer | Documented in overview (Phrase layer tags) |
| `NP` | 1179 | 2 | noun phrase | Documented in overview (Phrase layer tags) |
| `NP-ADV` | 3 | 0 | noun phrase + unspecified adverbial function |  |
| `NP-CZZ;{POSSIBILITY}` | 1 | 1 | noun phrase + used with causee function | Sort/reference annotation `;{POSSIBILITY}` |
| `NP-DOB1` | 1 | 1 | noun phrase + used with derived primary object function |  |
| `NP-LGS` | 58 | 58 | noun phrase + logical subject |  |
| `NP-LOC` | 2 | 2 | noun phrase + used with locational function |  |
| `NP-MSR` | 1 | 0 | noun phrase + used with measurement function |  |
| `NP-OB1` | 34 | 34 | noun phrase + used as primary object |  |
| `NP-OB1;{DREAM}` | 1 | 1 | noun phrase + used as primary object | Sort/reference annotation `;{DREAM}` |
| `NP-OB2` | 1 | 1 | noun phrase + used as secondary object |  |
| `NP-PRD` | 103 | 0 | noun phrase + used as predicate |  |
| `NP-SBJ` | 331 | 328 | noun phrase + used as subject |  |
| `NP-TMP` | 12 | 0 | noun phrase + used with temporal function |  |
| `NP;*` | 1 | 0 | noun phrase | Sort/reference annotation `;*` |
| `NP;*OB1*` | 1 | 0 | noun phrase | Sort/reference annotation `;*OB1*` |
| `NP;*OB2*` | 1 | 0 | noun phrase | Sort/reference annotation `;*OB2*` |
| `NP;*SBJ*` | 2 | 0 | noun phrase | Sort/reference annotation `;*SBJ*` |
| `NP;{DREAM}` | 1 | 0 | noun phrase | Sort/reference annotation `;{DREAM}` |
| `NP;{POSSIBILITY}` | 1 | 0 | noun phrase | Sort/reference annotation `;{POSSIBILITY}` |
| `NPR` | 44 | 44 | proper noun | Documented in overview (Word class tags) |
| `NUM` | 64 | 64 | numeral | Documented in overview (Word class tags) |
| `NUMCLP` | 66 | 0 | numeral-classifier phrase | Documented in overview (Phrase layer tags) |
| `P-COMP` | 49 | 49 | complementizer particle | Documented in overview (Word class tags) |
| `P-CONN` | 229 | 229 | conjunctional particle | Documented in overview (Word class tags) |
| `P-FINAL` | 12 | 12 | final particle | Documented in overview (Word class tags) |
| `P-OPTR` | 220 | 220 | toritate particle | Documented in overview (Word class tags) |
| `P-ROLE` | 818 | 818 | role particle | Documented in overview (Word class tags) |
| `PASS` | 71 | 71 | direct passive | Documented in overview (Word class tags) |
| `PNL` | 7 | 7 | prenominal | Documented in overview (Word class tags) |
| `PP` | 480 | 0 | particle phrase | Documented in overview (Phrase layer tags) |
| `PP-1` | 1 | 0 | particle phrase | Coindexation suffix `-1` |
| `PP-CMPL` | 9 | 0 | particle phrase + used with complement function |  |
| `PP-CONJ` | 13 | 0 | particle phrase + conjunct of coordination |  |
| `PP-CZZ` | 2 | 0 | particle phrase + used with causee function |  |
| `PP-DSBJ` | 4 | 0 | particle phrase + used with derived subject function |  |
| `PP-LGS` | 11 | 0 | particle phrase + logical subject |  |
| `PP-MSR` | 5 | 0 | particle phrase + used with measurement function |  |
| `PP-OB1` | 184 | 0 | particle phrase + used as primary object |  |
| `PP-OB2` | 2 | 0 | particle phrase + used as secondary object |  |
| `PP-PRD` | 7 | 0 | particle phrase + used as predicate |  |
| `PP-SBJ` | 207 | 0 | particle phrase + used as subject |  |
| `PP-SBJ2` | 4 | 0 | particle phrase + used as secondary subject |  |
| `PP-SCON` | 12 | 2 | particle phrase + subordinate element of subordinate conjunction |  |
| `PP-SCON-CND` | 6 | 0 | particle phrase + subordinate element of subordinate conjunction + used as conditional |  |
| `PP-TMP` | 7 | 0 | particle phrase + used with temporal function |  |
| `PP-TPC` | 5 | 0 | particle phrase + topic |  |
| `PP;*OB1*` | 1 | 0 | particle phrase | Sort/reference annotation `;*OB1*` |
| `PRN` | 56 | 1 | parenthetical | Documented in overview (Phrase layer tags) |
| `PRN-1` | 1 | 0 | parenthetical | Coindexation suffix `-1` |
| `PRO` | 44 | 44 | pronoun | Documented in overview (Word class tags) |
| `PULB` | 42 | 42 | (not documented in overview) | No direct mapping in overview tables |
| `PULQ` | 35 | 35 | (not documented in overview) | No direct mapping in overview tables |
| `PUNC` | 416 | 416 | (not documented in overview) | No direct mapping in overview tables |
| `PURB` | 43 | 43 | (not documented in overview) | No direct mapping in overview tables |
| `PURQ` | 35 | 35 | (not documented in overview) | No direct mapping in overview tables |
| `Q` | 23 | 23 | quantifier | Documented in overview (Word class tags) |
| `SYM` | 9 | 9 | symbol | Documented in overview (Word class tags) |
| `VB` | 443 | 443 | verb (or verb stem) | Documented in overview (Word class tags) |
| `VB0` | 168 | 168 | light verb | Documented in overview (Word class tags) |
| `VB2` | 115 | 115 | secondary verb | Documented in overview (Word class tags) |
| `WADV` | 4 | 4 | indeterminate adverb | Documented in overview (Word class tags) |
| `WD` | 2 | 2 | indeterminate determiner | Documented in overview (Word class tags) |
| `WNUM` | 2 | 2 | indeterminate numeral | Documented in overview (Word class tags) |
| `WPRO` | 6 | 6 | indeterminate pronoun | Documented in overview (Word class tags) |
