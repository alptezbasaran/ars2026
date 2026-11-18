"""The presenter's script as text, from the speaker notes: script/ars2026-script.md.

The notes in slides/index.qmd and slides/sections/01...06 are the source of the talk. This
script collects them in deck order under a short "before you start" list, gives every slide
its page in the slide PDF (also the number that G jumps to in the browser), its length at the
speaking rate and the clock at its end, and resolves the bracketed pointers of the prepared
answers (the text after `---` in the closing slide's notes) to slide and page numbers.
script_pdf.py prints the same content with a picture of every slide, as a PDF and as a web
page; `make script` runs both and adds a Word copy.

Slide numbers are the ones the navigation strip shows; an animation slide shows none there,
so it takes the number of the slide before it plus a letter (1a). On an animation slide the
time is the longer of the narration and the playback. Text in square brackets is a note to
the presenter and is not counted.
Usage: python scripts/notes_to_script.py [--wpm 140] [--out script/ars2026-script.md]"""
import argparse, glob, os, re
from links import DECK_URL

ANIM_S = {"anim-det": 37.5, "anim-coupling": 38, "anim-parallel-engine": 34}   # playback, seconds
TITLE = "From ADS-IDAC to OpenPRA: Enabling Dynamic Probabilistic Risk Assessment for Advanced Reactors"
AUTHORS = "Alp Tezbasaran and Mihai A. Diaconeasa, North Carolina State University"
PRESENTER = "Kirill Shumilov"
SLOT = ("ARS 2026, session Uncertainty Quantification, room Bougainvillea (program as read on November 15). "
        "Wednesday, November 18, 2026, 10:40 to 11:00 MST, the third of five talks: a 20 minute slot.")
SLOT_MIN = 20
SLIDES_PDF = "ars2026-slides.pdf"          # the deck as a PDF, beside the script: the fallback without a network
GIST = ("Dynamic PRA grows the event tree while a plant simulator runs. The paper shows how one such engine, "
        "ADS-IDAC, was rebuilt in two moves: the plant physics became a service behind an interface of six "
        "endpoints, so that other codes connect without merging code, and the tree is now traversed in parallel. "
        "The evidence: a web workflow, two very different reactors behind the same interface, a run that is 156 "
        "times faster on a laptop, and trees of tens of thousands of sequences generated in under an hour.")
SKIP = "memory-fault"   # the slide to leave out when the session runs late


def words(t):
    return len(re.findall(r"[\w'’]+", re.sub(r"\[[^\]]*\]", "", t, flags=re.S)))


def load(src="slides"):
    """Every slide of the deck in order, mainline and backup, and the prepared answers."""
    files = [os.path.join(src, "index.qmd")] + sorted(glob.glob(os.path.join(src, "sections", "0[1-7]-*.qmd")))
    slides, answers = [], ""
    for f in files:
        txt = open(f, encoding="utf-8").read()
        for blk in re.split(r'(?m)^(?=## )', txt)[1:]:
            head = blk.splitlines()[0]
            m = re.search(r'\{#([\w-]+)([^}]*)\}', head)
            sid, attrs = m.group(1), m.group(2)
            sec = re.search(r'data-section="(\d)"', attrs)
            ifr = re.search(r'background-iframe="([^"]+)"', attrs)
            nm = re.search(r'(?ms)^:::\s*\{\.notes\}\s*\n(.*?)^:::\s*$', blk)
            spoken, _, after = (nm.group(1).strip() if nm else "").partition("\n---")
            if after.strip():
                answers = after.strip()
            slides.append(dict(id=sid, title=re.sub(r'\s*\{.*$', '', head[3:]).strip(), notes=spoken.strip(),
                               section=int(sec.group(1)) if sec else 0, iframe=ifr.group(1) if ifr else "",
                               counted="uncounted" not in attrs and ".divider" not in attrs))
    return slides, answers


def timeline(slides, wpm=140):
    """Give every slide its page and its label, and every slide of the talk its words, its
    seconds and the clock at its end. Returns the length of the talk in seconds."""
    n = sum(1 for s in slides if s["counted"] and s["section"] <= 6)
    k = letter = b = 0
    clock = 0.0
    for i, s in enumerate(slides):
        s["page"] = i + 1
        s["talk"] = s["section"] <= 6
        if s["id"] == "title":
            s["label"], s["ref"] = "Title slide", "the title slide"
        elif s["id"] == "thank-you":
            s["label"], s["ref"] = "Closing slide", "the closing slide"
        elif s["talk"] and s["counted"]:
            k += 1
            letter = 0
            s["label"], s["ref"] = f"Slide {k} of {n}", f"slide {k}"
        elif s["talk"]:
            letter += 1
            s["label"], s["ref"] = f"Animation {k}{chr(96 + letter)}", f"the animation after slide {k}"
        elif s["counted"]:
            b += 1
            s["label"], s["ref"] = f"Backup B{b}", f"backup B{b}"
        else:
            s["label"], s["ref"] = "Backup", "a backup page"
        if s["talk"]:
            s["words"] = words(s["notes"])
            s["seconds"] = s["words"] / wpm * 60
            if s["iframe"]:
                s["seconds"] = max(s["seconds"], ANIM_S.get(s["id"], 0))
            clock += s["seconds"]
            s["clock"] = clock
    return clock


def mmss(sec, step=5):
    sec = round(sec / step) * step
    return f"{int(sec // 60)}:{int(sec % 60):02d}"


