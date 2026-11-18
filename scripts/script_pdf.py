"""The presenter's script with a picture of every slide, as a printable PDF and as one web
page: script/ars2026-script.pdf and script/ars2026-script.html. A first page of instructions,
the talk at a glance, then every screen of the talk with its picture, the words to say, its
length and the clock, then the prepared answers with the slides to show. The text is the
speaker notes (notes_to_script.py reads them); the pictures are taken from the served deck at
1280 x 720, an animation at its last frame, as in the slide PDF.
Usage: script_pdf.py --base http://serve/index.html [--wpm 140] [--out script/ars2026-script.pdf]"""
import base64, html, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "qa"))
sys.path.insert(0, HERE)
from _common import *
import notes_to_script as N

ap = parser(__doc__)
ap.add_argument("--wpm", type=float, default=140)
ap.add_argument("--out", default="script/ars2026-script.pdf")
ap.add_argument("--html", default="script/ars2026-script.html")
a = ap.parse_args()
slides, answers = N.load("slides")
total = N.timeline(slides, a.wpm)
talk = [s for s in slides if s["talk"]]
base_dir = a.base.rsplit("/", 1)[0]

CSS = """
*{box-sizing:border-box}
html{font-size:11.5pt}
body{font-family:"Open Sans","Helvetica Neue",Arial,sans-serif;color:#111;line-height:1.42;margin:0;
     text-rendering:geometricPrecision;-webkit-print-color-adjust:exact;print-color-adjust:exact}
@media screen{body{max-width:7.6in;margin:0 auto;padding:.5in .3in}}
.kicker{font-size:8.5pt;letter-spacing:.14em;text-transform:uppercase;color:#B40000;font-weight:700;margin:0 0 3pt}
h1{font-size:19pt;line-height:1.22;font-weight:700;margin:0 0 5pt}
.paper{font-size:11pt;line-height:1.4;margin:0 0 2pt}
.slot{font-size:9.5pt;color:#444;line-height:1.4;margin:0}
.gist{font-size:10.5pt;line-height:1.42;margin:9pt 0 0;padding:6pt 10pt;background:#f4f1ee;border-left:3pt solid #B40000}
h2.sec{font-size:10pt;text-transform:uppercase;letter-spacing:.12em;color:#B40000;border-bottom:1.2pt solid #B40000;
       padding-bottom:2pt;margin:12pt 0 7pt}
dl.before{display:grid;grid-template-columns:1.1in 1fr;column-gap:12pt;row-gap:6.5pt;font-size:10.5pt;line-height:1.4;margin:0}
dl.before dt{font-weight:700}
dl.before dd{margin:0}
table.pace{width:100%;border-collapse:collapse;font-size:9pt;line-height:1.3;margin-bottom:12pt}
table.pace th{text-align:left;font-weight:700;color:#444;border-bottom:1pt solid #999;padding:2pt 8pt 2pt 0}
table.pace td{padding:1.5pt 8pt 1.5pt 0;border-bottom:.5pt solid #ddd;vertical-align:top}
table.pace .n{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums;padding-right:0;padding-left:14pt;width:1%}
table.pace td:first-child,table.pace th:first-child{white-space:nowrap;width:1%;padding-right:14pt}
table.pace td.c{font-weight:700;color:#B40000}
.front{break-after:page}
section.slide{display:grid;grid-template-columns:2.2in 1fr;column-gap:.25in;break-inside:avoid;padding:9pt 0 4pt;
              border-top:1.2pt solid #999}
.pic img{width:100%;display:block;border:.75pt solid #aaa}
.meta{font-size:9pt;color:#444;line-height:1.4;margin-top:5pt}
.meta .clock{font-size:14pt;font-weight:700;color:#B40000;line-height:1.15;display:block}
.say h2{font-size:11.5pt;line-height:1.3;margin:0 0 5pt;font-weight:700}
.say h2 .lab{display:block;font-size:8.5pt;letter-spacing:.12em;text-transform:uppercase;color:#B40000}
.say p{margin:0 0 6pt}
.say p.sd{font-size:9.5pt;line-height:1.4;color:#555;font-style:italic;border-left:2.5pt solid #bbb;padding-left:7pt}
.fill{color:#B40000;font-weight:700}
.answers{break-before:page}
.answers .lead{font-size:10pt;line-height:1.38;margin:0 0 7pt}
.qa{break-inside:avoid;font-size:10pt;line-height:1.38;margin:0 0 5.5pt}
.qa p{margin:0}
.qa .q{font-weight:700}
.qa .show{margin-top:1pt;font-size:8.8pt;color:#B40000}
"""

