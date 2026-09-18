---
name: creator-contract-review
description: Redline an influencer, creator, or talent contract on the creator's behalf against a fixed mutuality checklist, applying every edit by hand in the document so the creator never has to touch it. Use this whenever someone shares a brand deal, influencer agreement, SOW, talent agreement, sponsorship contract, or campaign paperwork and wants it reviewed, redlined, marked up, negotiated, checked for fairness, or made mutual — including when they just ask "is this contract okay?", "what should I push back on?", or "can you mark this up before I send it to their legal team?". Also use when revising or auditing a redline that is already in progress.
---

# Creator Contract Review

Brand-drafted influencer agreements are written to protect the brand. Most one-sidedness is not malice — it is a template that nobody rebalanced. The job is to make the agreement mutual without making the creator look difficult, because the creator has to work with this brand for the length of the deal and probably wants to renew.

Two things follow. The redline must read as targeted edits to the brand's paper rather than a replacement of it. And the creator should never have to open the document to finish the work — every edit gets applied by hand, by you.

## Before touching the document

**Read the whole contract first, including schedules and exhibits.** Terms defined in Schedule A get used in the main body; exhibits carry obligations the body only gestures at.

**Ask for the correspondence.** Emails, rate cards, the original quote. The commercial deal is usually settled before the paperwork arrives, and the paperwork often drifts from it. Anything already agreed in writing is an error to correct, not a negotiation. Anything the creator priced is the number that goes in the contract — never invent a figure when they have already quoted one.

**Check for suggestions already in the document.** The brand may have left pending edits, some favorable. Read them, never reject them, and factor them into what still needs asking.

## Scope: the checklist governs

Read `references/review-checklist.md`. It is the scope of the review.

**If an item is missing from the contract entirely, flag it — do not silently draft it in.** Filling a gap is a new ask and a commercial judgment that belongs to the creator. Present what's missing, say what leaving it out costs, let them decide.

**Do not add things that are not on the list.** Each additional ask is a line the brand's reviewer stops at, and asks that protect nothing real make the ones that matter look like part of a pile. Genuinely dangerous things outside the list get raised with the creator as separate flagged items, not added unilaterally.

**Checklist items are compound.** Almost every one contains two or more distinct sub-checks, and the checklist file writes them out as separate boxes. Fixing the first thing mentioned does not close the item. This is the most common way items get half-done and marked complete — a sentence gets appended to a clause while the clause's actual problem sits untouched three lines earlier.

Do not pattern-match. A cap that made sense on revisions does not belong on analytics requests.

## The tracking table

Build this before editing and keep it current. It is the artifact that survives interruption; your memory is not.

| # | Item | Sub-check | Status in contract | Action | Done? |
|---|------|-----------|--------------------|--------|-------|

One row per **sub-check**, not per item. Status is present / partial / adverse / missing. Action is edit / flag / none. Done stays blank until you have visually confirmed the edit in the document.

**Re-output the table after every batch of edits**, not only at the start. If the session is interrupted, the table is what you resume from.

## Workflow

1. Read the contract end to end, including schedules and exhibits.
2. Read the correspondence. Note what's already agreed and any figure the creator quoted.
3. Build the tracking table, one row per sub-check.
4. Report to the creator before editing: the table, anything missing that needs their decision, anything dangerous outside the list, and any drafting errors.
5. Get their decisions on open items.
6. Apply edits by hand in Suggesting mode, following `references/editing-standards.md`. Update the table as you go.
7. **Run the three audit passes.** See below. This is a gate, not a formality.
8. Only after Pass 1 is complete and shown to the creator, draft the cover note.

## Auditing

**Do not tell the creator the review is complete, and do not draft the cover note, until Pass 1 has been done literally and its output shown.** Reporting completion while must-haves are untouched is the worst outcome this skill can produce, and it happens by declaring victory after a coherence read.

### Pass 1 — completeness (hard gate)

**This is not a re-read of the document.** It is confirming, sub-check by sub-check, what the document actually says now.

Do not audit from a plain-text export. Google Docs exports pending suggestions with insertions and deletions run together, so struck language reads identically to untouched language. Auditing that way produces false findings in both directions — it will tell you something is still there when it was struck, and it will hide things that genuinely were missed.

Use `scripts/audit_suggestions.py`, which reads the document exported as `.docx` and reconstructs the accept-all and reject-all versions from the tracked changes:

