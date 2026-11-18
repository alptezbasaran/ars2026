# Presenter's script, ARS 2026

**From ADS-IDAC to OpenPRA: Enabling Dynamic Probabilistic Risk Assessment for Advanced Reactors.** Alp Tezbasaran and Mihai A. Diaconeasa, North Carolina State University. Presented by Kirill Shumilov. ARS 2026, session Uncertainty Quantification, room Bougainvillea (program as read on November 15). Wednesday, November 18, 2026, 10:40 to 11:00 MST, the third of five talks: a 20 minute slot.

**The talk in brief.** Dynamic PRA grows the event tree while a plant simulator runs. The paper shows how one such engine, ADS-IDAC, was rebuilt in two moves: the plant physics became a service behind an interface of six endpoints, so that other codes connect without merging code, and the tree is now traversed in parallel. The evidence: a web workflow, two very different reactors behind the same interface, a run that is 156 times faster on a laptop, and trees of tens of thousands of sequences generated in under an hour.

The same script with a picture of every slide: `ars2026-script.pdf` and `ars2026-script.html`, in
this folder. All of them are generated from the speaker notes: edit the notes in `slides/`, then run
`make script`.

## Before you start

- **The slides.** The meeting's presenter template says to bring the slides on a USB drive and to use the session room's laptop, not your own: put ars2026-slides.pdf on a drive. If that laptop has a network connection, open https://alptezbasaran.github.io/ars2026/ in its browser instead and press F for full screen: the animations play there. The QR code on the title slide is the same address.
- **What to read.** Read the plain text aloud. Text in square brackets is a note to you, not speech.
- **Moving on.** 19 screens: the title, 14 numbered slides, 3 animations and the closing slide. One press of the right arrow or the clicker per screen; nothing builds inside a slide.
- **Animations.** Each starts by itself, runs 34 to 38 seconds and stops on its last picture. Start reading when it appears; move on when you have finished the text. The PDF shows only the last picture; the text fits both.
- **Pace.** 2055 words: about 15 minutes at a calm 140 words a minute, leaving about 5 for questions. The clock given for each slide is the time when you finish it. Running late? Skip slide 7 (Large trees stay in memory, and a study can stop and resume): it saves about a minute.
- **In the browser.** G, a number, Enter jumps to that slide (the PDF page numbers given here). S opens a second window with this text, the next slide and a timer. Backup slides for questions follow the closing slide.
- **Questions.** Prepared answers are at the end. If a question is not there, do not guess: Alp is on the Teams call and can take it.
- **How to say it.** ADS-IDAC is "A-D-S eye-dack"; RELAP5 is "ree-lap five"; LZ4 is "L-Z-four"; OpenPRA is "open P-R-A"; SAS4A/SASSYS-1 is "sass four A, sassis one".

---

## Title slide

[PDF page 1 · 82 words, about 35 s · clock when you finish: 0:35]

Good morning. My name is Kirill Shumilov, and I am presenting work by Alp
Tezbasaran and Mihai Diaconeasa, at NC State.

This talk is about tooling. Dynamic PRA is the right method for advanced
reactors, and the paper shows what it took to turn one dynamic PRA engine,
ADS-IDAC, into a platform that other codes can connect to and that runs at
scale, on its way into OpenPRA.

The slides are online, and the QR code on this slide opens them.

## Slide 1 of 14 · Advanced reactors are where the fixed event tree is weakest

[PDF page 2 · 110 words, about 45 s · clock when you finish: 1:20]

Why do advanced reactors need dynamic PRA? A classical PRA fixes the accident
sequences before any computation: the analyst draws the event tree, and timing
enters only through success criteria and human error probabilities.

That is weakest exactly where advanced reactors differ from the operating
fleet. Passive safety is not a component that works or fails; its success is
the outcome of a thermal-hydraulic transient. There is little operating
experience to fix the sequences in advance. And the operating concepts are
new: reduced staffing, remote supervision, autonomous control.

Dynamic PRA grows the tree while a simulator runs, so the sequences are an
output of the analysis, not an input.

## Animation 1a · How a dynamic event tree is built

[PDF page 3 · 100 words, about 45 s · clock when you finish: 2:05]

[Animation. It starts by itself, runs about thirty-eight seconds and stops on
its last picture. Start reading as soon as it appears, and move on when you
have finished the text. The slide PDF shows the last picture only; the text is
the same.]

Here is how such a tree is built. A plant simulation starts at the initiating
event, on the left. At every pivotal event, marked with a flag, the full state
is saved, and one branch starts for each possible outcome: a component fails
or holds, the crew acts early or late. Between the flags it is deterministic
physics.

