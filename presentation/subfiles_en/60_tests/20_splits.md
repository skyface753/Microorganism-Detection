<section data-visibility="uncounted">
    <h2>Data Ratios</h2>
    <p>T1: 100% real</p>
    <p>57 muddy + 3356 clean = 3413</p>
    <div class="stretch">
        <canvas data-chart="pie">
        ,Real: Muddy, Real: Clean
        T1, 57, 3356
        </canvas>
    </div>
    <div class="placeholder-bottom"></div>
Note:
1,69% Abweichung zu 3356
</section>

<section data-visibility="uncounted">
    <h3>Data Ratios</h3>
    <p>T2: 3413 Bilder</p>
    <div class="pie-chart-side-by-side">
        <p>60% syn + 40% real</p>
        <canvas data-chart="pie">
            ,60% Alpha, 40% Real
            T2-30, 2014, 1399
        </canvas>
    </div>
    <div class="pie-chart-side-by-side">
    <p>90% syn + 10% real</p>
        <canvas data-chart="pie">
            ,90% Alpha, 10% Real
            T2-90, 3020, 393
        </canvas>
    </div>
</section>

<!-- T3 -->
<section data-visibility="uncounted">
    <h3>Data Ratios</h3>
    <p>T3: 3413 Bilder</p>
    <div class="pie-chart-side-by-side">
        <p>60% syn + 40% real</p>
        <canvas data-chart="pie">
            ,20% Alpha, 20% Gaussian, 20% Pyramid, 40% Real
            T2-30, 671, 671, 671, 1401
        </canvas>
    </div>
    <div class="pie-chart-side-by-side">
    <p>90% syn + 10% real</p>
        <canvas data-chart="pie">
            ,30% Alpha, 30% Gaussian, 30% Pyramid, 10% Real
            T2-90, 1007, 1007, 1007, 393
        </canvas>
    </div>
</section>

<!-- <section>
    <h2>Aufteilung</h2>
    <p>T3: 3356 Bilder</p>
    <p>30% syn + 70% real</p>
    <p>336 alpha + 336 gaus + 336 pyramid + 2349 clean ≈ 3356</p>
    <div style="height:40vh; float: left; width: 50%">
        <canvas data-chart="pie">
            ,Synthetic: Alpha, Synthetic: Gaussian, Synthetic: Pyramid, Real: Clean
            T2-30, 336, 336, 336, 2349
        </canvas>
    </div>
    <div style="height:40vh; float: left; width: 50%">
        <p>90% syn + 10% real</p>
        <p>1007 alpha + 1007 gaus + 1007 pyramid + 336 clean ≈ 3356</p>
        <canvas data-chart="pie">
            ,Synthetic: Alpha, Synthetic: Gaussian, Synthetic: Pyramid, Real: Clean
            T2-90, 1007, 1007, 1007, 336
        </canvas>
    </div>
</section> -->

<!-- t1 = 3413
t2+t3 = 3356 -->

<style>
    .placeholder-bottom {
        height: 3vh;
    }
    .pie-chart-side-by-side{
        height: 43vh;
        width: 50%;
        float: left;
    }
</style>
