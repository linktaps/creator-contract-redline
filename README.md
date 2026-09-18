# creator-contract-redline

A Claude Skill for redlining creator and influencer contracts against a fixed
mutuality checklist, applying every edit as a tracked change in the document so
the creator never has to touch it.

> **Not legal advice.** This is a checklist and a set of editing tools, not a
> lawyer. It will be wrong sometimes. Read the redline before you send it and
> the contract before you sign it. See [DISCLAIMER.md](DISCLAIMER.md).

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

As a plugin marketplace:

```
/plugin marketplace add linktaps/creator-contract-redline
/plugin install creator-contract-redline@creator-contract-redline
```

Or clone it straight into your personal skills folder:

```bash
git clone https://github.com/linktaps/creator-contract-redline.git \
  ~/.claude/skills/creator-contract-redline
```

## Layout

This is a single-skill plugin, so `SKILL.md` sits at the plugin root rather than
under `skills/`. That keeps the slash form `/creator-contract-redline` instead of
the doubled `/creator-contract-redline:creator-contract-redline`, and it means
the repository root is also a working skill directory you can copy anywhere.

```
.claude-plugin/
  marketplace.json                  marketplace definition
  plugin.json                       plugin manifest
SKILL.md                            workflow, tracking, the three audit passes
references/review-checklist.md      the scope of the review — 20+ compound items
references/editing-standards.md     what a clean, surgical suggestion looks like
references/docx-round-trip.md       authoring tracked changes in XML
scripts/audit_suggestions.py        the Pass 1 gate
scripts/apply_tracked_changes.py    author suggestions into a .docx, with guards
```

## The audit script

Google Docs suggestions and Word tracked changes are the same thing on disk, so
a redline can be reconstructed two ways — with every suggestion accepted, and
with every one rejected. Auditing from a plain-text export cannot do this:
insertions and deletions run together, so struck language reads identically to
untouched language.

```bash
# fidelity: would rejecting the whole redline restore the brand's draft?
python scripts/audit_suggestions.py redline.docx --baseline brand-draft.docx

# completeness: are the adverse phrases still in the accepted version?
python scripts/audit_suggestions.py redline.docx --check phrases.txt

# what's in the document and who authored it
python scripts/audit_suggestions.py redline.docx --list
```

Exits non-zero when anything is unresolved, so it can hard-gate the workflow.

The phrase gate proves the bad language left. It cannot see additions, and
roughly half a mutuality redline is additions — so assert the expected new
wording separately.

## The applier

`scripts/apply_tracked_changes.py` writes suggestions into a `.docx` directly.
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
