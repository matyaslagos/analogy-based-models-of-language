#!/usr/bin/env python3
# Module imports
import pickle
import math
import radix_trie_updated as rt
import similarity_metrics as sm
from pprint import pp
from random import shuffle, sample
from collections import defaultdict

sim_metrics = ["jacc", "min_conf", "l1", "cosine", "js_div", "skew_div"]
sim_metrics_shuffled = sim_metrics.copy()
shuffle(sim_metrics_shuffled)
sim_metric_codemap = {sim_metric: "s" + str(i) for i, sim_metric in enumerate(sim_metrics_shuffled)}
def sim_metric_code(sim_metric):
    #return sim_metric_codemap[sim_metric]
    return sim_metric

np_sample_sizes = [5, 10, 25, 50, 100]

raw_corpus = pickle.load(open(f"../extracted_sequence_files/all_sequences.pkl", "rb"))
corpus = [("<#",) + sentence + ("#>",) for sentence in raw_corpus.elements()]
distr = rt.RadixTrie()
distr.setup(corpus)

def sort_by_freqs(sequence_set, distr_trie):
    freq_dict = {}
    for sequence in sequence_set:
        try:
            freq_dict[sequence] = distr_trie.freq(sequence)
        except:
            continue
    return sorted(freq_dict.items(), key=lambda x: x[1], reverse=True)

target_seqs_counter = pickle.load(open(f"../extracted_sequence_files/singleword_target_sequences.pkl", "rb"))
all_target_seqs = set(target_seqs_counter.keys())
most_frequent_target_seqs = list(target_seqs_counter.most_common(25))
most_frequent_target_seq_items = [
    {"word": w,
     "correct": True,
     "frequency": freq}
    for w, freq in most_frequent_target_seqs
]

all_non_target_seqs = {(x,) for x in distr.fw_root.children.keys()} - all_target_seqs
most_frequent_non_target_seqs = sort_by_freqs(all_non_target_seqs, distr)
most_frequent_non_target_seq_items = [
    {"word": w,
     "correct": False,
     "frequency": freq}
    for w, freq in most_frequent_non_target_seqs
]

multiword_source_seqs = set(pickle.load(open(f"../extracted_sequence_files/multiword_source_sequences.pkl", "rb")).keys())

