# From ADS-IDAC to OpenPRA: the ARS 2026 talk

Slides and presenter's script for the paper *From ADS-IDAC to OpenPRA: Enabling Dynamic
Probabilistic Risk Assessment for Advanced Reactors* by Alp Tezbasaran and Mihai A. Diaconeasa
(North Carolina State University), given at Advanced Reactor Safety (ARS 2026), ANS Winter
Conference and Expo, Phoenix, Arizona, on November 18, 2026.

- **Deck:** https://alptezbasaran.github.io/ars2026/
- **Presenter's script:** [`script/ars2026-script.pdf`](script/ars2026-script.pdf), with a
  picture of every slide, the words to say and a running clock. The same text is there as
  [Markdown](script/ars2026-script.md), as a [web page](script/ars2026-script.html) and as a
  [Word file](script/ars2026-script.docx).
- **Deck as a PDF:** [`script/ars2026-slides.pdf`](script/ars2026-slides.pdf), one page per
  slide, for a room without a network. Each animation appears as its last frame.

## Presenting

Open the deck in a browser. It is a [Quarto](https://quarto.org) reveal.js deck:

| Key | What it does |
|---|---|
| right arrow, space, or a clicker | next slide; nothing builds inside a slide |
| `F` | full screen |
| `S` | speaker view: the script for the slide, the next slide and a timer |
| `G`, a number, `Enter` | jump to that slide; the numbers are the PDF pages the script gives |
| `Esc` | overview of all slides |

The three animation slides start by themselves and stop on their last frame. Backup slides
for questions follow the closing slide.

## Building

Everything runs in Docker; the host needs Docker and `make`.

```sh
make images        # build the toolchain images, once
make preview       # live preview on http://localhost:4002/slides/index.html
make render        # one render to slides/index.html
make serve         # serve the rendered deck on http://localhost:18091/index.html
make qa            # render, serve and run every check
make script        # the presenter's script in script/, in four formats
make pdf           # the deck as a PDF
make deploy-test   # build the last commit as the Pages workflow does, and check it
```

The deck has to be served over HTTP, not opened as a file: the animation slides load their
pages in iframes. `make help` lists every target.

## Layout

```
slides/index.qmd            the title slide and the includes
slides/sections/            the talk (01 to 06) and the backup slides (07); the speaker notes are the script
slides/theme/theme.scss     the theme
slides/assets/              animation pages, fonts, MathJax, the navigation strip
slides/figs/                figures, screenshots and QR codes, all committed
scripts/                    the figure scripts and the script generator
scripts/qa/                 the checks behind `make qa`
script/                     the presenter's script and the deck as a PDF, generated
tikz/                       sources of the TikZ diagrams
.github/workflows/          the Pages deployment
```

The rendered HTML is not committed: the Pages workflow renders its own copy.

## The checks

`make qa` renders the deck and then runs, against the served copy:

- a sweep of every slide for console errors, failed requests and broken images;
- fit: no slide leaves its stage, at 1280 x 720 and on a matrix of twelve laptop and projector
  screens;
- the balance of the red title band on eight window sizes;
- the clicker inside every animation page;
- caption length in the animations;
- both QR codes, decoded back from the rendered slides.

## Deployment

`.github/workflows/deploy-page.yml` runs on every push to `main`: it renders the deck with
Quarto 1.6.40 and publishes the `slides/` folder to GitHub Pages. In a new repository, turn
Pages on first: **Settings, Pages, Build and deployment, Source: GitHub Actions**.

`make deploy-test` rehearses that locally. It takes a clean copy of the last commit, renders
it with the same Quarto version, serves it under `/ars2026/` as Pages does, and runs the
sweep, the fit check, the band check, the clicker test and the QR check against it. The copy
stays on http://localhost:18092/ars2026/ until `make stop`.

The QR code on the title slide points to the deployed deck, and the one on the closing slide
to the archive record of ADS-IDAC. Both addresses are in `scripts/links.py`; after changing
one, run `make figures`.