def resolve(ptr, slides):
    """A pointer of the prepared answers ('rest-contract; Backup: the contract in full') as
    the slides to show: ['slide 5 (PDF page 7)', 'backup B1 (PDF page 21)']."""
    out = []
    for part in ptr.split(";"):
        part = re.sub(r'\s+', ' ', part).strip()   # a pointer may wrap over two lines of the notes
        if part.lower().startswith("backup:"):
            key = part.split(":", 1)[1].strip().lower()
            hit = next((s for s in slides if not s["talk"] and s["counted"] and key in s["title"].lower()), None)
        else:
            hit = next((s for s in slides if s["id"] == part), None)
        if hit is None:
            raise SystemExit(f"prepared answers: the pointer '{part}' names no slide")
        out.append(f"{hit['ref']} (PDF page {hit['page']})")
    return out


def parse_answers(answers, slides):
    """The prepared answers as (heading, lead paragraph, [(question, answer, [slides to show])])."""
    head, _, rest = answers.partition("\n")
    head = re.sub(r'^#+\s*', '', head).strip()
    lead, _, bullets = rest.partition("\n- **")
    items = []
    for q, body in re.findall(r'(?ms)^- \*\*(.*?)\*\*(.*?)(?=^- \*\*|\Z)', "- **" + bullets):
        ptrs = [p for ptr in re.findall(r'\[([^\]]+)\]', body) for p in resolve(ptr, slides)]
        ans = re.sub(r'\s+', ' ', re.sub(r'\s*\[[^\]]+\]', '', body)).strip()
        items.append((re.sub(r'\s+', ' ', q).strip(), ans, ptrs))
    return head, re.sub(r'\s+', ' ', lead).strip(), items


def before_you_start(slides, total, wpm):
    """What a presenter who has not seen the deck needs to know, as (lead, text) pairs."""
    talk = [s for s in slides if s["talk"]]
    anims = [s for s in talk if s["iframe"]]
    counted = [s for s in talk if s["counted"]]
    skip = next(s for s in slides if s["id"] == SKIP)
    lo, hi = min(ANIM_S[s["id"]] for s in anims), max(ANIM_S[s["id"]] for s in anims)
    return [
        ("The slides", f"Open {DECK_URL} in a browser and press F for full screen (the QR code on the title slide "
                       f"is the same address). Keep {SLIDES_PDF} on the laptop too: the same deck, one page per "
                       "slide, and it works without a network."),
        ("What to read", "Read the plain text aloud. Text in square brackets is a note to you, not speech."),
        ("Moving on", f"{len(talk)} screens: the title, {len(counted)} numbered slides, {len(anims)} animations and the "
                      "closing slide. One press of the right arrow or the clicker per screen; nothing builds inside "
                      "a slide."),
        ("Animations", f"Each starts by itself, runs {lo:.0f} to {hi:.0f} seconds and stops on its last picture. Start "
                       "reading when it appears; move on when you have finished the text. The PDF shows only the "
                       "last picture; the text fits both."),
        ("Pace", f"{sum(s['words'] for s in talk)} words: about {total / 60:.0f} minutes at a calm {wpm:.0f} words a "
                 f"minute, leaving about {SLOT_MIN - total / 60:.0f} for questions. The clock given for each slide is "
                 f"the time when you finish it. Running late? Skip {skip['ref']} ({skip['title']}): it saves about "
                 "a minute."),
        ("In the browser", "G, a number, Enter jumps to that slide (the PDF page numbers given here). S opens a "
                           "second window with this text, the next slide and a timer. Backup slides for questions "
                           "follow the closing slide."),
        ("Questions", "Prepared answers are at the end. If a question is not there, do not guess: Alp is on the "
                      "Teams call and can take it."),
        ("How to say it", 'ADS-IDAC is "A-D-S eye-dack"; RELAP5 is "ree-lap five"; LZ4 is "L-Z-four"; OpenPRA is '
                          '"open P-R-A"; SAS4A/SASSYS-1 is "sass four A, sassis one".'),
    ]


def heading(s):
    return s["label"] + (" · " + s["title"] if s["title"] else "")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", default="slides")
    ap.add_argument("--wpm", type=float, default=140)
    ap.add_argument("--out", default="script/ars2026-script.md")
    a = ap.parse_args()
    slides, answers = load(a.src)
    total = timeline(slides, a.wpm)
    talk = [s for s in slides if s["talk"]]

    out = ["# Presenter's script, ARS 2026\n",
           f"**{TITLE}.** {AUTHORS}. Presented by {PRESENTER}. {SLOT}\n",
           f"**The talk in brief.** {GIST}\n",
           "The same script with a picture of every slide: `ars2026-script.pdf` and `ars2026-script.html`, in\n"
           "this folder. All of them are generated from the speaker notes: edit the notes in `slides/`, then run\n"
           "`make script`.\n",
           "## Before you start\n"]
    out.append("\n".join(f"- **{lead}.** {text}" for lead, text in before_you_start(slides, total, a.wpm)) + "\n")
    out.append("---\n")
    for s in talk:
        out.append(f"## {heading(s)}\n")
        out.append(f"[PDF page {s['page']} · {s['words']} words, about {round(s['seconds'] / 5) * 5:.0f} s · "
                   f"clock when you finish: {mmss(s['clock'])}]\n")
        out.append(s["notes"] + "\n")
    if answers:
        head, lead, items = parse_answers(answers, slides)
        out.append("---\n")
        out.append(f"## {head}\n")
        if lead:
            out.append(lead + "\n")
        for q, ans, ptrs in items:
            out.append(f"- **{q}** {ans}" + (f" *Show: {'; '.join(ptrs)}.*" if ptrs else ""))
        out.append("")
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(out))
    print(f"wrote {a.out}: {len(talk)} screens, {sum(s['words'] for s in talk)} spoken words, "
          f"{total / 60:.1f} min at {a.wpm:.0f} wpm")
