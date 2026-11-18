# ARS 2026 deck: Quarto reveal.js. Every target runs in Docker (see compose.yaml),
# so the host needs Docker and make, and nothing else.

TIKZ_SRCS := $(wildcard tikz/fig-*.tex)
TIKZ_SVGS := $(patsubst tikz/fig-%.tex,slides/figs/tikz/%.svg,$(TIKZ_SRCS))

# Host port of `make serve`; inside the compose network the deck is http://serve/index.html
SERVE_PORT ?= 18091
DECK_URL   := http://serve/index.html
TOOLS      := docker compose run --rm tools
PDF        := dist/ars2026-deck.pdf
SCRIPT     := script/ars2026-script
# `make deploy-test`: the site under the repository's name, as GitHub Pages serves it
PAGES_PORT ?= 18092
PAGES_URL  := http://pages/ars2026/index.html

help:
	@echo "images       build every toolchain image (once)"
	@echo "preview      live preview on http://localhost:4002/slides/index.html"
	@echo "render       render the deck to slides/index.html"
	@echo "figures      regenerate the Python figures, the screenshots and the QR codes"
	@echo "tikz         rebuild the TikZ SVGs whose .tex is newer"
	@echo "serve        serve the rendered deck on http://localhost:$(SERVE_PORT)"
	@echo "qa           render, serve, and run the QA checks"
	@echo "fill         how full each slide is, its text sizes, and screenshots at a laptop's full screen"
	@echo "timing       words and minutes of the speaker notes, per slide"
	@echo "script       the presenter's script in script/: Markdown, web page, PDF and Word"
	@echo "pdf          the deck as a PDF: $(PDF), and a copy beside the script"
	@echo "png          render, serve, and write every slide at 1920 x 1080 to dist/png/"
	@echo "deploy-test  build the last commit the way the Pages workflow does, serve it under /ars2026/ and check it"
	@echo "tools-shell  a shell in the Python toolchain"
	@echo "stop         stop every running service"

images:
	docker compose build

preview:
	docker compose up slides

render:
	docker compose run --rm slides quarto render slides/index.qmd --to revealjs

# Data figures, cropped screenshots and the QR codes; every result is committed, so
# rendering never needs Python.
figures:
	$(TOOLS) sh -c 'set -e; \
	  python scripts/gen_arch_moves_svg.py; \
	  python scripts/gen_speedup_svg.py; \
	  python scripts/gen_walltime_svg.py; \
	  python scripts/gen_tree_ladder_svg.py; \
	  python scripts/gen_multinode_svg.py; \
	  python scripts/prep_screens.py; \
	  python scripts/gen_qr.py; \
	  python scripts/qa/svg_embed_font.py'

tikz: $(TIKZ_SVGS)

slides/figs/tikz/%.svg: tikz/fig-%.tex tikz/preamble.tex
	docker compose run --rm texlive sh -c '\
	  cd tikz && mkdir -p build && \
	  lualatex -interaction=nonstopmode -halt-on-error -output-directory=build fig-$*.tex >/dev/null && \
	  pdftocairo -svg build/fig-$*.pdf ../slides/figs/tikz/$*.svg'

# The bind mount can keep serving a file's old bytes right after a rewrite; a
# restart refreshes the container's view before anything is measured or exported.
serve:
	SERVE_PORT=$(SERVE_PORT) docker compose up -d serve
	docker compose restart serve >/dev/null
	@echo "deck served at http://localhost:$(SERVE_PORT)/index.html"

# screen_fit.py runs the deck on a matrix of laptop and projector screens (16:10 and 16:9,
# full screen and in a browser window) and fails on any slide that leaves its stage, its
# slideref line or the window.
qa: render serve
	$(TOOLS) python scripts/qa/deck_sweep.py   --base $(DECK_URL) --out scripts/qa/out/sweep
	$(TOOLS) python scripts/qa/deck_fit.py     --base $(DECK_URL) --all
	$(TOOLS) python scripts/qa/screen_fit.py   --base $(DECK_URL)
	$(TOOLS) python scripts/qa/dash_scan.py    --base $(DECK_URL)
	$(TOOLS) python scripts/qa/band_balance.py --base $(DECK_URL)
	$(TOOLS) python scripts/qa/bridge_test.py  --base $(DECK_URL)
	$(TOOLS) python scripts/qa/caption_fit.py  --base $(DECK_URL)
	$(TOOLS) python scripts/qa/qr_check.py     --base $(DECK_URL)

# How full each slide is at the 1280 x 720 stage, and its text sizes; then the same deck as
# a 16-inch laptop shows it full screen, one PNG per slide in scripts/qa/out/laptop/.
fill: serve
	$(TOOLS) python scripts/qa/screen_fit.py --base $(DECK_URL) --fill --shots scripts/qa/out/laptop --shot 1728x1117

timing:
	$(TOOLS) python scripts/qa/notes_timing.py --wpm 140 --out scripts/qa/out/rehearsal_sheet.md

# The presenter's script, from the speaker notes, in four formats: Markdown; a web page and a
# PDF with a picture of every slide, its words and the clock; and a Word copy of the Markdown.
script: render serve
	$(TOOLS) python scripts/notes_to_script.py --wpm 140 --out $(SCRIPT).md
	$(TOOLS) python scripts/script_pdf.py --base $(DECK_URL) --wpm 140 --out $(SCRIPT).pdf --html $(SCRIPT).html
	docker compose run --rm slides quarto pandoc $(SCRIPT).md -o $(SCRIPT).docx

# The deck as a PDF, each animation replaced by its last frame: the fallback for a room
# without a network. A copy goes beside the script, where the presenter finds it.
pdf: render serve
	$(TOOLS) python scripts/qa/pdf_export.py --base $(DECK_URL) --out $(PDF) --notes
	cp $(PDF) script/ars2026-slides.pdf

png: render serve
	$(TOOLS) python scripts/qa/png_export.py --base $(DECK_URL)

# What GitHub Pages will serve, built the way .github/workflows/deploy-page.yml builds it: a
# clean copy of the last commit (so a file the deck needs but that is not committed shows up
# as missing), rendered with the pinned Quarto, served under /ars2026/ and checked. The copy
# stays in .deploy-test/ and on http://localhost:$(PAGES_PORT)/ars2026/ until `make stop`.
deploy-test:
	rm -rf .deploy-test && mkdir -p .deploy-test
	git archive --format=tar HEAD | tar -x -C .deploy-test
	docker run --rm -v "$(CURDIR)/.deploy-test:/project" -w /project slides-ars2026/quarto:1.6.40 \
	  quarto render slides/index.qmd --to revealjs
	PAGES_PORT=$(PAGES_PORT) docker compose up -d pages
	docker compose restart pages >/dev/null
	$(TOOLS) python scripts/qa/deck_sweep.py   --base $(PAGES_URL) --out scripts/qa/out/pages
	$(TOOLS) python scripts/qa/screen_fit.py   --base $(PAGES_URL)
	$(TOOLS) python scripts/qa/band_balance.py --base $(PAGES_URL)
	$(TOOLS) python scripts/qa/bridge_test.py  --base $(PAGES_URL)
	$(TOOLS) python scripts/qa/qr_check.py     --base $(PAGES_URL)
	@echo "the site as Pages will serve it: http://localhost:$(PAGES_PORT)/ars2026/"

tools-shell:
	$(TOOLS) bash

stop:
	docker compose down

.PHONY: help images preview render figures tikz serve qa fill timing script pdf png deploy-test tools-shell stop
