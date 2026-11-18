"""The deck's two QR codes, as SVG in slides/figs/:
  qr_deck.svg    the deck itself on GitHub Pages, for the title slide
  qr_engine.svg  the engine's archive record, for the closing slide (the concept DOI of
                 ADS-IDAC on Zenodo, the one the engine's CITATION.cff gives)
The addresses are in scripts/links.py. Dark modules in the deck's ink on white, error
correction level M, the standard four-module quiet zone. scripts/qa/qr_check.py decodes both
codes back from the rendered slides.
Usage: python scripts/gen_qr.py"""
import os
import segno
from links import DECK_URL, ENGINE_URL
from svgkit import FIGS, INK, ROOT

for name, url, title in (("qr_deck.svg", DECK_URL, "QR code: these slides"),
                         ("qr_engine.svg", ENGINE_URL, "QR code: ADS-IDAC on Zenodo")):
    qr = segno.make(url, error="m", micro=False)
    out = os.path.join(FIGS, name)
    tmp = out + ".tmp"
    qr.save(tmp, kind="svg", dark=INK, light="#FFFFFF", border=4, scale=1, xmldecl=False,
            svgclass=None, lineclass=None, title=title)
    os.replace(tmp, out)
    print(f"wrote {os.path.relpath(out, ROOT)}: {url}, version {qr.version}, error {qr.error}, "
          f"{qr.symbol_size(border=4)} modules with border")
