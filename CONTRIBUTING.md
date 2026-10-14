# Contributing to TBO 2

Thank you for considering it. This project is at an early stage, which means small
contributions have a visible effect and there is no large codebase to learn before you can be
useful.

For the practical steps — cloning, setting up an environment, running the tests, and the
prompt to hand your AI agent — see
**[Contributing in the README](README.md#contributing)**. This document covers what a change
needs to look like once you have made it.

## What is most useful right now

The [roadmap](ROADMAP.md) is organised in phases, each with verifiable exit criteria. Anything
marked as unfinished in a phase that is currently in progress is fair game.

If you want a suggestion, these are small and self-contained:

- **Visual regression tests** with reference images and a documented tolerance, so a renderer
  change cannot silently alter output.
- **`docs/file-format-v1.md`**, written from the observed behaviour of the legacy reader in
  `legacy/`, including decimal separators and path handling.
- **Stable identifiers** between the domain objects and their `QGraphicsItem` counterparts.
- **More `.tbo` fixtures**: Unicode, long paths, external images, transforms, multiple pages,
  and documents with missing resources.
- **A formatter and an `EditorConfig`**, so diffs stop being about whitespace.
- **Qt tests in CI**, currently local-only because tearing down a `QGraphicsView` aborts under
  a headless runner.
- **Packaging**: a Flatpak build that works again, and a release job that publishes artifacts
  instead of leaving them to expire.

If you would rather discuss an idea first, open a
[Discussion](https://github.com/wachin/TBO/discussions) or an
[issue](https://github.com/wachin/TBO/issues). Asking costs nothing and prevents a wasted
afternoon.

## The rules of the game

1. **One logical change per pull request.** Do not combine formatting, refactoring and
   behaviour changes. A pull request that does three things cannot be reviewed or reverted.
2. **Every change needs evidence.** Add a test, or explain in the description exactly how you
   verified it by hand. "It works" is not evidence.
3. **The document model is the source of truth.** Qt is a view of it, never the other way
   around. If a change requires the model to know about widgets, something is wrong.
4. **Every document mutation goes through a command.** Undo and redo are a feature, not a
   convenience: a change that bypasses `QUndoStack` will be sent back.
5. **Compatibility with `.tbo` is not negotiable.** The format is why the project exists. If a
   change affects reading or writing it, say so in the pull request.
6. **Keep the test suite green.** Run it before opening the pull request.
7. **Ask instead of guessing** when a decision affects compatibility, licensing or the file
   format.

## Working with an AI agent

The project is developed with AI coding agents and that is a supported way to contribute, not a
shortcut to be hidden. Two things make the difference between an agent that helps and one that
creates work for a reviewer:

- **Make it read before it writes.** The
  [first prompt](README.md#the-prompt-that-started-this-project) exists for that reason: it
  requires the agent to explore the legacy code and agree on a plan before creating a single
  file. An agent that starts editing immediately will produce a plausible change that ignores
  three constraints it never read.
- **You are responsible for the result.** Read the diff. If you cannot explain why a line is
  there, it does not belong in the pull request. "The agent wrote it" is not a justification a
  reviewer can accept.

Agents are good at the mechanical part — finding every call site, writing the test that covers
the branch you just added, keeping a refactor consistent across files. They are not good at
knowing what this project values. That part is yours.

## Commits and pull requests

Commit messages follow the [Conventional Commits](https://www.conventionalcommits.org/)
convention, matching the existing history:

```text
feat(canvas): keep panel identifiers stable across reloads
fix(tbo): reject documents with a non-finite scale
docs: describe the legacy decimal separator handling
test(export): cover SVG output for an empty page
chore(ci): run the Qt integration tests under Xvfb
```

A good pull request description answers four questions:

1. What was wrong, or what was missing?
2. What did you change?
3. How did you verify it? (test name, command, or manual steps)
4. What did you deliberately leave out?

If the change is visible in the interface, a screenshot or a short recording is worth more than
a paragraph.

## Licensing

TBO 2 is released under the **GNU GPL v3 or later**. By submitting a contribution you agree
that it may be distributed under the same terms. Do not paste code from a project with an
incompatible licence, and do not paste code you do not have the right to contribute — this
includes large blocks generated verbatim from a model whose training data you cannot account
for. Small, reviewed, understood changes are the expectation; wholesale generated files are
not.

The original C/GTK implementation lives in `legacy/` as a reference and remains the work of its
original authors, credited in [AUTHORS](AUTHORS).

## Reporting bugs

Open an [issue](https://github.com/wachin/TBO/issues) with:

- what you did, what you expected, and what happened instead;
- the TBO version and your operating system;
- if the application closed unexpectedly, whatever it printed in the terminal.

**If a `.tbo` document causes a crash**, that is a priority. Attach it if you can share it, or
say so if you cannot — a description of its structure is still useful.

If a security scanner flags a release artifact, please say so in an issue. False positives are
reported to the vendor concerned, which is the only way they get fixed. See
[docs/virustotal](docs/virustotal/README.md) for how the released binaries are checked.

## Code of conduct

Be straightforward and be kind. Critique the change, not the person who made it. Assume the
other person is acting in good faith, and explain your reasoning when you disagree — a review
comment that says only "no" wastes everybody's time.