Each branch carries a conditional probability, and the sequences end at
different times, in different end states. The tree is the output. And every
pivotal event is a record: the time, the saved state, the trigger, and each
alternative with its probability.

## Slide 2 of 14 · Two barriers to routine dynamic PRA

[PDF page 4 · 117 words, about 50 s · clock when you finish: 2:55]

If the method fits this well, why is it not in routine use? The method is more
than twenty years old, and what held it back is tooling. Two barriers keep
coming back.

The first is monolithic coupling: the engine is welded to one physics code, in
one process, so moving it to the physics of an advanced reactor means merging
code.

The second is combinatorial growth: every branch point multiplies the
sequences, and each sequence is a full transient. A proper dynamic PRA takes
tens to hundreds of thousands of simulations, perhaps more.

ADS-IDAC, which couples RELAP5, the IDAC crew model, and hardware reliability,
had both: one physics code, and one sequence at a time.

## Slide 3 of 14 · Two moves that remove the barriers

[PDF page 5 · 81 words, about 35 s · clock when you finish: 3:30]

So the work is two moves, one for each barrier.

The first move separates the PRA core, meaning time advancement, branching,
and the crew model, from the plant physics. Physics becomes a service behind a
documented interface. The second move traverses the tree in parallel.

Both rest on one primitive, checkpoint and restore: save the complete state of
a simulation, and bring it back to life somewhere else.

I will take the two moves in turn, and then show the evidence.

## Slide 4 of 14 · Move 1: physics behind a RESTful interface

[PDF page 6 · 127 words, about 55 s · clock when you finish: 4:25]

Move one. On the left is the engine as it was: the PRA core and RELAP5
compiled into one process. On the right is the same core, but every access to
the physics now goes through a solver interface, and the core asks for exactly
five things: advance time, apply an intervention, report state, checkpoint,
and restore.

There are two implementations. RELAP5 still runs in process, which keeps the
validated coupling. And a REST client drives any external solver over HTTP:
that is the RESTful interface.

The checkpoint is the key element. It returns the complete state as an opaque
buffer, and restore rebuilds it, so the transient continues as if never
interrupted. For RELAP5, that meant replacing the disk-based restart with an
in-memory one.

## Slide 5 of 14 · The whole interface: six endpoints

[PDF page 7 · 115 words, about 50 s · clock when you finish: 5:15]

This table is the whole interface, which the paper calls the solver contract.
The solver is a service that holds sessions. Six endpoints change state, and
two only read.

The data format is deliberately generic. Every advance returns five arrays:
volumes, junctions, control variables, and two kinds of trips. A mapper on the
solver side packs the solver's own state into those arrays, so the engine
never parses a plant-specific field.

Trips fire once and latch, and the engine derives pivotal events from them, so
the rules for branching are part of the interface.

Coupling a new code means implementing these six endpoints: not merging code,
not matching a compiler, not sharing a process.

## Animation 5a · The interface in action

[PDF page 8 · 110 words, about 45 s · clock when you finish: 6:00]

[Animation, about thirty-eight seconds. It starts by itself and stops on its
last picture; the slide PDF shows that picture only.]

Here is the interface in action, as one sequence. On the left, the engine; in
the middle, the six verbs; on the right, an advanced reactor simulator in
RELAP5's place: for example SAM, SAS4A/SASSYS-1, RELAP5-3D, MELCOR, or your
own code. None of these is coupled yet; the point is that the engine does not
care which.

A trip fires inside an advance response and becomes a pivotal event. The
checkpoint comes back as a token that the engine never looks inside, and the
restore takes the other branch.

At the bottom right are the two services that use this interface today: a PWR
and a space reactor.

## Slide 6 of 14 · Move 2: the tree is traversed in parallel

[PDF page 9 · 125 words, about 55 s · clock when you finish: 6:55]

Move two. Once the state can be checkpointed, sibling sequences are
independent, so the tree should be easy to run in parallel. The difficulty is
that the work is not known in advance: a branch exists only when a simulation
reaches a pivotal event. So the scheduler has to be dynamic.

Rank zero is a server that never runs physics and only does the bookkeeping.
When a worker branches, it keeps the restart state and tells the server two
integers. When the server pairs that branch with a free worker, the state
travels directly from worker to worker.

So the server stays near twenty-five megabytes whatever the size of the tree.
And if no other worker is free, the worker runs its own branch.

## Animation 6a · The parallel engine in action

