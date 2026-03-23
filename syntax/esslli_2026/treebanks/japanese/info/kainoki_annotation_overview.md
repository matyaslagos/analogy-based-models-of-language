# Annotation overview

1.1   Introduction

This manual details an annotation scheme for parsing contemporary Japanese. Syntactic structure is represented with labelled parentheses adapting the format of the Penn Treebank (Bies et al. 1995). More particularly, the Penn Historical Corpora scheme (Santorini 2010) has informed the ‘look’ of the annotation. This includes:

    adoption of the CorpusSearch format (described in section 1.3.1 below) as the underlying encoding,
    not having any explicit verb phrase structure (although verb phrase structure is implicitly present when there are interpretive consequences),
    the use of IP, ADVP, NP, and PP tag labels,
    the presentation of phrase conjunction structure with CONJP layers, and
    the marking of function for all clausal nodes and all clause level constituents.

The annotation also contains plenty that is innovative, including information to resolve both inter and intra sentential anaphoric dependencies from a discourse perspective.

    Annotation is carried out with a general text editor on text files.

    Annotation practice strives first for observational adequacy. The aim is to present a consistent linguistic analysis for each attestation of an identifiable linguistic relation or process. Relations and processes are treated uniformly as much as possible, and their treatments are detailed in this documentation. Setting aside the issue of whether the system of description is theoretically correct, the practice is to render lexical and functional items, parts of speech, constituents of various categories and functions, and constructions defined by combinations of properties, in such ways as to be unambiguously identifiable. This documentation sets out basic principles both for the annotator (assigning segmentations, tags, and structural positions) and for the user (searching for classes of items, categories, and relationships between these). Examples of suitable tools for searching the parsed data without requiring any modification to the data include: CorpusSearch (Randall 2009) and Tregex (Levy and Andrew 2006).

    The current annotation also aims to offer syntactic analysis that can serve as a base for the subsequent generation of meaning representations using the methods of Treebank Semantics (Butler 2015). To this end, extra disambiguation information is added to feed the calculation of semantic analyses from the syntactic annotation. One example of this is seen in the different specifications of clause linkage (i.e., different types of non-final clauses). The annotation has the -SCON tag extension to identify clauses integrated with subordinate conjunction. Subordinate clause status influences the distribution of empty subject positions within such clauses and the antecedence relationships these positions have with respect to upstairs arguments (according to an antecedent calculation called ‘control’). These cases are contrasted with coordinate clause linkage, also identified with a tag extension: -CONJ (coordinating conjunction). Status as a coordinate clause influences the distribution of arguments shared between that clause and one or more other clauses (according to an antecedent calculation called ‘Across the Board extraction’ (ATB)).

    With these calculations in place, most antecedent relations in Japanese can be accurately determined without resorting to annotation with overt indexing, provided that the distinction between subordination and coordination is properly annotated. The practice provides a robust basis for calculating semantic dependencies, a simplified annotation scheme that is descriptively adequate, and a set of constraints on the distribution of null positions which have interesting consequences with respect to, for example, the placement of null elements.

    The purpose of the rest of this chapter is to introduce broad aspects of the annotation scheme, while subsequent chapters will focus on particular topics.

1.2   Tags

Tag labels are either word class tags (e.g., N=noun, P=particle, ADV=adverb), phrase level categories with minimally a basic label to indicate the form of the constituent (e.g., NP=noun phrase, PP=particle phrase, ADVP=adverb phrase), or clause level categories (e.g., IP-MAT=matrix clause, CP-FINAL=matrix clause with sentence final particle(s)). Frequently, label extensions (separated by a hyphen) are added to labels to indicate function (e.g., P-ROLE=role particle, NP-SBJ=subject noun phrase). In most cases there is one label extension, but more is possible (e.g., CP-QUE-OB1= question used as object, IP-ADV-SCON-CND=conditional clause).

    All tag labels used in this schema are listed below in Tables 1.1–1.5.

Table 1.1: Word class tags
ADJI-MD	modal イ-adjective
ADJI	イ-adjective
ADJN-MD	modal ナ-adjective
ADJN	ナ-adjective
ADV	adverb
AXD	auxiliary verb, past tense
AX	auxiliary verb (including copula)
CL	classifier
CONJ	coordinating conjunction
D	determiner
FN	formal noun
FW	foreign word
INTJ	interjection
MD	modal element
NEG	negation
N-MENTION	mentioned expression
NPR	proper noun
N	noun
NUM	numeral
PASS2	indirect passive
PASS	direct passive
P-COMP	complementizer particle
P-CONN	conjunctional particle
P-FINAL	final particle
P-INTJ	interjectional particle
PNL	prenominal
P-OPTR	toritate particle
P-ROLE	role particle
PRO	pronoun
PUL	left bracket
PUQ	quote
PUR	right bracket
PU	punctuation
Q	quantifier
SYM	symbol
VB0	light verb
VB2	secondary verb
VB	verb (or verb stem)
WADV	indeterminate adverb
WD	indeterminate determiner
WNUM	indeterminate numeral
WPRO	indeterminate pronoun

Table 1.2: Phrase layer tags
ADVP	adverb phrase
CONJP	conjunction phrase
INTJP	interjection phrase
NLYR	noun phrase intermediate layer
NP	noun phrase
NUMCLP	numeral-classifier phrase
PNLP	prenominal phrase
PP	particle phrase
PRN	parenthetical

Table 1.3: Clause layer tags
CP-EXL	exclamative
CP-FINAL	projection for sentence final particle)projection for sentence final particle
CP-IMP	imperative
CP-QUE	question (direct or indirect)
CP-THT	complementizer clause
FRAG	fragment
IP-ADV	adverbial clause
IP-EMB	gapless noun-modifying clause
IP-MAT	matrix clause
IP-NMZ	nominalized clause
IP-REL	relative clause
IP-SMC	small clause
IP-SUB	clause under CP layer
multi-sentence	multiple sentence

Table 1.4: Function tags
-ADV	unspecified adverbial function
-CMPL	used with complement function
-CND	used as conditional
-CNT	used with continuative function
-CONJ	conjunct of coordination
-CZZ	used with causee function
-DOB1	used with derived primary object function
-DSBJ	used with derived subject function
-LGS	logical subject
-LOC	used with locational function
-MSR	used with measurement function
-OB1	used as primary object
-OB2	used as secondary object
-POS	used with possessive function
-PRD	used as predicate
-PRP	used with purposive function
-SBJ	used as subject
-SBJ2	used as secondary subject
-SCON	subordinate element of subordinate conjunction
-TMP	used with temporal function
-TPC	topic
-VOC	vocative

Table 1.5: Other tags
FS	false start
LS	list item
LST	list
META	metadata
