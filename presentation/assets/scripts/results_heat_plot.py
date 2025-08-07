import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches

# Data for heatmap
tests = ['$T1_{baseline}$', '$T2.1_{alpha}$', '$T2.2_{gauss}$',
         '$T2.3_{poisson}$', '$T2.4_{pyramid}$', '$T3_{multip}$']
ratios = ["Baseline (0%)", "30%", "60%", "90%", "100%"]

# Fill mAP50 values (baseline doesn't have ratios, so we'll only use one row for it)
data = [
    [0.81, np.nan, np.nan, np.nan, np.nan],  # Baseline
    [np.nan, 0.93, 0.95, 0.94, 0.94],      # T1
    [np.nan, 0.92, 0.95, 0.92, 0.93],      # T2.1
    [np.nan, 0.30, 0.43, 0.26, 0.29],      # T2.2
    [np.nan, 0.95, 0.97, 0.93, 0.94],       # T2.3
    [np.nan, 0.98, 0.98, 0.99, 0.97],       # T3
]

# Convert data to numpy array for easier manipulation
data_array = np.array(data)

# Create mask for NaN values
nan_mask = np.isnan(data_array)

# Visualization function
sns.set_theme(style="ticks", palette=None, font_scale=1.2)


def plot_heatmap(cmap):
    plt.figure(figsize=(10, 6))

    # Create heatmap with a custom annotation function
    ax = sns.heatmap(data_array,
                     annot=True,
                     fmt=".2f",
                     vmin=0.25,
                     vmax=1,
                     cmap=cmap,
                     cbar_kws={'label': 'mAP@50'},
                     xticklabels=ratios,
                     yticklabels=tests,
                     linewidths=0.2,
                     linecolor="gray",
                     center=0.81,
                     mask=nan_mask)  # This will hide NaN cells

    # Custom annotation for NaN values (crossed out)
    for i in range(data_array.shape[0]):
        for j in range(data_array.shape[1]):
            if nan_mask[i, j]:
                continue  # comment to show NaN values
                plt.gca().add_patch(patches.Rectangle((j, i), 1, 1, fill=False, edgecolor='none'))
                plt.text(j + 0.5, i + 0.5, '✖',
                         ha='center', va='center',
                         color='red', fontsize=10,
                         rotation=45)

    # Customize plot
    plt.title(f"mAP@50 Heatmap for Tests and Synthetic-to-Real Ratios")
    plt.xlabel("Synthetic-to-Real Ratio")
    plt.ylabel("Tests")
    plt.tight_layout()

    # Save the plot
    plt.savefig(f"gfx/results/heat_plot_{cmap}.png")
    plt.close()  # Close the figure to free up memory


# Generate heatmaps
cmaps = ["YlGnBu"]
for cmap in cmaps:
    plot_heatmap(cmap)
