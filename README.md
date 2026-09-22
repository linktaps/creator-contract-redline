# creator-contract-redline

A Claude Skill for redlining creator/influencer contracts against a fixed
mutuality checklist, applying every edit as a tracked (Suggested) change in the
document so the creator never has to touch it.

The result is a redlined `.docx` file that works fully in Google Docs and Word. The
skill only adds tracked suggestions and never silently rewrites the brand's
text, so every change shows up as a suggestion to accept or reject.

The cheapest way is to upload a `.docx`. If the contract is a Google Doc, choose
**File → Download → Microsoft Word (.docx)** and upload that file. Claude can
also type the edits straight into a Google Doc in Suggesting mode during a
Claude in Chrome session, but that takes much longer and uses more of your
Claude usage.

> **Not legal advice.** This is a checklist and a set of editing tools, not a
> lawyer. It will be wrong sometimes. Read the redline before you send it and
> the contract before you sign it. See [DISCLAIMER.md](DISCLAIMER.md).

## Quick start: add it to the Claude desktop app

No coding needed. Takes about a minute.

1. Open the Claude desktop app and go to **Settings → Plugins**.
2. Choose to add a marketplace, and paste this:
   ```
   linktaps/creator-contract-redline
   ```
3. Find **creator-contract-redline** in the list and click **Install**.
4. Start a new chat, attach the contract as a `.docx` (for a Google Doc, use
   **File → Download → Microsoft Word**), and ask
   something like *"Can you redline this brand deal for me?"*
   Optional but helpful: also paste anything you've already agreed with the
   brand, such as the brief, the deliverables or rate, or emails and DMs about
   the deal.

Claude sends back a marked-up copy with every change as a suggestion the brand
can accept or reject. To get newer versions later, click **Update** on the same
Settings → Plugins screen.

Using the command line or Codex instead? See [Install](#install) below.

## What it does

Brand-drafted influencer agreements are written to protect the brand, and most
of the one-sidedness is not malice — it is a template nobody rebalanced. This
skill reads the whole agreement including schedules, compares it against a fixed
list of items that are commonly adverse, and writes suggested changes into the
document as native tracked changes that the brand can accept or reject clause by
clause.

It is built around one specific failure: **quietly dropping items.** Long
reviews get interrupted, memory of "what's done" degrades, and the model reports
completion while must-haves sit untouched. The tracking table, the three audit
passes and the two gates all exist because of that.

## Install

**Claude Code**, as a plugin marketplace:

```
/plugin marketplace add linktaps/creator-contract-redline
/plugin install creator-contract-redline@creator-contract-redline
```

**Codex CLI**, from the same repository. Codex reads Claude-style marketplaces
directly:

```bash
codex plugin marketplace add https://github.com/linktaps/creator-contract-redline.git
codex plugin add creator-contract-redline@creator-contract-redline
```

Then invoke it as `$creator-contract-redline` in a new thread.

**As a standalone skill**, for either tool: clone anywhere and link the skill
directory into the folder the tool scans. Claude Code scans `~/.claude/skills`,
Codex scans `~/.agents/skills`.

```bash
git clone https://github.com/linktaps/creator-contract-redline.git
ln -s "$PWD/creator-contract-redline/skills/creator-contract-redline" ~/.agents/skills/
```

## Layout

The skill lives under `skills/creator-contract-redline/` because that is the
one shape every host discovers: Claude Code and Codex both look for
`skills/<name>/SKILL.md` inside a plugin, and for `<name>/SKILL.md` inside a
personal skills folder. Everything the skill needs at run time — the checklist,
the editing standards and the two scripts — sits inside that directory, so it
can be copied or linked anywhere as a unit.

```
.claude-plugin/
  marketplace.json                  marketplace definition
  plugin.json                       plugin manifest
skills/creator-contract-redline/
  SKILL.md                          workflow, tracking, the three audit passes
  references/review-checklist.md    the scope of the review — 20+ compound items
  references/editing-standards.md   what a clean, surgical suggestion looks like
  references/docx-round-trip.md     authoring tracked changes in XML
  scripts/audit_suggestions.py      the Pass 1 gate
  scripts/apply_tracked_changes.py  author suggestions into a .docx, with guards
  scripts/accept_all.py             clean copy (every suggestion accepted), self-verified
  scripts/reject_all.py             the mirror: every suggestion rejected
```

## The audit script

Google Docs suggestions and Word tracked changes are the same thing on disk, so
a redline can be reconstructed two ways — with every suggestion accepted, and
with every one rejected. Auditing from a plain-text export cannot do this:
insertions and deletions run together, so struck language reads identically to
untouched language.

```bash
# fidelity: would rejecting the whole redline restore the brand's draft?
python skills/creator-contract-redline/scripts/audit_suggestions.py redline.docx --baseline brand-draft.docx --author "Creator Name"

# completeness: are the adverse phrases gone, and did the new wording land?
python skills/creator-contract-redline/scripts/audit_suggestions.py redline.docx --check phrases.txt --additions additions.txt

# what's in the document and who authored it
python skills/creator-contract-redline/scripts/audit_suggestions.py redline.docx --list
```

Exits non-zero when anything is unresolved, so it can hard-gate the workflow.

The phrase gate proves the bad language left. It cannot see additions, and
roughly half a mutuality redline is additions — so `--additions` asserts each
expected new clause appears exactly once (or `:: xN` times, for wording that
belongs in several clauses). `--baseline` also checks that every
other part of the package is byte-identical to the brand's draft, and with
`--author` that the other side's pending suggestions are exactly as they left
them. `--coverage` requires every must-have item and every tagged sub-check
(`#2a`, `#4e`, …) to be named somewhere, and `--prior earlier-redline.docx`
lists every edit an earlier redline of the same contract made that this one
dropped, so a re-run cannot lose work silently.

## The applier

`skills/creator-contract-redline/scripts/apply_tracked_changes.py` writes suggestions into a `.docx` directly.
Express the redline as a list of edits and re-run it from the pristine brand
draft each time; the edit list stays the source of truth.

```python
from apply_tracked_changes import Doc

d = Doc("brand-draft.docx", author="Creator Name")
d.edit("rep", "sixty (60) days", "thirty (30) days", label="net-30")
d.save("redline.docx")
```

Every anchor must match exactly once or it aborts naming the label, anchors
crossing an element boundary are refused, and the XML is parsed before the file
is written — because every check in the audit script is a regex, so malformed
markup passes all of them and fails only when a human opens the file.

## License

[MIT](LICENSE).
