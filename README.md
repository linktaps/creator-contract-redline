# creator-contract-review

A Claude Skill for redlining creator and influencer contracts against a fixed
mutuality checklist, applying every edit by hand in the document so the creator
never has to touch it.

```
SKILL.md                          workflow, scope, tracking, the three audit passes
references/review-checklist.md    the scope of the review — 20+ compound items
references/editing-standards.md   what a clean, surgical suggestion looks like
references/docx-round-trip.md     authoring tracked changes in XML and importing them
scripts/audit_suggestions.py      the Pass 1 gate: accept-all / reject-all reconstruction
```

## The audit script

```bash
# what's in the document and who authored it
python scripts/audit_suggestions.py redline.docx --list

# fidelity: would rejecting the whole redline restore the brand's draft?
python scripts/audit_suggestions.py redline.docx --baseline brand-draft.docx

# completeness: are the adverse phrases still in the accepted version?
python scripts/audit_suggestions.py redline.docx --check phrases.txt
```

Exits non-zero when anything is unresolved, so it can hard-gate the workflow.

## Installing

Copy this directory into your skills directory, or package it with
`skill-creator`'s `package_skill.py`.
