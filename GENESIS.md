# GENESIS — How TBO rose again

> Every resurrection starts with a single commit. This is the story of TBO's.

---

## The abandoned project

In 2013, a small comic editor called **TBO** went silent.

It was a free, GPL-licensed tool written in **C and GTK 3**, built around pages,
panels, text, images, and SVG artwork. It worked. People could make comics with
it. And then, one day, the development stopped. The last release was 1.0. The
repository sat untouched for more than a decade, gathering dust.

Nobody "planned" to abandon it. It just happened — the way open-source projects
fade when their maintainer moves on. The code stayed on disk, the format stayed
compatible, and the idea stayed in the back of a drawer.

Then, in 2026, someone opened that drawer again.

---

## The decision

The original codebase was roughly 8,800 lines of C. It depended on obsolete GTK
APIs, gnome-common, intltool and an autotools build from another era. Porting it
by hand, line by line, would have been a long, thankless marathon — and the
result would still carry the old architectural problems.

The decision was to **reimplement, not transliterate**. Rebuild the application
around a testable model, a modern UI, and explicit compatibility with the
existing `.tbo` files. And to do it in **Python and PyQt6**, with the help of an
AI coding agent.

That decision changed the project's future.

---

## What that first commit really did

The ROADMAP it introduced became the contract between the maintainer and the
AI agent. Every session began the same way:

> *"Continue with the port of this program to PyQt6. First review the current
> state of the project and the changes already made before modifying files."*

And every time, the roadmap told both sides where they were and where to go
next:

- **Phase 1** — a small, installable, testable skeleton.
- **Phase 2** — the document model and the safe `.tbo` reader/writer.
- **Phase 3** — the canvas and a shared renderer for screen and export.
- **Phase 4** — reversible editing commands and undo/redo.
- **Phase 5** — session recovery, preferences, theming, i18n.
- **Phase 6** — Debian packages, Flatpak manifests, CI, releases.
- **Phase 7** — everything that must wait until after 2.0.

One commit, one plan, one resurrection.

---

## Why AI is the right tool for reviving dead software

The author of this resurrection used an AI coding agent
(OpenCode + DeepSeek V4 Flash) to bring TBO back. The reasons matter:

1. **Dead code is perfect training material.** A project with a clear format
   (`.tbo`), a clear behavior (read → edit → save → reopen) and a clear goal
   (PyQt6 parity) is exactly the kind of task an agent can hold in context and
   work through across sessions.

2. **The agent never gets bored.** Porting 8,800 lines across dozens of files is
   repetitive. The agent happily re-ran tests, fixed the parser, rebuilt the
   `.deb`, regenerated translations, and documented the whole thing.

3. **The roadmap keeps it honest.** Because every change went through the
   roadmap, the project stayed coherent instead of becoming a pile of AI
   experiments. The roadmap is the guardrail.

4. **Human judgment stays in charge.** The AI proposed; the maintainer decided.
   The AI wrote; the maintainer tested. The AI suggested; the maintainer said
   *"keep it as the original developer made it"* or *"move that to its own tab"*.
   The tool accelerates; the human steers.

---

## For developers who are skeptical about AI

If you are reluctant to use AI to develop software, ask yourself one question:

> Is the alternative — leaving a useful, abandoned program in the dark — really
> better?

You do not need the AI to "be right" all the time. You need it to *keep
working*. Review the code, run the tests, keep the plan, and let the agent do
the heavy lifting. The ROADMAP is your checklist; the test suite is your truth.

This project went from a 2013 C/GTK orphan to a modern Python/PyQt6 application
with:

- a safe `.tbo` reader/writer and atomic saves;
- an interactive canvas with panels, objects, and full undo/redo;
- an asset library with a buildable character;
- PNG/PDF/SVG export and a presentation mode;
- English and Spanish translations via Qt Linguist;
- a Debian package, a Flatpak manifest, and CI workflows;
- a repository reorganized so the future lives at the root and the past lives
  under `legacy/`.

