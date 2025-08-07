## Blending

#### Poisson Blending

<div class="left-aligned-div">
    <ul>
        <li>Gradienten optimieren</li>
        <li>Laplace Operator</li>
        <li>Minimierung der Gradientendifferenzen</li>
    </ul>
</div>
<div class="right-aligned-div">
    <img src="assets/foundations/poisson.jpg" style="width: 100%" data-text="Poisson Blending" data-source="https://www.sciencedirect.com/science/article/pii/S0097849316300176"/>
</div>

Note:

- source patch g, assozierter vektor v, support omega, Ziel f\*,
  delta omega = boundary condition
- passt die Pixelintensitäten in der überlappenden Region an den umgebenden Hintergrund an
- Laplace Operator, um harmonische Funktion 𝑓 zu finden, die die Farbewerte des neuen Bereichs and die Umgebung angleicht.
- Ziel ist es, eine Funktion f zu finden, die die Differenzen der Gradienten zwischen Quell- und Zielbild minimiert
- (Der Laplace-Operator ordnet einem zweimal differenzierbaren Skalarfeld f die Divergenz seines Gradienten zu)

Laplace-Operator = Summe der zweiten Ableitungen
