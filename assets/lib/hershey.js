// Single-stroke (Hershey / EMS) text -> polylines, so lettering can be *drawn* with a pen or brush.
// window.HERSHEY must hold assets/hershey.json. Returns { polys: [{pts, ch, i}], width } in px; y is the baseline.
const HERSHEY_META = {
  // classic Hershey: y grows downward, baseline ~22, cap height ~21 units
  futural: { em: 32, base: 22, flip: false }, timesr: { em: 32, base: 22, flip: false }, scripts: { em: 32, base: 22, flip: false },
};
function hersheyPolys(text, font, x, y, size, opts = {}) {
  const F = window.HERSHEY[font], meta = HERSHEY_META[font] || { em: 1000, base: 0, flip: true };
  const sc = size / meta.em, track = opts.track || 0, polys = [];
  let cx = x;
  [...text].forEach((ch, i) => {
    const g = F[ch] || F[' '];
    if (g && g.d) {
      let cur = null, nums = [];
      const flush = () => { for (let k = 0; k + 1 < nums.length; k += 2) cur.push([nums[k], nums[k + 1]]); nums = []; };
      for (const tok of g.d.match(/[ML]|-?\d+(?:\.\d+)?/g) || []) {
        if (tok === 'M') { if (cur) flush(); cur = []; polys.push({ pts: cur, ch, i }); continue; }
        if (tok === 'L') continue;
        nums.push(Number(tok));
      }
      if (cur) flush();
      for (const p of polys) if (p.i === i && !p.done) {
        p.pts = p.pts.map(([gx, gy]) => [cx + gx * sc, y + (meta.flip ? -gy : gy - meta.base) * sc]); p.done = true;
      }
    }
    let adv = g ? g.w : meta.em * 0.3;
    if (!meta.flip && g && g.d) {            // classic Hershey: advance from the glyph's own extent
      const xs = (g.d.match(/-?\d+(?:\.\d+)?,/g) || []).map(v => parseFloat(v));
      if (xs.length) adv = Math.max(...xs) + 3;
    } else if (!meta.flip) adv = 10;
    cx += (adv + track) * sc;
  });
  return { polys, width: cx - x };
}