def experiment_run(always_shuffle=False):

    # Get sample of noun phrases
    noun_phrases = sorted(multiword_source_seqs.copy())
    if not always_shuffle:
        shuffle(noun_phrases)
        noun_phrase_samples = {n: noun_phrases[:n] for n in np_sample_sizes}
    else:
        noun_phrase_samples = {n: sample(noun_phrases, n) for n in np_sample_sizes}
    found_words_by_sample_size = {}
    # Test for incresing sample sizes
    for n in np_sample_sizes:
        noun_phrases_sample = noun_phrase_samples[n] # list of tuples of strings
        sample_freqs = [distr.freq(x) for x in noun_phrases_sample]
        # (a) Get dicts with items of form (w, P(noun_phrases_sample | w)) for neighbor words w of noun_phrases_sample
        # (used later for confusion similarities)
        np_mix_fw = rt.cond_probs_of_mix(distr, noun_phrases_sample, "fw") # right neighbors
        np_mix_bw = rt.cond_probs_of_mix(distr, noun_phrases_sample, "bw") # left neighbors

        # (b) Get dicts with items of form (w, P(w | noun_phrases_sample)) for neighbor words w of noun_phrases_sample
        # (used later for non-confusion similarities)
        np_neighbors_fw = rt.cond_probs_of_neighbors(distr, noun_phrases_sample, "fw") # right neighbors
        np_neighbors_bw = rt.cond_probs_of_neighbors(distr, noun_phrases_sample, "bw") # left neighbors

        # Get set of words that share at least one left and one right context with noun_phrases_sample
        candidates = rt.similar_word_candidates(distr, noun_phrases_sample)


        # For each candidate, get dicts with items of form (w, P(w | candidate)) for neighbor words w of candidate,
        # convert these dicts and the dicts of the noun phrase sample into vectors, and compute their similarities
        similarities = {metric: {} for metric in sim_metrics}
        for candidate in candidates:
            # Compute conditional probabilities of neighbors of candidate
            candidate_neighbors_fw = rt.cond_probs_of_neighbors(distr, [candidate], "fw") # right neighbors
            candidate_neighbors_bw = rt.cond_probs_of_neighbors(distr, [candidate], "bw") # left neighbors

            # Compute vectors for non-confusion similarity metrics
            np_fw_vector, candidate_fw_vector = rt.vectorize(np_neighbors_fw, candidate_neighbors_fw)
            np_bw_vector, candidate_bw_vector = rt.vectorize(np_neighbors_bw, candidate_neighbors_bw)

            # Compute similarities for all metrics
            for metric in sim_metrics:
                if metric in ["jacc", "l1", "cosine", "js_div", "skew_div"]:
                    # Compute similarity from vectors
                    sim_fw = rt.compute_similarity(np_fw_vector, candidate_fw_vector, metric)
                    sim_bw = rt.compute_similarity(np_bw_vector, candidate_bw_vector, metric)
                    sim = min(sim_fw, sim_bw)
                    similarities[metric][candidate] = sim

                elif metric in ["min_conf", "conf"]:
                    # Compute vectors for confusion similarity metrics
                    np_conf_fw_vector, candidate_fw_vector = rt.vectorize(np_mix_fw, candidate_neighbors_fw)
                    np_conf_bw_vector, candidate_bw_vector = rt.vectorize(np_mix_bw, candidate_neighbors_bw)

                    # Compute confusion score from vectors
                    sim_fw = rt.compute_similarity(np_conf_fw_vector, candidate_fw_vector, metric)
                    sim_bw = rt.compute_similarity(np_conf_bw_vector, candidate_bw_vector, metric)
                    sim = min(sim_fw, sim_bw)
                    similarities[metric][candidate] = sim
        found_words_by_metric = {"sample_freqs": sample_freqs}
        for metric, sim_dict in similarities.items():
            if metric in ["l1", "js_div", "skew_div"]:
                sorted_words = sorted(sim_dict.items(), key=lambda x: x[1])[:25]
            else:
                sorted_words = sorted(sim_dict.items(), key=lambda x: x[1], reverse=True)[:25]
            found_words = []
            for found_tuple, similarity_score in sorted_words:
                correct = found_tuple in all_target_seqs
                tup_freq = distr.freq(found_tuple) if not correct else target_seqs_counter[found_tuple] 
                found_words.append({
                    "word": found_tuple,
                    "similarity": similarity_score,
                    "frequency": tup_freq,
                    "correct": correct
                })
            found_words_by_metric[sim_metric_code(metric)] = found_words
        found_words_by_sample_size[n] = found_words_by_metric
    return found_words_by_sample_size

def averaged_results(results_by_run):
    avg_dict = {}
    for sim_metric in sim_metrics:
        sample_size_dict = {}
        for sample_size in [5, 10, 25, 50, 100]:
            summed_uplift = 0
            for run_number in range(1, 101):
                total_sample_freq = sum(results_by_run[run_number][sample_size]["sample_freqs"])
                found_words = results_by_run[run_number][sample_size][sim_metric]
                good_found_freq = sum(x["frequency"] for x in found_words if x["correct"])
                bad_found_freq = sum(x["frequency"] for x in found_words if not x["correct"])
                net_good_found_freq = good_found_freq - bad_found_freq
                found_freq_uplift = net_good_found_freq / total_sample_freq
                summed_uplift += found_freq_uplift
            avg_uplift = summed_uplift / 100
            sample_size_dict[sample_size] = avg_uplift
        avg_dict[sim_metric] = sample_size_dict
    return avg_dict

def main(n, always_shuffle=False):
    found_words_by_run = {}
    run_number = 1
    while run_number <= n:
        try:
            found_words_by_run[run_number] = experiment_run(always_shuffle)
            print(f"Finished run number {run_number}")
            run_number += 1
        except Error as e:
            print(f"Run number {run_number} failed")
            print(e)
            return
    result_dict = {
        "results_by_run": found_words_by_run,
        "best_possible_words": most_frequent_target_seq_items,
        "worst_possible_words": most_frequent_non_target_seq_items
    }
    pickle.dump(result_dict, open(f"full_results_03_14.pkl", "wb"))
    return found_words_by_run, most_frequent_target_seq_items, most_frequent_non_target_seq_items
