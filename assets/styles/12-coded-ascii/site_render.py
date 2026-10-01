"""Deterministic 30 fps capture of the ASCII site (virtual clock), with a per-frame state log.

The page's performance.now / requestAnimationFrame are replaced by a virtual clock that we step
one frame at a time, so every frame is exact and the log (chapter, progress, typed chars, theme,
clicks) can drive the sound design. Output: site/_render/frames/*.png, site/_render/log.json, site/demo.mp4 (silent).
"""
import asyncio, json, math, pathlib, shutil, subprocess, functools, threading, http.server
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent          # the style folder (contains site/)
OUT = ROOT / "site" / "_render"; FR = OUT / "frames"
shutil.rmtree(OUT, ignore_errors=True); FR.mkdir(parents=True)
FPS, W, H = 30, 1920, 1080

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
SRV = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
threading.Thread(target=SRV.serve_forever, daemon=True).start()

CLOCK = """
window.__vt = 0; const __q = [];
performance.now = () => window.__vt;
window.requestAnimationFrame = cb => { __q.push(cb); return __q.length; };
window.__step = ms => { window.__vt = ms; const cbs = __q.splice(0); cbs.forEach(cb => cb(ms)); return window.__c2c || null; };
"""

# ---- the shot script: (time, action) — scroll holds let each chapter's caption type out
N, TAIL = 6, 0.35
def target_p(k): return min(k + 0.55, N - 0.02)
ease = lambda x: 0.5 - 0.5 * math.cos(math.pi * max(0, min(1, x)))
HERO, MOVE, HOLD = 4.6, 1.4, 2.4
seg = []                                                      # (t0, t1, p0, p1)
t, p = HERO, 0.0
for k in range(1, N):
    seg.append((t, t + MOVE, p, target_p(k))); t += MOVE + HOLD; p = target_p(k)
DUR = t + 0.6
THEME_AT = [HERO + 2 * (MOVE + HOLD) + MOVE + 1.0, HERO + 4 * (MOVE + HOLD) + MOVE + 1.0]   # press T while holding on ch2 and ch4
CLICK_AT = 3.7

def progress(t):
    for t0, t1, p0, p1 in seg:
        if t < t0: return p0 if seg.index((t0, t1, p0, p1)) else 0.0
        if t <= t1: return p0 + (p1 - p0) * ease((t - t0) / (t1 - t0))
    return seg[-1][3]

def pointer(t):
    if 2.6 <= t <= 3.7:                                        # sweep across the title, then click the cup
        u = (t - 2.6) / 1.1
        return (260 + 1150 * u, 330 + 60 * math.sin(u * 6))
    return None


async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page(viewport={"width": W, "height": H})
        await pg.add_init_script(CLOCK)
        await pg.goto(f"http://127.0.0.1:{SRV.server_address[1]}/site/index.html", wait_until="networkidle")
        await pg.evaluate("document.fonts.ready")
        for _ in range(3): await pg.evaluate("window.__step(0)")
        maxs = await pg.evaluate("document.documentElement.scrollHeight - innerHeight")
        log, n = [], int(DUR * FPS)
        done_theme, clicked = set(), False
        for f in range(n):
            t = f / FPS
            await pg.evaluate(f"scrollTo(0, {progress(t) / (N - TAIL) * maxs})")
            pt = pointer(t)
            if pt: await pg.mouse.move(*pt)
            elif f and pointer((f - 1) / FPS): await pg.mouse.move(W - 5, H / 2)
            if t >= CLICK_AT and not clicked: await pg.mouse.click(*pointer(CLICK_AT)); clicked = True
            for i, ta in enumerate(THEME_AT):
                if t >= ta and i not in done_theme: await pg.keyboard.press("t"); done_theme.add(i)
            st = await pg.evaluate(f"window.__step({t * 1000})")
            await pg.screenshot(path=str(FR / f"f{f:05d}.png"))
            log.append({"f": f, "t": t, **(st or {})})
        await b.close()
    (OUT / "log.json").write_text(json.dumps({"fps": FPS, "dur": n / FPS, "click": CLICK_AT, "theme": THEME_AT, "frames": log}))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(FR / "f%05d.png"), "-c:v", "libx264", "-preset", "slow",
                    "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(ROOT / "site" / "demo.mp4")], check=True)
    print(f"{n} frames, {n / FPS:.1f}s -> site/demo.mp4")

asyncio.run(main())
