---
name: creator-contract-review
description: Redline an influencer, creator, or talent contract on the creator's behalf against a fixed mutuality checklist, applying every edit by hand in the document so the creator never has to touch it. Use this whenever someone shares a brand deal, influencer agreement, SOW, talent agreement, sponsorship contract, or campaign paperwork and wants it reviewed, redlined, marked up, negotiated, checked for fairness, or made mutual — including when they just ask "is this contract okay?", "what should I push back on?", or "can you mark this up before I send it to their legal team?". Also use when revising or auditing a redline that is already in progress.
---

# Creator Contract Review

Brand-drafted influencer agreements are written to protect the brand. Most one-sidedness is not malice — it is a template that nobody rebalanced. The job is to make the agreement mutual without making the creator look difficult, because the creator has to work with this brand for the length of the deal and probably wants to renew.

Two things follow. The redline must read as targeted edits to the brand's paper rather than a replacement of it. And the creator should never have to open the document to finish the work — every edit gets applied by hand, by you.

**The characteristic failure of this task is not bad editing. It is quietly dropping items.** These reviews run long and get interrupted. Memory of "what I've done and what's left" degrades, and the model reports completion while several must-haves sit untouched. Everything below about tracking and auditing exists because of that specific failure. Treat it as the main risk, not a formality.

## Before touching the document

**Read the whole contract first, including schedules and exhibits.** Terms defined in Schedule A get used in the main body; exhibits carry obligations the body only gestures at.

**Ask for the correspondence.** Emails, rate cards, the original quote. The commercial deal is usually settled before the paperwork arrives, and the paperwork often drifts from it. Anything already agreed in writing is an error to correct, not a negotiation. Anything the creator priced is the number that goes in the contract — never invent a figure when they have already quoted one.

**Produce a mismatch table and put it at the top of the report**, before any checklist finding:
what the contract says, what the correspondence says, and where. These are the strongest items in
the review and the only ones that are not arguable — the brand wrote the email. They also read
completely differently from the rest of the redline: a correction costs the brand nothing but
embarrassment, where every checklist item costs them something they drafted on purpose.

Three failure modes to hunt specifically:

- **"Updated" attachments that were not updated.** A brand that agrees a number by email and says
  it will revise the contract frequently sends the same file back. Check the agreed figure against
  the fee table every time, however confidently the email describes the attachment.
- **Requests the creator made that were never answered.** These sit between the parties unresolved
  and vanish on signature. A creator who asked in writing for a duration, a rate or a limit and
  got a reply about something else has an open item, not a settled one — list them separately from
  contradictions, because the fix is an answer rather than a correction.
- **Concessions already won that the paperwork still contradicts.** Where the brand has agreed in
  writing to drop a requirement, the clause imposing it is an error to correct. Say so plainly in
  the cover note and quote their sentence; it is the cheapest edit in the document to land.

**Check for suggestions already in the document.** The brand may have left pending edits, some favorable. Read them, never reject them, and factor them into what still needs asking.

**Work in tracked changes — this is a prerequisite, not a preference.** Redlines commonly arrive,
and get sent, as manual strikethrough and coloured text. On screen it looks equivalent. It is not:
nothing can be accepted or rejected, the other side has to retype rather than click, and every
check in Pass 1 — fidelity, structure, the completeness gate — needs tracked changes to exist. A
redline authored as formatting cannot be audited at all, so whatever errors it carries travel into
the signed agreement.

Google Docs calls this Suggesting mode; Word calls it Track Changes. They are the same thing on
disk, and everything below works on either.

That is an observed outcome, not a worry. A creator-side redline authored this way changed an
invoice trigger from "upon completion of all deliverables" to "upon publication of the Content" in
the compensation clause and missed the identical phrase in the fee table. Both survive in the
executed contract, which now gives two different answers about when the fee is due. A completeness
gate would have caught it in one line, and no gate could run.

If the creator's own earlier redline arrives as formatting, say so and re-author it as suggestions
before adding to it.

**Establish which document is the live one before editing anything.** The workflow below assumes a
Google Doc, and much of the time that assumption is wrong. Brands email `.docx` attachments, and a
creator who has not opened a Doc has no Doc. Three cases, and they are not interchangeable:

- **A Google Doc the creator can edit.** Suggesting mode, browser editing, export for the audit.
- **A local `.docx` and no Doc.** The default for an emailed contract. Do not upload it to Docs to
  get Suggesting mode — that adds a conversion the brand never asked for, and the brand's reviewer
  will open Word. Author tracked changes in the `.docx` directly (`references/docx-round-trip.md`)
  and audit that same file. It is the artifact that gets emailed back.