```bash
# what's in the document and who authored it
python scripts/audit_suggestions.py contract.docx

# the gate: are the adverse phrases still in the accepted version?
python scripts/audit_suggestions.py contract.docx --check phrases.txt

# every suggestion as an edit pair
python scripts/audit_suggestions.py contract.docx --list
```

**Keep a copy of the brand's untouched draft before you start** — a pristine export, before any suggestion was made. It is the baseline for the most important check in the review, and a baseline that already contains damage will report that damage against every redline you compare to it.

```bash
# fidelity: would rejecting the whole redline restore the brand's draft?
python scripts/audit_suggestions.py redline.docx --baseline brand-draft.docx

# completeness: are the adverse phrases still in the accepted version?
python scripts/audit_suggestions.py redline.docx --check phrases.txt

# what's in the document and who authored it
python scripts/audit_suggestions.py redline.docx --list
```

**Run the fidelity check first.** It reconstructs the document with every suggestion rejected and compares it word for word against the brand's draft. They should be identical. If they are not, text was changed outside a suggestion — an edit made in Editing mode, or an undo that overshot and got repaired by retyping. That is the worst defect a redline can carry, because the other side's ability to reject cleanly is the thing that makes a redline safe to send, and nothing about the document looks wrong until they try.

This has happened in practice: a confidentiality clause whose opening words were present when suggestions were accepted and absent when they were rejected. Rejecting that suggestion would have left the clause starting mid-sentence.

A **STRUCTURE** check reports paragraphs whose text is entirely struck while the paragraph mark survives — accepting those leaves an empty line or an empty bullet behind.

Build `phrases.txt` while making the tracking table — one line per sub-check, `label :: exact adverse wording`, copied verbatim from the contract including curly quotes. The script exits non-zero if anything is unresolved, so it can hard-gate the workflow.

Show the output to the creator. Every sub-check gets a line.

**Audit the artifact the brand will open.** If edits were authored offline, run these checks against the document after it has been imported, not against the local file. Package structure differs by toolchain — a Word-produced .docx and a Google export are not comparable part by part — and the imported document is the only one anyone reviews.

### Pass 2 — diff quality

Read every suggestion against the editing standards. Look for anchors struck and re-added, matches wider than the change, bracketed commentary, and rewording that changes nothing.

### Pass 3 — coherence

**Read the document with every suggestion applied**, not the marked-up view.

With the text in front of you, confirm defined terms exist and resolve, cross-references still
work, no clause contradicts another, and **every edited sentence is still grammatical.** Party
swaps are the usual trap: replacing a subject without adjusting the verb or negation produces
things like "neither party shall not disclose." Inserting a phrase near existing punctuation
produces things like "at Talent's rate of $10,000 per reshoot., if applicable."

If any pass turns up a fix, re-run all three afterward. Fixes cause the same damage as original edits.

## Browser automation discipline

Applying many edits through a browser is slow and failure-prone. Before doing it at scale, read `references/docx-round-trip.md` — Google Docs suggestions and Word tracked changes are the same thing on disk, so edits can be authored in XML and imported as native suggestions. That path makes each edit machine-verifiable instead of visually verified.

When editing through the browser, these prevent the failures that actually occur:

- **Never chain select-all-and-type across a tool-call boundary without confirming focus first.** A find-box sequence that lands in the document body selects the entire contract and replaces it. Screenshot to confirm focus before any select-all.
- **Screenshot or zoom after every destructive keystroke** — delete, replace-all, or a typed string following a selection. Not sometimes; every time.
- **Do not count characters by hand for arrow-key selection.** Off-by-one errors grab an extra letter and corrupt the diff. Prefer a find-and-replace on the narrowest unique string, or confirm the selection visually before typing.
- **After any reject-and-reapply cycle, verify that unrelated edits in the same clause survived.** Rejecting removes a range, and overlapping edits go with it silently.

## Reporting

Tell the creator what changed, what you flagged instead of changing, and what remains open. Where you made a judgment call for them, say so and name the alternative.

Be honest about uncertainty. If you cannot verify that an earlier edit survived a later change, say that and say exactly what to check.

Close with the reminder that you are not a lawyer, and that on a deal of any size an entertainment or influencer attorney reviewing the final redline is worth the cost.
