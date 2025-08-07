## Syn-to-Real Quantification

#### Different Methods

<div class="container">
    <div class="column self-trained">
        <div class="header self-trained">Self-Trained Model</div>
        <ul>
        <li>YoloV11 Model</li>
        <li>mAP as Metrik</li>
        <!-- <li>Diff: Before vs. After</li> -->
        <li>Quantify the Syn-to-Real Gap</li>
        </ul>
    </div>
    <div class="column fid">
        <div class="header fid">FID</div>
        <ul>
        <li>Fréchet Inception Distance</li>
        <li>Inception-v3 Modell</li>
        <li>Multivariate Gaussian distribution</li>
        <li>Mean and covariance to calculate</li>
        </ul>
    </div>
    <div class="column cmmd">
        <div class="header cmmd">CMMD</div>
        <ul>
        <li>CLIP Maximum Mean Discrepancy</li>
        <li>CLIP Network</li>
        <li>Distance between feature distributions</li>
        <li>No assumption about the distribution</li>
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
