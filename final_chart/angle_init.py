import matplotlib.pyplot as plt

# QAOA variants and their Normalised Range values
qaoa_variants = ['sa-QAOA', 'ma-QAOA', 'am-QAOA', 'ka-QAOA']
#normalised_range_values = [0.385345686, 0.398284765, 0.398284765, 0.161943772] # classical optimiser p=2
#normalised_range_values = [0.622090751, 0.618268159, 0.476258977, 0.123266235] # classical optimiser p=3
#normalised_range_values = [0.374622598, 0.427182067, 0.285467104, 0.345987064] # angle initialisation p=1
normalised_range_values = [0.29591207, 0.446341118, 0.355007524, 0.164302214] # angle initialisation p=3

# X positions for plotting
x_positions = range(len(qaoa_variants))

# Marker styles and colours matching the legend image
markers = {
    'sa-QAOA': {'marker': 'D', 'color': 'blue',    'label': 'Single angle'},     # Diamond
    'ma-QAOA': {'marker': 's', 'color': 'red',     'label': 'Multi-angle'},      # Square
    'am-QAOA': {'marker': '^', 'color': 'green',   'label': 'Automorphic angle'},# Triangle
    'ka-QAOA': {'marker': 'o', 'color': 'orange',  'label': 'k-angle'}           # Circle
}

plt.figure(figsize=(8, 6))

# Plot each point with the corresponding marker and colour
for i, variant in enumerate(qaoa_variants):
    plt.scatter(
        x=i,
        y=normalised_range_values[i],
        s=200,  # Marker size ~10pt
        marker=markers[variant]['marker'],
        color=markers[variant]['color'],
        label=markers[variant]['label']
    )

# Ensure y-axis starts at zero
plt.ylim(0, 0.7)

# Avoid duplicate labels in legend
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
#plt.legend(by_label.values(), by_label.keys(), title="Legend", fontsize='medium')

# Axis settings
plt.xticks(ticks=x_positions, labels=qaoa_variants)
plt.xlabel('QAOA Variant')
plt.ylabel('Normalised Range')
# plt.title('Normalised Range vs QAOA Variant')
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()
