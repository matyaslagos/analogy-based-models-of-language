import pickle
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patheffects as pe

# Set Times New Roman font
mpl.rcParams['font.family'] = 'Times New Roman'

# Load the data
with open('lassy_results.pkl', 'rb') as f:
    data = pickle.load(f)

# Remove "Confusion probability" from the data
to_be_removed = ["conf", "min_conf", "l1", "jacc", "cosine"]
for name in to_be_removed:
    if name in data:
        del data[name]

# Define line styles
line_styles = ["-"]

# Calculate average performance for each function to assign colors
performance_scores = {}
for name, values in data.items():
    avg_performance = sum(values.values()) / len(values) * 100
    performance_scores[name] = avg_performance

# Sort functions by performance
sorted_functions = sorted(performance_scores.items(), key=lambda x: x[1], reverse=True)

# Assign colors from warm (best) to cool (worst) - desaturated versions
# Red -> Orange -> Yellow -> Green -> Blue
color_gradient = ["#252521"]

# Create color mapping
function_colors = {}
for idx, (name, score) in enumerate(sorted_functions):
    function_colors[name] = color_gradient[idx]

# Create the plot
fig, ax = plt.subplots(figsize=(7, 6))

# X-axis values (actual values)
x_labels = [5, 10, 25, 50, 100]
# X-axis positions (evenly spaced)
x_positions = list(range(len(x_labels)))

# Store line information for legend
lines = []
labels = []

# Plot each similarity function
for idx, (name, values) in enumerate(data.items()):
    # Convert to percentages and extract y values in order
    y_values = [values[x] * 100 for x in x_labels]

    # Plot with different line styles and colors based on performance
    line = ax.plot(
        x_positions,
        y_values,
        linestyle=line_styles[idx % len(line_styles)],
        color=function_colors[name],
        linewidth=3,
        label=name
    )

    lines.append(line[0])
    labels.append(name)

# Sort by performance (average) to order the legend
performance_order = sorted(performance_scores.items(), key=lambda x: x[1], reverse=True)
sorted_labels = [name for name, _ in performance_order]
sorted_lines = [lines[labels.index(name)] for name in sorted_labels]

# Create legend with line samples on the right side
"""
legend = ax.legend(sorted_lines, sorted_labels,
                   loc='center left',
                   bbox_to_anchor=(1, 0.5),
                   frameon=False,
                   fontsize=10,
                   handlelength=7,
                   handleheight=2)
"""

# Set y-axis
ax.set_ylim(0, 100)
ax.set_yticks([0, 20, 40, 60, 80, 100])
ax.set_yticklabels([])  # Remove y-axis labels

# Set x-axis with even spacing
ax.set_xticks(x_positions)
ax.set_xticklabels([])  # Remove x-axis labels

# Add horizontal grid lines (thicker to match borders, solid light gray)
ax.grid(axis='y', which='major', linestyle='-', linewidth=2, color='lightgray')
ax.set_axisbelow(True)

# Remove right border and make other borders solid light gray and thicker
#ax.spines['right'].set_visible(False)
ax.spines['top'].set_color('gray')
ax.spines['top'].set_linewidth(2)
ax.spines['left'].set_color('gray')
ax.spines['left'].set_linewidth(2)
ax.spines['bottom'].set_color('gray')
ax.spines['bottom'].set_linewidth(2)
ax.spines['right'].set_color('gray')
ax.spines['right'].set_linewidth(2)

# Make tick marks light gray and thicker to match axis lines
ax.tick_params(axis='both', colors='gray', width=2, length=6)

# Adjust layout to prevent text cutoff
plt.tight_layout()
# Add extra space on the right for labels
#plt.subplots_adjust(right=0.75)

# Save the figure
plt.savefig('lassy_results_plot.png', dpi=300, bbox_inches='tight')
plt.savefig('lassy_results_plot.pdf', bbox_inches='tight')

print("Plot saved as 'lassy_results_plot.png' and 'lassy_results_plot.pdf'")
