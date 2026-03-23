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
    return sim_metric_codemap[sim_metric]

np_sample_sizes = [5, 10, 25, 50, 100]

raw_corpus = pickle.load(open(f"extracted_sequences/all_sequences.pkl", "rb"))
corpus = [["<#"] + sentence + ["#>"] for sentence in raw_corpus]
distr = rt.RadixTrie()
distr.setup(corpus)

# Get list of pronouns and list of proper nouns
pronoun_data = pickle.load(open(f"extracted_sequences/pronoun_sequences.pkl", "rb"))
pronouns = set(tuple(x) for x in pronoun_data)

noun_phrase_data = pickle.load(open(f"extracted_sequences/np_sequences.pkl", "rb"))
all_noun_phrases = set(tuple(x) for x in noun_phrase_data)

def experiment_run(always_shuffle=False):

    # Get sample of noun phrases
    noun_phrases = sorted(all_noun_phrases.copy())
    if not always_shuffle:
        shuffle(noun_phrases)
        noun_phrase_samples = {n: noun_phrases[:n] for n in np_sample_sizes}
    else:
        noun_phrase_samples = {n: sample(noun_phrases, n) for n in np_sample_sizes}
    found_words_by_sample_size = {}
    # Test for incresing sample sizes
    for n in np_sample_sizes:
        noun_phrases_sample = noun_phrase_samples[n] # list of tuples of strings
        sample_freq = sum(distr.freq(x) for x in noun_phrases_sample)
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
        found_words_by_metric = {"sample_freq": sample_freq}
        for metric, sim_dict in similarities.items():
            if metric in ["l1", "js_div", "skew_div"]:
                sorted_words = sorted(sim_dict.items(), key=lambda x: x[1])[:20]
            else:
                sorted_words = sorted(sim_dict.items(), key=lambda x: x[1], reverse=True)[:20]
            found_pronouns = {}
            wrong_words = {}
            for found_tuple, similarity_score in sorted_words:
                tup_freq = distr.freq(found_tuple)
                if found_tuple in pronouns | all_noun_phrases:
                    found_pronouns[found_tuple] = (similarity_score, tup_freq)
                else:
                    wrong_words[found_tuple] = (similarity_score, tup_freq)
            found_words_by_metric[sim_metric_code(metric)] = {"good": found_pronouns, "bad": wrong_words}
        found_words_by_sample_size[n] = found_words_by_metric
    return found_words_by_sample_size

def averaged_results(results):
    summed_results_dict = defaultdict(lambda: defaultdict(float))
    for run_number, results_by_sample_size in results.items():
        for sample_size, results_by_sim_metric in results_by_sample_size.items():
            for sim_metric in ["s1", "s2", "s3", "s4", "s5"]:
                found_words = results_by_sim_metric[sim_metric]
                sample_freq = results_by_sim_metric["sample_freq"]
                good_words, bad_words = found_words["good"], found_words["bad"]
                good_mass = sum(x[1] for x in good_words.values())
                bad_mass = sum(x[1] for x in bad_words.values())
                net_good_mass = good_mass - bad_mass
                net_uplift = net_good_mass / sample_freq
                summed_results_dict[sim_metric][sample_size] += net_uplift
    averaged_results_dict = {sim_metric:
                             {sample_size:
                              summed_results_dict[sim_metric][sample_size] / len(results)
                              for sample_size in np_sample_sizes}
                             for sim_metric in ["s1", "s2", "s3", "s4", "s5"]}
    return averaged_results_dict

def main(n, always_shuffle=False):
    found_words_by_run = {}
    run_number = 1
    while run_number <= n:
        if True:
            found_words_by_run[run_number] = experiment_run(always_shuffle)
            print(f"Finished run number {run_number}")
            run_number += 1
    averaged_results_dict = {}
    pickle.dump(found_words_by_run, open(f"japanese_full_results_02_20.pkl", "wb"))
    return found_words_by_run
