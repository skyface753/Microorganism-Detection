## FID

- Inception V3 Netzwerk
- ImageNet dataset
  - 1000 classes
  - 1.2 million images
- Assumption: Gaussian distributions

<p class="equation">\[
\text{dist}_{\text{F}}^2(P, Q) = \|\mu_P - \mu_Q\|_2^2 + \text{Tr}(\Sigma_P + \Sigma_Q - 2 (\Sigma_P \Sigma_Q)^{1/2})
\]</p>

Note:

- $\mu$ ist der Mittelwert
- $\Sigma$ ist die Kovarianzmatrix
- P und Q sind die Verteilungen
- Tr ist die Spur einer Matrix

Alternativen:

- Inception Score: Keine real-world Daten (nur Gen Verteilung)
- Global-Local image perceptual score
