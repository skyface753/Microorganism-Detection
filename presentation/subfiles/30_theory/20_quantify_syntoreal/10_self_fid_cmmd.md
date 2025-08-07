## Syn-to-Real Quantifizierung

#### Verschiedene Methoden

<div class="container">
    <div class="column self-trained">
        <div class="header self-trained">Self-Trained Model</div>
        <ul>
        <li>YoloV11 Model</li>
        <li>mAP als Metrik</li>
        <li>Vgl: Vorher vs. Nacher</li>
        <li>Quantifizierung der Syn-to-Real gap</li>
        </ul>
    </div>
    <div class="column fid">
        <div class="header fid">FID</div>
        <ul>
        <li>Fréchet Inception Distance</li>
        <li>Inception-v3 Modell</li>
        <li>Distanz zwischen Verteilung der Features</li>
        <!-- <li>Inception V3 Netzwerk</li> -->
        <li>Mittelwert und Kovarianz zur Berechnung</li>
        </ul>
    </div>
    <div class="column cmmd">
        <div class="header cmmd">CMMD</div>
        <ul>
        <li>CLIP Maximum Mean Discrepancy</li>
        <li>CLIP Netzwerk</li>
        <li>Distanz zwischen Verteilung der Features</li>
        <li>Keine Annahme über die Verteilung</li>
        <!-- <li>CLIP Netzwerk</li> -->
        <!-- <li>Messen der Distanz zwischen zwei Verteilungen</li> -->
        </ul>
    </div>
</div>

Note:
Convolutional neural network

FID = Frechet Distance + Inception Score
FID => Multivariate Gaussian distribution
CMMD = Maximum Mean Discrepancy + Contrastive Language-Image Pre-training
CMMD nicht! Standardabweichung

<style>
    .fid-formular, .cmmd-formular {
       font-size: 22px;
       margin-top: 50px;
    }
</style>
