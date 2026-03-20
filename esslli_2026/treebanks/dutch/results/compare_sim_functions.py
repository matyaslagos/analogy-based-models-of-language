import pickle
from collections import defaultdict # for easier handling of nested dicts
import scipy.stats # for statistical tests
import matplotlib.pyplot as plt # for plotting
import os # for directory creation

# Load ndcg_store
with open("ndcg_store.pkl", "rb") as f:
    ndcg_store = pickle.load(f)

# Access values as follows
# print(ndcg_store[32][50]["s1"])

# Get sample sizes
sample_sizes = sorted(ndcg_store[1].keys())
print("Sample sizes used:", sample_sizes)

# Create plots directory
os.makedirs('plots', exist_ok=True)

# For each sample size, compute averages per function and find the best
best_functions = {}  # {sample_size: (best_func, avg_score)}

for fixed_size in sample_sizes:
    # Compute average NDCG per function across all runs (for this size)
    averages_per_function = defaultdict(list)
    for run in ndcg_store:
        if fixed_size in ndcg_store[run]:
            for func in ndcg_store[run][fixed_size]:
                averages_per_function[func].append(ndcg_store[run][fixed_size][func])
    
    # Calculate averages and find the best function
    func_averages = {}
    for func, values in averages_per_function.items():
        avg = sum(values) / len(values) if values else 0
        func_averages[func] = avg
    
    if func_averages:
        best_func = max(func_averages, key=func_averages.get)
        best_score = func_averages[best_func]
        best_functions[fixed_size] = (best_func, best_score)
        print(f"Sample size {fixed_size}: Best function is {best_func} with avg NDCG {best_score:.4f}")
    else:
        print(f"Sample size {fixed_size}: No data")

    # Statistical tests to compare each function against the best one for each sample size

    # For the current sample size, get s* and its scores
    best_s, _ = best_functions[fixed_size]
    best_scores = {run: ndcg_store[run][fixed_size][best_s] for run in ndcg_store if fixed_size in ndcg_store[run]}

    # For each other function s, compute diffs
    for s in ndcg_store[1][fixed_size].keys():  # All funcs (assuming same across runs)
        if s == best_s:
            continue  # Skip s*
        
        # Compute diff_r for each run: score_s* - score_s
        diffs = []
        for run in ndcg_store:
            if fixed_size in ndcg_store[run] and s in ndcg_store[run][fixed_size]:
                diff = best_scores[run] - ndcg_store[run][fixed_size][s]
                diffs.append(diff)
        
        # Now diffs is a list of differences for this s and n
        print(f"Sample size {fixed_size}, Function {s}: {len(diffs)} diffs computed")
        
        # Plot diffs to check assumptions
        plt.figure(figsize=(8, 4))
        plt.hist(diffs, bins=20, alpha=0.7, edgecolor='black')
        plt.axvline(0, color='red', linestyle='--', label='Zero (no difference)')
        plt.title(f'Distribution of diffs for {s} vs {best_s} at size {fixed_size}')
        plt.xlabel('Difference (score_s* - score_s)')
        plt.ylabel('Frequency')
        plt.legend()
        plt.savefig(f'plots/diffs_{fixed_size}_{s}.png')
        plt.close()  # Close to free memory
        
        # t-Test: Test if mean of diffs != 0
        if len(diffs) > 1:  # Need at least 2 samples
            t_stat, p_value = scipy.stats.ttest_1samp(diffs, 0)
            print(f"  t-Test: t={t_stat:.3f}, p={p_value:.3f} ({'Significant' if p_value < 0.05 else 'Not significant'})")
        else:
            print("  t-Test: Not enough data")
        
        # Wilcoxon signed-rank test: Test if median of diffs != 0
        if len(diffs) > 1:
            stat, p_value = scipy.stats.wilcoxon(diffs)
            print(f"  Wilcoxon: stat={stat:.3f}, p={p_value:.3f} ({'Significant' if p_value < 0.05 else 'Not significant'})")
        else:
            print("  Wilcoxon: Not enough data")
    

# Print all best functions
print("\nSummary of best functions:")
for size, (func, score) in best_functions.items():
    print(f"  Size {size}: {func} ({score:.4f})")

################
