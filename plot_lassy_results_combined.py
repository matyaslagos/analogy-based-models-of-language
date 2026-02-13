import pickle
import matplotlib.pyplot as plt
import matplotlib as mpl

# Set Times New Roman font
mpl.rcParams['font.family'] = 'Verdana'

# Load both datasets
with open('lassy_results_correct pct_02_09.pkl', 'rb') as f:
    correct_data = pickle.load(f)

with open('lassy_results_pronoun pct_02_09.pkl', 'rb') as f:
    pronoun_data = pickle.load(f)

# Remove unwanted metrics if needed
to_be_removed = ["conf", "js_div", "l1", "jacc"]
for name in to_be_removed:
    if name in correct_data:
        del correct_data[name]
    if name in pronoun_data:
        del pronoun_data[name]

# Get all similarity metrics (should be same in both datasets)
metrics = list(correct_data.keys())

# Define line styles for the two datasets
line_styles_datasets = {
    'correct': '-',      # solid line for correct
    'pronoun': '--'      # dashed line for pronoun
}

# Create color mapping for each metric
# You can customize these colors based on your preference
color_palette = ["#466389", "#b5504b", "#6aa170"]
metric_colors = {}
for idx, metric in enumerate(metrics):
    metric_colors[metric] = color_palette[idx % len(color_palette)]

# Create the plot
fig, ax = plt.subplots(figsize=(7, 6))

# X-axis values (actual values)
x_labels = [5, 10, 25, 50, 100]
# X-axis positions (evenly spaced)
x_positions = list(range(len(x_labels)))

# Store line information for legend
lines = []
labels = []

# Plot each similarity metric - both correct and pronoun percentages
for metric in metrics:
    # Plot correct percentage
    if metric in correct_data:
        y_values_correct = [correct_data[metric][x] * 100 for x in x_labels]
        line_correct = ax.plot(
            x_positions,
            y_values_correct,
            linestyle=line_styles_datasets['correct'],
            color=metric_colors[metric],
            linewidth=2.5,
            label=f'{metric} (correct)'
        )
        lines.append(line_correct[0])
        labels.append(f'{metric} (correct)')

    # Plot pronoun percentage
    if metric in pronoun_data:
        y_values_pronoun = [pronoun_data[metric][x] * 100 for x in x_labels]
        line_pronoun = ax.plot(
            x_positions,
            y_values_pronoun,
            linestyle=line_styles_datasets['pronoun'],
            color=metric_colors[metric],
            linewidth=2.5,
            label=f'{metric} (pronoun)'
        )
        lines.append(line_pronoun[0])
        labels.append(f'{metric} (pronoun)')

# Add legend
legend = ax.legend(lines, labels,
                   loc='best',
                   frameon=True,
                   fontsize=9,
                   handlelength=3)

# Set y-axis
ax.set_ylim(0, 100)
ax.set_yticks([0, 20, 40, 60, 80, 100])
#ax.set_yticklabels([])

# Set x-axis with even spacing
ax.set_xticks(x_positions)
ax.set_xticklabels([5, 10, 25, 50, 100])

# Add horizontal grid lines
ax.grid(axis='y', which='major', linestyle='-', linewidth=2, color='lightgray', alpha=0.7)
ax.set_axisbelow(True)

# Style the borders
ax.spines['top'].set_color('gray')
ax.spines['top'].set_linewidth(2)
ax.spines['left'].set_color('gray')
ax.spines['left'].set_linewidth(2)
ax.spines['bottom'].set_color('gray')
ax.spines['bottom'].set_linewidth(2)
ax.spines['right'].set_color('gray')
ax.spines['right'].set_linewidth(2)

# Make tick marks
ax.tick_params(axis='both', colors='gray', width=2, length=6)

# Adjust layout
plt.tight_layout()

# Save the figure
plt.savefig('lassy_results_combined_plot.png', dpi=300, bbox_inches='tight')
plt.savefig('lassy_results_combined_plot.pdf', bbox_inches='tight')

print("Plot saved as 'lassy_results_combined_plot.png' and 'lassy_results_combined_plot.pdf'")
print(f"Plotted metrics: {metrics}")
