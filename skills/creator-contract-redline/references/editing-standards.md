# Editing Standards

How a redline looks determines how it is received. Identical substance reads completely differently depending on whether the markup shows targeted edits to the brand's paper or a wholesale rewrite of it. These standards exist to make the first one happen.

Audit every finished redline against this file.

---

## 1. Classify the change before writing it

Before drafting any replacement, decide which of three things is actually happening:

- **Insertion** — words going in, nothing coming out
- **Deletion** — words coming out, nothing going in
- **Swap** — genuinely different words in the same place

Most changes that feel like swaps are insertions or deletions. Getting this wrong is the single largest source of noisy redlines.

**Example.** "During the Term" → "During the applicable License Term" looks like a swap. It is an insertion of two words. Written as a swap it strikes six words; written as an insertion it strikes none.

**Example.** "the right to use and support with paid media the Posts" → "the right to use the Posts" is a deletion of five words. Written as a swap it strikes eleven.

Combined, those two changes in one sentence go from a seventeen-word strike to two words in and five words out.

## 2. Match only what changes

Find-and-replace strikes the entire matched string and re-inserts the replacement. **Match width is diff width.** A thirteen-word match to insert two words produces a thirteen-word strike.

Before running a replacement, ask: what is the narrowest string that contains the change and is still unique?

**Example.** To add "uncured material" to "make-good Posts required due to Talent's failure to comply with this Agreement": matching the whole phrase strikes thirteen words. Placing the cursor after "Talent's" and typing the two words strikes nothing.

**When the narrow string is not unique, locate it inside a unique context — never widen the
strike.** "the Term" occurs twenty times in a typical SOW; striking it in "During the Term, the
Brand shall have the right…" does not justify striking the whole sentence. Find a wider string
that is unique, then anchor the edit on the narrow string inside it. In
`apply_tracked_changes.py` that is `within=`: the context locates, the anchor is what changes.
The context may include text inserted by an earlier edit in the same run — anchoring an
insertion on a lone "." inside "…as published by Talent." works even though ", as published by
Talent" is itself a suggestion.

## 3. Never anchor by replacing text with itself plus an addition

The most common way to add a sentence is to find an existing sentence and replace it with itself plus the new text. This strikes the anchor and re-adds it, making it look like you rewrote a sentence you left alone.

For pure additions, place the cursor and type. Find the anchor text, collapse the selection to its end, then type. The result registers as an addition with nothing struck.

This matters most where the anchor is significant. Anchoring a definitions block to the Term sentence makes it look like you are rewriting the Term when you are only adding definitions after it.

## 4. Mirror their language on mutuality items

When asking for reciprocity, reuse the brand's own wording with the parties swapped. This is both cleaner and much harder to argue with — objecting means objecting to a standard they wrote and applied to the creator three lines earlier.

- One-way confidentiality: change "Talent shall not disclose" to "neither party shall disclose" and "without Brand's prior written consent" to "without the other party's prior written consent". Do not write a new clause.
- One-way indemnity: mirror their existing numbered structure with the parties reversed, lifting the generic clauses verbatim.
- One-way morals: reuse their trigger language — the same standard, the same phrasing, reversed.
- Brand-only termination: change "Brand shall have the right to terminate" to "Either party shall have the right to terminate" inside their existing sentence.

There are two ways to make a one-way clause mutual: rewrite the brand's sentence so it runs both
ways, or leave their sentence untouched and append a reversed copy of it underneath. **Prefer the
second.** It reads as a smaller ask even when the substance is identical, because their paragraph
shows no strikethrough at all — the diff is pure insertion. Resist tidying the mirrored copy while
you write it: reproducing their phrasing verbatim, awkwardness included, is what makes the symmetry
impossible to argue with.

**A mirror carries over what the words do, not only the words.** An exception that limits
the brand's obligation "to the extent caused by the acts or omissions of Brand" is narrow in
the brand's clause and swallows the brand indemnity when swapped, because the creator's act —
posting what the brand approved — is how every covered claim arises. Before keeping a mirrored
carve-out, ask whether it excludes the thing the new clause exists to cover. (Checklist #1 has
the replacement wording.)