- **A `.docx` that will be imported to Docs before sending.** Author offline if that is easier, but
  run Pass 1 against the *imported* document, because import resolves font and size inheritance and
  a typography failure can appear or vanish across it.

Ask which one applies. The answer decides the editing mechanics and which file Pass 1 audits, and
guessing wrong means auditing a file nobody will open.

## Scope: the checklist governs

Read `references/review-checklist.md`. It is the scope of the review.

**If an item is missing from the contract entirely, flag it — do not silently draft it in.** Filling a gap is a new ask and a commercial judgment that belongs to the creator. Present what's missing, say what leaving it out costs, let them decide.

**Do not add things that are not on the list.** Each additional ask is a line the brand's reviewer stops at, and asks that protect nothing real make the ones that matter look like part of a pile. Genuinely dangerous things outside the list get raised with the creator as separate flagged items, not added unilaterally.

**Checklist items are compound.** Almost every one contains two or more distinct sub-checks, and the checklist file writes them out as separate boxes. Fixing the first thing mentioned does not close the item. This is the most common way items get half-done and marked complete — a sentence gets appended to a clause while the clause's actual problem sits untouched three lines earlier.

Do not pattern-match. A cap that made sense on revisions does not belong on analytics requests.

## What a term means, not what it sounds like

A sub-check is answered by what the contract defines, not by what a phrase suggests. The dangerous phrases are the ones that read as plain English and therefore never get looked up: "live post", "goes live", "live post date", "final content is live". They sound like they mean the obvious thing — publication on the creator's own feed. Undefined, they mean whatever the brand argues they mean, and the obvious reading is the creator's to lose.

This is how item 9 gets marked satisfied on a contract that does not satisfy it. A grant running "60 days after each live post" looks like it triggers on the creator's publication, so the trigger box gets ticked — while nothing in the document rules out the brand treating approval, or its own repost, as the trigger. A defined term that is obviously adverse gets caught every time. An undefined term that reads favorably is the one that survives the review.

During the first read, list every clock in the agreement and, for each, the event that starts it and the event that ends it: usage window, exclusivity window, payment clock, feed-retention obligation, the Term itself. Then, for each event, name the clause that defines it. If you cannot name one, the phrase is undefined and every sub-check resting on it is **partial** — not present — however natural the reading.

Two patterns are worth hunting directly:

- **One undefined idea wearing several phrasings across body and exhibits.** "live post" in §3(a), "goes live" in one exhibit, "live post date" in another, "final content is live" in the term clause. The fix is a definition written once plus a sweep for consistency, not a patch to whichever clause you noticed first.
- **A duration with no trigger at all.** "Content must remain on the Influencer's primary feed for at least (1) year" never says one year from what.

Defining a term the contract already uses is an **edit**, not a flag. It does not create an obligation; it fixes the meaning both sides already assume, and it reads to the brand's reviewer as a clarification rather than an ask. That is a different thing from a clause the contract lacks entirely, which stays a flag.

## The tracking table

Build this before editing and keep it current. It is the artifact that survives interruption; your memory is not.

| # | Item | Sub-check | Status in contract | Action | Done? |
|---|------|-----------|--------------------|--------|-------|

One row per **sub-check**, not per item. Status is present / partial / adverse / missing. Action is edit / flag / none. Done stays blank until you have visually confirmed the edit in the document.

Where a status turns on what a word means, the status cell carries the clause that defines the word — `present (§1(c))`, not `present`. If you cannot fill in the reference, the status is partial. This single habit is what catches undefined triggers; without it, "reads as the creator's publication" and "is the creator's publication" are recorded identically.

**Re-output the table after every batch of edits**, not only at the start. If the session is interrupted, the table is what you resume from.

**Write the table with a file-writing tool, not a shell heredoc.** Status cells quote the contract,
so they carry curly quotes, apostrophes, parentheses, backticks and `|`. A `cat <<'EOF'` block of a
hundred such rows fails on the shell's parsing long before it fails on yours, and the failure
arrives as an unhelpful line number rather than as the offending row. Pipes inside a Markdown table
cell need escaping in any case.

## Workflow

1. Read the contract end to end, including schedules and exhibits. On that pass, list the clocks and the event at each end, and note which of those events the document actually defines.
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

**Parse the XML first — before any of the checks below.** Every check in
`audit_suggestions.py` is a regex over the markup; not one of them parses it. A
`.docx` whose `document.xml` has an unclosed element passes the whole audit and
then refuses to open. If edits were authored as XML, run `ET.fromstring()` on
each part and open the finished file with a document library before showing
anyone a green report. See `references/docx-round-trip.md`.