All of it — the port, the packaging, the translations, and even this very file —
was produced with the help of an AI coding agent.

---

## The first commit is the hardest part

Write the plan first. Make the first commit a commit of intent. Then open the
editor, point the agent at the roadmap, and say:

> *"Continúa con el port de este programa a PyQt6."*

or, in English:

> *"Continue with the port of this program to PyQt6."*

Then let it work.

---

## The first prompt (a template you can copy)

If you are starting a port of your own, here is a complete, battle-tested first
prompt. It tells the agent to explore before touching anything, to produce a
roadmap, and to start with a small, testable skeleton:

```text
You are working on TBO, a comic editor originally written in C and GTK 3
(unmaintained since 2013). The legacy source code lives in the `legacy/`
directory at the repository root.

Your task is to port this program to Python and PyQt6 as TBO 2. Before
modifying anything, do the following in order:

1. EXPLORE — Read the legacy code under `legacy/src/` and the historical
   documentation under `legacy/doc/`, `legacy/po/`, and the root files. Do NOT
   modify or create any files yet. Summarize:
   - what the application does (its features and data model);
   - the structure of the legacy `.tbo` format (root element, attributes,
     objects, transforms, colors, paths);
   - the main architectural pieces (document model, canvas, tools, save/load,
     export);
   - which behaviors must be preserved for compatibility.

2. PLAN — Propose a ROADMAP.md for the modernization to PyQt6, with phases and
   exit criteria, following these principles:
   - Reimplement, do not transliterate: keep useful behavior, not the C
     structure or its defects.
   - The document model must be independent of Qt widgets (plain dataclasses),
     so documents can load, modify, and export without opening a window.
   - Every document change must be an undoable command (QUndoStack).
   - Read/write the legacy `.tbo` v1 format with a safe parser: size limits,
     strict validation, contextual errors, and atomic saves. Treat user files
     as untrusted input.
   - The legacy code stays in `legacy/` as a reference oracle; do not grow it.

3. After I approve the plan, start with the first phase: a small, installable,
   testable Python skeleton (pyproject.toml, package layout under `src/tbo/`,
   tests with pytest/pytest-qt) that opens a minimal PyQt6 window.

Throughout the work:
- Before each step, re-check the current state of the repository and the
  changes already made before modifying files.
- Run the test suite after meaningful changes and keep it green.
- Use clear, conventional commit messages (e.g. `feat(...)`, `fix(...)`,
  `docs(...)`), one logical change per commit.
- Ask me when a decision affects compatibility, licensing, or the file format
  instead of guessing.
```

Why this prompt works:

- **Explore first, touch nothing**: the agent studies the code before writing
  any.
- **Summarize the format and the architecture**: forces it to understand the
  "oracle" before reimplementing.
- **State the principles explicitly**: reimplement, widget-free model, undoable
  commands, safe parser, legacy as reference.
- **Roadmap before code**: the same idea as the first commit.
- **Set the work rules**: re-check state before each step, keep tests green,
  conventional commits, ask before touching compatibility, licensing, or format.

Replace `TBO`, `legacy/`, and `src/tbo/` with your own project names, and the
same template will take you from an abandoned codebase to a modern port.

---

## The first commit

The first prompt ends with a clear instruction: *propose a ROADMAP.md before
writing code*. So the very first commit of the resurrection was not code — it
was that plan:

```bash
git add ROADMAP.md
git commit -m "docs(roadmap): pivot to Python/PyQt6 reimplementation"
```

A port without a plan is a wandering session; a port with a roadmap is a
project. That commit did not compile, but it made everything else possible.

---

> *"Behold, I will do a new thing; now it shall spring forth; shall ye not know
> it? I will even make a way in the wilderness, and rivers in the desert."*
>
> — Isaiah 43:19 (King James Version)

God bless you.
