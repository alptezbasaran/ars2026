# TeX toolchain for the TikZ figures: LuaLaTeX from TeX Live, pdftocairo
# (poppler-utils) to turn each PDF into an SVG, and Open Sans for figure text.
#
# The SVGs committed under slides/figs/tikz/ were produced with TeX Live 2026.
# Once TeX Live 2027 is released, build with TEXLIVE_TAG=TL2026-historic to
# reproduce them exactly.
ARG TEXLIVE_TAG=latest
FROM texlive/texlive:${TEXLIVE_TAG}

RUN apt-get update \
 && apt-get install -y --no-install-recommends poppler-utils fonts-open-sans \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
