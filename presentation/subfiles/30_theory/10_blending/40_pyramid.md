## Blending

#### Pyramid Blending

<div class="left-aligned-div">
    <ul>
      <li>Erzeugt Laplace und Gauss Pyramide</li>
      <li>Rekonstruiert Bild aus den Pyramiden</li>
    </ul>
    <p style="font-size: 22px; margin-top: 50px">
    $$L_{\text{blend}}^k = M^k \cdot L_{\text{image1}}^k + (1 - M^k)
    \cdot L_{\text{image2}}^k$$
    </p>
</div>
<div class="right-aligned-div">
    <img src="assets/foundations/pyramid-blending.png" style="width: 100%" data-source="https://ieeexplore.ieee.org/document/9206855?figureId=fig1#fig1" data-text="Pyramid Blending"/>
</div>

Note:

- Laplace: Differenz zwischen Original und geglättetem Bild
  (high-frequency details) => Kanten behalten
- Gauss: Glättet Bild (low-frequency details) => Kanten weg
- Laplace Pyramid = Differenz zwischen Gauss Pyramid und nächst
  höheres Level (upsampeled) Gauss Pyramid

1. Berechnen der Gauss Pyramide für Maske und Komplement
2. Laplacian Pyramide durch Differenz der Gauss Pyramide
   berechnen => Kanten und Texturen behalten
3. Laplacian Komponenten der beiden Bilder mit den Gewichten der Maske kombinieren