**Run the fidelity check first.** It reconstructs the document with every suggestion rejected and compares it word for word against the brand's draft. They should be identical. If they are not, text was changed outside a suggestion — an edit made in Editing mode, or an undo that overshot and got repaired by retyping. That is the worst defect a redline can carry, because the other side's ability to reject cleanly is the thing that makes a redline safe to send, and nothing about the document looks wrong until they try.

This has happened in practice: a confidentiality clause whose opening words were present when suggestions were accepted and absent when they were rejected. Rejecting that suggestion would have left the clause starting mid-sentence.

A **STRUCTURE** check reports paragraphs whose text is entirely struck while the paragraph mark survives — accepting those leaves an empty line or an empty bullet behind.

A **FORMATTING** check runs alongside, with no baseline needed. It finds the size and typeface the body text uses and flags any inserted run that doesn't declare them — those inherit the document default and render visibly larger and in the wrong face. This catches the defect that no text comparison can see: the words are correct and the document still looks wrong.

The same check reports **LAYOUT** and **TYPE** separately. LAYOUT counts tab stops and page breaks in the reject-all view — comparing raw counts instead would flag tabs inside newly inserted clauses as damage and tabs inside deleted paragraphs as losses. TYPE compares character formatting per character on text present in both documents, so bold, italics, size and typeface cannot drift unnoticed. Tab stops and page breaks are easy to destroy while editing and invisible in any text comparison — losing the tab after a clause caption runs the label into the body ("Use:During the Term…"). A layout failure is cosmetic rather than dangerous, but it is the kind of thing the other side's reviewer notices.

Build `phrases.txt` while making the tracking table — one line per sub-check, `label :: exact adverse wording`, copied verbatim from the contract including curly quotes. The script exits non-zero if anything is unresolved, so it can hard-gate the workflow.

**A phrase gate cannot see additions, and roughly half a mutuality redline is additions.** Nothing in `--check` can confirm that a brand-side indemnity, a liability cap or a deemed-approval window actually arrived. Build `additions.txt` alongside it — one line per sub-check whose action is an insertion, `label :: exact wording the edit must produce` — and assert every line is present in the accept-all text. The phrase gate proves the bad language left; only this proves the good language landed.

This also disposes of a state that otherwise eats time. A surviving adverse phrase is expected wherever the fix was an addition placed beside text that should stay: the creator's own indemnity survives a mutuality edit, "worldwide license" survives having "non-exclusive," inserted in front of it. Those are phrase-selection artifacts, not misses — but they are indistinguishable from real misses until the additions check confirms the counterpart exists.

Read the result rather than skimming it. Three states need judgment:

- **PARTIAL (x2 before, x1 still present)** — the phrase occurs in more than one place and only some were handled. Usually the body was edited and an exhibit was not, or the same stock sentence appears in two clauses. Find out which instance survived; sometimes the survivor is legitimately different and should stay.
- **STILL PRESENT — but this clause WAS edited** — the most dangerous state. Something was changed in that clause while the adverse wording stayed, usually because a protective sentence was added beside the problem instead of replacing it. The clause now contradicts itself and reads as handled. Always read it in full.
- **STILL PRESENT — clause untouched** — either a genuine miss or a deliberate flag. Check the tracking table for which.
- **not found in either** — the phrase is wrong, not the item fine. Fix the phrase and re-run.

Then search the accepted text for runs of underscores. Any blank placeholder outside the signature block is a blocking open item, not a completed edit.

Do not use the suggestion count as a verification metric. Importing a .docx merges adjacent tracked changes, so 154 suggestions can arrive as 111 with identical content. Compare the reconstructed text, never the counts.

Show the output to the creator. Every sub-check gets a line.

**Audit the artifact the brand will open — and know which one that is.** A locally authored `.docx`
and the same file after import into Docs are not equivalent: Google resolves font and size
inheritance on import, so a typography failure in the local file can vanish on import, and a file
that passes after import can still be wrong if the `.docx` itself is what gets emailed. Package
structure also differs by toolchain, so a Word-produced `.docx` and a Google export are not
comparable part by part.

So there is no general rule about which file to audit — there is a question to ask. **Which file is
the creator sending?**

- Sending the `.docx` they were emailed, with tracked changes added → audit that `.docx`.
- Sending a link to a Doc, or a fresh export of one → import first, then audit the imported
  document, because that is the one anyone reviews.