**Refer to the creator by the contract's defined term, never by a pronoun you chose.** New text
says "Influencer" and "Influencer's", or "its" where the creator contracts through a company.
Where the brand's draft writes "his/her", that tells you nothing about the creator — and a
redline that writes "her agents" has guessed the gender of a real person in a document going
out under their name. The same goes for a pet or anyone else the content features.

**Bind the party that can be bound.** Where an agency signs "for the benefit of its client" and
the client does not sign, a mirrored duty written as "Agency and Client shall not…" puts an
obligation on a company that is not a party — and the template's third-party-beneficiary clause
usually adds that the client "is not bound by any of Agency's agreements or covenants". The
brand's reviewer will strike "Client" or point at that sentence, and either way the creator's
protection against the company actually using the Content is gone. Write new brand-side duties
as "Agency shall, and shall cause Client to, …", so the client's failure is the agency's breach,
and add a client acknowledgment block — a signature line for the client agreeing to the sections
that name it — as the ask that actually binds the client (checklist #1). A third-party-beneficiary
sentence is not a substitute: it cannot make a promise the client never gave. Breach triggers follow the same logic: a client that is not bound cannot
breach, so "unless Agency and/or Client are in material breach" names the Agency alone. Read
every "Agency and Client" in new text against that clause before Pass 3 closes. Checklist #1 covers who gives the indemnity.

**Use the contract's own names for the parties in any sentence the checklist supplies.** The
checklist's model wording says "Brand" and "Influencer"; a contract whose parties are
"Agency", "Client" and "Lender" defines neither. Substituting the contract's defined terms is
not rewording, and it applies to wording the creator chose from a list of options. An undefined
"Brand" is the first thing the other side's counsel will query.

Write fresh language only where there is no counterpart to mirror — a limitation of liability clause
where none exists, for instance.

## 5. No bracketed commentary in the contract body

Never write `[TALENT COMMENT — ...]` or explanatory brackets into the document. It reads as arguing with the reviewer, and it is text they have to delete before executing.

All reasoning belongs in the cover note. The document carries edits; the email carries argument.

## 6. Delete rather than replace-with-explanation

When something is out of scope, strike it. Do not replace it with a sentence explaining why it was struck, and do not replace it with a prohibition.

**Example.** If paid media is not being granted, the whitelisting bullet gets deleted. It does not get replaced with "Brand shall have no right to engage in Allowlisting", which both explains itself unnecessarily and pre-decides something that belongs in the separate paid usage agreement.

Declining to grant something is not the same as prohibiting it, and the difference is worth real money later.

**The exception: a condition on an obligation the creator relies on.** Striking a whole bullet
leaves nothing behind. Striking a condition from the middle of a sentence can leave a sentence
that no longer says anything. "Payment of the Fee will be sent after content is verified and
complete" with its brand-controlled condition struck becomes "Payment of the Fee will be sent."
— sent when? The better edit replaces the condition with a pointer: "in accordance with the
payment terms set forth below." Where the struck words answered *when*, *how much* or *on what condition*, put the
governing term in their place, preferably as a cross-reference to the clause that already
answers it.

## 6a. Do not strike what does nothing

Redundant words the brand wrote — "this Agreement or Statement of Work" where there is no
separate SOW, a doubled "and/or", a harmless synonym, a sentence that appears word for word in
two sections — cost the creator nothing where they are.
Striking them adds a line the brand's reviewer has to read and costs nothing to leave. Before any
deletion, ask what changes if it is accepted. If the answer is nothing, do not
make it.

## 6b. Put a definition where the term first does work

A new definition belongs beside the first clause that uses it, as a parenthetical — "a period of
sixty (60) consecutive calendar days commencing on the date Influencer first publishes the
Content on Influencer's own channel (the "Live Date")" in the usage grant. Where the contract has
a definitions section written as paragraphs, it goes there instead. **Where the defined terms are
a table, the definition goes inside the row that first uses the term, as the parenthetical above
— never as a new row.** A tracked row insertion is table-structure markup that
`apply_tracked_changes.py` cannot write and `accept_all.py` / `reject_all.py` cannot build a
clean copy from, so a hand-written row bypasses every guard the scripts carry. It does not go at the end
of whichever clause happens to come first: a "Live Date" definition appended to the Services
paragraph reads to the creator and to the brand's counsel alike as text dropped in rather than
drafted. §3 still applies: a
definition added beside an existing sentence is an insertion, never a rewrite of that sentence.

## 7. Don't draft the clause you've already won

If the correspondence shows the brand already conceded a point and is revising the language themselves, do not draft their clause for them. Drafting it implies the subject belongs in this agreement and hands them a starting position you chose.

Strike what is out of scope, state plainly that it is not granted and not included in the fee, and leave the rest for the separate paper.

## 8. Don't invent numbers

Check the correspondence for rates the creator already quoted before writing any figure. Writing a number lower than what they quoted — into a contract, in their own voice — is worse than leaving it blank.

Where a figure is genuinely needed and none exists, flag it for the creator rather than picking one.
The exception is a default the checklist itself states — the turnaround floors in #14. Those are
positions, not guesses, and they only ever move a number in the creator's direction.

Be careful with derived figures. A total fee divided by deliverable count is not a per-deliverable rate if the fee was built from a per-asset base plus bundled syndication and exclusivity. A wrong derived number in a contract becomes the number the other side reaches for at termination.

The rule against guessing is the floor. Where the creator supplies a figure, it is still worth
saying what the figure is *for*, because the wrong basis produces a defensible-looking number
that does not survive contact with the other side. **A reshoot fee is a production rate, not the
deal.** The base fee bought production plus usage, exclusivity and the creator's audience; a
reshoot buys production again and nothing else, so a reshoot fee equal to the base fee invites
the brand to reject the whole clause rather than negotiate the number — and the clause is worth
more than the rate. Say this once, then use whatever the creator decides.

## 9. Fix the right axis

When a clause is objectionable, identify precisely what makes it objectionable before editing.

**Prefer replacing the trigger to writing around it.** "Lender shall invoice upon completion of
all deliverables" is objectionable because "completion" is undefined and brand-controlled — the
brand can withhold approval and the invoice never becomes due. The instinct is to append a sentence
deeming timely-submitted content to complete the deliverable where the brand caused the delay. The
better edit is three words: "upon **publication of the Content**". It replaces the ambiguous noun
with a fact neither side can argue about, instead of legislating around it. A shorter edit that
removes the ambiguity beats a longer one that survives it.

**Example.** An analytics clause reading "all analytics and performance data reasonably requested by Brand and/or as otherwise requested" has two problems: unbounded frequency and unbounded scope. Capping the number of requests fixes the smaller one and leaves the larger — the brand can still demand account-level audience data. Scoping it to per-post data surfaced in the platform's native dashboard fixes the real problem and is more generous on frequency, which makes it easier to accept.

## 10. Prefer boundaries to enumerations

A list of permitted metrics goes stale as platforms rename and retire them, and anything omitted becomes an argument. "Whatever the platform's native dashboard surfaces for that post" cannot go stale, is verifiable by both sides, and is harder to object to.

Same logic applies to channel lists, deliverable specs, and data definitions.

**Enumeration is still right in two places:** exclusion lists (the named competitor brands in an
exclusivity clause, the metrics carved out of an analytics request, the carve-outs from a liability
cap), where the list is the limit and a boundary would be broader; and lists the counterparty
wrote, where replacing their enumeration with your boundary reads as a rewrite. It is wrong when
defining what the **creator owns** — handles, channels, marks — because the list goes stale the day
the creator opens a new account, and whatever is missing from it is presumptively not theirs. Draw
those by ownership: "owned or controlled by Talent".

## 10a. One suggestion per thing the other side can say yes to

A suggestion is the unit of acceptance. Whatever sits inside one `<w:del>` is
taken or refused together, so bundling several sentences into a single deletion
means the weakest one governs the fate of the rest.

This costs real ground where a clause has a core the brand will defend and
satellites it would concede. A payment clause struck as one 65-word block
can contain three separate sentences: the pay-when-paid condition itself, a
sentence stripping the creator's right to hold the agency liable, and a sentence
pointing the creator at a party it has no standing to sue. The agency will never
accept losing the first. Bundled, rejecting it silently restores all
three.

Before writing a deletion that spans more than one sentence, ask whether the
other side might accept part of it. If so, make it several suggestions. The diff
looks longer and concedes less.

The corollary: **where the adverse core is certain to survive, edit around it
rather than at it.** Conditions the brand will not drop are still bounded by
what the creator adds beside them — an outer date, a diligence obligation, a
subordinating clause. Those read as making the brand's own sentence work rather
than as attacking it, which is exactly why they land.

## 10b. Calibrate the ask to what the counterparty can actually give

Some clauses exist because the counterparty has no commercial choice. An agency
on a pass-through deal cannot take its client's credit risk onto its own balance
sheet, so pay-when-paid is not a drafting preference it will trade. The same is
true of usage and exclusivity terms the outreach email already described as
non-negotiable.

Asking anyway is not free. It spends goodwill on a certain refusal, and it makes
the adjacent asks — the ones that would have landed — look like part of a pile.

Ask the creator, or ask someone who has negotiated with that counterparty before.
Where an item is known to be immovable, say so in the report, record the fallback
in the tracking table, and put the redline's effort into the sub-checks around it.
An unmade ask is never granted, but an unwinnable one costs the winnable ones.

## 11. Keep reasoning consistent across related clauses

Where several clauses share a rationale, edit them the same way with the same wording. Three bullets struck on the single ground that paid media is not in this agreement reads as one coherent position. The same three edited three different ways reads as three separate objections to fight about.

Each struck bullet is still its own suggestion (§10a), and **each one deletes its paragraph mark**
as well as its text — otherwise accepting leaves an empty bullet behind. A block of struck bullets
usually has blank spacer paragraphs between them; those go too, or the list closes up with a gap.

## 12. Verify after every reject-and-reapply

Rejecting a suggestion removes a range from the document, and any other edit overlapping that range can go with it silently. This is invisible unless you look.

After any cycle of rejecting and re-applying, verify that unrelated edits in the same clause survived. On a redline with several such cycles, do a full completeness pass at the end against the checklist — do not trust your memory of having made an edit.

The stakes are high: a paid-media carve-out, the single most important sentence in a redline, can vanish entirely and leave behind a clause that grants exactly what it was meant to exclude.

## 13. Re-read the whole sentence after a party swap

Swapping a subject changes what the rest of the sentence needs. "Talent shall not disclose" becoming "neither party shall not disclose" is a double negative that inverts the clause. Check verb agreement, negation, and possessives every time a party name changes.

The same applies to insertions near punctuation. Dropping a rate into "...additional compensation, if applicable." without handling the existing comma and period yields "...additional compensation, at Talent's rate of $10,000 per reshoot., if applicable." Read the finished sentence, not just the inserted phrase.

**Deletions strand punctuation too.** A phrase set off by a pair of commas, or joined by "or" to a neighbour, leaves one comma behind when only part of it is struck: deleting "or incidental" from "any direct, or incidental, damages" yields "any direct, damages". Include the stranded mark in the deletion, or strike the matching one beside it, and read the sentence as accepted.

## 14. Amending a clause's tail does not fix its head

A clause can contain two separate problems. Appending a sentence that solves the second one leaves the first untouched while creating the impression the clause was handled.

**Example.** An extension clause both lets the brand extend the term "without any additional compensation to Talent" and pushes payment dates back. Adding a sentence at the end saying brand-caused delays don't postpone payment addresses neither of the original two problems — but the clause now has an edit in it, and the item gets marked done.

Before closing any clause, re-read it from the start and confirm every problem you identified is actually addressed.

**A trigger with several limbs is narrowed in every limb.** Triggers aimed at the creator usually come as a list — "brings Talent into public disrepute, …, or which shocks, insults, or offends any group, or reflects unfavorably upon Brand"; "Compliance Purposes, negligence, willful misconduct or any failure or shortcoming". Narrowing the limb that mentions the problem leaves the others to do the same work. Put one qualifier after the whole list ("in each case in a manner that materially injures Brand") or narrow each limb, and read the finished trigger limb by limb (checklist #5, #12).

## 15. Adding a carve-out does not remove the obligation it carves out from

A clause can be made worse by a well-meaning addition. If the contract says Talent delivers "final approved native files" on request, adding a sentence that "raw footage, outtakes, unused takes, and project or source files are not deliverables" does not fix it — a native file *is* a source file. The clause now says two opposite things, and which one governs is exactly the argument you were trying to prevent.

The adverse wording has to come out. A protective sentence beside it is not a substitute, and it is worse than doing nothing because the clause reads as handled on a tracking table.

`audit_suggestions.py --check` distinguishes these: a surviving phrase in a clause that was edited reports **"but this clause WAS edited"** rather than "clause untouched". The first always needs reading in full.

## 16. A blank is an open item, never a completed edit

The rule against inventing numbers is right, but it has a failure mode: inserting `$______` into the contract and marking the sub-check done. A contract going to the brand's legal team with blank lines in it is not sendable, and a completeness table showing that item green is actively misleading.

When a figure is needed and the correspondence doesn't supply one, the order of preference is:

1. **Ask the creator before inserting.** Usually they know their rate; it takes one question.
2. If they're unavailable and the edit must go in, insert the placeholder — then list every blank at the **top** of the report as blocking, and mark the sub-check open, not done.

Never let a blank reach the audit table as a pass. Search the finished document for runs of
underscores before declaring completeness; the only ones that belong are in the signature block.

**Blanks do not always look blank.** Check every party name, entity name, date and figure against
the correspondence as well. Template placeholders reach signature blocks looking like ordinary
text — a surname of "X", "[Name]", "TBD", a lone initial. An influencer named "Creator X" in the
defined-terms table, the signature block and the inducement rider can be read four times without
question, because the rule being applied is looking for `_____`. A name that appears consistently throughout is not
thereby verified; it is consistently wrong.

**Find them on the first read, and ask before drafting.** A placeholder name, a missing figure or
a wrong entity is a decision like any other, so it goes into the step-4 question list — "The
contract names you 'Creator X' in three places. What is the correct legal name?" — and is answered
before the first edit, then made as a tracked correction. Do not guess it; the author name the
creator gave for the tracked changes may be a manager's or a handle, not the signatory. Refusing
to guess is right; raising it only in the final message is not, because it leaves a blocking item
after the redline is otherwise finished.

**The worst placeholder is a real name — someone else's.** A contract assembled from the last deal
carries the previous creator's name and that deal's effective date in the preamble, and it passes
every blank-hunting check because it is a perfectly ordinary name in a perfectly ordinary sentence.
Read the preamble against the correspondence specifically: the parties, the effective date and the
client. Two things follow when you find one. The creator may be signing an agreement that names
somebody else as the counterparty, which is worth fixing for its own sake; and the brand has
disclosed another creator's name and deal date, which is worth mentioning in the cover note
without making a point of it.

**A wrong product line is the same failure.** "Client grants Influencer a licence to use any
Brand baking-soda materials" in a contract for a cat-litter campaign is template residue, and it
means the trademark licence does not cover the product the creator is actually being asked to
feature. Check that the brand, product and campaign named in the grant are the ones in the brief.

## 17. Verify each fix by name

When an audit pass turns up a defect and you fix it, confirm that specific fix landed before reporting it fixed. Re-running the passes generally is not the same as checking the one thing you just changed.

**Verify with an extractor that sees the whole document.** `python-docx`'s `paragraph.text`
silently skips text inside `<w:sdt>` content controls, which contracts use for fill-in fields and
signature blocks. A check built on it reports text as missing that is present, and raises a false
"text differs" alarm on a clean copy. Use the audit script's reconstruction or a raw
walk over `<w:t>` elements.

The common failure: a stray character in a clause reported as found and repaired, and still there in the delivered document. The fix was asserted, not verified.

## 18. Narrowing a requirement does not remove what it points at

If the body requires releases "in the form attached hereto as Exhibit 1", narrowing that sentence leaves Exhibit 1 sitting in the document with its original content. Anyone who signs it is still bound by it, and the brand's reviewer sees a schedule the redline apparently accepted.

When an edit narrows or conditions a reference to an exhibit, schedule or appendix, check the referenced material itself as a separate sub-check. The same goes for duplicated blocks — an exhibit that contains the same section twice needs both handled.

## 19. Mechanical notes

- **Curly quotes and apostrophes must match exactly.** Contracts use `'` and `"`, not `'` and `"`. A straight apostrophe will not match.
- **Find-and-replace does not interpret `\n` or `\t`** in the replacement field — they land as literal characters. Paragraph breaks must be placed by cursor.
- **Find-and-replace cannot match across paragraph breaks.** Multi-paragraph deletions require selecting the range and deleting it: click at the start, shift-click or shift-arrow to the end, delete.
- **Watch for double spaces and inconsistent spacing** in the source. Template-assembled contracts are full of them and they break exact matches.
- **Do not build contract text in a shell heredoc.** Quoted contract language carries curly quotes,
  apostrophes, backticks, parentheses and `|`; a `cat <<'EOF'` block of it fails on the shell's
  parsing and reports a line number that is not the offending line. This applies to the tracking
  table, `phrases.txt` and `additions.txt` alike — write them with a file-writing tool. Inside a
  Markdown table a literal `|` needs escaping regardless.

## Audit checklist

Run against the finished redline:

- [ ] Every suggestion classified correctly — no swap that should have been an insertion or deletion
- [ ] No match wider than the change it makes
- [ ] No anchor struck and re-added
- [ ] Mutuality items mirror the brand's wording rather than replacing it
- [ ] No bracketed commentary anywhere in the body
- [ ] Out-of-scope items struck, not replaced with explanations or prohibitions
- [ ] **No struck condition leaves a stub** — where the words answered when, how much or on what
      condition, a cross-reference to the governing clause replaces them
- [ ] **No deletion that changes nothing** — redundant brand wording left where it is
- [ ] **New definitions sit at first use or in the definitions section**, not appended to an
      unrelated clause
- [ ] **Every number moved in the creator's direction** — checked against the Direction column,
      including numbers the creator supplied
- [ ] No invented figures; all numbers traceable to the correspondence or flagged
- [ ] Related clauses edited on consistent reasoning
- [ ] Every checklist **sub-check** marked for change is actually present in the document
- [ ] No clause closed on the strength of an edit to its tail while its head is untouched
- [ ] **Every limb of a narrowed trigger is narrowed** — one qualifier over the whole list, or each limb in turn
- [ ] Every party swap re-read for verb agreement, negation, and possessives
- [ ] **No mirrored carve-out swallows the clause it sits in** — a brand indemnity excepts the
      creator's material breach, gross negligence or willful misconduct, not their "acts or omissions"
- [ ] **No pronoun for the creator** — "Influencer" / "Influencer's" throughout new text
- [ ] No malformed punctuation where a phrase was inserted beside, or struck from between, existing commas or periods
- [ ] **No new duty binds a party that did not sign** — on an agency deal, "Agency shall, and shall cause Client to", not "Agency and Client shall"
- [ ] **Every party name in new text is a term the contract defines** — including wording taken from the checklist or chosen by the creator
- [ ] **No blank placeholders anywhere except the signature block** — search for runs of underscores
- [ ] **Party names, entities, dates and figures checked against the correspondence** — placeholders
      do not always look like blanks
- [ ] **Every defect found in an earlier pass verified fixed by name**, not assumed
- [ ] Exhibits and schedules referenced by an edited sentence checked in their own right
- [ ] **Deleting a whole paragraph or bullet also deletes its paragraph mark** — otherwise an empty line or bullet survives acceptance
- [ ] **No strike widened to make an anchor unique** — a non-unique word was located inside a unique context instead
- [ ] **No clause left contradicting itself** — adverse wording removed, not merely carved out beside
- [ ] **No run had its `<w:rPr>` rebuilt from scratch** — copy and modify, never reconstruct, or the run silently inherits a different default
- [ ] **Character formatting on surviving text is unchanged** — check per character, not per run, since editing one word splits the run around it
- [ ] **Inserted text renders at the document's size and face** — no run inheriting docDefaults, no non-breaking spaces standing in for a tab stop
- [ ] Marked-up clauses read as coherent prose; defined terms exist and resolve
- [ ] Where a duplicated paragraph was fixed, both copies were handled
- [ ] **The file parses.** Every part of the `.docx` is well-formed XML and a
      document library opens it. No regex check in the audit script can see this,
      and a corrupt file passes all of them
- [ ] **No edit spanned an element boundary** — a `<w:hyperlink>`, a table cell, a
      paragraph mark. The flat text hides these, and replacing across one deletes
      the markup in between
- [ ] **No deletion bundles a sentence the brand would concede with one it will
      refuse** — the suggestion is the unit of acceptance
- [ ] **Nothing in the redline asks for something the counterparty structurally
      cannot give**, unless the creator decided to ask anyway with that understood
