import math
import pickle
from pprint import pp

# g gain score 
def gain_score(d, sample_total_freq):
    is_correct = d["correct"]
    freq = d["frequency"]
    if is_correct:
        return math.log(freq) / sample_total_freq
    else:
        return -math.log(freq) / sample_total_freq

# lambda discount factor
def discount_factor(index):
    return math.log2(index + 1)

# DCG@k
def dcg_k(pi, sample_total_freq):
    dcg = 0
    for i, d in enumerate(pi, start=1):
        dcg += gain_score(d, sample_total_freq) / discount_factor(i)
    return dcg

# NDCG@k with min-max normalization, following Gienapp et al. (2020)
def ndcg_k_min(pi, sample_total_freq):
    ideal_dcg = dcg_k(most_freq_correct, sample_total_freq)
    worst_dcg = dcg_k(most_freq_incorrect, sample_total_freq)
    actual_dcg = dcg_k(pi, sample_total_freq)
    if ideal_dcg == worst_dcg:
        return 0.0
    else:
        return (actual_dcg - worst_dcg) / (ideal_dcg - worst_dcg)

with open("results.pkl", "rb") as f:
    result_dict = pickle.load(f)
results_by_run = result_dict["results_by_run"]
most_freq_correct = result_dict["best_possible_words"]
most_freq_incorrect = result_dict["worst_possible_words"]

ndcg_store = {}  # 3D dict: {run: {sample_size: {func: ndcg_value}}}

for run in results_by_run:
    ndcg_store[run] = {}
    for sample_size in results_by_run[run]:
        ndcg_store[run][sample_size] = {}
        sample_total_freq = sum(results_by_run[run][sample_size]["sample_freqs"])
        #print(results_by_run[run][sample_size])
        for function in results_by_run[run][sample_size]:
            # TODO: nem lehetne esetleg máshol -- eggyel kijjebb -- tárolni a sample_freqs-t,
            # hogy tényleg csak a hasonlósági függvények legyenek itt?
            if function != "sample_freqs":
                found_words= results_by_run[run][sample_size][function]
                ndcg_value = ndcg_k_min(found_words, sample_total_freq)
                ndcg_store[run][sample_size][function] = ndcg_value

# Checking that ndcg_store is populated correctly for run 32, sample size 50, and function "min_conf":
found_words = results_by_run[32][50]["min_conf"]
sample_total_freq = sum(results_by_run[32][50]["sample_freqs"])
print(ndcg_k_min(found_words, sample_total_freq))

print(ndcg_store[32][50]["min_conf"])

# Save ndcg_store for use in other scripts
with open("ndcg_store.pkl", "wb") as f:
    pickle.dump(ndcg_store, f)
               
