import matplotlib.pyplot as plt
import numpy as np

# Data
tests = ['$T1_{baseline}$', '$T2.1_{alpha}$', '$T2.2_{gauss}$',
         '$T2.3_{poisson}$', '$T2.4_{pyramid}$', '$T3_{multip}$']
cmmd = [2.635, 0.433, 0.384, 0.506, 0.389, 0.330]
fid = [408.434, 210.000, 198.130, 221.460, 178.489, 185.293]

x = np.arange(len(tests))  # The label locations
width = 0.4  # The width of the bars

# Create a figure and axis
fig, ax1 = plt.subplots(figsize=(10, 6))

# cmmd_color = 'skyblue'
fid_color = '#fd8d3c'
cmmd_color = '#4169E1'

# Plot CMMD on the primary y-axis
bars1 = ax1.bar(x - width/2, cmmd, width, label='CMMD', color=cmmd_color)
ax1.set_ylabel('CMMD', fontsize=12, color=cmmd_color)
ax1.tick_params(axis='y', labelcolor=cmmd_color)

# Create a secondary y-axis for FID
ax2 = ax1.twinx()
bars2 = ax2.bar(x + width/2, fid, width, label='FID', color=fid_color)
ax2.set_ylabel('FID', fontsize=12, color=fid_color)
ax2.tick_params(axis='y', labelcolor=fid_color)

# Add x-axis labels, title, and legend
ax1.set_xticks(x)
ax1.set_xticklabels(tests)
ax1.set_xlabel('Tests', fontsize=12)
plt.title('Comparison of CMMD and FID Across Tests', fontsize=14)

# Add value labels on both sets of bars
for bars, axis in [(bars1, ax1), (bars2, ax2)]:
    for bar in bars:
        height = bar.get_height()
        axis.annotate(f'{height:.3f}',
                      xy=(bar.get_x() + bar.get_width() / 2, height),
                      xytext=(0, 3),  # Offset text slightly above the bar
                      textcoords="offset points",
                      ha='center', va='bottom', fontsize=9)

# Improve layout
fig.tight_layout()
plt.savefig('gfx/results/fid_cmmd_plot.png', transparent=False)
plt.savefig('gfx/results/fid_cmmd_plot_transparent.png', transparent=True)
plt.show()