[PDF page 10 · 89 words, about 40 s · clock when you finish: 7:35]

[Animation, about thirty-four seconds. It starts by itself and stops on its
last picture; the slide PDF shows that picture only.]

Here it is on a small tree. On the left, rank zero: a table of workers and a
queue, and no simulation state. In the middle, six workers, each running one
transient.

A worker reaches a branch point, saves its state, reports two numbers, and
keeps going. The server pairs the branch with a free worker, and the state
moves from worker to worker.

On the right, the same tree builds up in simulation time. At the end the
outputs merge into one tree, identical to the serial run.

## Slide 7 of 14 · Large trees stay in memory, and a study can stop and resume

[PDF page 11 · 123 words, about 55 s · clock when you finish: 8:25]

[If you are running late, skip this slide. It saves about a minute.]

Two more things make large trees practical.

First, memory. The queued restart data can be compressed with LZ4, about three
to one, which cuts both peak memory and message traffic. And an adaptive limit
moves individual restart operations between memory and files, so a run slows
down instead of failing when a tree outgrows the memory.

Second, a study can stop and resume, thanks to the same checkpoint primitive.
The whole study can be saved and picked up again in a different mode or on a
different number of ranks: a serial study resumes under MPI, a twelve-rank
study on four.

And the merged output of a parallel run has the same layout as a serial run,
which the validation tests check.

## Slide 8 of 14 · Dynamic event trees from a web browser

[PDF page 12 · 124 words, about 55 s · clock when you finish: 9:20]

The same interface also makes the method easier to get into. A web workflow
builds dynamic event trees from a browser, against any solver that implements
the interface.

In the model builder, on the left, you choose the domain, configure the plant,
and schedule operator actions. The monitor, in the middle, shows the tree
growing live: every bar is a sequence, forking at branch points. And the
results view, on the right, is an interactive plot of the pivotal events. None
of it needs MPI, Fortran, or a local toolchain.

One clarification. Branching here comes from scheduled operator actions and
trip firings; the cognitive branching of the IDAC crew model stays in the C++
engine, which drives the same solvers through the same interface.

## Slide 9 of 14 · One interface, two very different reactors

[PDF page 13 · 140 words, about 60 s · clock when you finish: 10:20]

Does the interface really work for any solver? The paper tests that with two
very different plants behind the same interface.

The first is the PWR: RELAP5 at full fidelity, and beside it a lumped PWR
service that implements the interface in a few hundred lines.

The second, in the picture, is a compact space fission reactor for nuclear
electric propulsion: control drums, heat pipes, a closed Brayton converter,
radiators, and Hall thrusters, with thirty-two control variables and forty
trips. It is built from the public information on NASA's SR-1 Freedom.

The space reactor was chosen on purpose. With remote and autonomous operation,
a software policy takes the place of the control-room crew, and this is an
area where dynamic PRA has no established tooling. Between the two reactors,
only the solver service and its mapper differ.

## Slide 10 of 14 · ADS-IDAC now runs anywhere, and much faster

[PDF page 14 · 134 words, about 55 s · clock when you finish: 11:15]

What does all of this buy? ADS-IDAC now runs efficiently on a laptop or a
workstation, and much faster.

The chart follows one benchmark run. The original engine took seven hundred
fifty-two seconds on a workstation. Serial optimizations bring that to a
hundred ninety-three, and a modern toolchain to eighty-one. On a fourteen-core
laptop the same run takes twenty-one seconds on one core, and four point eight
on ten ranks. End to end, that is a hundred fifty-six times faster.

And that comparison is conservative: the seven hundred fifty-two seconds were
timed on a modern workstation with a solid-state disk, so the original setup
was slower still.

This benchmark tree is small. On more realistic scenarios, with many more
sequences, parallelism pays off even more.

## Slide 11 of 14 · Gigantic trees: tens of thousands of sequences

[PDF page 15 · 112 words, about 50 s · clock when you finish: 12:05]

How large can the trees get? These are the two largest so far, both on the
three-loop plant.

On the left, a steam generator tube rupture with every crew decision free to
fork, over a ten-thousand-second mission: twelve thousand three hundred
sequences, and a hundred sixty-nine thousand pivotal events.

On the right, a more realistic scenario on the same plant, in a tree designed
to be wide and deep: thirty-five thousand six hundred sequences in one hour of
mission time, and more than eleven million pivotal events.

The picture is a sample of that second tree. Every line is a full plant
transient with a simulated crew.

## Slide 12 of 14 · Generated efficiently: days of computing become under an hour

