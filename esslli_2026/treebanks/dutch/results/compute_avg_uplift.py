import pickle
from collections import defaultdict

result_dict = pickle.load(open("results.pkl", "rb"))
results_by_run = result_dict["results_by_run"]
most_freq_correct = result_dict["best_possible_words"]
most_freq_incorrect = result_dict["worst_possible_words"]

def compute_uplifts():
    relative_net_uplifts = defaultdict(lambda: defaultdict(list))

    for results_by_sample_freq in results_by_run.values():
        for sample_size, results_by_sim_func in results_by_sample_freq.items():
            source_freq_mass = sum(results_by_sim_func["sample_freqs"])
            for sim_func in results_by_sim_func.keys() - {"sample_freqs"}:
                found_items = results_by_sim_func[sim_func]
                net_uplift = sum(x["frequency"] * (-1, 1)[x["correct"]] for x in found_items)
                relative_net_uplift = net_uplift / source_freq_mass
                relative_net_uplifts[sim_func][sample_size].append(relative_net_uplift)
    return relative_net_uplifts

def compute_avg_uplifts(uplifts):
    avg_uplifts = {}
    for sim_func, uplifts_by_sample_freq in uplifts.items():
        avg_uplifts_by_sample_freq = {}
        for sample_freq, uplifts in uplifts_by_sample_freq.items():
            avg_uplift = sum(uplifts) / 100
            avg_uplifts_by_sample_freq[sample_freq] = avg_uplift
        avg_uplifts[sim_func] = avg_uplifts_by_sample_freq
    return avg_uplifts

def main():
    return compute_avg_uplifts(compute_uplifts())
