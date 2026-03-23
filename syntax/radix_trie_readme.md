Module imports
```python
import pickle
import radix_trie as rt
from pprint import pp
from random import shuffle
from similarity_metrics import jaccard_coefficient, min_confusion_probability
```
Data structure setup
```python
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
Get dictionaries of form `{w: P(noun_phrases_sample | w)}` for neighbor words `w` of NP list
(only used for confusion similarities)
```python
np_mix_fw = rt.cond_probs_of_mix(distr, noun_phrases_sample, "fw") # right neighbors
np_mix_bw = rt.cond_probs_of_mix(distr, noun_phrases_sample, "bw") # left neighbors
```
Get dictionaries of form `{w: P(w | noun_phrases_sample)}` for neighbor words `w` of NP list
```python
np_neighbors_fw = rt.cond_probs_of_neighbors(distr, noun_phrases_sample, "fw") # right neighbors
np_neighbors_bw = rt.cond_probs_of_neighbors(distr, noun_phrases_sample, "bw") # left neighbors
```
Get set of words that share at least one left & one right context with NP list
(others have no chance of being similar to NP list, so we disregard them)
```python
candidates = rt.similar_word_candidates(distr, noun_phrases_sample)
```
For each `candidate`, get dictionaries of form `{w: P(w | candidate)}` for neighbor words `w` of `candidate`,
make vectors out of these dictionaries, and compare with dictionaries of NP list

**TODOs**:
- write `vectorize()` function that converts above dicts into vectors such that coordinates line up, so
that it can be used like below
- generalize this script so that:
    - it tests NP lists of increasing sizes
    - it tests all similarity functions in `similarity_metrics`

(note: for `l1_norm` and `jensen_shannon_divergence`, bigger value means _less_ similar)
```python
similarities = {}
for candidate in candidates:
    # Compute conditional probabilities of neighbors of candidate
    candidate_neighbors_fw = rt.cond_probs_of_neighbors(distr, [candidate], "fw") # right neighbors
    candidate_neighbors_bw = rt.cond_probs_of_neighbors(distr, [candidate], "bw") # left neighbors
    # Compute vectors for non-confusion similarity metrics
    np_fw_vector, candidate_fw_vector = vectorize(np_neighbors_fw, candidate_neighbors_fw)
    np_bw_vector, candidate_bw_vector = vectorize(np_neighbors_bw, candidate_neighbors_bw)
    # Compute e.g. Jaccard coefficient from vectors
    jaccard_sim_fw = jaccard_similarity(np_fw_vector, candidate_fw_vector)
    jaccard_sim_bw = jaccard_similarity(np_bw_vector, candidate_bw_vector)
    jaccard_sim = min(jaccard_sim_fw, jaccard_sim_bw)
    # Compute vectors for confusion similarity metrics
    np_conf_fw_vector, candidate_fw_vector = vectorize(np_mix_fw, candidate_neighbors_fw)
    np_conf_fw_vector, candidate_fw_vector = vectorize(np_mix_fw, candidate_neighbors_fw)
    # Compute e.g. min-confusion score from vectors
    min_conf_sim_fw = min_confusion_probability(np_conf_fw_vector, candidate_fw_vector)
    min_conf_sim_bw = min_confusion_probability(np_conf_bw_vector, candidate_bw_vector)
    min_conf_sim = min(min_conf_sim_fw, min_conf_sim_bw)
    similarities[candidate] = {"jacc": jaccard_sim, "min_conf": min_conf_sim}
```
Sort e.g. min-confusion scores and print 10 most similar words to `noun_phrases_sample`
```python
min_conf_sims = {candidate: sims["min_conf"] for candidate, sims in similarities.items()}
sorted_min_conf_sims = sorted(min_conf_sims.items(), key=lambda x: x[1], reverse=True)
pp(sorted_min_conf_sims[:10])
```
