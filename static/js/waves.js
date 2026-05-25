(function () {
    const canvas = document.getElementById('waveCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let t = 0;

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    const ribbons = [
        { centerY: 0.62, thickness: 0.13, freq: 0.0028, speed: 0.18, phaseOff: 0.0,  brightness: 0.85 },
        { centerY: 0.50, thickness: 0.10, freq: 0.0032, speed: 0.22, phaseOff: 1.2,  brightness: 1.0  },
        { centerY: 0.40, thickness: 0.08, freq: 0.0025, speed: 0.15, phaseOff: 2.5,  brightness: 0.65 },
        { centerY: 0.68, thickness: 0.07, freq: 0.0035, speed: 0.20, phaseOff: 3.8,  brightness: 0.50 },
        { centerY: 0.55, thickness: 0.05, freq: 0.0040, speed: 0.28, phaseOff: 0.7,  brightness: 0.40 },
    ];

    function waveY(x, centerY, freq, phase) {
        const H = canvas.height;
        return centerY * H
            + Math.sin(x * freq + phase) * H * 0.10
            + Math.sin(x * freq * 0.6 + phase * 1.4) * H * 0.04
            + Math.sin(x * freq * 1.8 + phase * 0.8) * H * 0.02;
    }

    function drawRibbon(r) {
        const W = canvas.width;
        const H = canvas.height;
        const phase = t * r.speed + r.phaseOff;
        const halfT = (r.thickness * H) / 2;

        const topPts = [];
        const botPts = [];
        for (let x = 0; x <= W; x += 2) {
            const cy = waveY(x, r.centerY, r.freq, phase);
            topPts.push([x, cy - halfT]);
            botPts.push([x, cy + halfT]);
        }

        ctx.save();
        ctx.beginPath();
        ctx.moveTo(topPts[0][0], topPts[0][1]);
        for (let i = 1; i < topPts.length; i++) ctx.lineTo(topPts[i][0], topPts[i][1]);
        for (let i = botPts.length - 1; i >= 0; i--) ctx.lineTo(botPts[i][0], botPts[i][1]);
        ctx.closePath();

        const midX = W / 2;
        const cy = waveY(midX, r.centerY, r.freq, phase);
        const b = r.brightness;
        const grad = ctx.createLinearGradient(0, cy - halfT, 0, cy + halfT);
        grad.addColorStop(0.0,  `rgba(60,0,0,${0.55 * b})`);
        grad.addColorStop(0.20, `rgba(140,0,0,${0.75 * b})`);
        grad.addColorStop(0.42, `rgba(210,10,10,${0.90 * b})`);
        grad.addColorStop(0.50, `rgba(240,30,30,${0.95 * b})`);
        grad.addColorStop(0.58, `rgba(210,10,10,${0.90 * b})`);
        grad.addColorStop(0.80, `rgba(140,0,0,${0.75 * b})`);
        grad.addColorStop(1.0,  `rgba(60,0,0,${0.55 * b})`);

        ctx.fillStyle = grad;
        ctx.fill();

        ctx.beginPath();
        ctx.moveTo(topPts[0][0], topPts[0][1] + halfT * 0.35);
        for (let i = 1; i < topPts.length; i++) {
            const cy2 = waveY(topPts[i][0], r.centerY, r.freq, phase);
            ctx.lineTo(topPts[i][0], cy2 - halfT * 0.05);
        }
        for (let i = topPts.length - 1; i >= 0; i--) {
            const cy2 = waveY(topPts[i][0], r.centerY, r.freq, phase);
            ctx.lineTo(topPts[i][0], cy2 + halfT * 0.18);
        }
        ctx.closePath();

        const highlightGrad = ctx.createLinearGradient(W * 0.1, 0, W * 0.9, 0);
        highlightGrad.addColorStop(0.0,  `rgba(255,100,100,0)`);
        highlightGrad.addColorStop(0.25, `rgba(255,180,180,${0.22 * b})`);
        highlightGrad.addColorStop(0.50, `rgba(255,240,240,${0.35 * b})`);
        highlightGrad.addColorStop(0.75, `rgba(255,180,180,${0.22 * b})`);
        highlightGrad.addColorStop(1.0,  `rgba(255,100,100,0)`);
        ctx.fillStyle = highlightGrad;
        ctx.fill();

        ctx.restore();
    }

    function render() {
        const W = canvas.width;
        const H = canvas.height;
        ctx.fillStyle = '#000000';
        ctx.fillRect(0, 0, W, H);
        for (let i = ribbons.length - 1; i >= 0; i--) {
            drawRibbon(ribbons[i]);
        }
        t += 0.008;
        requestAnimationFrame(render);
    }

    render();
})();
