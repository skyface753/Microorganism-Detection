import matplotlib.pyplot as plt
import numpy as np

# Tests inklusive Baseline
tests = ['Vorher', 'Version 1', 'Version 2']

# Beste mAP50-Werte pro Test (Baseline bleibt unverändert)
# Beste Werte für T2.1, T2.3, T2.4, T3
best_values = [0.81, 0.95, 0.99]

# Baseline-Wert für Vergleich
baseline = 0.0

# Verbesserungen berechnen (Baseline bleibt bei 0)
improvement = [val - baseline for val in best_values]

# Balkendiagramm erstellen
fig, ax = plt.subplots(figsize=(8, 5))
x = np.arange(len(tests))  # x-Positionen für Balken
# farbverlauf YiGnBu
bar_colors = plt.cm.YlGnBu(np.linspace(0.4, 0.8, len(tests)))

# Balken plotten
ax.bar(x, improvement, color=bar_colors)

# Baseline als gestrichelte Linie
ax.axhline(0, color='black', linestyle='--', linewidth=1)

# Achsenbeschriftung & Titel
ax.set_xticks(x)
ax.set_xticklabels(tests)
ax.set_xlabel("Test Szenario")
ax.set_ylabel("mAP@50")
ax.set_title("Bärtierchen-Erkennung")

# Layout anpassen & speichern
plt.tight_layout()
plt.savefig("assets/results/bar_chart_best_improvement_v1.png")
plt.show()
