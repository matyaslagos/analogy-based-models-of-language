# NLTK Penn Treebank usage guide

Install NLTK, then start Python interpreter, then import NLTK
```python
pip3 install nltk
python3
>>> import nltk
```

Import Penn Treebank corpus sample
```python
>>> from nltk.corpus import treebank
>>> nltk.download("treebank")
```

Inspect sentences in the corpus sample
```python
>>> sentence = treebank.parsed_sents()[0] # tree of first sentence
>>> subtree_list = list(sentence.subtrees()) # list of all subtrees of tree
>>> subtree = subtree_list[21] # pick a subtree
>>> subtree.label() # syntactic category of subtree, e.g. 'NP'
>>> subtree.leaves() # list of terminal strings of subtree, e.g. ['a', 'nonexecutive', 'director']
```

Task: write function `concordance_by_label()` for returning list of `[left_context, sequence, right_context]` triples where `sequence` is string labelled with input label, and `left_context` and `right_context` are its full left and right contexts in the sentence.
```python
>>> concordance_by_label(treebank, 'NP')
[[['i', 'saw'], ['a', 'nonexecutive', 'director'], ['yesterday']], [['did'], ['my', 'letter'], ['arrive']], ...]
```
