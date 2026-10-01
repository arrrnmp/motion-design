// Shared print simulator: spot-ink plates -> halftone screens -> misregistration -> multiply on paper.
// Each plate is a canvas whose ALPHA is ink density (draw with rgba(0,0,0,d)); >= solidAt prints solid.
// Used by the riso, linocut, manga and space-age directions. Deterministic (seeded).
function makePlate(W, H) { const c = document.createElement('canvas'); c.width = W; c.height = H; return c.getContext('2d'); }

function printPlates(outCanvas, plates, paper, opts = {}) {
  const W = outCanvas.width, H = outCanvas.height;
  let s = opts.seed || 7; const rnd = () => ((s = (s * 16807) % 2147483647) / 2147483647);
  const P = new Float32Array(1024); for (let i = 0; i < 1024; i++) P[i] = rnd();
  const h = (x, y) => P[((x * 73 + y * 151) % 1024 + 1024) % 1024];
  const vn = (x, y) => { const X = Math.floor(x), Y = Math.floor(y), fx = x - X, fy = y - Y, q = t => t * t * (3 - 2 * t);
    const a = h(X, Y), b = h(X + 1, Y), c = h(X, Y + 1), d = h(X + 1, Y + 1);
    return a + (b - a) * q(fx) + (c - a) * q(fy) + (a - b - c + d) * q(fx) * q(fy); };

  const cov = plates.map(pl => {
    const a = pl.ctx.getImageData(0, 0, W, H).data, out = new Float32Array(W * H);
    const th = (pl.angle || 0) * Math.PI / 180, cs = Math.cos(th), sn = Math.sin(th), k = 2 * Math.PI / (pl.cell || 10);
    const solidAt = pl.solidAt ?? 0.97, speck = pl.speckle ?? 0.03, roller = pl.roller ?? 0.15;
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const i = y * W + x, d = a[i * 4 + 3] / 255;
      if (d < 0.01) continue;
      let c;
      if (d >= solidAt) c = 1;
      else { const u = (x * cs + y * sn) * k, v = (-x * sn + y * cs) * k; c = d > 1 - (0.5 + 0.25 * (Math.cos(u) + Math.cos(v))) ? 1 : 0; }
      if (!c) continue;
      if (rnd() < speck) c *= 0.35;
      out[i] = c * (1 - roller + roller * vn(x / 260, y / 80)) * (pl.strength ?? 0.95);
    }
    return out;
  });

  const ctx = outCanvas.getContext('2d'), img = ctx.createImageData(W, H), px = img.data;
  const age = opts.age || 0;
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const o = (y * W + x) * 4;
    const f = 1 - 0.035 * rnd() - 0.03 * vn(x / 3, y / 3);
    // paper ageing: darker toward the edges + a few foxing spots
    const ex = Math.min(x, W - x) / W, ey = Math.min(y, H - y) / H, edge = Math.max(0, 0.08 - Math.min(ex, ey)) / 0.08;
    const fox = age ? Math.max(0, vn(x / 22 + 40, y / 22) - 0.82) * 4 : 0;
    let r = paper[0] * f, g = paper[1] * f, b = paper[2] * f;
    const yel = age * (0.5 * edge + 0.25 * vn(x / 300, y / 300) + fox);
    r *= 1 - yel * 0.08; g *= 1 - yel * 0.16; b *= 1 - yel * 0.32;
    plates.forEach((pl, j) => {
      const [ox, oy] = pl.offset || [0, 0], sx = x - ox, sy = y - oy;
      if (sx < 0 || sy < 0 || sx >= W || sy >= H) return;
      const c = cov[j][sy * W + sx]; if (!c) return;
      r *= 1 - c * (1 - pl.rgb[0] / 255); g *= 1 - c * (1 - pl.rgb[1] / 255); b *= 1 - c * (1 - pl.rgb[2] / 255);
    });
    px[o] = r; px[o + 1] = g; px[o + 2] = b; px[o + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);
}