[PDF page 16 · 128 words, about 55 s · clock when you finish: 13:00]

And generating these trees is efficient.

The chart shows the time to build the larger tree, about thirty-five thousand
sequences, on a cluster. Each time the number of ranks doubles, the time
halves, all the way to seven hundred sixty-eight ranks. That is ninety-four to
ninety-eight percent of ideal scaling.

On one core, this tree would take about twelve and a half days. On five
hundred twelve ranks, the whole study is one job of under an hour.

The tube-rupture tree converges in fifty-seven minutes on seven hundred
sixty-eight ranks, and a second, independent run reproduced it exactly.

At this scale, the point is not that a tree is faster to generate. It is that
it can be generated at all.

## Slide 13 of 14 · From ADS-IDAC to OpenPRA

[PDF page 17 · 101 words, about 45 s · clock when you finish: 13:40]

Where does it go next? Three threads.

First, a new implementation of the tree core, being brought to byte-identical
agreement with the C++ engine on the reference benchmark.

Second, the destination in the title: integration into the open-source OpenPRA
ecosystem, as its dynamic PRA engine. The modern engine and the web workflow
have been developed for it, and the integration is in progress.

Third, tools to read the output at scale: sequence clustering and interactive
visualization, under active development. Parallel traversal solves the compute
half of the combinatorial problem; reading tens of thousands of sequences is
the other half.

## Slide 14 of 14 · Conclusions

[PDF page 18 · 129 words, about 55 s · clock when you finish: 14:35]

To conclude. Dynamic PRA has been held back by its tooling, not by its theory:
engines welded to one physics code and limited to one sequence at a time. This
work removes both barriers with two moves that rest on one primitive.

Physics is now a service behind an interface of six endpoints, so the models
an advanced reactor needs, including surrogates and digital twins, connect
without merging code. One interface serves a PWR and a space fission reactor.

And the tree is traversed in parallel. ADS-IDAC now runs anywhere and much
faster, and trees of tens of thousands of sequences are generated in under an
hour.

For advanced reactor safety, that turns dynamic PRA from a research method
into a usable capability. The next step is OpenPRA.

## Closing slide

[PDF page 19 · 8 words, about 5 s · clock when you finish: 14:40]

Thank you. We are happy to take questions.

---

## If asked: prepared answers

If a question is not on this list, do not guess: Alp is on the Teams call and can take it.

