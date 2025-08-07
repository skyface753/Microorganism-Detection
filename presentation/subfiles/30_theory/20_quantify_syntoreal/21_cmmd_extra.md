## CMMD

- CLIP model
  - 400 Millionen Bilder
  - Text-Bild Paare
- Distanz zwischen Verteilung der Embeddings
- Keine Annahme über die Verteilung

<p class="equation">\[
\text{dist}_{C}^2(P, Q) = \mathbb{E}_{x,x' \sim P}[k(x, x')] + \mathbb{E}_{y,y' \sim Q}[k(y, y')] - 2 \mathbb{E}_{x \sim P, y \sim Q}[k(x, y)]
\]</p>
<p class="equation">\[
k(x, y) = \exp\left(-\frac{\|x - y\|^2}{2\sigma^2}\right)
\]</p>

Note:

- $\mathbb{E}$ ist der Erwartungswert
- Sigma = Standardabweichung
- Aber sigma in cmmd nicht! Standardabweichung, sondern Hyperparameter
- Squared euclidean distance
- Kernel:
  - Kleine Abstände ||x - y|| führen zu Werten nahe 1 (ähnliche Punkte haben eine hohe Ähnlichkeit)
  - Große Abstände ||x - y|| führen zu Werten nahe 0 (unterschiedliche Punkte haben eine geringe Ähnlichkeit)
  - Exponential, damit entfernte Punkte vernachlässigt werden