FOOT = ('<div style="width:100%; font-family:Arial,Helvetica,sans-serif; font-size:8pt; color:#666; padding:0 0.65in; '
        'display:flex; justify-content:space-between;"><span>ARS 2026 · From ADS-IDAC to OpenPRA · presenter\'s '
        'script</span><span>script page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>')

# pdf_export.py's way to an animation's last frame
SEEK = ("() => { const A = window.__anim; if (A) { const T = A.T || A.T_END || (A.seek && 1e9); "
        "A.seek(typeof T === 'number' ? T : 1e9); } }")


def esc(t):
    return html.escape(t, quote=False)


def inline(t):
    """Escaped text; **bold**, and a bracketed blank inside a sentence set off as a fill-in."""
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(t))
    return re.sub(r"\[([^\]]+)\]", r'<span class="fill">[\1]</span>', t)


def paragraphs(notes):
    out = []
    for p in re.split(r"\n\s*\n", notes.strip()):
        p = re.sub(r"\s+", " ", p).strip()
        if p.startswith("[") and p.endswith("]") and p.count("[") == 1:
            out.append(f'<p class="sd">{esc(p)}</p>')      # a note to the presenter
        elif p:
            out.append(f"<p>{inline(p)}</p>")
    return "\n".join(out)


def build(pics, fonts):
    """The page. `fonts` is where Open Sans comes from: the served deck while printing, the
    published deck for the copy that is kept (it falls back to a system font offline)."""
    h = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         "<title>Presenter's script, ARS 2026</title>",
         f'<link href="{fonts}" rel="stylesheet">', f"<style>{CSS}</style></head><body>",
         '<header class="front">', "<p class=\"kicker\">ARS 2026 · presenter's script</p>",
         f"<h1>{esc(N.TITLE)}</h1>",
         f'<p class="paper">{esc(N.AUTHORS)}<br>Presented by {esc(N.PRESENTER)}</p>', f'<p class="slot">{esc(N.SLOT)}</p>',
         f'<p class="gist"><b>The talk in brief.</b> {esc(N.GIST)}</p>',
         '<h2 class="sec">Before you start</h2>', '<dl class="before">']
    for lead, text in N.before_you_start(slides, total, a.wpm):
        h.append(f"<dt>{esc(lead)}</dt><dd>{esc(text)}</dd>")
    # the first sheet is the instructions; the table opens the second, above the title slide
    h += ["</dl>", "</header>", "<main>", '<h2 class="sec">The talk at a glance</h2>', '<table class="pace">',
          '<tr><th>Screen</th><th>On it</th><th class="n">PDF page</th><th class="n">About</th>'
          '<th class="n">Clock at the end</th></tr>']
    for s in talk:
        h.append(f"<tr><td>{esc(s['label'])}</td><td>{esc(s['title'])}</td><td class='n'>{s['page']}</td>"
                 f"<td class='n'>{round(s['seconds'] / 5) * 5:.0f} s</td><td class='n c'>{N.mmss(s['clock'])}</td></tr>")
    h.append("</table>")
    for s in talk:
        pic = base64.b64encode(pics[s["id"]]).decode("ascii")
        h += ['<section class="slide">',
              f'<div class="pic"><img alt="" src="data:image/jpeg;base64,{pic}">',
              f'<div class="meta"><span class="clock">{N.mmss(s["clock"])}</span>on the clock when you finish<br>'
              f'about {round(s["seconds"] / 5) * 5:.0f} s · {s["words"]} words · PDF page {s["page"]}</div></div>',
              f'<div class="say"><h2><span class="lab">{esc(s["label"])}</span>{esc(s["title"])}</h2>',
              paragraphs(s["notes"]), "</div></section>"]
    h.append("</main>")
    if answers:
        head, lead, items = N.parse_answers(answers, slides)
        h += ['<section class="answers">', f'<h2 class="sec">{esc(head)}</h2>']
        if lead:
            h.append(f'<p class="lead">{esc(lead)}</p>')
        for q, ans, ptrs in items:
            show = f'<p class="show">Show: {esc("; ".join(ptrs))}</p>' if ptrs else ""
            h.append(f'<div class="qa"><p class="q">{esc(q)}</p><p>{inline(ans)}</p>{show}</div>')
        h.append("</section>")
    h.append("</body></html>")
    return "\n".join(h)


