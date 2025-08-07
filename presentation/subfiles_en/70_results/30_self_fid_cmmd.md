## Results

#### Comparison

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
Annotation: FID and CMMD are scaled to the range [0,1] by min-max normalization. The self-trained value is calculated as 1-mAP, as this is the difference between a perfect model (mAP = 1 for real data) and the model, trained on the experimental datasets. This way, the values of the three metrics are scaled to the same range. For the tests, the average value over the different syn-to-real ratios was calculated.
</div>
