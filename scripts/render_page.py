#!/usr/bin/env python3

# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Aaron Mompié
# This file is part of motion-design (https://github.com/arrrnmp/motion-design).
# Licensed under the GNU Affero General Public License, version 3 or later.

"""Render an HTML style page to a still PNG, or (if it exposes renderFrame) to frames + MP4.

  render_page.py page.html out.png                 # still (1920x1080); waits for window.__ready
  render_page.py anim.html out.mp4 [--workers 4]   # animation: page must set window.FRAMES, window.FPS and
                                                   # window.renderFrame(f) -> PNG data URL (see assets/styles/*/anim.html)
  --root DIR   directory served over http (default: 3 levels up from the page, i.e. the skill's assets/ for templates);
               pages fetch() local files, so file:// is not enough.
  --frames a:b render a sub-range to <out>_frames/ only (for checking); --size WxH to override the viewport.

Frames render at the page's native FPS and are encoded at 24 fps (frames duplicated), so stepped styles stay
on 2s; nearest-neighbour upscale keeps pixel art crisp. Prints loaded fonts and page errors: check both.
Needs: pip install playwright pillow && playwright install chromium; ffmpeg.
"""
import sys, base64, asyncio, pathlib, subprocess, functools, threading, http.server, time, argparse
from playwright.async_api import async_playwright

ap = argparse.ArgumentParser(); ap.add_argument("page"); ap.add_argument("out")
ap.add_argument("--root"); ap.add_argument("--workers", type=int, default=4); ap.add_argument("--frames"); ap.add_argument("--size", default="1920x1080")
A = ap.parse_args()
page = pathlib.Path(A.page).resolve(); out = pathlib.Path(A.out).resolve()
root = pathlib.Path(A.root).resolve() if A.root else page.parents[2]
VW, VH = map(int, A.size.split("x"))

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(root)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f"http://127.0.0.1:{srv.server_address[1]}/{page.relative_to(root).as_posix()}"


async def open_page(b):
    pg = await b.new_page(viewport={"width": VW, "height": VH}); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    await pg.goto(URL, wait_until="networkidle"); await pg.evaluate("document.fonts.ready")
    try: await pg.wait_for_function("window.__ready !== false", timeout=120000)
    except Exception: errs.append("timeout waiting for window.__ready")
    return pg, errs


async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg, errs = await open_page(b)
        fonts = await pg.evaluate("[...new Set([...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family+' '+f.weight))]")
        anim = await pg.evaluate("typeof window.renderFrame === 'function'")
        print("fonts:", fonts, "errors:", errs)
        if not anim or out.suffix.lower() == ".png":
            await pg.screenshot(path=str(out)); print("wrote", out); await b.close(); return
        n, fps = await pg.evaluate("[window.FRAMES, window.FPS]"); await pg.close()
        fd = out.with_name(out.stem + "_frames"); fd.mkdir(exist_ok=True)
        lo, hi = map(int, A.frames.split(":")) if A.frames else (0, n)
        frames = list(range(lo, hi)); t0 = time.time()
        async def worker(chunk):
            p, e = await open_page(b)
            for f in chunk:
                data = await p.evaluate(f"window.renderFrame({f})")
                (fd / f"f{f:05d}.png").write_bytes(base64.b64decode(data.split(",", 1)[1]))
            if e: print("page errors:", e)
            await p.close()
        await asyncio.gather(*(worker(frames[i::A.workers]) for i in range(A.workers)))
        await b.close()
    print(f"{len(frames)} frames in {time.time() - t0:.1f}s")
    if A.frames: return
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-i", str(fd / "f%05d.png"),
                    "-vf", f"scale={VW}:{VH}:flags=neighbor,fps=24", "-c:v", "libx264", "-preset", "slow", "-crf", "14",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)], check=True)
    print("wrote", out, f"({n} frames @ {fps} fps -> 24 fps)")

asyncio.run(main())