with sync_playwright() as pw:
    # without this flag headless Chromium on Linux lays text out with hinted, rounded glyph advances,
    # and the PDF shows uneven letter spacing ("t o", "T he")
    browser = pw.chromium.launch(channel=CHANNEL, headless=True, args=["--font-render-hinting=none"])
    ctx = browser.new_context(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
    page = ctx.new_page()
    page.goto(a.base + "#/", wait_until="load")
    page.wait_for_function("window.Reveal && Reveal.isReady && Reveal.isReady()", timeout=30000)
    page.wait_for_timeout(600)
    deck = slide_list(page)
    if [d["id"] for d in deck] != [s["id"] for s in slides]:
        raise SystemExit("the rendered deck and the sources list different slides: run `make render` first")
    pics = {}
    for d in deck:
        s = slides[d["h"]]
        if s["talk"] and not s["iframe"]:
            goto(page, d["h"], settle=0.7)
            pics[s["id"]] = page.screenshot(type="jpeg", quality=82)
    for s in talk:
        if s["iframe"]:
            page.goto(f"{base_dir}/{s['iframe']}", wait_until="load")
            page.wait_for_timeout(800)
            page.evaluate(SEEK)
            page.wait_for_timeout(600)
            pics[s["id"]] = page.screenshot(type="jpeg", quality=82)
    page.close()

    os.makedirs(os.path.dirname(a.html) or ".", exist_ok=True)
    kept = build(pics, N.DECK_URL + "assets/fonts/open-sans.css")
    open(a.html, "w", encoding="utf-8").write(kept)
    print("page ->", a.html, f"({len(kept) // 1024} KB)")
    # printed from memory, at an address under the served deck so that its fonts resolve
    doc = build(pics, "assets/fonts/open-sans.css")
    p = ctx.new_page()
    p.route(re.compile(r".*/_script\.html$"),
            lambda route: route.fulfill(status=200, content_type="text/html; charset=utf-8", body=doc))
    p.goto(base_dir + "/_script.html", wait_until="load")
    p.evaluate("() => document.fonts.ready.then(() => true)")
    p.wait_for_timeout(400)
    if not p.evaluate("() => document.fonts.check('12pt \"Open Sans\"')"):
        raise SystemExit("Open Sans did not load: the PDF would be set in a fallback font")
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    p.pdf(path=a.out, format="Letter", print_background=True, display_header_footer=True,
          header_template="<span></span>", footer_template=FOOT,
          margin={"top": "0.6in", "bottom": "0.75in", "left": "0.65in", "right": "0.65in"})
    print("pdf ->", a.out, f"({os.path.getsize(a.out) // 1024} KB): {len(talk)} screens, "
          f"{sum(s['words'] for s in talk)} words, {total / 60:.1f} min at {a.wpm:.0f} wpm")
    browser.close()
