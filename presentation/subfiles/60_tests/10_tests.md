## Tests

<div style="display: flex; flex-direction: column; margin-bottom: 2vh;">
<div class="container">
    <div class="column blue">
    <div class="header blue">T1 - Baseline</div>
    <ul>
        <li>Clean + Muddy</li>
        <li>100% echte Daten</li>
    </ul>
    </div>
    <div class="column purple">
    <div class="header purple">T2 - Einzeln</div>
    <ul>
        <li>Einzelne Blending Methoden</li>
        <li>Clean + Syn</li>
        <li>Verschiedene Syn-to-Real Ratios</li>
    </ul>
    </div>
    <div class="column orange">
    <div class="header orange">T3 - Multiple</div>
    <ul>
        <li>Alpha, Gauss und Pyramid</li>
        <li>Jedes Bild mit allen Methoden</li>
        <li>Clean + Syn</li>
        <li>Verschiedene Syn-to-Real Ratios</li>
    </ul>
    </div>
</div>
<div class="bottom-container">
    <p>Test-Daten: Echte Daten aus Muddy Environment</p>
</div>
</div>
<aside class="notes">
<ul>
    <li>Muddy Data: 280+356 = 636</li>
    <li>356 Background</li>
    <li>223+57=280 => 223 Test, 57 Foreground Obj</li>
    <li>Clean: 3356</li>
</ul>
<ul>
    <li>T1: 3356 Clean + 57 Muddy</li>
    <li>T2: 3356 Clean + Syn Bilder (57 Obj)</li>
    <li>T3: 3356 Clean + Syn Bilder (57 Obj)</li>
    <li>
    Bei T2+T3: Jeweils max 3356 Bilder insgesamt, wegen
    Vergleichbarkeit
    </li>
</ul>
</aside>
