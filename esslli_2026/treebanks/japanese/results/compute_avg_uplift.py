import os
import math
import pickle
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl-cache")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/xdg-cache")
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
Path(os.environ["XDG_CACHE_HOME"]).mkdir(parents=True, exist_ok=True)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


RESULTS_PATH = Path("results.pkl")
PLOT_DIR = Path("plots")
PLOT_FUNCTIONS = ("skew_div", "cosine")
PLOT_COLORS = {
    "skew_div": "#4C78A8",
    "cosine": "#B35C44",
}
PLOT_LABELS = {
    "skew_div": "Skew divergence",
    "cosine": "Cosine similarity",
}

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Computer Modern Roman", "CMU Serif", "DejaVu Serif"],
        "mathtext.fontset": "cm",
    }
)


with RESULTS_PATH.open("rb") as f:
    result_dict = pickle.load(f)

results_by_run = result_dict["results_by_run"]


def compute_uplifts():
    relative_net_uplifts = defaultdict(lambda: defaultdict(list))

    for results_by_sample_freq in results_by_run.values():
        for sample_size, results_by_sim_func in results_by_sample_freq.items():
            source_freq_mass = sum(
                math.log(freq + 1, 2) for freq in results_by_sim_func["sample_freqs"]
            )
            for sim_func in results_by_sim_func.keys() - {"sample_freqs"}:
                found_items = results_by_sim_func[sim_func]
                net_uplift = sum(
                    math.log(item["frequency"], 2) * (-1, 1)[item["correct"]]
                    for item in found_items
                )
                relative_net_uplift = net_uplift / source_freq_mass
                relative_net_uplifts[sim_func][sample_size].append(relative_net_uplift)

    return relative_net_uplifts


def compute_uplift_summary(uplifts):
    uplift_summary = {}

    for sim_func, uplifts_by_sample_size in uplifts.items():
        summary_by_sample_size = {}
        for sample_size, uplift_values in sorted(uplifts_by_sample_size.items()):
            avg_uplift = mean(uplift_values)
            std_uplift = stdev(uplift_values) if len(uplift_values) > 1 else 0.0
            summary_by_sample_size[sample_size] = {
                "avg": avg_uplift,
                "std": std_uplift,
                "n": len(uplift_values),
            }
        uplift_summary[sim_func] = summary_by_sample_size

    return uplift_summary


def plot_uplift_summary(uplift_summary, sim_funcs=PLOT_FUNCTIONS):
    PLOT_DIR.mkdir(exist_ok=True)

    plt.figure(figsize=(8, 5))
    x_labels = sorted({size for func in sim_funcs if func in uplift_summary for size in uplift_summary[func]})
    x_positions = list(range(len(x_labels)))

    for sim_func in sim_funcs:
        if sim_func not in uplift_summary:
            continue

        sample_sizes = sorted(uplift_summary[sim_func])
        averages = [uplift_summary[sim_func][size]["avg"] for size in sample_sizes]
        std_devs = [uplift_summary[sim_func][size]["std"] for size in sample_sizes]
        positions = [x_labels.index(size) for size in sample_sizes]
        color = PLOT_COLORS.get(sim_func)

        plt.errorbar(
            positions,
            averages,
            yerr=std_devs,
            marker="o",
            linewidth=1.8,
            color=color,
            ecolor=color,
            elinewidth=0.9,
            capsize=2.5,
            capthick=0.9,
            alpha=0.95,
            label=PLOT_LABELS.get(sim_func, sim_func),
        )

    plt.xlabel("Sample size")
    plt.ylabel("Average relative net uplift (100 runs)")
    plt.title("Average relative net uplift by sample size (on Japanese data)")
    plt.xticks(x_positions, x_labels)
    plt.legend()
    plt.tight_layout()
    output_path = PLOT_DIR / "avg_uplift_skew_div_cosine.pdf"
    plt.savefig(output_path, dpi=200)
    plt.close()
    return output_path


def main():
    uplift_summary = compute_uplift_summary(compute_uplifts())
    plot_path = plot_uplift_summary(uplift_summary)

    for sim_func in PLOT_FUNCTIONS:
        if sim_func not in uplift_summary:
            continue
        print(sim_func)
        for sample_size, stats in sorted(uplift_summary[sim_func].items()):
            print(
                f"  sample_size={sample_size:>3} "
                f"avg={stats['avg']:.6f} std={stats['std']:.6f} n={stats['n']}"
            )

    print(f"plot={plot_path}")
    return uplift_summary


if __name__ == "__main__":
    main()