- **Is the code available?** The closing slide carries the DOI of the ADS-IDAC 5.0.0 release on Zenodo. For access and licensing, Alp is the person to write to. *Show: the closing slide (PDF page 19).*
- **How is this different from RAVEN, ADAPT, MCDET or EMRALD?** Simulator neutrality is not new; ADAPT has it by design. What is different is the form of the coupling: a documented service contract with in-memory state exchange and typed branching semantics, together with a parallel traversal engine and crew cognition in one platform. *Show: backup B3 (PDF page 23).*
- **Why HTTP and not a linked library?** Isolation. A service shares no compiler and no process with the engine, so coupling a new code is implementing endpoints, not merging code. The in-process interface is still there, and RELAP5 uses it. *Show: slide 4 (PDF page 6); backup B1 (PDF page 21).*
- **What does the HTTP hop cost?** The paper does not report it. The validated RELAP5 path stays in process; an external code pays one request per advance. *Show: slide 5 (PDF page 7).*
- **Have you coupled SAM, or any advanced reactor code?** Not yet. Two services speak the contract today, a lumped PWR and a space reactor model, and RELAP5 runs in process behind the same five calls. An advanced reactor system code needs a wrapper that implements the six endpoints, and the code must be able to save and restore its complete state. *Show: slide 5 (PDF page 7); slide 9 (PDF page 13).*
- **Does the browser workflow run the IDAC crew?** No. Its branching comes from scheduled operator actions and trip firings; the cognitive branching is in the C++ engine, which drives the same solvers through the same contract. *Show: slide 8 (PDF page 12).*
- **Is the space reactor NASA's SR-1?** It is a model built from the public description of SR-1 Freedom: HALEU fuel, heat pipes, a closed Brayton converter at twenty kilowatts electric, and Hall thrusters. Little of the design is public, so every other value is an assumption. It is representative, not a design model, and its numbers say nothing about SR-1 itself. *Show: backup B11 (PDF page 33).*
- **Is that spacecraft crewed?** No. Onboard fault protection responds first, and ground commands arrive after the light time. What matters for dynamic PRA is the responder slot: in remote and autonomous operation a software policy sits where the control-room crew sits. *Show: slide 9 (PDF page 13); backup B11 (PDF page 33).*
- **The paper describes a liquid-metal loop, Stirling conversion and seventeen control variables?** That was the model when the paper was written. It has since been rebuilt from the public description of SR-1 Freedom, and the contract did not change. *Show: slide 9 (PDF page 13).*
- **Are the speedups inflated by the serial optimizations?** No: the slide shows each factor as its own step. Parallel speedups are counted against the optimized serial run on the same machine and build, and each cluster number says what it is counted from. *Show: slide 10 (PDF page 14); backup B6 (PDF page 26).*
- **Why is the 156 times conservative?** The 752 seconds were timed on a modern workstation with a solid-state disk, and about half of that time went to re-reading the same files. On slower or shared storage the original engine took longer. *Show: slide 10 (PDF page 14).*
- **What is the modern toolchain?** GNU Fortran at full optimization. The reference Intel build ran RELAP5 without optimization, so this step alone is two to two and a half times. *Show: backup B7 (PDF page 27).*
- **Which machines?** An 8-core Linux workstation and a 14-core Apple-silicon laptop. *Show: backup B6 (PDF page 26).*
- **What exactly is the MPI factor?** 21.4 seconds on one core of the laptop against 4.8 seconds on ten ranks: 4.46 times, rounded to about four on the slide. *Show: slide 10 (PDF page 14); backup B8 (PDF page 28).*
- **Why does parallelism pay more on realistic scenarios?** A wider and deeper tree keeps more workers busy. On the benchmark the tree runs out of branches near ten ranks; on the 35,000-sequence tree the engine keeps 94 to 98 percent of ideal scaling up to 768 ranks. *Show: slide 12 (PDF page 16); backup B13 (PDF page 35).*
- **The paper reports only 1.7 times across eight nodes?** That benchmark tree is deliberately narrowed and runs out of width. On a tree wide enough to feed every worker, the tree phase keeps 94 to 98 percent of ideal scaling up to 768 ranks, counted from each node type's smallest run. *Show: backup B9 (PDF page 29); slide 12 (PDF page 16); backup B13 (PDF page 35).*
- **Are these large trees in the paper?** No. The paper reports the workstation and the first multi-node measurements. The large trees are from Alp's dissertation, NC State 2026, Chapter 3, run on NC State's Hazel cluster. *Show: slide 11 (PDF page 15); backup B9 (PDF page 29).*
- **What is the 12.5 days?** A projection: the worker time measured on the cluster, added up as if one core of the optimized serial engine ran every sequence. *Show: slide 12 (PDF page 16).*
- **Why two lines in the scaling chart?** Two kinds of nodes on the same cluster: 32-core Intel nodes up to 256 ranks, and 192-core AMD nodes from 256 to 768. Each line is compared with its own ideal. *Show: slide 12 (PDF page 16); backup B13 (PDF page 35).*
- **How do you know a resumed study is correct?** Resume is regression tested across execution modes and rank counts: each tested permutation has to reproduce the reference sequence counts, and the cluster resume reproduced the end states of the straight run. *Show: backup B10 (PDF page 32).*
- **Is parallel output the same as serial output?** On the validation cases, yes: each rank writes in its own directory, the merge reproduces the serial layout, and the tests assert that the merged results agree. *Show: slide 7 (PDF page 11).*
- **Is the crew model a validated HRA method?** No. IDAC is a cognitive model of a crew in a closed loop with the plant. It generates behavior and branches; it does not certify human error rates. *Show: backup B5 (PDF page 25).*
- **What about uncertainty quantification?** The tree resolves the aleatory uncertainties into branches. Epistemic uncertainty is an outer loop that repeats the tree, so its cost is the number of samples times the cost of a tree, and parallel traversal divides the second factor. (Optional: the talk before this one in the session, on hierarchical uncertainty propagation, is the place to point.) *Show: slide 12 (PDF page 16).*
- **Fifty-seven minutes for the whole tube-rupture study?** For the tree. The engine's total wall time was 1 h 52 min, because it spent about as long merging its output as computing the tree. That limit was removed before the 35,000-sequence runs, which finish tree, merge and extraction in one job. *Show: slide 12 (PDF page 16).*
- **Is it 35,613 sequences or about 35,000?** The tree's size differs between runs, from 34,918 to 35,613 sequences, about two percent, because staggered hardware failures make some forks sensitive to timing. 35,613 is the run whose histories are shown; the timings come from several runs. The tube-rupture tree reproduces exactly. *Show: slide 11 (PDF page 15); slide 12 (PDF page 16).*