Auditing the local file when a Doc gets sent, or the Doc when the `.docx` gets sent, produces a
clean report about a document nobody opens.

### Pass 2 — diff quality

Read every suggestion against the editing standards. Look for anchors struck and re-added, matches wider than the change, bracketed commentary, and rewording that changes nothing.

### Pass 3 — coherence

**Reconstruct the accept-all text and read that.** Not the marked-up document with the changes
applied mentally — the actual text, dumped from the file. Reading it in your head reproduces what
you meant to write, and the point of this pass is to find the places where the file says something
else.

Nothing earlier in Pass 1 substitutes for this. A tool that mis-places an insertion produces a
perfect reject-all, a clean structure check, intact layout and type, and a `--check` run in which
every adverse phrase is correctly resolved — while the version the brand would sign reads
`re-shouncured material failure on the part ofoting costs`. Every automated gate passed on that
document.

With the text in front of you, confirm defined terms exist and resolve, cross-references still
work, no clause contradicts another, and **every edited sentence is still grammatical.** Party
swaps are the usual trap: replacing a subject without adjusting the verb or negation produces
things like "neither party shall not disclose." Inserting a phrase near existing punctuation
produces things like "at Talent's rate of $10,000 per reshoot., if applicable."

If any pass turns up a fix, re-run all three afterward. Fixes cause the same damage as original edits.

## Browser automation discipline

Applying many edits through a browser is slow and failure-prone. Before doing it at scale, read `references/docx-round-trip.md` — Google Docs suggestions and Word tracked changes are the same thing on disk, so edits can be authored in XML and imported as native suggestions. That path makes each edit machine-verifiable instead of visually verified.

**`scripts/apply_tracked_changes.py` already implements it.** Use it rather than
writing another one: it carries the guards that are expensive to rediscover —
each anchor must match exactly once, an anchor crossing an element boundary is
refused instead of silently eating the markup, the XML is parsed before the file
is written, and whole clauses are cloned from a sibling paragraph so tabs and
underlined captions survive. Express the redline as a list of edits, keep the
pristine brand draft as the input, and re-run from it after every change; the
edit list stays the source of truth and the reject-all view stays byte-identical
to what the brand sent.

When editing through the browser, these prevent the failures that actually occur:

- **Never chain select-all-and-type across a tool-call boundary without confirming focus first.** A find-box sequence that lands in the document body selects the entire contract and replaces it. Screenshot to confirm focus before any select-all.
- **Screenshot or zoom after every destructive keystroke** — delete, replace-all, or a typed string following a selection. Not sometimes; every time.
- **Do not count characters by hand for arrow-key selection.** Off-by-one errors grab an extra letter and corrupt the diff. Prefer a find-and-replace on the narrowest unique string, or confirm the selection visually before typing.
- **After any reject-and-reapply cycle, verify that unrelated edits in the same clause survived.** Rejecting removes a range, and overlapping edits go with it silently.

## Reporting

Tell the creator what changed, what you flagged instead of changing, and what remains open. Where you made a judgment call for them, say so and name the alternative.

**Say which asks are cheap and which are expensive.** Presenting forty items at one volume
misrepresents what is likely to move. Mutuality items and missing definitions land: they are cheap
for the brand to grant, they mirror language the brand wrote, and they survive review. Rate
insertions, payment-term changes and narrowing of the brand's usage rights are commercial asks that
get traded away first. Both belong in the redline — an unmade ask is never granted — but the
creator is the one spending the goodwill and should know where it is going.

The same judgment applies inside a clause. A Name and Likeness paragraph that is perpetual, permits
standalone use of the creator's face, and runs "for trade and archival purposes" can be rewritten
wholesale, or it can have the two words "and for trade" deleted. The second removes the most
open-ended permission and leaves a clause the brand will not fight about. Know which one you are
doing and why.

Be honest about uncertainty. If you cannot verify that an earlier edit survived a later change, say that and say exactly what to check.

Close with the reminder that you are not a lawyer, and that on a deal of any size an entertainment or influencer attorney reviewing the final redline is worth the cost.

**Say it every time, and say it plainly.** This is drafting assistance, not a
legal opinion; using it creates no attorney-client relationship; the redline can
misread a clause or produce an edit that says something other than what it
claims to. The creator must read the redline before sending it and the contract
before signing it — an edit they did not read is theirs the moment it goes out.
Contract law also varies by jurisdiction and this review does not research
theirs. Do not soften this into a single trailing clause the reader skims past;
it is the part that protects them from the tool. `DISCLAIMER.md` in the skill
directory has the full text if they want it.
