import matplotlib.pyplot as plt
import numpy as np

# Data
methods = ['Baseline', 'T1-AlphaBlending', 'T1-GaussianBlending',
           'T1-PoissonBlending', 'T1-PyramidBlending', 'T3-Multip']
ratios = ['100% Real', '30% Syn', '60% Syn', '90% Syn', '100% Syn']
data = {
    'Baseline': [0.81, np.nan, np.nan, np.nan, np.nan],
    'T1-AlphaBlending': [np.nan, 0.93, 0.95, 0.94, 0.94],
    'T1-GaussianBlending': [np.nan, 0.92, 0.95, 0.92, 0.93],
    'T1-PoissonBlending': [np.nan, 0.30, 0.43, 0.26, 0.29],
    'T1-PyramidBlending': [np.nan, 0.95, 0.97, 0.93, 0.94],
    'T3-Multip': [np.nan, 0.98, 0.98, 0.99, 0.97]
}

# Define blue color palette
bar_colors = ['#ffb000', '#fe6100', '#648fff', '#dc267f',
              '#785ef0']  # Different shades of blue

# Create the bar chart
x = np.arange(len(methods))  # the label locations
width = 0.15  # the width of the bars

fig, ax = plt.subplots(figsize=(12, 6))

# Plot each ratio
for i, ratio in enumerate(ratios):
    values = [data[method][i] if not np.isnan(
        data[method][i]) else np.nan for method in methods]
    ax.bar(x + i * width, values, width, label=ratio, color=bar_colors[i])
    # add the values on top of the bars
    for j, value in enumerate(values):
        if not np.isnan(value):
            ax.text(j + i * width, value + 0.01, f'{value:.2f}',
                    ha='center', va='bottom', fontsize=8)

# Add labels, title, and legend
ax.set_xlabel('Methods', fontsize=12)
ax.set_ylabel('Accuracy', fontsize=12)
ax.set_title('Synthetic Data Blending Methods Performance', fontsize=14)
ax.set_xticks(x + 2 * width)
ax.set_xticklabels(methods, rotation=45, ha='right')
ax.legend(title='Synthetic-to-Real Ratio', loc=(0.515, 0.6))  # over T2-Poisson
# ax.legend(title='Synthetic-to-Real Ratio', loc=(0.07, 0.65))
# start at 0.2 and end at 1.0
ax.set_ylim(0.2, 1.1)


# Display the chart
plt.tight_layout()
plt.savefig('gfx/results/bar_plot.png', transparent=False)
plt.show()
