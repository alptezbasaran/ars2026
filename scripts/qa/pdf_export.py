"""PDF fallback of the deck. Captures each animation page's final frame as a PNG
(slides/assets/anim/frames/<name>.png), swaps the background iframes for those frames
in the print pass, and prints reveal's ?print-pdf layout at 1280x720 per page.
Writes <out> (slides only) and <out>-notes (speaker notes overlaid) when --notes is set.
Usage: pdf_export.py [--base URL] [--out dist/ars2026-deck.pdf] [--notes]"""
import os, sys, re, time, json
sys.path.insert(0, os.path.dirname(__file__))
from _common import *

ap = parser(__doc__); ap.add_argument("--out", default="dist/ars2026-deck.pdf"); ap.add_argument("--notes", action="store_true")
ap.add_argument("--frames", default="slides/assets/anim/frames")
a = ap.parse_args(); os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True); os.makedirs(a.frames, exist_ok=True)
base_dir = a.base.rsplit("/", 1)[0]
# how to reach each page's last frame
END = {"det-animation.html": "seek", "coupling-animation.html": "seek", "parallel-engine-animation.html": "seek",
       "362-mpi-dispatch.html": "seek", "serialization-animation.html": "seek"}
def png_name(ref):  # 'x.html?backup=1' -> 'x-backup-1.png'; a page referenced with a query gets its own frame
    base, _, q = ref.partition("?")
    return base.replace(".html", "") + ("-" + re.sub(r"[^A-Za-z0-9]+", "-", q).strip("-") if q else "") + ".png"
with sync_playwright() as pw:
    browser = pw.chromium.launch(channel=CHANNEL, headless=True)
    ctx = browser.new_context(viewport={"width": 1280, "height": 720}, device_scale_factor=2)
    page = ctx.new_page()
    frames = {}
    for name, how in END.items():
        url = f"{base_dir}/assets/anim/{name}" + (f"?{how}" if how.startswith("t=") else "")
        page.goto(url, wait_until="load"); time.sleep(0.8)
        if how == "seek":
            page.evaluate("() => { const A = window.__anim; if (A) { const T = A.T || A.T_END || (A.seek && 1e9); A.seek(typeof T === 'number' ? T : 1e9); } }")
            time.sleep(0.6)
        elif how == "wait":
            time.sleep(4.2)
        else:
            time.sleep(0.6)
        out = os.path.join(a.frames, png_name(name)); page.screenshot(path=out); frames[name] = out
        print("frame ->", out)
    page.close()
    # print pass: serve index.html with the iframe backgrounds swapped for the frames
    html = None
    def handle(route, request):
        body = route.fetch().text()
        def swap(m):
            name = os.path.basename(m.group(1))
            return f'data-background-image="assets/anim/frames/{png_name(name)}" data-background-size="contain" data-background-color="#ffffff"'
        body = re.sub(r'data-background-iframe="([^"]+)"(\s+data-background-interactive="true")?', swap, body)
        # the theme hides the outline heading only for iframe backgrounds; hide it for the swapped frames too
        body = body.replace('</head>', '<style>.reveal .slides section[data-background-image] > h2 { display: none !important; }</style></head>', 1)
        route.fulfill(status=200, content_type="text/html", body=body)
    for variant, suffix in ((False, ""), (True, "-notes")) if a.notes else ((False, ""),):
        p = ctx.new_page(); p.route(re.compile(r".*/index\.html(\?.*)?$"), handle)
        url = a.base + "?print-pdf" + ("&showNotes=true" if variant else "")
        p.goto(url, wait_until="load"); p.wait_for_function("window.Reveal && Reveal.isReady && Reveal.isReady()", timeout=60000)
        time.sleep(4.0)  # let images, fonts and the print layout settle
        out = a.out[:-4] + suffix + ".pdf" if a.out.endswith(".pdf") else a.out + suffix
        p.pdf(path=out, width="1280px", height="720px", print_background=True, prefer_css_page_size=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        print("pdf ->", out, f"({os.path.getsize(out)//1024} KB)"); p.close()
    browser.close()
