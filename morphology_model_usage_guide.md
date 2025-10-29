# Usage guide for [`morphology_model.py`](https://github.com/matyaslagos/analogical-path-models/blob/main/morphology_model.py)

## Setup and usage of some functions

Setting up the model:
```python
# file custom_io.py should be in same folder as morphology_model.py
import morphology_model as mor
model = mor.MorphModel()
model.setup() # ~10 secs, needs file with path 'corpora/sztaki_corpus_2017_2018_0001_clean.tsv'
```
Carrying out testing:
```python
test_corpus = mor.import_test_data() # needs file with path 'corpora/sztaki_corpus_2017_2018_0002_clean.tsv'
test_results = mor.testing(model, test_corpus)
```
Dictionary `test_results` has keys `True` and `False` with `set` values containing tuples of form `(target_word, produced_word, lemma_frequency, tag)`.
E.g. in `test_results[False]`, there could be a tuple `('külsőm', 'külsejem', ('Poss', 'Nom', '1Sg'), 'külső', 39)`, indicating that
the lemma `'külső'` occurred `39` times in the training data, its `('Poss', 'Nom', '1Sg')` form is `'külsőm'`, and the model
(wrongly) guessed that this form is `'külsejem'`.
