import matplotlib.pyplot as plt
import numpy as np

# Data
baseline = 0.81
test2_1 = {"min": 0.93, "max": 0.95, "mean": 0.94}
test2_2 = {"min": 0.92, "max": 0.95, "mean": 0.925}
test2_3 = {"min": 0.26, "max": 0.43, "mean": 0.345}
test2_4 = {"min": 0.93, "max": 0.97, "mean": 0.95}
test3 = {"min": 0.97, "max": 0.99, "mean": 0.98}

# Plot settings
tests = ['$T1_{baseline}$', '$T2.1_{alpha}$', '$T2.2_{gauss}$',
         '$T2.3_{poisson}$', '$T2.4_{pyramid}$', '$T3_{multip}$']
means = [baseline, test2_1["mean"], test2_2["mean"],
         test2_3["mean"], test2_4["mean"], test3["mean"]]
mins = [baseline, test2_1["min"], test2_2["min"],
        test2_3["min"], test2_4["min"], test3["min"]]
maxs = [baseline, test2_1["max"], test2_2["max"],
        test2_3["max"], test2_4["max"], test3["max"]]

# Initialize figure
fig, ax = plt.subplots(figsize=(8, 5))

# Plot baseline as a single point
ax.scatter(0, baseline, color="black", label="Baseline", zorder=1)

# Plot candlesticks for Test 1 and Test 2
for i, (mean, min_val, max_val) in enumerate(zip(means[1:], mins[1:], maxs[1:]), start=1):
    ax.plot([i, i], [min_val, max_val], color="blue", zorder=2)  # Whisker line
    ax.scatter(i, mean, color="red", zorder=3)  # Mean point

# Customize plot
ax.set_xticks(range(len(tests)))
ax.set_xticklabels(tests)
ax.set_ylim(0.2, 1.0)
ax.set_ylabel("mAP@50")
ax.set_title("Performance Evaluation with Baseline and Tests")
ax.legend(["Baseline", "Range (Min-Max)", "Mean"], loc="lower right")

# Show grid for better readability
ax.grid(axis="y", linestyle="--", alpha=0.7)

# Show plot
plt.tight_layout()
# Save the plot
plt.savefig("gfx/results/box_plot.png")
plt.show()
