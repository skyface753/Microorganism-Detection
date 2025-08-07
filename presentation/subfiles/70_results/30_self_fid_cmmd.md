## Results

#### Vergleich der Ergebnisse

<div class="stretch">
    <canvas data-chart="line">
    ,T2.1, T2.2, T2.3, T2.4, T3
    Self-Trained, 0.06, 0.07, 0.68, 0.05, 0.02
    FID, 0.51, 0.49, 0.54, 0.44, 0.45
    CMMD, 0.433, 0.384, 0.506, 0.389, 0.330
    </canvas>
</div>
<!-- small caption -->
<div style="font-size: 14px; text-align: center; margin-bottom: 3vh;">
Anmerkung: FID ist durch Min-Max-Normalisierung auf den Bereich [0,1] skaliert. Der Wert des Self-Trained Models ist invertiert. Dadurch wurden die Werte der drei Metriken auf den gleichen Bereich skaliert. Für die Tests wurde jeweils der Durchschnittswert über die verschiedenen Syn-to-Real Ratios berechnet.
</div>
