Module imports
```python
import pickle
import radix_trie as rt
from random import shuffle
```
Data structure setup
```python
# Set up data structure
corpus = rt.txt_to_list("corpora/lassy_corpus.txt")
distr = rt.RadixTrie()
distr.setup(corpus)
```
Get sample of noun phrases
```python
noun_phrases = pickle.load(open("corpora/lassy_noun_phrases.pkl", "rb"))
shuffle(noun_phrases)
noun_phrases_sample = noun_phrases[:50] # list of tuples of strings
```
Get dictionary of form `{w: P(noun_phrases_sample | w)}` for neighbor words `w` of NP list
```python
np_mix_fw = rt.cond_probs_of_mix(distr, noun_phrases_sample, "fw") # right neighbors
np_mix_bw = rt.cond_probs_of_mix(distr, noun_phrases_sample, "bw") # left neighbors
```
Get dictionary of form `{w: P(w | noun_phrases_sample)}` for neighbor words `w` of NP list
```python
np_neighbors_fw = rt.cond_probs_of_neighbors(distr, noun_phrases_sample, "fw") # right neighbors
np_neighbors_bw = rt.cond_probs_of_neighbors(distr, noun_phrases_sample, "bw") # left neighbors
```
Get set of words that share at least one left & one right context with NP list
```python
candidates = rt.similar_word_candidates(distr, noun_phrases_sample)
```
For each `candidate`, get dictionary of form `{w: P(w | candidate)}` for neighbor words `w` of `candidate`
```python
cond_probs_by_candidate = {}
for candidate in candidates:
    candidate_neighbors_fw = rt.cond_probs_of_neighbors(distr, [candidate], "fw") # right neighbors
    candidate_neighbors_bw = rt.cond_probs_of_neighbors(distr, [candidate], "bw") # left neighbors
```
